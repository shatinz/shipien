import os
import sys
import json
import time
import asyncio
import re
import requests
import paramiko
from telethon import TelegramClient, events

# Configuration Constants
SSH_HOST = "136.244.111.62"
SSH_USER = "root"
SSH_KEY_PATH = os.path.expanduser(r"C:\Users\PC\.ssh\id_ed25519")
REMOTE_DIR = "/root/shipien"

LOCAL_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

# Loaded from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
ADMIN_ID = 8373593549

# Session file path for Telethon
SESSION_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "product_manager")

# Load Telegram config
TELEGRAM_CONFIG_PATH = r"C:\Users\PC\.gemini\config\skills\telegram_agent\config.json"
try:
    with open(TELEGRAM_CONFIG_PATH, "r") as f:
        tg_config = json.load(f)
    api_id = tg_config["accounts"]["shipien"]["api_id"]
    api_hash = tg_config["accounts"]["shipien"]["api_hash"]
except Exception as e:
    print(f"Error loading Telegram config: {e}")
    # Fallback default values
    api_id = 32873433
    api_hash = "b68947d35939e8bae141919ce5510204"

# Initialize Telethon Client
client = TelegramClient(SESSION_PATH, api_id, api_hash)

# State File
STATE_FILE = os.path.join(LOCAL_DATA_DIR, "STATE.json")

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"last_run": 0, "proposals": []}

def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=2)
    except Exception as e:
        print(f"Error saving state: {e}")

# SFTP Sync Function
def sync_data():
    print("Syncing data from server...")
    import subprocess
    try:
        # Download files using SCP command line
        for filename in ["users.json", "plans.json", "prize_codes.json"]:
            remote_path = f"new-server:{REMOTE_DIR}/{filename}"
            local_path = os.path.join(LOCAL_DATA_DIR, filename)
            
            # Run SCP command
            cmd = ["scp", "-o", "StrictHostKeyChecking=accept-new", remote_path, local_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                print(f"Synced {filename}")
            else:
                # If file doesn't exist on server, scp might fail with exit code 1 (normal if new deployment)
                print(f"Note on {filename} sync: {res.stderr.strip()}")
        return True
    except Exception as e:
        print(f"SCP sync failed: {e}")
        return False


# Analysis Function
def analyze_business():
    users_path = os.path.join(LOCAL_DATA_DIR, "users.json")
    plans_path = os.path.join(LOCAL_DATA_DIR, "plans.json")
    
    if not os.path.exists(users_path) or not os.path.exists(plans_path):
        return "No data synced yet or missing database files."

    try:
        with open(users_path, "r", encoding="utf-8") as f:
            users_data = json.load(f)
        with open(plans_path, "r", encoding="utf-8") as f:
            plans_data = json.load(f)
    except Exception as e:
        return f"Error reading data files: {e}"

    total_users = len(users_data)
    user_types = {}
    total_sales = 0
    total_purchases_count = 0
    total_debt = 0
    
    for uid, u in users_data.items():
        utype = u.get("user_type", "new")
        user_types[utype] = user_types.get(utype, 0) + 1
        buy_count = u.get("buy_count", 0)
        total_purchases_count += buy_count
        total_debt += u.get("debt", 0)
        
        # Estimate purchases based on history
        history = u.get("purchase_history", [])
        for item in history:
            plan_key = item.get("plan_key")
            # Get plan price (regular or trusted)
            plan_info = plans_data.get("plans", {}).get(plan_key, {})
            price_fa = plan_info.get("price", {}).get("fa", "0")
            if utype == "trusted_seller":
                price_fa = plan_info.get("trusted_price", plan_info.get("price", {})).get("fa", "0")
            
            price_digits = "".join(re.findall(r"\d+", price_fa))
            price_num = int(price_digits) if price_digits else 0
            total_sales += price_num

    plans_inventory = {}
    plans_section = plans_data.get("plans", {})
    for plan_key, p in plans_section.items():
        plans_inventory[plan_key] = {
            "name": p.get("name", {}).get("en", plan_key),
            "links_remaining": len(p.get("links", [])),
            "price_fa": p.get("price", {}).get("fa", "0")
        }

    summary = f"""Business Status Summary:
- Total registered users: {total_users}
- User Tiers Breakdown: {user_types}
- Total estimated sales: {total_sales:,} tomans (across {total_purchases_count} checkouts)
- Outstanding partner debt: {total_debt:,} tomans
- Inventory Stock levels:
"""
    for pk, info in plans_inventory.items():
        summary += f"  * {info['name']} (ID: {pk}): {info['links_remaining']} configs remaining (Price: {info['price_fa']})\n"
        
    return summary

# Gemini API Integration
def call_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=20)
        if resp.status_code == 200:
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return f"Error contacting Gemini API (Status {resp.status_code}): {resp.text}"
    except Exception as e:
        return f"Exception contacting Gemini API: {e}"

# Core Daily Loop Logic
async def run_daily_pm_loop(force=False):
    state = load_state()
    now = time.time()
    
    # Run once every 24 hours (86400 seconds) unless forced
    if not force and (now - state.get("last_run", 0)) < 86400:
        return
        
    print("Running Product Manager Loop...")
    sync_success = sync_data()
    
    summary = analyze_business()
    
    prompt = f"""You are the autonomous AI Product Manager for Shipien, a premium VPN selling bot operating in Iran.
Your goal is to optimize VPN sales, improve user experience, manage pricing/tiers, monitor server load, and alert the admin about inventory issues.
Shipien buys VPS units when needed, creates configurations (links), sells them for a profit, or deletes/scales them down to save cost.

Here is the current business status synced from the production server:
{summary}

Write a detailed Product Manager Report for the owner (the admin).
Include:
1. **Critical Alerts:** (e.g. if any plan has 0 links remaining, warn that checkouts will fail, and suggest buying/setting up a new VPS node to restock).
2. **Sales & growth ideas:** Propose changes in prices, tiers, or referral program bonuses.
3. **UX & Product suggestions:** (e.g. promoting regular buyers to trusted sellers or 'old users' to unlock card payment).
4. **Action Items:** Short, actionable checklist for the owner.

Format your response as a polished, concise, Telegram-friendly markdown message. Start with "📊 *Product Manager Daily Report*".
"""
    report = call_gemini(prompt)
    
    # Send report to owner
    try:
        await client.send_message(ADMIN_ID, report)
        print("Report sent successfully to admin.")
    except Exception as e:
        print(f"Failed to send report to admin: {e}")
        
    state["last_run"] = now
    state["last_report"] = report
    save_state(state)

# Background Loop
async def background_scheduler():
    while True:
        try:
            await run_daily_pm_loop()
        except Exception as e:
            print(f"Error in scheduler loop: {e}")
        await asyncio.sleep(3600)  # Check every hour

# Telegram Chat Handlers
@client.on(events.NewMessage(chats=ADMIN_ID))
async def handle_admin_messages(event):
    message_text = event.raw_text.strip()
    print(f"Received message from admin: {message_text}")
    
    if message_text.lower() == "/status":
        sync_data()
        summary = analyze_business()
        await event.reply(f"📡 *Shipien Status Update*\n\n```{summary}```", parse_mode='Markdown')
        return
        
    if message_text.lower() == "/sync":
        success = sync_data()
        if success:
            await event.reply("✅ Data successfully synced from server!")
        else:
            await event.reply("❌ SFTP sync failed. Check terminal logs.")
        return
        
    if message_text.lower() == "/run":
        await event.reply("⏳ Running Product Manager analysis now...")
        await run_daily_pm_loop(force=True)
        return
        
    # Generate conversational AI response
    await event.respond("⏳ *Product Manager is typing...*")
    
    summary = analyze_business()
    state = load_state()
    
    prompt = f"""You are the autonomous AI Product Manager for Shipien VPN. You are chatting in real-time with the owner/admin.
You must be helpful, professional, and strategic, offering suggestions for VPN inventory, pricing, customer retention, and operations.

Current business metrics:
{summary}

Owner says: "{message_text}"

Formulate a concise, direct reply in Markdown. Offer ideas, answer their questions, or suggest running specific actions (like `/run` or `/sync`).
"""
    reply = call_gemini(prompt)
    await event.reply(reply)

# Main Executable
async def main():
    print("Starting Product Manager Agent Client...")
    await client.start()
    
    # Run once immediately on start
    await run_daily_pm_loop(force=False)
    
    # Start scheduler task in background
    client.loop.create_task(background_scheduler())
    
    print("Product Manager Agent is running and listening for Telegram commands.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    # Run client
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Agent stopped by user.")

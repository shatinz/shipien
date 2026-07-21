import subprocess
import time
import os
import sys
import telebot

# Add directory to sys.path to import from configs
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from configs import TOKEN, ADMIN_ID
except ImportError:
    print("Error: Could not import configs.py. Make sure watchdog.py is run in /root/shipien.")
    sys.exit(1)

bot = telebot.TeleBot(TOKEN)

# Thresholds
RAM_THRESHOLD = 85.0      # Warning threshold to clear cache
CRITICAL_RAM_THRESHOLD = 95.0  # Critical warning threshold
ALERT_COOLDOWN = 600      # 10 minutes cooldown between alerts

last_alert_time = 0

def get_ram_usage():
    try:
        meminfo = {}
        with open('/proc/meminfo', 'r') as f:
            for line in f:
                parts = line.split(':')
                if len(parts) == 2:
                    meminfo[parts[0].strip()] = int(parts[1].split()[0])
        
        total = meminfo.get('MemTotal', 1)
        available = meminfo.get('MemAvailable', 0)
        used = total - available
        percent = (used / total) * 100.0
        return percent, total // 1024, available // 1024
    except Exception as e:
        print(f"Error reading RAM: {e}")
        return 0.0, 0, 0

def get_cpu_load():
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip().split()
        return load[0], load[1], load[2]
    except Exception as e:
        print(f"Error reading CPU: {e}")
        return "N/A", "N/A", "N/A"

def get_disk_usage():
    try:
        res = subprocess.check_output("df -h / | tail -n 1", shell=True).decode().split()
        if len(res) >= 5:
            return res[4], res[3]  # (Used%, Available size)
        return "N/A", "N/A"
    except Exception as e:
        print(f"Error reading disk: {e}")
        return "N/A", "N/A"

def get_top_processes():
    try:
        # Get top 5 RAM consuming processes
        cmd = "ps -eo %mem,%cpu,comm --sort=-%mem | head -n 6"
        res = subprocess.check_output(cmd, shell=True).decode().strip()
        return res
    except Exception as e:
        return f"Error getting processes: {e}"

def clear_caches():
    try:
        # sync dirty pages to disk first
        subprocess.run("sync", shell=True)
        # Clear pagecache, dentries, and inodes
        with open("/proc/sys/vm/drop_caches", "w") as f:
            f.write("3")
        return True
    except Exception as e:
        print(f"Error clearing cache: {e}")
        return False

def escape_md(text):
    if not text: return ""
    return str(text).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')

def main():
    global last_alert_time
    print("Shipien Watchdog Service started.")
    
    # Wait for bot setup to stabilize on startup
    time.sleep(10)
    
    while True:
        try:
            ram_pct, ram_total, ram_avail = get_ram_usage()
            load1, load5, load15 = get_cpu_load()
            disk_pct, disk_avail = get_disk_usage()
            
            # Check if RAM is exceeding threshold
            if ram_pct >= RAM_THRESHOLD:
                # Store original RAM status
                before_avail = ram_avail
                
                # Trigger self-healing cache clear
                clear_success = clear_caches()
                
                # Check RAM status after clearing
                time.sleep(2)  # Wait for kernel to update stats
                ram_pct_after, ram_total_after, ram_avail_after = get_ram_usage()
                freed_ram = ram_avail_after - before_avail
                
                now = time.time()
                # Check cooldown to avoid alerting spam
                if (now - last_alert_time) >= ALERT_COOLDOWN:
                    top_procs = get_top_processes()
                    
                    status_emoji = "⚠️" if ram_pct_after < CRITICAL_RAM_THRESHOLD else "🚨"
                    alert_title = "*System Healing Alert*" if ram_pct_after < CRITICAL_RAM_THRESHOLD else "*System CRITICAL Alert*"
                    
                    message = (
                        f"{status_emoji} {alert_title}\n\n"
                        f"🖥️ *Resource Usage Update:*\n"
                        f"• *RAM:* `{ram_pct:.1f}%` ({ram_total - ram_avail}MB / {ram_total}MB)\n"
                        f"• *CPU Load (1m, 5m, 15m):* `{load1}`, `{load5}`, `{load15}`\n"
                        f"• *Disk Space Used:* `{disk_pct}` (Free: `{disk_avail}`)\n\n"
                        f"🔧 *Self-Healing Action:*\n"
                        f"• Clearing page/inode caches: {'✅ Success' if clear_success else '❌ Failed'}\n"
                        f"• RAM recovered: `{freed_ram} MB` (New usage: `{ram_pct_after:.1f}%`)\n\n"
                        f"📋 *Top Resource Consuming Processes:*\n"
                        f"```\n{top_procs}\n```"
                    )
                    
                    try:
                        bot.send_message(ADMIN_ID, message, parse_mode='Markdown')
                        last_alert_time = now
                    except Exception as telegram_err:
                        print(f"Failed to send Telegram alert: {telegram_err}")
            
        except Exception as err:
            print(f"Error in watchdog loop: {err}")
            
        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    main()

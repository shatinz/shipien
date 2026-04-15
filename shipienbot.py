import telebot
from telebot import types
from configs import TOKEN, ADMIN_ID, CARD_NUMBER
import json
import os
import threading
import time

# Language dictionary
LANGS = {
    'en': {
        'welcome': "Welcome to Shipien VPN! 🚀\nPlease choose your language:\n\nخوش آمدید! لطفا زبان خود را انتخاب کنید.",
        'main_menu': "Main Menu:",
        'plans': "💎 Available VPN Plans:\n\nChoose a plan below to continue.",
        'receipt_received': "✅ Your payment receipt has been received. Please wait for admin approval.",
        'link_sent': "🎉 Your VPN link is ready:",
        'rejected': "❌ Your payment was not approved. Please contact support.",
        'no_links': "😔 Server is full for this plan. We will recharge soon. Please try again later.",
        'admin_no_links': "[ADMIN] Out of links for plan: {plan}",
        'admin_one_left': "[ADMIN] Only 1 link left for plan: {plan}",
        'help': "Use the menu below to navigate.",
        'already_trial': "⚠️ You have already used your free trial.",
        'select_plan': "⚠️ Please select a plan from '💎 VPN Plans' first.",
        'after_choose_plan': "You have chosen: *{plan}*\nPrice: *{price}*\n\n💳 Pay to card: `{card}`\n\nAfter payment, send the receipt (photo or text) here. ⬇️",
        'back': '⬅️ Back',
        'show_plans': '💎 VPN Plans',
        'my_info': '👤 My Info',
        'contact_admin': '📬 Message Admin',
        'msg_to_admin_prompt': '📝 Please send your message for the admin below:',
        'msg_sent_to_admin': '✅ Your message has been sent to the admin. We will reply shortly.',
        'admin_new_msg': '📬 New message from user `{user_id}` (@{username}):\n\n{text}',
        'admin_reply_btn': 'Reply',
        'reply_to_user_prompt': 'Enter your reply for user `{user_id}`:',
        'reply_sent': '✅ Your reply has been sent to the user.',
        'msg_from_admin': '🔔 *Reply from Admin:*\n\n{text}',
        'choose_lang_btn': '🌐 Change Language'
    },
    'fa': {
        'welcome': "به شیپین وی‌پی‌ان خوش آمدید! 🚀\nلطفا زبان خود را انتخاب کنید:\n\nWelcome! Please choose your language.",
        'main_menu': "منوی اصلی:",
        'plans': "💎 پلن‌های موجود:\n\nیکی از پلن‌ها را برای ادامه انتخاب کنید.",
        'receipt_received': "✅ رسید پرداخت شما دریافت شد. لطفا منتظر تایید ادمین باشید.",
        'link_sent': "🎉 لینک VPN شما آماده است:",
        'rejected': "❌ پرداخت شما تایید نشد. لطفا با پشتیبانی تماس بگیرید.",
        'no_links': "😔 ظرفیت این پلن پر شده است. به زودی شارژ خواهد شد. لطفا بعدا تلاش کنید.",
        'admin_no_links': "[ادمین] لینک برای پلن {plan} تمام شد.",
        'admin_one_left': "[ادمین] فقط ۱ لینک برای پلن {plan} باقی مانده است.",
        'help': "از منوی زیر برای جابجایی استفاده کنید.",
        'already_trial': "⚠️ شما قبلاً از تست رایگان استفاده کرده‌اید.",
        'select_plan': "⚠️ لطفاً ابتدا از بخش '💎 پلن‌های VPN' یک پلن انتخاب کنید.",
        'after_choose_plan': "شما پلن *{plan}* را انتخاب کردید.\nقیمت: *{price}*\n\n💳 واریز به کارت: `{card}`\n\nبعد از پرداخت، رسید را (عکس یا متن) در زیر ارسال کنید. ⬇️",
        'back': '⬅️ بازگشت',
        'show_plans': '💎 پلن‌های VPN',
        'my_info': '👤 اطلاعات من',
        'contact_admin': '📬 پیام به ادمین',
        'msg_to_admin_prompt': '📝 لطفا پیام خود را برای ادمین در زیر ارسال کنید:',
        'msg_sent_to_admin': '✅ پیام شما برای ادمین ارسال شد. به زودی پاسخ خواهیم داد.',
        'admin_new_msg': '📬 پیام جدید از کاربر `{user_id}` (@{username}):\n\n{text}',
        'admin_reply_btn': 'پاسخ',
        'reply_to_user_prompt': 'پاسخ خود را برای کاربر `{user_id}` وارد کنید:',
        'reply_sent': '✅ پاسخ شما برای کاربر ارسال شد.',
        'msg_from_admin': '🔔 *پاسخ ادمین:*\n\n{text}',
        'choose_lang_btn': '🌐 تغییر زبان'
    }
}

USERS_FILE = 'users.json'
PLANS_FILE = 'plans.json'

def load_json(filename, default_val):
    try:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
    return default_val

def save_json(filename, data):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

users = load_json(USERS_FILE, {})
plans_data = load_json(PLANS_FILE, {})

def update_user(user_id, **kwargs):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {}
    users[user_id].update(kwargs)
    save_json(USERS_FILE, users)

def get_user_lang(user_id):
    return users.get(str(user_id), {}).get('lang', 'en')

bot = telebot.TeleBot(TOKEN)

def generate_and_send_report(bot, chat_id):
    try:
        total_users = len(users)
        status_counts = {}
        for u in users.values():
            s = u.get('status', 'unknown')
            status_counts[s] = status_counts.get(s, 0) + 1
        
        report = f"📊 *Shipien Status Report*\n\n"
        report += f"✅ *Bot Status:* `Running`\n"
        report += f"👥 *Total Users:* `{total_users}`\n"
        report += f"📈 *Statuses Summary:*\n"
        for s, count in status_counts.items():
            report += f"- {s}: `{count}`\n"
        
        report += f"\n💎 *VPN Links Remaining:*\n"
        for plan_key, data in plans_data.items():
            links_count = len(data.get('links', []))
            report += f"- {plan_key}: `{links_count}`\n"
        
        bot.send_message(chat_id, report, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Error sending report: {e}")

def send_backups(bot, chat_id):
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'rb') as f:
                bot.send_document(chat_id, f, caption="📂 *Users Database Backup* (JSON)", parse_mode='Markdown')
        if os.path.exists(PLANS_FILE):
            with open(PLANS_FILE, 'rb') as f:
                bot.send_document(chat_id, f, caption="📂 *Plans & Links Database Backup* (JSON)", parse_mode='Markdown')
    except Exception as e:
        print(f"Error sending backups: {e}")

def daily_report_loop():
    time.sleep(10) # Wait for bot to initialize
    while True:
        generate_and_send_report(bot, ADMIN_ID)
        send_backups(bot, ADMIN_ID)
        time.sleep(86400) # 24 hours

# Start the reporting thread in background
threading.Thread(target=daily_report_loop, daemon=True).start()

# Main Menu Generator
def get_main_menu(user_id):
    lang = get_user_lang(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton(LANGS[lang]['show_plans']),
        types.KeyboardButton(LANGS[lang]['my_info'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['contact_admin']),
        types.KeyboardButton(LANGS[lang]['choose_lang_btn'])
    )
    return markup

# Admin Dashboard
@bot.message_handler(commands=['admin'], func=lambda m: str(m.chat.id) == str(ADMIN_ID))
def admin_dashboard(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚙️ Manage Plans & Links", callback_data="admin_manage_plans"))
    markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast_start"))
    markup.add(types.InlineKeyboardButton("📊 Get Status Report", callback_data="admin_get_report"))
    bot.send_message(ADMIN_ID, "--- 🛠 Admin Dashboard ---", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_get_report")
def admin_get_report(call):
    generate_and_send_report(bot, ADMIN_ID)
    send_backups(bot, ADMIN_ID)
    bot.answer_callback_query(call.id, "Report and Backups generated!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_manage_plans")
def admin_manage_plans(call):
    markup = types.InlineKeyboardMarkup()
    for plan_key, data in plans_data.items():
        name = data['name']['en']
        links_count = len(data.get('links', []))
        markup.add(types.InlineKeyboardButton(f"{name} ({links_count})", callback_data=f"admin_view_plan_{plan_key}"))
    
    markup.add(types.InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_back_to_dash"))
    bot.edit_message_text("Select a plan to manage:", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_view_plan_"))
def admin_view_plan(call):
    plan_key = call.data.replace("admin_view_plan_", "")
    if plan_key not in plans_data:
        bot.answer_callback_query(call.id, "Plan not found.")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("➕ Bulk Add Links", callback_data=f"admin_bulkadd_links_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🗑 List/Delete Links", callback_data=f"admin_list_links_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Plans", callback_data="admin_manage_plans"))
    
    name = plans_data[plan_key]['name']['en']
    bot.edit_message_text(f"Plan: {name}\nSelect action:", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_bulkadd_links_"))
def admin_bulkadd_prompt(call):
    plan_key = call.data.replace("admin_bulkadd_links_", "")
    update_user(ADMIN_ID, admin_state=f"bulkadd_{plan_key}")
    bot.edit_message_text(f"Send the links for {plan_key} (one per line):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_back_to_dash")
def admin_back_to_dash(call):
    admin_dashboard(call.message)
    bot.delete_message(ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_broadcast_start")
def admin_broadcast_prompt(call):
    update_user(ADMIN_ID, admin_state="admin_broadcast_start")
    bot.edit_message_text("Send the message for ALL users:", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_reply_user_"))
def admin_reply_prompt(call):
    user_id = call.data.replace("admin_reply_user_", "")
    update_user(ADMIN_ID, admin_state=f"reply_to_{user_id}")
    lang = get_user_lang(ADMIN_ID)
    bot.send_message(ADMIN_ID, LANGS[lang]['reply_to_user_prompt'].format(user_id=user_id))
    bot.answer_callback_query(call.id)

# User Interface Handlers
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('English 🇬🇧', callback_data='lang_en'))
    markup.add(types.InlineKeyboardButton('فارسی 🇮🇷', callback_data='lang_fa'))
    
    bot.send_message(message.chat.id, LANGS['en']['welcome'], reply_markup=markup)
    update_user(message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        status='started')

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_lang_callback(call):
    lang = call.data.split('_')[1]
    update_user(call.message.chat.id, lang=lang)
    bot.send_message(call.message.chat.id, LANGS[lang]['main_menu'], reply_markup=get_main_menu(call.message.chat.id))
    bot.answer_callback_query(call.id)
    bot.delete_message(call.message.chat.id, call.message.message_id)

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['show_plans'], LANGS['fa']['show_plans']])
def show_plans(message):
    lang = get_user_lang(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    available_plans = {k: v for k, v in plans_data.items() if len(v.get('links', [])) > 0}
    
    if not available_plans:
        bot.send_message(message.chat.id, LANGS[lang]['no_links'])
        return

    for plan_key, data in available_plans.items():
        name = data['name'].get(lang, data['name']['en'])
        price = data['price'].get(lang, data['price']['en'])
        markup.add(types.InlineKeyboardButton(f"{name} - {price}", callback_data=f"select_plan_{plan_key}"))
    
    bot.send_message(message.chat.id, LANGS[lang]['plans'], reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['my_info'], LANGS['fa']['my_info']])
def show_my_info(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    u = users.get(user_id, {})
    
    status = u.get('status', 'N/A')
    trial = "Used" if u.get('trial_used') else "Not Used"
    
    if lang == 'fa':
        info = f"👤 *اطلاعات من*\n\nشناسه کاربر: `{user_id}`\nوضعیت: {status}\nتست رایگان: {'استفاده شده' if u.get('trial_used') else 'استفاده نشده'}"
    else:
        info = f"👤 *My Info*\n\nUser ID: `{user_id}`\nStatus: {status}\nTrial: {trial}"
    
    bot.send_message(message.chat.id, info, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['contact_admin'], LANGS['fa']['contact_admin']])
def contact_admin(message):
    lang = get_user_lang(message.chat.id)
    update_user(message.chat.id, user_state='waiting_for_admin_msg')
    bot.send_message(message.chat.id, LANGS[lang]['msg_to_admin_prompt'])

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['choose_lang_btn'], LANGS['fa']['choose_lang_btn']])
def change_lang(message):
    start(message)

# Text and Media handling
@bot.message_handler(content_types=['photo', 'text'])
def handle_all_messages(message):
    user_id = str(message.chat.id)
    u = users.get(user_id, {})
    lang = get_user_lang(user_id)
    
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return

    # Handle Admin States
    if user_id == str(ADMIN_ID) and u.get('admin_state'):
        state = u.get('admin_state')
        
        if state.startswith("bulkadd_"):
            plan_key = state.replace("bulkadd_", "")
            links = [line.strip() for line in message.text.split('\n') if line.strip()]
            if links:
                plans_data[plan_key].setdefault('links', []).extend(links)
                save_json(PLANS_FILE, plans_data)
                bot.send_message(ADMIN_ID, f"Added {len(links)} links. Total: {len(plans_data[plan_key]['links'])}")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state == "admin_broadcast_start":
            text = message.text.strip()
            success = 0
            for uid in users:
                try:
                    bot.send_message(uid, text)
                    success += 1
                except: pass
            update_user(ADMIN_ID, admin_state=None)
            bot.send_message(ADMIN_ID, f"Broadcast sent to {success} users.")
            admin_dashboard(message)
            return

        elif state.startswith("reply_to_"):
            target_uid = state.split('_')[2]
            target_lang = get_user_lang(target_uid)
            try:
                bot.send_message(target_uid, LANGS[target_lang]['msg_from_admin'].format(text=message.text), parse_mode='Markdown')
                bot.send_message(ADMIN_ID, LANGS[lang]['reply_sent'])
            except:
                bot.send_message(ADMIN_ID, "Failed to send message.")
            update_user(ADMIN_ID, admin_state=None)
            return

    # Handle User States
    if u.get('user_state') == 'waiting_for_admin_msg':
        update_user(user_id, user_state=None)
        caption = LANGS['en']['admin_new_msg'].format(user_id=user_id, username=message.from_user.username or 'N/A', text=message.text or '[Media]')
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(LANGS['en']['admin_reply_btn'], callback_data=f"admin_reply_user_{user_id}"))
        bot.send_message(ADMIN_ID, caption, reply_markup=markup, parse_mode='Markdown')
        bot.send_message(user_id, LANGS[lang]['msg_sent_to_admin'])
        return

    # Handle Receipts
    plan_key = u.get('pending_plan')
    if plan_key and (message.content_type == 'photo' or (message.text and not message.text.startswith('/'))):
        plan_info = plans_data.get(plan_key)
        if not plan_info: return
        
        caption = f"💰 *Payment Receipt*\nUser: `{user_id}`\nUsername: @{message.from_user.username or '-'}\nPlan: {plan_info['name']['en']}"
        markup = types.InlineKeyboardMarkup()
        links = plan_info.get('links', [])
        for i in range(min(5, len(links))):
            markup.add(types.InlineKeyboardButton(f"✅ Approve #{i+1}", callback_data=f"admin_approve_{user_id}_{plan_key}_{i}"))
        markup.add(types.InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user_id}"))
        
        if message.content_type == 'photo':
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.send_message(ADMIN_ID, caption + f"\n\nText: {message.text}", reply_markup=markup, parse_mode='Markdown')
        
        bot.send_message(user_id, LANGS[lang]['receipt_received'])
        update_user(user_id, status='pending_approval')
        return

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_plan_'))
def select_plan_callback(call):
    plan_key = call.data.replace('select_plan_', '')
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    
    if plan_key not in plans_data: return
    plan_info = plans_data[plan_key]
    links = plan_info.get('links', [])
    
    if not links:
        bot.answer_callback_query(call.id, LANGS[lang]['no_links'], show_alert=True)
        return
    
    if plan_info.get('is_trial'):
        if users.get(user_id, {}).get('trial_used'):
            bot.answer_callback_query(call.id, LANGS[lang]['already_trial'], show_alert=True)
            return
        
        link = links.pop(0)
        save_json(PLANS_FILE, plans_data)
        update_user(user_id, trial_used=True, status='approved', last_plan=plan_key)
        bot.send_message(user_id, f"{LANGS[lang]['link_sent']}\n\n`{link}`", parse_mode='Markdown')
        bot.answer_callback_query(call.id, "Trial link sent!")
        return

    update_user(user_id, pending_plan=plan_key)
    name = plan_info['name'].get(lang, plan_info['name']['en'])
    price = plan_info['price'].get(lang, plan_info['price']['en'])
    msg = LANGS[lang]['after_choose_plan'].format(plan=name, price=price, card=CARD_NUMBER)
    bot.send_message(user_id, msg, parse_mode='Markdown', reply_markup=get_main_menu(user_id))
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_approve_') or call.data.startswith('admin_reject_'))
def admin_process_receipt(call):
    data = call.data.split('_')
    action = data[1]
    target_uid = data[2]
    lang = get_user_lang(target_uid)
    
    if action == 'approve':
        # data format: admin_approve_{user_id}_{plan_key}_{idx}
        idx = int(data[-1])
        plan_key = "_".join(data[3:-1])
        if plan_key in plans_data and idx < len(plans_data[plan_key]['links']):
            link = plans_data[plan_key]['links'].pop(idx)
            save_json(PLANS_FILE, plans_data)
            update_user(target_uid, status='approved', last_plan=plan_key, pending_plan=None)
            bot.send_message(target_uid, f"{LANGS[lang]['link_sent']}\n\n`{link}`", parse_mode='Markdown')
            bot.answer_callback_query(call.id, "Approved!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(ADMIN_ID, f"✅ User {target_uid} approved for {plan_key}.")
        else:
            bot.answer_callback_query(call.id, "Error: Link missing.")
    elif action == 'reject':
        update_user(target_uid, status='rejected', pending_plan=None)
        bot.send_message(target_uid, LANGS[lang]['rejected'])
        bot.answer_callback_query(call.id, "Rejected.")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_list_links_"))
def admin_list_links(call):
    plan_key = call.data.replace("admin_list_links_", "")
    links = plans_data.get(plan_key, {}).get('links', [])
    markup = types.InlineKeyboardMarkup()
    for i, link in enumerate(links):
        markup.add(types.InlineKeyboardButton(f"🗑 {i}: {link[:30]}...", callback_data=f"admin_del_link_{plan_key}_{i}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"admin_view_plan_{plan_key}"))
    bot.edit_message_text(f"Links for {plan_key}:", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_del_link_"))
def admin_del_link(call):
    # data format: admin_del_link_{plan_key}_{idx}
    temp = call.data.replace("admin_del_link_", "")
    plan_key, idx_str = temp.rsplit("_", 1)
    idx = int(idx_str)
    if plan_key in plans_data and idx < len(plans_data[plan_key]['links']):
        plans_data[plan_key]['links'].pop(idx)
        save_json(PLANS_FILE, plans_data)
        admin_list_links(call)
    bot.answer_callback_query(call.id, "Deleted.")

print("Bot is running...")
bot.infinity_polling()

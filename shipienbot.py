import telebot
from telebot import types
from configs import TOKEN, ADMIN_ID
from vless import vless_trial, vless_week, vless_month, vless_3month
import json
import ast

# Language dictionary
LANGS = {
    'en': {
        'welcome': "Welcome! Please choose your language:\nخوش آمدید! لطفا زبان خود را انتخاب کنید.\nAdmin: @shipienadmin",
        'plans': "Available VPN Plans:\n1. 1-day Free Trial\n2. 1 Week (7GB): 55,000 Toman\n3. 1 Month (30GB): 200,000 Toman\n4. 2 Months (60GB): 350,000 Toman\n\nChoose a plan below to continue.",
        'buy': "To purchase, please pay to our account and send the payment receipt (photo or text) here.\n\nAfter payment, your request will be reviewed and you will receive your VPN link.",
        'receipt_received': "Your payment receipt has been received. Please wait for admin approval.",
        'link_sent': "Your VPN link:",
        'rejected': "Your payment was not approved. Please contact support.",
        'choose_link': "Select a VLESS link to send:",
        'no_links': "Server is full for this plan. We will recharge soon. Please try again later.",
        'admin_no_links': "[ADMIN] Out of links for plan: {plan}",
        'admin_one_left': "[ADMIN] Only 1 link left for plan: {plan}",
        'help': "Send /plans to see plans, or /start to restart.",
        'already_trial': "You have already used your free trial. Each user can only get one free trial.",
        'select_plan': "Please select a plan first using /plans.",
        'after_choose_plan': "You have chosen: {plan} with price {price}.\nPay to card: <> and send the receipt.",
        'back': 'Back',
    },
    'fa': {
        'welcome': "خوش آمدید! لطفا زبان خود را انتخاب کنید:\nWelcome! Please choose your language.\nادمین: @shipienadmin",
        'plans': "پلن های موجود:\n1. تست یک روزه رایگان\n2. یک هفته (۷ گیگ): ۵۵ هزار تومان\n3. یک ماهه (۳۰ گیگ): ۲۰۰ هزار تومان\n4. دو ماهه (۶۰ گیگ): ۳۵۰ هزار تومان\n\nیکی از پلن‌ها را انتخاب کنید.",
        'buy': "برای خرید، مبلغ را به حساب ما واریز کنید و رسید پرداخت (عکس یا متن) را اینجا ارسال کنید.\n\nپس از بررسی، لینک VPN برای شما ارسال می‌شود.",
        'receipt_received': "رسید پرداخت شما دریافت شد. لطفا منتظر تایید ادمین باشید.",
        'link_sent': "لینک VPN شما:",
        'rejected': "پرداخت شما تایید نشد. لطفا با پشتیبانی تماس بگیرید.",
        'choose_link': "یک لینک VLESS را انتخاب کنید:",
        'no_links': "سرور برای این پلن پر شده است. به زودی شارژ خواهد شد. لطفا بعدا تلاش کنید.",
        'admin_no_links': "[ادمین] لینک برای پلن {plan} تمام شد.",
        'admin_one_left': "[ادمین] فقط ۱ لینک برای پلن {plan} باقی مانده است.",
        'help': "برای مشاهده پلن‌ها /plans یا برای شروع مجدد /start را ارسال کنید.",
        'already_trial': "شما قبلاً از تست رایگان استفاده کرده‌اید. هر کاربر فقط یکبار می‌تواند تست رایگان دریافت کند.",
        'select_plan': "لطفاً ابتدا یک پلن را با /plans انتخاب کنید.",
        'after_choose_plan': "شما پلن {plan} با قیمت {price} را انتخاب کردید.\nبه کارت  < >  واریز کنید و رسید را ارسال نمایید.",
        'back': 'بازگشت',
    }
}

user_lang = {}
used_links = set()
USERS_FILE = 'users.json'
VLESS_FILE = 'vless.py'

def load_users():
    try:
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

users = load_users()

# Update user info helper
def update_user(user_id, **kwargs):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {}
    users[user_id].update(kwargs)
    save_users(users)

bot = telebot.TeleBot(TOKEN)

# Language selection
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('English', 'فارسی')
    bot.send_message(message.chat.id, LANGS['en']['welcome'], reply_markup=markup)
    # Track user basic info
    update_user(message.chat.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        status='started')

@bot.message_handler(func=lambda m: m.text in ['English', 'فارسی'])
def set_lang(message):
    lang = 'fa' if message.text == 'فارسی' else 'en'
    user_lang[message.chat.id] = lang
    update_user(message.chat.id, lang=lang)
    bot.send_message(message.chat.id, LANGS[lang]['help'], reply_markup=types.ReplyKeyboardRemove())

# Plan names and mapping
PLANS = {
    'trial': {'en': '1-day Free Trial', 'fa': 'تست یک روزه رایگان'},
    'week': {'en': '1 Week (7GB)', 'fa': 'یک هفته (۷ گیگ)'},
    'month': {'en': '1 Month (30GB)', 'fa': 'یک ماهه (۳۰ گیگ)'},
    '2month': {'en': '2 Months (60GB)', 'fa': 'دو ماهه (۶۰ گیگ)'},
}
PLAN_LISTS = {
    'trial': vless_trial,
    'week': vless_week,
    'month': vless_month,
    '2month': vless_3month,  # Use vless_3month for 2 month plan for now
}

PLAN_PRICES = {
    'trial': {'en': 'Free', 'fa': 'رایگان'},
    'week': {'en': '55,000 Toman', 'fa': '۵۵ هزار تومان'},
    'month': {'en': '200,000 Toman', 'fa': '۲۰۰ هزار تومان'},
    '2month': {'en': '350,000 Toman', 'fa': '۳۵۰ هزار تومان'},
}

# Add plan selection command
@bot.message_handler(commands=['plans'])
def plans(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for key in PLANS:
        markup.add(PLANS[key][lang])
    bot.send_message(message.chat.id, LANGS[lang]['plans'], reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in [PLANS[k]['en'] for k in PLANS] + [PLANS[k]['fa'] for k in PLANS])
def choose_plan(message):
    lang = user_lang.get(message.chat.id, 'en')
    # Find plan key
    plan = None
    for k in PLANS:
        if message.text in PLANS[k].values():
            plan = k
            break
    if plan == 'trial':
        # Check if user already had a trial
        u = users.get(str(message.chat.id), {})
        if u.get('trial_used'):
            bot.send_message(message.chat.id, LANGS[lang]['already_trial'])
            return
        # Send trial link immediately
        available_links = [i for i in range(len(PLAN_LISTS['trial']))]
        if not available_links:
            bot.send_message(message.chat.id, LANGS[lang]['no_links'])
            bot.send_message(ADMIN_ID, LANGS[lang]['admin_no_links'].format(plan=PLANS[plan][lang]))
            return
        if len(available_links) == 1:
            bot.send_message(ADMIN_ID, LANGS[lang]['admin_one_left'].format(plan=PLANS[plan][lang]))
        link_idx = available_links[0]
        update_user(message.chat.id, plan=plan, status='approved', link=PLAN_LISTS['trial'][link_idx], trial_used=True)
        bot.send_message(message.chat.id, LANGS[lang]['link_sent'])
        bot.send_message(message.chat.id, PLAN_LISTS['trial'][link_idx])
        remove_vless_link('trial', link_idx)
        return
    update_user(message.chat.id, plan=plan)
    # Add Back button
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(LANGS[lang]['back'])
    # Check for available links for paid plans
    available_links = [i for i in range(len(PLAN_LISTS[plan]))]
    if not available_links:
        bot.send_message(message.chat.id, LANGS[lang]['no_links'])
        bot.send_message(ADMIN_ID, LANGS[lang]['admin_no_links'].format(plan=PLANS[plan][lang]))
        return
    if len(available_links) == 1:
        bot.send_message(ADMIN_ID, LANGS[lang]['admin_one_left'].format(plan=PLANS[plan][lang]))
    bot.send_message(
        message.chat.id,
        LANGS[lang]['after_choose_plan'].format(plan=PLANS[plan][lang], price=PLAN_PRICES[plan][lang]),
        reply_markup=markup
    )

# Add 'Back' to LANGS
def ensure_back_in_langs():
    for l in LANGS:
        if 'back' not in LANGS[l]:
            LANGS[l]['back'] = 'Back' if l == 'en' else 'بازگشت'
ensure_back_in_langs()

# Handle Back button
@bot.message_handler(func=lambda m: m.text in [LANGS[l]['back'] for l in LANGS])
def back_to_plans(message):
    lang = user_lang.get(message.chat.id, 'en')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for key in PLANS:
        markup.add(PLANS[key][lang])
    bot.send_message(message.chat.id, LANGS[lang]['plans'], reply_markup=markup)

# Handle payment receipt (photo or text)
@bot.message_handler(content_types=['photo', 'text'])
def handle_receipt(message):
    if message.text and message.text.startswith('/'):
        return  # Ignore commands
    lang = user_lang.get(message.chat.id, 'en')
    u = users.get(str(message.chat.id), {})
    plan = u.get('plan')
    if not plan:
        bot.send_message(message.chat.id, LANGS[lang]['select_plan'])
        return
    # For trial, check if already used
    if plan == 'trial':
        if u.get('trial_used'):
            bot.send_message(message.chat.id, LANGS[lang]['already_trial'])
            return
        # Send trial link automatically
        available_links = [i for i in range(len(PLAN_LISTS['trial']))]
        if not available_links:
            bot.send_message(message.chat.id, LANGS[lang]['no_links'])
            bot.send_message(ADMIN_ID, LANGS[lang]['admin_no_links'].format(plan=PLANS[plan][lang]))
            return
        if len(available_links) == 1:
            bot.send_message(ADMIN_ID, LANGS[lang]['admin_one_left'].format(plan=PLANS[plan][lang]))
        link_idx = available_links[0]
        update_user(message.chat.id, status='approved', link=PLAN_LISTS['trial'][link_idx], trial_used=True)
        bot.send_message(message.chat.id, LANGS[lang]['link_sent'])
        bot.send_message(message.chat.id, PLAN_LISTS['trial'][link_idx])
        remove_vless_link('trial', link_idx)
        return
    # Only send receipt to admin for paid plans
    update_user(message.chat.id, status='pending')
    # Check for available links for paid plans before sending to admin
    available_links = [i for i in range(len(PLAN_LISTS[plan]))]
    if not available_links:
        bot.send_message(message.chat.id, LANGS[lang]['no_links'])
        bot.send_message(ADMIN_ID, LANGS[lang]['admin_no_links'].format(plan=PLANS[plan][lang]))
        return
    if len(available_links) == 1:
        bot.send_message(ADMIN_ID, LANGS[lang]['admin_one_left'].format(plan=PLANS[plan][lang]))
    # Forward to admin with inline buttons for the selected plan
    caption = f"Payment receipt from user {message.from_user.id}\nUsername: @{message.from_user.username or '-'}\nName: {message.from_user.first_name} {message.from_user.last_name or ''}\nPlan: {PLANS[plan][lang]}"
    markup = types.InlineKeyboardMarkup()
    for i in available_links:
        markup.add(types.InlineKeyboardButton(f"Send {PLANS[plan][lang]} #{i+1}", callback_data=f"sendlink_{message.from_user.id}_{plan}_{i}"))
    markup.add(types.InlineKeyboardButton(LANGS[lang]['no_links'], callback_data="nolinks"))
    markup.add(types.InlineKeyboardButton("Reject", callback_data=f"reject_{message.from_user.id}"))
    if plan != 'trial':
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            bot.send_photo(ADMIN_ID, file_id, caption=caption, reply_markup=markup)
        else:
            bot.send_message(ADMIN_ID, caption + f"\nText: {message.text}", reply_markup=markup)
        bot.send_message(message.chat.id, LANGS[lang]['receipt_received'])

# Admin button handler
@bot.callback_query_handler(func=lambda call: call.data.startswith('sendlink_') or call.data.startswith('reject_') or call.data == 'nolinks')
def admin_action(call):
    if str(call.from_user.id) != str(ADMIN_ID):
        bot.answer_callback_query(call.id, "Not authorized.")
        return
    if call.data == 'nolinks':
        bot.answer_callback_query(call.id, LANGS[user_lang.get(call.from_user.id, 'en')]['no_links'])
        return
    if call.data.startswith('reject_'):
        user_id = int(call.data.split('_')[1])
        lang = user_lang.get(user_id, 'en')
        update_user(user_id, status='rejected')
        bot.send_message(user_id, LANGS[lang]['rejected'])
        bot.answer_callback_query(call.id, LANGS[lang]['rejected'])
        return
    if call.data.startswith('sendlink_'):
        parts = call.data.split('_')
        user_id = int(parts[1])
        plan = parts[2]
        link_idx = int(parts[3])
        lang = user_lang.get(user_id, 'en')
        # For trial, mark as used
        if plan == 'trial':
            update_user(user_id, trial_used=True)
        update_user(user_id, status='approved', link=PLAN_LISTS[plan][link_idx])
        bot.send_message(user_id, LANGS[lang]['link_sent'])
        bot.send_message(user_id, PLAN_LISTS[plan][link_idx])
        bot.answer_callback_query(call.id, LANGS[lang]['link_sent'])
        # Remove the link from vless.py
        remove_vless_link(plan, link_idx)

# Helper to remove a link from the correct list in vless.py
def remove_vless_link(plan, idx):
    # Remove from memory
    PLAN_LISTS[plan].pop(idx)
    # Write back to vless.py
    with open(VLESS_FILE, 'r') as f:
        content = f.read()
    start = content.find(f'{plan}_')
    start = content.find('[', start)
    end = content.find(']', start)
    if start == -1 or end == -1:
        return
    links_list = ast.literal_eval(content[start:end+1])
    if 0 <= idx < len(links_list):
        links_list.pop(idx)
    new_content = content[:start] + str(links_list) + content[end+1:]
    with open(VLESS_FILE, 'w') as f:
        f.write(new_content)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    lang = user_lang.get(message.chat.id, 'en')
    bot.send_message(message.chat.id, LANGS[lang]['help'])

bot.polling()

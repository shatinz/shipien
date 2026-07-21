import telebot
from telebot import types
from configs import TOKEN, ADMIN_ID, CARD_NUMBER, TON_ADDRESS, TON_COMMENT, USDT_ERC20_ADDRESS, CHANNEL_ID
import json
import os
import threading
import time
import qrcode
import io
import requests
import re
import urllib.parse
import sqlite3
import random
import string
import uuid
import subprocess

def check_client_name_exists(name):
    import sqlite3
    db_path = "/usr/local/s-ui/db/s-ui.db"
    if not os.path.exists(db_path):
        return False
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM clients WHERE name = ?;", (name,))
        row = cursor.fetchone()
        return row is not None
    except Exception as e:
        print(f"Error checking client name existence: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def get_client_name_by_password(password):
    import sqlite3
    db_path = "/usr/local/s-ui/db/s-ui.db"
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, config FROM clients;")
        rows = cursor.fetchall()
        for name, config_bytes in rows:
            try:
                config_str = config_bytes.decode('utf-8')
                config_json = json.loads(config_str)
                for proto in config_json.values():
                    if isinstance(proto, dict) and proto.get('password') == password:
                        return name
            except Exception:
                continue
    except Exception as e:
        print(f"Error lookup client name: {e}")
    finally:
        if 'conn' in locals():
            conn.close()
    return None

def add_sui_client(remark, expiry_days, volume_gb, custom_name=None):
    import requests
    
    name = custom_name if custom_name else "".join(random.choices(string.ascii_letters + string.digits, k=8))
    password = "".join(random.choices(string.ascii_letters + string.digits, k=10))
    client_uuid = str(uuid.uuid4())
    
    config_dict = {
        "anytls": {"name": name, "password": password},
        "http": {"password": password, "username": name},
        "hysteria": {"auth_str": password, "name": name},
        "hysteria2": {"name": name, "password": password},
        "mixed": {"password": password, "username": name},
        "naive": {"password": password, "username": name},
        "shadowsocks": {"name": name, "password": "1IIJASI1IVtdx7bPMGyMOzIyS+VBVBFCi60mRtapX/Q="},
        "shadowsocks16": {"name": name, "password": "z09seDSz4la2sJV/hskfjw=="},
        "shadowtls": {"name": name, "password": "1IIJASI1IVtdx7bPMGyMOzIyS+VBVBFCi60mRtapX/Q="},
        "socks": {"password": password, "username": name},
        "trojan": {"name": name, "password": password},
        "tuic": {"name": name, "password": password, "uuid": client_uuid},
        "vless": {"flow": "xtls-rprx-vision", "name": name, "uuid": client_uuid},
        "vmess": {"alterId": 0, "name": name, "uuid": client_uuid}
    }
    
    volume_bytes = int(volume_gb * 1024 * 1024 * 1024) if volume_gb > 0 else 0
    expiry_ts = int(time.time() + expiry_days * 86400) if expiry_days > 0 else 0
    
    client_data = {
        "id": 0,
        "enable": True,
        "name": name,
        "inbounds": [1],
        "config": config_dict,
        "links": [],
        "volume": volume_bytes,
        "expiry": expiry_ts,
        "desc": remark,
        "group": "",
        "remark": remark
    }
    
    base_url = "http://h2.morningislighting.ir:2095/app/apiv2"
    token = "shipien_bot_token_2026"
    headers = {
        "Token": token
    }
    params = {
        "object": "clients",
        "action": "new",
        "data": json.dumps(client_data)
    }
    
    try:
        r = requests.post(f"{base_url}/save", params=params, headers=headers, timeout=10)
        r.raise_for_status()
        res = r.json()
        if not res.get("success"):
            raise Exception(res.get("msg", "Unknown API error"))
    except Exception as e:
        print(f"Error calling S-UI API: {e}")
        raise e
        
    db_path = "/usr/local/s-ui/db/s-ui.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT links FROM clients WHERE name = ?", (name,))
        row = cursor.fetchone()
        if not row or not row[0]:
            raise Exception(f"Client {name} links not found in database after API save")
        
        # links column is BLOB / bytes in sqlite3, decode and parse as JSON
        links_data = json.loads(row[0].decode('utf-8'))
        if not links_data or not isinstance(links_data, list):
            raise Exception("Invalid links format in database")
            
        link_uri = links_data[0].get("uri")
        if not link_uri:
            raise Exception("No URI found in the generated links")
            
        return link_uri
    finally:
        conn.close()

BALE_TOKEN = "1307415301:iJ-ljBTWFwmzn8Eef0CiexHZo_KityNu_54"

# Language dictionary
LANGS = {
    'en': {
        'welcome': "Welcome to Shipien VPN! 🚀\nPlease choose your language:\n\nخوش آمدید! لطفا زبان خود را انتخاب کنید.",
        'main_menu': "🏠 *Main Menu:*\n\nExplore our high-speed VPN services below.",
        'plans': "💎 *Available VPN Plans:*\n\nChoose a plan that fits your needs.",
        'receipt_received': "✅ *Receipt Received!*\nYour payment has been sent for admin approval. Please wait.",
        'link_sent': "🎉 *Your VPN Link is Ready:*",
        'rejected': "❌ *Payment Rejected*\nYour payment was not approved. Please contact support for details.",
        'no_links': "😔 *Out of Stock*\nThis plan is currently out of stock. We'll recharge soon!",
        'admin_no_links': "[ADMIN] Out of links for plan: {plan}",
        'admin_one_left': "[ADMIN] Only 1 link left for plan: {plan}",
        'help': "Use the menu below to navigate.",
        'already_trial': "⚠️ *Trial Already Used*\nYou have already used your free trial.",
        'select_plan': "⚠️ Please select a plan from '💎 Buy Plans' first.",
        'select_quantity': "🔢 *Select Quantity*\nHow many configurations for *{plan}*?",
        'after_choose_plan': "📦 *Order Summary*\n\nPlan: *{plan}* x{qty}\nTotal Price: *{total_price}*\n{desc}\n\n💳 *Payment (Card):*\n`{card}`\n\nAfter payment, send the receipt (photo/text) below. ⬇️",
        'after_choose_plan_crypto': "📦 *Order Summary*\n\nPlan: *{plan}* x{qty}\nTotal Price: *{total_price}*\n{desc}\n\n💎 *Payment (TON):*\n`{ton}`\n\nAfter payment, send the transaction hash or receipt photo below. ⬇️",
        'after_choose_plan_usdt': "📦 *Order Summary*\n\nPlan: *{plan}* x{qty}\nTotal Price: *{total_price}*\n{desc}\n\n💵 *Payment (USDT ERC20):*\n`{address}`\n\nAfter payment, send the transaction hash or receipt photo below. ⬇️",
        'choose_payment_method': "💳 *Select Payment Method:*",
        'pay_card_btn': "💳 Card to Card",
        'pay_crypto_btn': "💎 TON (Crypto)",
        'pay_usdt_btn': "💵 USDT (ERC20)",
        'pay_stars_btn': "⭐ Telegram Stars",
        'pay_trusted_btn': '🤝 Trusted Seller (Post-pay)',
        'trusted_info': "🤝 *Trusted Seller Status*\n\nDebt: `{debt}`\nLast 48h purchases: `{pending_amount}`\n\nYour prices are automatically discounted.",
        'trusted_payment_received': "✅ *Order Confirmed*\nAs a Trusted Seller, your configurations are sent immediately. Please clear your balance every 48 hours.",
        'admin_trusted_report': "📊 *Trusted Seller Daily Report*\n\nUser: `{user_id}` (@{username})\nDebt: `{debt}`\n\n*Recent Purchases:*\n{purchases}\n\n*Recent Debt Changes:*\n{debt_history}",

        'stars_payment_received': "✅ *Payment Successful!*\nYour Stars payment was received. Your link is being sent...",
        'back': '⬅️ Back',
        'show_plans': '💎 Buy Plans',
        'view_tiers': '📁 Available Tiers',
        'my_info': '👤 My Profile',
        'contact_admin': '📬 Contact Support',
        'my_purchases': '📦 My Services',
        'history_header': "🧾 *Your Purchase History*\n\n",
        'no_purchases': "⚠️ You haven't purchased any plans yet.",
        'msg_to_admin_prompt': '📝 *Send Message*\nPlease type your message for the support team:',
        'msg_sent_to_admin': '✅ *Message Sent!*\nWe have received your message and will reply shortly.',
        'admin_new_msg': '📬 New message from user `{user_id}` (@{username}):\n\n{text}',
        'admin_reply_btn': 'Reply',
        'reply_to_user_prompt': 'Enter your reply for user `{user_id}`:',
        'reply_sent': '✅ Reply sent to user.',
        'msg_from_admin': '🔔 *Support Response:*\n\n{text}',
        'choose_lang_btn': '🌐 Language',
        'join_channel_prompt': "⚠️ *Access Restricted*\nTo use this bot, please join our official channel: {channel}\n\nAfter joining, click 'Verified' below.",
        'join_btn': "📢 Join Channel",
        'verify_btn': "✅ Verified",
        'not_joined_alert': "❌ You haven't joined the channel yet!",
        'how_to_connect': '📚 How to Connect',
        'referral': '👥 Referral Program',
        'server_status': '📡 Server Status',
        'status_online': '🟢 All Systems Operational',
        'status_load': '📈 Current Load: {load}%',
        'referral_text': "🚀 *Earn Cash with Referrals*\n\nInvite your friends and get paid when they join and buy!\n\n• Each successful invite → +30 تومان\n\n🎯 *Bonuses:*\n• Invite 3 users → +100 تومان\n\n⏱ *Limited-Time Boost:*\nReach 5 successful invites and get 💥 +120 تومان!\n\n💰 *Example:*\nInvite 5 friends → earn up to 370 تومان\n\n💎 *Available Plans:*\n{prices}\n\n🔗 *Your referral link:*\n`{link}`\n\nStart inviting and earn.",
        'prize_redeem_btn': '🎁 Redeem Prize Code',
        'enter_prize_code': '🔑 *Enter Prize Code*\nPlease enter your code below:',
        'prize_success': '🎉 *Congratulations!*\nYou have redeemed a `{amount}` toman prize. Your new balance is `{balance}`.',
        'prize_invalid': '❌ *Invalid Code*\nThis code is incorrect, expired, or has reached its maximum uses.',
        'prize_already_used': '⚠️ *Already Used*\nYou have already used this prize code.',
        'admin_prize_added': '✅ *Prize Code Created*\nCode: `{code}`\nAmount: `{amount}`\nDuration: `{hours}`h\nMax Uses: `{limit}`',
        'connect_guide': "📚 *How to Connect*\n\nChoose your device type to see the guide:",
        'guide_ios': "🍏 *iOS Guide (iPhone)*\n1. Install Karing from App Store.\nApp Store (Karing): https://apps.apple.com/us/app/karing/id6472431552\n2. Copy the sing-box JSON Subscription Link sent by the bot.\n3. Open Karing ➔ Profiles ➔ Add Profile (Import from Link/Clipboard) and Connect.",
        'guide_android': "🤖 *Android Guide*\n1. Install sing-box from Play Store.\nPlay Store: https://play.google.com/store/apps/details?id=io.nekohasekai.sfa\nDirect APK: https://github.com/SagerNet/sing-box/releases\n2. Copy the sing-box JSON Subscription Link.\n3. Open sing-box ➔ Profiles ➔ Import Profile ➔ Paste and Connect.",
        'guide_pc': "💻 *Desktop Guide (Windows/Mac)*\n1. Download sing-box client: https://github.com/SagerNet/sing-box/releases\n2. Import the JSON config and connect.",
        'upload_bale': '☁️ Upload to Bale',
        'bale_id_prompt': '🆔 To get your Bale Chat ID, send any message to @teldownloadbot on Bale app.\n\nThen, paste your *Bale Chat ID* here:',
        'bale_media_prompt': '📁 Great! Now send the *Photo, Music, or File* you want to upload to Bale:',
        'uploading': '⏳ Uploading to Bale...',
        'upload_success': '✅ Uploaded successfully! Check your Bale app.',
        'upload_fail': '❌ Upload failed. Please check your Bale ID and try again.',
        'send_to_email_btn': '📧 Send to Friend via Email',
        'gmail_btn': '📧 Gmail',
        'other_email_btn': '📧 Other Email',
        'wallet': '💳 Wallet',
        'charge_wallet': '➕ Charge Wallet',
        'wallet_balance_msg': "💳 *Your Wallet*\n\nBalance: `{balance}`",
        'pay_wallet_btn': '💳 Pay with Wallet',
        'wallet_charged_success': "✅ *Wallet Charged!*\nYour wallet has been charged with `{amount}`. New balance: `{balance}`",
        'insufficient_balance': "❌ *Insufficient Balance*\nPlease charge your wallet or choose another payment method.",
        'wallet_payment_success': "✅ *Payment Successful!*\nAmount `{amount}` was deducted from your wallet.",
        'enter_amount': "🔢 *Enter Amount*\nPlease enter the amount you want to charge your wallet:",
        'invalid_amount': "❌ *Invalid Amount*\nPlease enter a valid number.",
        'charge_summary': "📦 *Charge Summary*\n\nAmount: *{amount}*\n\n💳 *Payment (Card):*\n`{card}`\n\nAfter payment, send the receipt below. ⬇️",
        'charge_summary_crypto': "📦 *Charge Summary*\n\nAmount: *{amount}*\n\n💎 *Payment (TON):*\n`{ton}`\n\nAfter payment, send the receipt below. ⬇️",
        'charge_summary_usdt': "📦 *Charge Summary*\n\nAmount: *{amount}*\n\n💵 *Payment (USDT ERC20):*\n`{address}`\n\nAfter payment, send the receipt below. ⬇️",
    },
    'fa': {
        'welcome': "به شیپین وی‌پی‌ان خوش آمدید! 🚀\nلطفا زبان خود را انتخاب کنید:\n\nWelcome! Please choose your language.",
        'main_menu': "🏠 *منوی اصلی:*\n\nاز خدمات پرسرعت ما در زیر استفاده کنید.",
        'plans': "💎 *پلن‌های موجود:*\n\nپلن مناسب خود را انتخاب کنید.",
        'receipt_received': "✅ *رسید دریافت شد!*\nرسید شما برای تایید ادمین ارسال شد. لطفا منتظر بمانید.",
        'link_sent': "🎉 *لینک VPN شما آماده است:*",
        'rejected': "❌ *پرداخت تایید نشد*\nپرداخت شما توسط ادمین رد شد. برای اطلاعات بیشتر با پشتیبانی تماس بگیرید.",
        'no_links': "😔 *ناموجود*\nاین پلن در حال حاضر موجود نیست. به زودی شارژ خواهد شد!",
        'admin_no_links': "[ادمین] لینک برای پلن {plan} تمام شد.",
        'admin_one_left': "[ادمین] فقط ۱ لینک برای پلن {plan} باقی مانده است.",
        'help': "از منوی زیر برای جابجایی استفاده کنید.",
        'already_trial': "⚠️ *تست استفاده شده*\nشما قبلاً از تست رایگان استفاده کرده‌اید.",
        'select_plan': "⚠️ لطفاً ابتدا از بخش '💎 خرید پلن' یک پلن انتخاب کنید.",
        'select_quantity': "🔢 *انتخاب تعداد*\nچه تعداد اکانت برای پلن *{plan}* می‌خواهید؟",
        'after_choose_plan': "📦 *خلاصه سفارش*\n\nپلن: *{plan}* به تعداد {qty}\nقیمت کل: *{total_price}*\n{desc}\n\n💳 *واریز به کارت:*\n`{card}`\n\nبعد از پرداخت، رسید را در زیر ارسال کنید. ⬇️",
        'after_choose_plan_crypto': "📦 *خلاصه سفارش*\n\nپلن: *{plan}* به تعداد {qty}\nقیمت کل: *{total_price}*\n{desc}\n\n💎 *واریز به آدرس TON:*\n`{ton}`\n\nبعد از پرداخت، رسید یا هش تراکنش را در زیر ارسال کنید. ⬇️",
        'after_choose_plan_usdt': "📦 *خلاصه سفارش*\n\nپلن: *{plan}* به تعداد {qty}\nقیمت کل: *{total_price}*\n{desc}\n\n💵 *واریز به آدرس USDT (ERC20):*\n`{address}`\n\nبعد از پرداخت، رسید یا هش تراکنش را در زیر ارسال کنید. ⬇️",
        'choose_payment_method': "💳 *روش پرداخت را انتخاب کنید:*",
        'pay_card_btn': "💳 کارت به کارت",
        'pay_crypto_btn': "💎 ارز دیجیتال (TON)",
        'pay_usdt_btn': "💵 تتر (USDT)",
        'pay_stars_btn': "⭐ استارز تلگرام",
        'pay_trusted_btn': '🤝 پنل همکار (پرداخت اعتباری)',
        'trusted_info': "🤝 *وضعیت پنل همکار*\n\nبدهی: `{debt}`\nخرید ۴۸ ساعت اخیر: `{pending_amount}`\n\nقیمت‌های شما با تخفیف ویژه محاسبه می‌شود.",
        'trusted_payment_received': "✅ *سفارش تایید شد*\nبه عنوان همکار معتبر، لینک‌ها بلافاصله ارسال شدند. لطفا هر ۴۸ ساعت تسویه حساب کنید.",
        'admin_trusted_report': "📊 *گزارش روزانه پنل همکار*\n\nکاربر: `{user_id}` (@{username})\nبدهی: `{debt}`\n\n*خریدهای اخیر:*\n{purchases}\n\n*تغییرات بدهی:*\n{debt_history}",

        'stars_payment_received': "✅ *پرداخت موفق!*\nپرداخت ستاره‌ای شما دریافت شد. لینک در حال ارسال است...",
        'back': '⬅️ بازگشت',
        'show_plans': '💎 خرید پلن',
        'view_tiers': '📁 مشاهده سرویس‌ها',
        'my_info': '👤 پروفایل من',
        'contact_admin': '📬 پشتیبانی آنلاین',
        'my_purchases': '📦 سرویس‌های من',
        'history_header': "🧾 *تاریخچه خرید شما*\n\n",
        'no_purchases': "⚠️ شما هنوز خریدی نداشته‌اید.",
        'msg_to_admin_prompt': '📝 *ارسال پیام*\nلطفا پیام خود را برای تیم پشتیبانی بنویسید:',
        'msg_sent_to_admin': '✅ *پیام ارسال شد!*\nپیام شما دریافت شد و به زودی پاسخ خواهیم داد.',
        'admin_new_msg': '📬 پیام جدید از کاربر `{user_id}` (@{username}):\n\n{text}',
        'admin_reply_btn': 'پاسخ',
        'reply_to_user_prompt': 'پاسخ خود را برای کاربر `{user_id}` وارد کنید:',
        'reply_sent': '✅ پاسخ برای کاربر ارسال شد.',
        'msg_from_admin': '🔔 *پاسخ پشتیبانی:*\n\n{text}',
        'choose_lang_btn': '🌐 تغییر زبان',
        'join_channel_prompt': "⚠️ *دسترسی محدود*\nبرای استفاده از ربات، باید در کانال رسمی ما عضو شوید: {channel}\n\nبعد از عضویت، روی 'تایید عضویت' بزنید.",
        'join_btn': "📢 عضویت در کانال",
        'verify_btn': "✅ تایید عضویت",
        'not_joined_alert': "❌ شما هنوز در کانال عضو نشده‌اید!",
        'how_to_connect': '📚 راهنمای اتصال',
        'referral': '👥 زیر مجموعه گیری',
        'server_status': '📡 وضعیت سرورها',
        'status_online': '🟢 تمامی سرورها فعال هستند',
        'status_load': '📈 بار ترافیکی: {load}%',
        'referral_text': "🚀 *کسب درآمد با دعوت از دوستان*\n\nدوستان خود را دعوت کنید و با خرید آن‌ها هدیه نقدی بگیرید!\n\n• هر دعوت موفق → +۳۰ تومان\n\n🎯 *جوایز ویژه:*\n• دعوت ۳ نفر → +۱۰۰ تومان هدیه\n\n⏱ *تخفیف و هدیه محدود:*\nاگر ۵ نفر را دعوت کنید مبلغ 💥 +۱۲۰ تومان هدیه می‌گیرید!\n\n💰 *مثال:*\nدعوت ۵ دوست → تا سقف ۳۷۰ تومان درآمد\n\n💎 *لیست قیمت‌ها:*\n{prices}\n\n🔗 *لینک دعوت شما:*\n`{link}`\n\nهمین حالا شروع کنید و درآمد کسب کنید.",
        'prize_redeem_btn': '🎁 ثبت کد هدیه',
        'enter_prize_code': '🔑 *ورود کد هدیه*\nلطفاً کد خود را در زیر وارد کنید:',
        'prize_success': '🎉 *تبریک!*\nشما مبلغ `{amount}` تومان هدیه دریافت کردید. موجودی جدید: `{balance}`',
        'prize_invalid': '❌ *کد نامعتبر*\nاین کد اشتباه است، منقضی شده یا ظرفیت آن تکمیل شده است.',
        'prize_already_used': '⚠️ *قبلاً استفاده شده*\nشما قبلاً از این کد هدیه استفاده کرده‌اید.',
        'admin_prize_added': '✅ *کد هدیه ساخته شد*\nکد: `{code}`\nمبلغ: `{amount}`\nزمان: `{hours}` ساعت\nظرفیت: `{limit}` نفر',

        'connect_guide': "📚 *راهنمای اتصال*\n\nدستگاه خود را انتخاب کنید:",
        'guide_ios': "🍏 *راهنمای iOS (آیفون)*\n۱. برنامه Karing را از اپ استور دانلود کنید:\nلینک اپ استور (Karing): https://apps.apple.com/us/app/karing/id6472431552\n۲. لینک اشتراک JSON فرستاده شده را کپی کنید.\n۳. وارد برنامه شوید ➔ بخش Profiles ➔ گزینه Add Profile (وارد کردن از کلیپ‌بورد/لینک) را انتخاب کرده و متصل شوید.",
        'guide_android': "🤖 *راهنمای اندروید*\n۱. برنامه sing-box را دانلود و نصب کنید:\nلینک گوگل پلی: https://play.google.com/store/apps/details?id=io.nekohasekai.sfa\nدانلود مستقیم APK: https://github.com/SagerNet/sing-box/releases\n۲. لینک اشتراک JSON را کپی کنید.\n۳. وارد برنامه شوید ➔ بخش Profiles ➔ گزینه Import Profile ➔ لینک را وارد کرده و متصل شوید.",
        'guide_pc': "💻 *راهنمای ویندوز و مک*\n۱. کلاینت دسکتاپ sing-box را دانلود کنید: https://github.com/SagerNet/sing-box/releases\n۲. لینک اشتراک JSON را وارد کرده و متصل شوید.",
        'upload_bale': '☁️ آپلود در بله',
        'bale_id_prompt': '🆔 برای دریافت شناسه خود، هر پیامی را به @teldownloadbot در برنامه بله ارسال کنید.\n\nسپس *شناسه چت (Bale Chat ID)* خود را اینجا بفرستید:',
        'bale_media_prompt': '📁 بسیار عالی! حالا *عکس، موسیقی یا فایل* خود را برای آپلود در بله ارسال کنید:',
        'uploading': '⏳ در حال آپلود در بله...',
        'upload_success': '✅ آپلود با موفقیت انجام شد! برنامه بله خود را چک کنید.',
        'upload_fail': '❌ آپلود با خطا مواجه شد. لطفا شناسه بله خود را چک کرده و دوباره تلاش کنید.',
        'send_to_email_btn': '📧 ارسال کانفیگ برای دوستان (ایمیل)',
        'gmail_btn': '📧 جیمیل (Gmail)',
        'other_email_btn': '📧 سایر ایمیل‌ها',
        'wallet': '💳 کیف پول',
        'charge_wallet': '➕ شارژ کیف پول',
        'wallet_balance_msg': "💳 *کیف پول شما*\n\nموجودی: `{balance}`",
        'pay_wallet_btn': '💳 پرداخت با موجودی کیف پول',
        'wallet_charged_success': "✅ *کیف پول شارژ شد!*\nمبلغ `{amount}` به کیف پول شما اضافه شد. موجودی جدید: `{balance}`",
        'insufficient_balance': "❌ *موجودی کافی نیست*\nلطفاً کیف پول خود را شارژ کنید یا روش دیگری برای پرداخت انتخاب کنید.",
        'wallet_payment_success': "✅ *پرداخت موفق!* \nمبلغ `{amount}` از کیف پول شما کسر شد.",
        'enter_amount': "🔢 *ورود مبلغ*\nلطفاً مبلغی که می‌خواهید کیف پول خود را شارژ کنید (به تومان) وارد کنید:",
        'invalid_amount': "❌ *مبلغ نامعتبر*\nلطفاً یک عدد معتبر وارد کنید.",
        'charge_summary': "📦 *خلاصه شارژ*\n\nمبلغ: *{amount}*\n\n💳 *واریز به کارت:*\n`{card}`\n\nبعد از پرداخت، رسید را در زیر ارسال کنید. ⬇️",
        'charge_summary_crypto': "📦 *خلاصه شارژ*\n\nمبلغ: *{amount}*\n\n💎 *واریز به آدرس TON:*\n`{ton}`\n\nبعد از پرداخت، رسید را در زیر ارسال کنید. ⬇️",
        'charge_summary_usdt': "📦 *خلاصه شارژ*\n\nمبلغ: *{amount}*\n\n💵 *واریز به آدرس USDT (ERC20):*\n`{address}`\n\nبعد از پرداخت، رسید را در زیر ارسال کنید. ⬇️",
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

# Load data
users = load_json(USERS_FILE, {})
all_plans_data = load_json(PLANS_FILE, {"tiers": {}, "plans": {}})
tiers_data = all_plans_data.get('tiers', {})
plans_data = all_plans_data.get('plans', {})

def save_all_plans():
    save_json(PLANS_FILE, {"tiers": tiers_data, "plans": plans_data})

def is_subscribed(user_id):
    if str(user_id) == str(ADMIN_ID): return True
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        if member.status in ['member', 'administrator', 'creator', 'left']:
            # For testing purposes if CHANNEL_ID is not properly set or bot not admin, 
            # we might get errors or 'left'.
            # Usually we check for member, administrator, creator.
            if member.status in ['member', 'administrator', 'creator']:
                return True
    except Exception as e:
        print(f"Error checking subscription: {e}")
        # If bot is not admin in channel, this will fail. 
        # For now, if it fails, we might want to return True to not lock everyone out 
        # or False to enforce it. Usually we return True if we can't check.
        # But user wants mandatory join.
    return False

def get_join_markup(lang):
    markup = types.InlineKeyboardMarkup()
    # Ensure CHANNEL_ID starts with @ for the link, or use the handle
    handle = CHANNEL_ID.lstrip('@')
    url = f"https://t.me/{handle}"
    markup.add(types.InlineKeyboardButton(LANGS[lang]['join_btn'], url=url))
    markup.add(types.InlineKeyboardButton(LANGS[lang]['verify_btn'], callback_data="verify_subscription"))
    return markup

def check_sub_callback(call):
    user_id = str(call.message.chat.id)
    if user_id == str(ADMIN_ID): return True
    if is_subscribed(user_id): return True
    
    lang = get_user_lang(user_id)
    try:
        bot.answer_callback_query(call.id, LANGS[lang]['not_joined_alert'], show_alert=True)
    except: pass
    bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
    return False

def update_user(user_id, **kwargs):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {'buy_count': 0, 'purchase_history': [], 'wallet_balance': 0, 'debt': 0, 'debt_history': [], 'trusted_plans': {}}
    users[user_id].update(kwargs)
    save_json(USERS_FILE, users)

def add_purchase_to_history(user_id, plan_key, links):
    user_id = str(user_id)
    if user_id not in users:
        users[user_id] = {'buy_count': 0, 'purchase_history': []}
    
    users[user_id]['buy_count'] = users[user_id].get('buy_count', 0) + 1
    
    purchase = {
        'timestamp': time.time(),
        'plan_key': plan_key,
        'links': links
    }
    
    if 'purchase_history' not in users[user_id]:
        users[user_id]['purchase_history'] = []
    
    users[user_id]['purchase_history'].append(purchase)
    save_json(USERS_FILE, users)

def get_user_lang(user_id):
    return users.get(str(user_id), {}).get('lang', 'en')

def get_user_id_by_username(username):
    username = username.lstrip('@').lower()
    for uid, data in users.items():
        if data.get('username') and data['username'].lower() == username:
            return uid
    return None

def escape_md(text):
    if not text: return ""
    return str(text).replace('_', '\\_').replace('*', '\\*').replace('`', '\\`').replace('[', '\\[')

def parse_anytls_link(link):
    try:
        raw = link.replace("anytls://", "")
        auth_host, query_frag = raw.split("?", 1) if "?" in raw else (raw, "")
        auth, host_port = auth_host.split("@")
        password = auth
        server, port_str = host_port.split(":")
        port = int(port_str)
        
        sni = server
        node_tag = "anytls-node"
        if query_frag:
            query, fragment = query_frag.split("#", 1) if "#" in query_frag else (query_frag, "")
            if fragment:
                node_tag = urllib.parse.unquote(fragment)
            for param in query.split("&"):
                if "=" in param:
                    k, v = param.split("=")
                    if k == "sni":
                        sni = urllib.parse.unquote(v)
        return password, server, port, sni, node_tag
    except Exception as e:
        print(f"Error parsing anytls link: {e}")
        return None

def generate_singbox_json(password, server, port, sni, node_tag="anytls-node"):
    config = {
        "inbounds": [
            {
                "type": "tun",
                "address": [
                    "172.19.0.1/30",
                    "fdfe:dcba:9876::1/126"
                ],
                "auto_route": True,
                "endpoint_independent_nat": False,
                "mtu": 9000,
                "platform": {
                    "http_proxy": {
                        "enabled": True,
                        "server": "127.0.0.1",
                        "server_port": 2080
                    }
                },
                "stack": "system",
                "strict_route": False
            },
            {
                "type": "mixed",
                "listen": "127.0.0.1",
                "listen_port": 2080,
                "users": []
            }
        ],
        "outbounds": [
            {
                "type": "selector",
                "tag": "proxy",
                "outbounds": [
                    "auto",
                    "direct",
                    node_tag
                ]
            },
            {
                "type": "urltest",
                "tag": "auto",
                "outbounds": [
                    node_tag
                ],
                "url": "http://www.gstatic.com/generate_204",
                "interval": "10m",
                "tolerance": 50
            },
            {
                "type": "direct",
                "tag": "direct"
            },
            {
                "type": "anytls",
                "tag": node_tag,
                "server": server,
                "server_port": port,
                "password": password,
                "tls": {
                    "enabled": True,
                    "server_name": sni
                }
            }
        ],
        "route": {
            "auto_detect_interface": True,
            "final": "proxy",
            "rules": [
                {
                    "action": "sniff"
                },
                {
                    "action": "route",
                    "clash_mode": "Direct",
                    "outbound": "direct"
                },
                {
                    "action": "route",
                    "clash_mode": "Global",
                    "outbound": "proxy"
                }
            ]
        }
    }
    return json.dumps(config, indent=2)

def send_config_with_qr(user_id, link, lang, plan_name="VPN Plan"):
    try:
        import base64
        b64_link = base64.b64encode(link.encode('utf-8')).decode('utf-8')
        
        parsed = parse_anytls_link(link)
        client_name = None
        if parsed:
            password, server, port, sni, node_tag = parsed
            client_name = get_client_name_by_password(password)

        if client_name:
            b64_sub_url = f"http://h2.morningislighting.ir:2096/sub/{client_name}"
            json_sub_url = f"http://h2.morningislighting.ir:2096/sub/{client_name}?format=json"
            clash_sub_url = f"http://h2.morningislighting.ir:2096/sub/{client_name}?format=clash"
        else:
            b64_sub_url = f"https://shipien-web.vercel.app/api/vpn/config/direct/sub?c={b64_link}"
            json_sub_url = f"https://shipien-web.vercel.app/api/vpn/config/direct?c={b64_link}"
            clash_sub_url = ""

        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("🍏 iOS (Karing)", url="https://apps.apple.com/us/app/karing/id6472431552"),
            types.InlineKeyboardButton("🤖 Android (Play Store)", url="https://play.google.com/store/apps/details?id=io.nekohasekai.sfa")
        )
        markup.add(
            types.InlineKeyboardButton("📋 Base64 Subscription", url=b64_sub_url),
            types.InlineKeyboardButton("🌐 JSON Subscription", url=json_sub_url)
        )
        if clash_sub_url:
            markup.add(types.InlineKeyboardButton("⚡ Clash Subscription", url=clash_sub_url))

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(json_sub_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        bio = io.BytesIO()
        bio.name = 'config_qr.png'
        img.save(bio, 'PNG')
        bio.seek(0)

        json_str = None
        if client_name:
            try:
                headers = {'Host': 'h2.morningislighting.ir'}
                r = requests.get(f'http://127.0.0.1:2096/sub/{client_name}?format=json', headers=headers, timeout=5)
                if r.status_code == 200:
                    raw_json = r.json()
                    if 'outbounds' in raw_json:
                        for out in raw_json['outbounds']:
                            if out.get('server') in ['136.244.111.62', '108.61.198.98']:
                                out['server'] = 'h2.morningislighting.ir'
                    json_str = json.dumps(raw_json, indent=2)
            except Exception as e:
                print(f"Error fetching raw config from panel: {e}")

        if not json_str and parsed:
            password, server, port, sni, node_tag = parsed
            json_str = generate_singbox_json(password, server, port, sni, node_tag)

        if lang == 'fa':
            caption = (
                f"🎉 *سرویس {plan_name} شما آماده است!*\n\n"
                f"🔗 *لینک اتصال مستقیم (anytls):*\n`{link}`\n\n"
                f"📋 *لینک اشتراک Base64 (مخصوص Karing و V2Ray):*\n`{b64_sub_url}`\n\n"
                f"🌐 *لینک اشتراک JSON (مخصوص sing-box):*\n`{json_sub_url}`\n"
            )
            if clash_sub_url:
                caption += f"⚡ *لینک اشتراک Clash (مخصوص Clash/Karing):*\n`{clash_sub_url}`\n"
            caption += (
                f"\n📱 *کد QR جهت ایمپورت مستقیم در برنامه ایجاد شده است.*\n\n"
                f"📁 *فایل پیکربندی JSON (مخصوص Karing و sing-box) به این پیام پیوست شد.*"
            )
        else:
            caption = (
                f"🎉 *Your {plan_name} is ready!*\n\n"
                f"🔗 *anytls Connection Link:*\n`{link}`\n\n"
                f"📋 *Base64 Subscription Link (for Karing/V2Ray):*\n`{b64_sub_url}`\n\n"
                f"🌐 *JSON Subscription Link (for sing-box):*\n`{json_sub_url}`\n"
            )
            if clash_sub_url:
                caption += f"⚡ *Clash Subscription Link (for Clash/Karing):*\n`{clash_sub_url}`\n"
            caption += (
                f"\n📱 *The QR Code is for importing directly into the client.*\n\n"
                f"📁 *The JSON Config File (for Karing/sing-box) is attached to this message.*"
            )

        bot.send_photo(user_id, bio, caption=caption, parse_mode='Markdown', reply_markup=markup)
        
        if json_str:
            file_bio = io.BytesIO(json_str.encode('utf-8'))
            file_bio.name = f"{client_name or 'config'}.json"
            bot.send_document(user_id, file_bio, caption=f"📄 {client_name or 'config'}.json ({plan_name})")
            
    except Exception as e:
        print(f"Error sending QR: {e}")
        bot.send_message(user_id, f"*{plan_name}*\n\n{LANGS[lang]['link_sent']}\n\n`{link}`", parse_mode='Markdown')
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
        if os.path.exists(PRIZE_CODES_FILE):
            with open(PRIZE_CODES_FILE, 'rb') as f:
                bot.send_document(chat_id, f, caption="📂 *Prize Codes Database Backup* (JSON)", parse_mode='Markdown')
        
        sui_db_path = "/usr/local/s-ui/db/s-ui.db"
        if os.path.exists(sui_db_path):
            with open(sui_db_path, 'rb') as f:
                bot.send_document(chat_id, f, caption="📂 *s-ui Database Backup* (SQLite)", parse_mode='Markdown')
    except Exception as e:
        print(f"Error sending backups: {e}")

def send_trusted_daily_reports(bot):
    now = time.time()
    one_day = 86400
    for uid, data in users.items():
        if data.get('user_type') == 'trusted_seller':
            # Collect purchases in last 24h
            history = data.get('purchase_history', [])
            recent_purchases = [p for p in history if now - p['timestamp'] < one_day]
            
            # Collect debt changes in last 24h
            debt_history = data.get('debt_history', [])
            recent_debt = [d for d in debt_history if now - d['timestamp'] < one_day]
            
            if not recent_purchases and not recent_debt:
                continue
                
            p_text = ""
            for p in recent_purchases:
                p_text += f"- {p['plan_key']} ({time.strftime('%H:%M', time.localtime(p['timestamp']))})\n"
            
            d_text = ""
            for d in recent_debt:
                d_text += f"- {d['amount']} ({d['description']})\n"
            
            # Check 48h limit
            two_days = 172800
            pending_48h = [p for p in history if now - p['timestamp'] < two_days]
            if pending_48h and data.get('debt', 0) > 0:
                bot.send_message(ADMIN_ID, f"⚠️ *Payment Alert*\nTrusted Seller `{uid}` (@{escape_md(data.get('username'))}) has unpaid purchases from the last 48 hours.\nCurrent Debt: `{data.get('debt')}`", parse_mode='Markdown')

            report = LANGS['en']['admin_trusted_report'].format(
                user_id=uid,
                username=escape_md(data.get('username', 'N/A')),
                debt=data.get('debt', 0),
                purchases=escape_md(p_text) or "None",
                debt_history=escape_md(d_text) or "None"
            )
            bot.send_message(ADMIN_ID, report, parse_mode='Markdown')

def daily_report_loop():
    time.sleep(10) # Wait for bot to initialize
    while True:
        generate_and_send_report(bot, ADMIN_ID)
        send_backups(bot, ADMIN_ID)
        send_trusted_daily_reports(bot)
        time.sleep(86400) # 24 hours

def bale_id_helper_loop():
    last_update_id = 0
    while True:
        try:
            url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
            resp = requests.get(url, timeout=35).json()
            if resp.get('ok') and resp.get('result'):
                for update in resp['result']:
                    last_update_id = update['update_id']
                    if 'message' in update:
                        chat_id = update['message']['chat']['id']
                        # Reply with their ID
                        reply_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/sendMessage"
                        msg_text = f"Your Bale Chat ID is: `{chat_id}`\n\nCopy and paste this into the Shipien Telegram Bot."
                        requests.post(reply_url, json={'chat_id': chat_id, 'text': msg_text, 'parse_mode': 'Markdown'})
        except Exception as e:
            print(f"Bale ID Helper Error: {e}")
        time.sleep(1)

# Start the reporting thread in background
threading.Thread(target=daily_report_loop, daemon=True).start()
# Start the Bale ID helper thread
threading.Thread(target=bale_id_helper_loop, daemon=True).start()

# Main Menu Generator
PRIZE_CODES_FILE = 'prize_codes.json'
prize_codes = load_json(PRIZE_CODES_FILE, {})

def save_prize_codes():
    save_json(PRIZE_CODES_FILE, prize_codes)

def get_main_menu(user_id):
    lang = get_user_lang(user_id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton("🌐 Open Web App", web_app=types.WebAppInfo(url="https://shipien-web.vercel.app/dashboard"))
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['show_plans']),
        types.KeyboardButton(LANGS[lang]['view_tiers'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['how_to_connect']),
        types.KeyboardButton(LANGS[lang]['my_info'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['my_purchases']),
        types.KeyboardButton(LANGS[lang]['wallet'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['referral']),
        types.KeyboardButton(LANGS[lang]['server_status'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['upload_bale']),
        types.KeyboardButton(LANGS[lang]['prize_redeem_btn'])
    )
    markup.add(
        types.KeyboardButton(LANGS[lang]['contact_admin']),
        types.KeyboardButton(LANGS[lang]['choose_lang_btn'])
    )
    return markup

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['how_to_connect'], LANGS['fa']['how_to_connect']])
def how_to_connect_menu(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    if not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🍏 iOS", callback_data="guide_ios"))
    markup.add(types.InlineKeyboardButton("🤖 Android", callback_data="guide_android"))
    markup.add(types.InlineKeyboardButton("💻 Windows/PC", callback_data="guide_pc"))
    
    bot.send_message(user_id, LANGS[lang]['connect_guide'], reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data.startswith('guide_'))
def guide_callback(call):
    lang = get_user_lang(call.message.chat.id)
    guide_key = call.data
    bot.edit_message_text(LANGS[lang][guide_key], call.message.chat.id, call.message.message_id, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['server_status'], LANGS['fa']['server_status']])
def server_status_check(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    
    # Simple mock status for now
    import random
    load = random.randint(15, 45)
    status_text = f"📡 *{LANGS[lang]['server_status']}*\n\n"
    status_text += f"{LANGS[lang]['status_online']}\n"
    status_text += f"{LANGS[lang]['status_load'].format(load=load)}\n"
    status_text += f"⏱ Ping: `{random.randint(40, 120)}ms`"
    
    bot.send_message(user_id, status_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['referral'], LANGS['fa']['referral'], '👥 دعوت و کسب درآمد', '👥 زیر مجموعه گیری'])
def referral_program(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)

    u = users.get(user_id, {})
    
    # Generate price list for banner
    prices_text = ""
    for pk, pd in plans_data.items():
        name = pd['name'].get(lang, pd['name']['en'])
        price = pd['price'].get(lang, pd['price']['en'])
        prices_text += f"• {name}: {price}\n"

    bot_username = bot.get_me().username
    ref_link = f"https://t.me/{bot_username}?start=ref_{user_id}"

    markup = types.InlineKeyboardMarkup()
    share_text = LANGS[lang].get('share_ref_text', f"🚀 Get high-speed VPN with Shipien!\nJoin now using my link and get a bonus:\n{ref_link}").format(link=ref_link)
    share_url = f"https://t.me/share/url?url={urllib.parse.quote(ref_link)}&text={urllib.parse.quote(share_text)}"
    markup.add(types.InlineKeyboardButton(LANGS[lang].get('share_ref_btn', "🔗 Share with Friends"), url=share_url))

    text = LANGS[lang]['referral_text'].format(prices=prices_text, link=ref_link)
    bot.send_message(user_id, text, parse_mode='Markdown', reply_markup=markup)
@bot.message_handler(func=lambda m: m.text in [LANGS['en']['upload_bale'], LANGS['fa']['upload_bale']])
def upload_to_bale_start(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    u = users.get(user_id, {})
    
    if u.get('bale_chat_id'):
        update_user(user_id, user_state='waiting_for_bale_media')
        bot.send_message(user_id, LANGS[lang]['bale_media_prompt'], parse_mode='Markdown')
    else:
        update_user(user_id, user_state='waiting_for_bale_id')
        bot.send_message(user_id, LANGS[lang]['bale_id_prompt'], parse_mode='Markdown')

def handle_bale_upload(bot, message, user_id, lang, bale_chat_id):
    try:
        bot.send_message(user_id, LANGS[lang]['uploading'])
        
        file_id = None
        method = None
        file_key = None
        
        if message.content_type == 'photo':
            file_id = message.photo[-1].file_id
            method = "sendPhoto"
            file_key = "photo"
        elif message.content_type == 'audio':
            file_id = message.audio.file_id
            method = "sendAudio"
            file_key = "audio"
        elif message.content_type == 'voice':
            file_id = message.voice.file_id
            method = "sendVoice"
            file_key = "voice"
        elif message.content_type == 'document':
            file_id = message.document.file_id
            method = "sendDocument"
            file_key = "document"
        elif message.content_type == 'video':
            file_id = message.video.file_id
            method = "sendVideo"
            file_key = "video"
            
        if not file_id:
            return False

        # Get file path from Telegram
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Upload to Bale
        bale_url = f"https://tapi.bale.ai/bot{BALE_TOKEN}/{method}"
        files = {file_key: ('file', downloaded_file)}
        data = {'chat_id': bale_chat_id}
        
        if message.caption:
            data['caption'] = message.caption
            
        response = requests.post(bale_url, data=data, files=files)
        
        if response.status_code == 200:
            bot.send_message(user_id, LANGS[lang]['upload_success'])
            return True
        else:
            print(f"Bale Upload Fail: {response.text}")
            bot.send_message(user_id, LANGS[lang]['upload_fail'])
            return False
            
    except Exception as e:
        print(f"Error in handle_bale_upload: {e}")
        bot.send_message(user_id, LANGS[lang]['upload_fail'])
        return False

def is_admin(user_id):
    user_id = str(user_id)
    if user_id == str(ADMIN_ID):
        return True
    u = users.get(user_id, {})
    return u.get('user_type') == 'admin'

# Admin Dashboard
@bot.message_handler(commands=['admin'], func=lambda m: is_admin(m.chat.id))
def admin_dashboard(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚙️ Manage Plans & Links", callback_data="admin_manage_plans"))
    markup.add(types.InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast_start"))
    markup.add(types.InlineKeyboardButton("📊 Get Status Report", callback_data="admin_get_report"))
    bot.send_message(ADMIN_ID, "--- 🛠 Admin Dashboard ---\n\nUse `/send @username [plan_key] [count]` to send links.\nUse `/balance @username [amount]` to manage balance.\nUse `/debt @username [amount] [desc]` to add debt (+ or -).\nUse `/addprize [code] [amount] [hours] [limit]` to create prize code.\nUse `/msg @username [text]` to send a message.\nUse `/users` to list all users.\nUse `/promote @username` to promote to old.\nUse `/promote_trusted @username` to promote to Trusted Seller.\nUse `/promote_admin @username` to promote to Admin.\nUse `/bulk_promote id1 id2 ...` to promote multiple users by ID.\nUse `/refresh_all` to update the menu for all users.", reply_markup=markup)

@bot.message_handler(commands=['promote_admin'], func=lambda m: is_admin(m.chat.id))
def admin_promote_admin(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: `/promote_admin @username`")
            return
        
        target_username = parts[1]
        target_uid = get_user_id_by_username(target_username)
        
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        update_user(target_uid, user_type='admin')
        bot.reply_to(message, f"✅ User @{target_username.lstrip('@')} (ID: `{target_uid}`) promoted to ADMIN.")
        bot.send_message(target_uid, "👑 You have been promoted to Admin! You now have access to admin commands.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['promote_trusted'], func=lambda m: is_admin(m.chat.id))
def admin_promote_trusted(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: `/promote_trusted @username`")
            return
        
        target_username = parts[1]
        target_uid = get_user_id_by_username(target_username)
        
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        update_user(target_uid, user_type='trusted_seller')
        bot.reply_to(message, f"✅ User @{target_username.lstrip('@')} (ID: `{target_uid}`) promoted to TRUSTED SELLER.")
        bot.send_message(target_uid, "🤝 You have been promoted to a Trusted Seller! You can now order without immediate payment and get special discounts.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['debt'], func=lambda m: is_admin(m.chat.id))
def admin_manage_debt(message):
    try:
        parts = message.text.split(maxsplit=3)
        if len(parts) < 3:
            bot.reply_to(message, "Usage: `/debt @username [amount] [description]`")
            return
        
        target_username = parts[1]
        amount_str = parts[2]
        desc = parts[3] if len(parts) > 3 else "No description"
        
        target_uid = get_user_id_by_username(target_username)
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        u = users.get(target_uid, {})
        current_debt = u.get('debt', 0)
        
        if amount_str.startswith('+'):
            amount = int(amount_str[1:])
        elif amount_str.startswith('-'):
            amount = -int(amount_str[1:])
        else:
            amount = int(amount_str)
            
        new_debt = current_debt + amount
        
        # Record in debt history
        history = u.get('debt_history', [])
        history.append({
            'timestamp': time.time(),
            'amount': amount,
            'description': desc,
            'new_total': new_debt
        })
        
        update_user(target_uid, debt=new_debt, debt_history=history)
        bot.reply_to(message, f"✅ Debt for @{target_username.lstrip('@')} updated. \nChange: `{amount}`\nNew Total Debt: `{new_debt}`\nDesc: {desc}")
        
        target_lang = get_user_lang(target_uid)
        bot.send_message(target_uid, f"📊 Your debt balance has been updated by admin.\nChange: `{amount}`\nNew Balance: `{new_debt}`\nReason: {desc}")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['send'], func=lambda m: is_admin(m.chat.id))
def admin_send_bulk(message):
    try:
        parts = message.text.split()
        if len(parts) < 4:
            bot.reply_to(message, "Usage: `/send @username [plan_key] [count]`")
            return
        
        target_username = parts[1]
        plan_key = parts[2]
        count = int(parts[3])
        
        target_uid = get_user_id_by_username(target_username)
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found in database.")
            return
        
        if plan_key not in plans_data:
            bot.reply_to(message, f"Plan `{escape_md(plan_key)}` not found.")
            return
        
        target_lang = get_user_lang(target_uid)
        plan_name = plans_data[plan_key]['name'].get(target_lang, plans_data[plan_key]['name']['en'])
        expiry_days = plans_data[plan_key].get('expiry_days', 30)
        volume_gb = plans_data[plan_key].get('volume_gb', 0)
        
        sent_count = 0
        for i in range(count):
            remark = f"admin-gift-{target_uid}-{i+1}"
            try:
                link = add_sui_client(remark, expiry_days, volume_gb)
                if link:
                    send_config_with_qr(target_uid, link, target_lang, plan_name=plan_name)
                    sent_count += 1
            except Exception as e:
                print(f"Error creating client: {e}")
        bot.reply_to(message, f"✅ Successfully sent {sent_count} links to `{escape_md(target_username)}`.")
        bot.send_message(target_uid, f"🎁 Admin has sent you {sent_count} VPN config(s)!")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['balance'], func=lambda m: is_admin(m.chat.id))
def admin_set_balance(message):
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, "Usage: `/balance @username [amount]` or `/balance @username +[amount]`")
            return
        
        target_username = parts[1]
        amount_str = parts[2]
        
        target_uid = get_user_id_by_username(target_username)
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        u = users.get(target_uid, {})
        current_balance = u.get('wallet_balance', 0)
        
        if amount_str.startswith('+'):
            amount = int(amount_str[1:])
            new_balance = current_balance + amount
        elif amount_str.startswith('-'):
            amount = int(amount_str[1:])
            new_balance = current_balance - amount
        else:
            new_balance = int(amount_str)
            
        update_user(target_uid, wallet_balance=new_balance)
        bot.reply_to(message, f"✅ Balance for @{target_username.lstrip('@')} updated. \nOld: `{current_balance}`\nNew: `{new_balance}`")
        
        target_lang = get_user_lang(target_uid)
        bot.send_message(target_uid, f"💰 Your wallet balance has been updated by admin.\nNew Balance: `{new_balance}`")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['msg'], func=lambda m: is_admin(m.chat.id))
def admin_msg_user(message):
    try:
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot.reply_to(message, "Usage: `/msg @username [text]`")
            return
        
        target_username = parts[1]
        text = parts[2]
        
        target_uid = get_user_id_by_username(target_username)
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        target_lang = get_user_lang(target_uid)
        bot.send_message(target_uid, LANGS[target_lang]['msg_from_admin'].format(text=escape_md(text)), parse_mode='Markdown')
        bot.reply_to(message, f"✅ Message sent to `{escape_md(target_username)}`.")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['users'], func=lambda m: is_admin(m.chat.id))
def admin_list_users(message):
    try:
        if not users:
            bot.reply_to(message, "No users found in database.")
            return
        
        text = "👥 *List of Users:*\n\n"
        for uid, data in users.items():
            username = data.get('username', 'N/A')
            user_type = data.get('user_type', 'new')
            text += f"ID: `{uid}` | @{username} | Type: `{user_type}`\n"
            
            if len(text) > 3500:
                bot.send_message(ADMIN_ID, text, parse_mode='Markdown')
                text = ""
        
        if text:
            bot.send_message(ADMIN_ID, text, parse_mode='Markdown')
            
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['promote'], func=lambda m: is_admin(m.chat.id))
def admin_promote_by_username(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: `/promote @username`")
            return
        
        target_username = parts[1]
        target_uid = get_user_id_by_username(target_username)
        
        if not target_uid:
            bot.reply_to(message, f"User `{escape_md(target_username)}` not found.")
            return
        
        update_user(target_uid, user_type='old')
        bot.reply_to(message, f"✅ User @{target_username.lstrip('@')} (ID: `{target_uid}`) promoted to OLD.")
        bot.send_message(target_uid, "🌟 You have been promoted to a regular user. You can now use Card-to-Card payment!")
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['bulk_promote'], func=lambda m: is_admin(m.chat.id))
def admin_bulk_promote(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Usage: `/bulk_promote id1 id2 id3 ...`")
            return
        
        target_ids = parts[1:]
        success_count = 0
        failed_ids = []
        
        for uid in target_ids:
            uid = uid.strip()
            if uid in users:
                update_user(uid, user_type='old')
                try:
                    bot.send_message(uid, "🌟 You have been promoted to a regular user. You can now use Card-to-Card payment!")
                except: pass
                success_count += 1
            else:
                failed_ids.append(uid)
        
        response = f"✅ Successfully promoted {success_count} users."
        if failed_ids:
            response += f"\n❌ Failed to find these IDs in database: `{', '.join(failed_ids)}`"
            
        bot.reply_to(message, response, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=['refresh_all'], func=lambda m: is_admin(m.chat.id))
def admin_refresh_all(message):
    try:
        success = 0
        for uid in users:
            try:
                lang = get_user_lang(uid)
                bot.send_message(uid, LANGS[lang]['main_menu'], reply_markup=get_main_menu(uid))
                success += 1
                time.sleep(0.05)
            except:
                pass
        bot.reply_to(message, f"✅ Refresh command sent to {success} users.")
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "admin_get_report")
def admin_get_report(call):
    generate_and_send_report(bot, ADMIN_ID)
    send_backups(bot, ADMIN_ID)
    bot.answer_callback_query(call.id, "Report and Backups generated!")

@bot.callback_query_handler(func=lambda call: call.data == "admin_manage_plans")
def admin_manage_tiers(call):
    markup = types.InlineKeyboardMarkup()
    for tier_key, data in tiers_data.items():
        name = data['name']['en']
        markup.add(types.InlineKeyboardButton(f"📁 Tier: {name}", callback_data=f"admin_view_tier_{tier_key}"))
    
    markup.add(types.InlineKeyboardButton("📋 All Plans (Standalone)", callback_data="admin_list_all_plans"))
    markup.add(types.InlineKeyboardButton("➕ Add New Tier", callback_data="admin_add_tier_start"))
    markup.add(types.InlineKeyboardButton("➕ Add New Plan", callback_data="admin_add_plan_start"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Dashboard", callback_data="admin_back_to_dash"))
    bot.edit_message_text("Manage Tiers or Plans:", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "admin_list_all_plans")
def admin_list_all_plans(call):
    markup = types.InlineKeyboardMarkup()
    for plan_key, data in plans_data.items():
        name = data['name']['en']
        links_count = len(data.get('links', []))
        markup.add(types.InlineKeyboardButton(f"{name} (ID: {plan_key}) ({links_count})", callback_data=f"admin_view_plan_{plan_key}"))
    
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_manage_plans"))
    bot.edit_message_text("All Available Plans:", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_view_tier_"))
def admin_view_tier(call):
    tier_key = call.data.replace("admin_view_tier_", "")
    if tier_key not in tiers_data:
        bot.answer_callback_query(call.id, "Tier not found.")
        return
    
    tier_info = tiers_data[tier_key]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏷 Rename Tier", callback_data=f"admin_rename_tier_{tier_key}"))
    markup.add(types.InlineKeyboardButton("📝 Edit Tier Description", callback_data=f"admin_edit_tier_desc_{tier_key}"))
    
    for plan_key in tier_info.get('plans', []):
        if plan_key in plans_data:
            name = plans_data[plan_key]['name']['en']
            links_count = len(plans_data[plan_key].get('links', []))
            markup.add(types.InlineKeyboardButton(f"  └ {name} (ID: {plan_key}) ({links_count})", callback_data=f"admin_view_plan_{plan_key}"))
    
    markup.add(types.InlineKeyboardButton("➕ Add Plan to this Tier", callback_data=f"admin_tier_add_plan_{tier_key}"))
    markup.add(types.InlineKeyboardButton("❌ Delete Tier", callback_data=f"admin_delete_tier_{tier_key}"))
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data="admin_manage_plans"))
    
    info_text = f"Tier: {tier_info['name']['en']}\nDesc: {tier_info['description']['en'][:100]}...\n\nManage Tier:"
    bot.edit_message_text(info_text, ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_rename_tier_"))
def admin_rename_tier_prompt(call):
    tier_key = call.data.replace("admin_rename_tier_", "")
    update_user(ADMIN_ID, admin_state=f"rename_tier_{tier_key}")
    bot.edit_message_text(f"Send the new NAME for Tier {tier_key} (Format: English_Name|Farsi_Name):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_tier_desc_"))
def admin_edit_tier_desc_prompt(call):
    tier_key = call.data.replace("admin_edit_tier_desc_", "")
    update_user(ADMIN_ID, admin_state=f"edit_tier_desc_{tier_key}")
    bot.edit_message_text(f"Send the new DESCRIPTION for Tier {tier_key} (Format: English_Desc|Farsi_Desc):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_tier_add_plan_"))
def admin_tier_add_plan_prompt(call):
    tier_key = call.data.replace("admin_tier_add_plan_", "")
    update_user(ADMIN_ID, admin_state=f"tier_add_plan_{tier_key}")
    bot.edit_message_text(f"Send the Plan ID to add to Tier {tier_key}:", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data == "admin_add_tier_start")
def admin_add_tier_start(call):
    update_user(ADMIN_ID, admin_state="add_tier_id")
    bot.edit_message_text("Send the ID for the new Tier (e.g. `business`):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_delete_tier_"))
def admin_delete_tier(call):
    tier_key = call.data.replace("admin_delete_tier_", "")
    if tier_key in tiers_data:
        del tiers_data[tier_key]
        save_all_plans()
        bot.answer_callback_query(call.id, "Tier deleted.")
    admin_manage_tiers(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_rename_plan_"))
def admin_rename_plan_prompt(call):
    plan_key = call.data.replace("admin_rename_plan_", "")
    update_user(ADMIN_ID, admin_state=f"rename_plan_{plan_key}")
    bot.edit_message_text(f"Send the new NAME for {plan_key} (Format: English_Name|Farsi_Name):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_confirm_delete_plan_"))
def admin_confirm_delete_plan(call):
    plan_key = call.data.replace("admin_confirm_delete_plan_", "")
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("✅ YES, Delete", callback_data=f"admin_delete_plan_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🔙 Cancel", callback_data=f"admin_view_plan_{plan_key}"))
    bot.edit_message_text(f"⚠️ Are you sure you want to delete the plan `{plan_key}`? All its links will be lost!", ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_delete_plan_"))
def admin_delete_plan(call):
    plan_key = call.data.replace("admin_delete_plan_", "")
    if plan_key in plans_data:
        del plans_data[plan_key]
        save_all_plans()
        bot.answer_callback_query(call.id, "Plan deleted.")
    admin_manage_plans(call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_view_plan_"))
def admin_view_plan(call):
    plan_key = call.data.replace("admin_view_plan_", "")
    if plan_key not in plans_data:
        bot.answer_callback_query(call.id, "Plan not found.")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏷 Rename Plan", callback_data=f"admin_rename_plan_{plan_key}"))
    markup.add(types.InlineKeyboardButton("💰 Change Price", callback_data=f"admin_edit_price_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🤝 Edit Trusted Price", callback_data=f"admin_edit_trusted_price_{plan_key}"))
    markup.add(types.InlineKeyboardButton("⭐ Change Stars Price", callback_data=f"admin_edit_stars_{plan_key}"))
    markup.add(types.InlineKeyboardButton("📝 Change Description", callback_data=f"admin_edit_desc_{plan_key}"))
    markup.add(types.InlineKeyboardButton("➕ Bulk Add Links", callback_data=f"admin_bulkadd_links_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🗑 List/Delete Links", callback_data=f"admin_list_links_{plan_key}"))
    markup.add(types.InlineKeyboardButton("❌ Delete Plan", callback_data=f"admin_confirm_delete_plan_{plan_key}"))
    markup.add(types.InlineKeyboardButton("🔙 Back to Plans", callback_data="admin_manage_plans"))
    
    name = plans_data[plan_key]['name']['en']
    price_en = plans_data[plan_key]['price']['en']
    price_fa = plans_data[plan_key]['price']['fa']
    trusted_price_en = plans_data[plan_key].get('trusted_price', {}).get('en', 'Same as Regular')
    trusted_price_fa = plans_data[plan_key].get('trusted_price', {}).get('fa', 'Same as Regular')
    stars_price = plans_data[plan_key].get('stars_price', 'Not Set')
    
    desc_data = plans_data[plan_key].get('description', {'en': 'None', 'fa': 'None'})
    desc_en = desc_data.get('en', 'None')
    
    info_text = f"Plan: {name}\n💰 Price (EN): {price_en}\n💰 Price (FA): {price_fa}\n🤝 Trusted Price (EN): {trusted_price_en}\n🤝 Trusted Price (FA): {trusted_price_fa}\n⭐ Stars: {stars_price}\n📝 Desc (EN): {desc_en}\n\nSelect action:"
    bot.edit_message_text(info_text, ADMIN_ID, call.message.message_id, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_stars_"))
def admin_edit_stars_prompt(call):
    plan_key = call.data.replace("admin_edit_stars_", "")
    update_user(ADMIN_ID, admin_state=f"edit_stars_{plan_key}")
    bot.edit_message_text(f"Send the new STARS price for {plan_key} (Number only):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_price_"))
def admin_edit_price_prompt(call):
    plan_key = call.data.replace("admin_edit_price_", "")
    update_user(ADMIN_ID, admin_state=f"edit_price_{plan_key}")
    bot.edit_message_text(f"Send the new price for {plan_key} (Format: English_Price|Farsi_Price):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_trusted_price_"))
def admin_edit_trusted_price_prompt(call):
    plan_key = call.data.replace("admin_edit_trusted_price_", "")
    update_user(ADMIN_ID, admin_state=f"edit_trusted_price_{plan_key}")
    bot.edit_message_text(f"Send the new TRUSTED price for {plan_key} (Format: English_Price|Farsi_Price):", ADMIN_ID, call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("admin_edit_desc_"))
def admin_edit_desc_prompt(call):
    plan_key = call.data.replace("admin_edit_desc_", "")
    update_user(ADMIN_ID, admin_state=f"edit_desc_{plan_key}")
    bot.edit_message_text(f"Send the new description for {plan_key} (Format: English_Desc|Farsi_Desc):", ADMIN_ID, call.message.message_id)

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
def start(message, force_lang_select=False):
    user_id = str(message.chat.id)

    # Handle Referrals
    if user_id not in users and len(message.text.split()) > 1:
        payload = message.text.split()[1]
        if payload.startswith('ref_'):
            referrer_id = payload.replace('ref_', '')
            if referrer_id in users and referrer_id != user_id:
                ref_data = users[referrer_id]

                # Check if this user was already referred
                if 'referred_by' not in users.get(user_id, {}):
                    # Basic reward for the invite
                    reward_amount = 30

                    # Track referral
                    now = time.time()
                    referrals = ref_data.get('referrals_list', [])
                    referrals.append({'uid': user_id, 'timestamp': now})
                    ref_data['referrals_list'] = referrals
                    ref_data['ref_count'] = len(referrals)

                    # Update balance and history
                    ref_data['wallet_balance'] = ref_data.get('wallet_balance', 0) + reward_amount

                    # Check Bonuses
                    bonuses = ref_data.get('bonuses_claimed', [])
                    bonus_msg = ""

                    # Bonus 3 users (+100)
                    if len(referrals) >= 3 and 'bonus_3' not in bonuses:
                        ref_data['wallet_balance'] += 100
                        bonuses.append('bonus_3')
                        bonus_msg += "\n🎯 *Bonus:* +100 تومان for 3 invites!"

                    # Bonus 5 users
                    if len(referrals) >= 5 and 'bonus_5' not in bonuses:
                        # Check 48h boost (+120 instead of +80)
                        # We'll check if the 5th referral is within 48h of the 1st
                        if now - referrals[0]['timestamp'] <= 172800:
                            ref_data['wallet_balance'] += 120
                            bonuses.append('bonus_5')
                            bonus_msg += "\n💥 *Boost:* +120 تومان for 5 invites within 48h!"
                        else:
                            ref_data['wallet_balance'] += 80
                            bonuses.append('bonus_5')
                            bonus_msg += "\n🎯 *Bonus:* +80 تومان for 5 invites!"

                    ref_data['bonuses_claimed'] = bonuses
                    save_json(USERS_FILE, users)

                    try:
                        target_lang = get_user_lang(referrer_id)
                        reward_msg = f"🎉 *New Referral!*\nSomeone joined using your link. You earned {reward_amount} تومان!{bonus_msg}"
                        bot.send_message(referrer_id, reward_msg, parse_mode='Markdown')
                    except: pass

    # First, let them choose language if not set or forced
    if user_id not in users or 'lang' not in users[user_id] or force_lang_select:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('English 🇬🇧', callback_data='lang_en'))
        markup.add(types.InlineKeyboardButton('فارسی 🇮🇷', callback_data='lang_fa'))
        
        # If forcing lang selection, use the user's current lang for the welcome message if possible
        welcome_lang = get_user_lang(user_id) if user_id in users else 'en'
        bot.send_message(message.chat.id, LANGS[welcome_lang]['welcome'], reply_markup=markup)
        
        if user_id not in users:
            update_user(message.chat.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                status='started')
        return

    lang = get_user_lang(user_id)
    
    # Check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    bot.send_message(message.chat.id, LANGS[lang]['main_menu'], reply_markup=get_main_menu(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "verify_subscription")
def verify_subscription_callback(call):
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    if is_subscribed(user_id):
        bot.answer_callback_query(call.id, "✅ Verified!", show_alert=False)
        bot.send_message(user_id, LANGS[lang]['main_menu'], reply_markup=get_main_menu(user_id))
        bot.delete_message(user_id, call.message.message_id)
    else:
        bot.answer_callback_query(call.id, LANGS[lang]['not_joined_alert'], show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith('lang_'))
def set_lang_callback(call):
    lang = call.data.split('_')[1]
    user_id = str(call.message.chat.id)
    update_user(user_id, lang=lang)
    
    bot.answer_callback_query(call.id)
    bot.delete_message(user_id, call.message.message_id)
    
    # After language is set, check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
    else:
        bot.send_message(user_id, LANGS[lang]['main_menu'], reply_markup=get_main_menu(user_id))

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['view_tiers'], LANGS['fa']['view_tiers']])
def show_all_tiers_info(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    
    # Check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return
    
    if not tiers_data:
        bot.send_message(message.chat.id, "No tiers available.")
        return

    full_text = f"💎 *{LANGS[lang]['view_tiers']}*\n\n"
    
    for tier_key, data in tiers_data.items():
        name = data['name'].get(lang, data['name']['en'])
        desc = data['description'].get(lang, data['description']['en'])
        
        full_text += f"━━━━━━━━━━━━━━━\n"
        full_text += f"📁 *{name}*\n"
        full_text += f"📝 {desc}\n\n"
        full_text += f"*Plans:*\n"
        
        for plan_key in data.get('plans', []):
            if plan_key in plans_data:
                p_data = plans_data[plan_key]
                p_name = p_data['name'].get(lang, p_data['name']['en'])
                p_price = p_data['price'].get(lang, p_data['price']['en'])
                p_desc = p_data.get('description', {}).get(lang, p_data.get('description', {}).get('en', ''))
                
                full_text += f"🔹 {p_name} — `{p_price}`\n"
                if p_desc:
                    full_text += f"   └ {p_desc}\n"
        
        full_text += "\n"

    bot.send_message(message.chat.id, full_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['show_plans'], LANGS['fa']['show_plans']])
def show_tiers(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    
    # Check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return
    
    markup = types.InlineKeyboardMarkup()
    
    if not tiers_data:
        bot.send_message(message.chat.id, "No tiers available.")
        return

    for tier_key, data in tiers_data.items():
        name = data['name'].get(lang, data['name']['en'])
        markup.add(types.InlineKeyboardButton(name, callback_data=f"select_tier_{tier_key}"))
    
    bot.send_message(message.chat.id, LANGS[lang]['plans'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('select_tier_'))
def select_tier_callback(call):
    if not check_sub_callback(call): return
    tier_key = call.data.replace("select_tier_", "")
    lang = get_user_lang(call.message.chat.id)
    
    if tier_key not in tiers_data:
        bot.answer_callback_query(call.id, "Tier not found.")
        return
    
    tier_info = tiers_data[tier_key]
    desc = tier_info['description'].get(lang, tier_info['description']['en'])
    
    markup = types.InlineKeyboardMarkup()
    for plan_key in tier_info.get('plans', []):
        if plan_key in plans_data:
            data = plans_data[plan_key]
            links_count = 999
            
            name = data['name'].get(lang, data['name']['en'])
            price = data['price'].get(lang, data['price']['en'])
            
            label = f"{name} - {price}"
            markup.add(types.InlineKeyboardButton(label, callback_data=f"select_plan_{plan_key}"))
    
    markup.add(types.InlineKeyboardButton(LANGS[lang]['back'], callback_data="back_to_tiers"))
    
    bot.edit_message_text(f"*{tier_info['name'].get(lang, tier_info['name']['en'])}*\n\n{desc}\n\nSelect a plan:", 
                          call.message.chat.id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == "back_to_tiers")
def back_to_tiers_callback(call):
    if not check_sub_callback(call): return
    lang = get_user_lang(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    for tier_key, data in tiers_data.items():
        name = data['name'].get(lang, data['name']['en'])
        markup.add(types.InlineKeyboardButton(name, callback_data=f"select_tier_{tier_key}"))
    
    bot.edit_message_text(LANGS[lang]['plans'], call.message.chat.id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['my_purchases'], LANGS['fa']['my_purchases']] or m.text == '/my_services')
def show_my_services(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    
    # Check subscription
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    history = users.get(user_id, {}).get('purchase_history', [])
    if not history:
        bot.send_message(user_id, LANGS[lang]['no_purchases'], parse_mode='Markdown')
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    
    header = (
        "📦 *سرویس‌های فعال شما:*\n\n"
        "یکی از سرویس‌های خود را از لیست زیر انتخاب کنید تا مشخصات اتصال، لینک‌های اشتراک و فایل کانفیگ مربوطه را دریافت کنید:"
        if lang == 'fa' else
        "📦 *Your Active Services:*\n\n"
        "Select one of your services below to retrieve its connection links, subscription URLs, and configuration file:"
    )

    for idx, item in enumerate(history):
        plan_key = item['plan_key']
        plan_name = plans_data.get(plan_key, {}).get('name', {}).get(lang, plan_key)
        date = time.strftime('%Y-%m-%d', time.localtime(item['timestamp']))
        
        btn_label = f"📅 {date} — {plan_name}"
        markup.add(types.InlineKeyboardButton(btn_label, callback_data=f"get_my_config_{idx}"))

    bot.send_message(user_id, header, parse_mode='Markdown', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('get_my_config_'))
def handle_get_my_config(call):
    if not check_sub_callback(call): return
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    
    try:
        idx = int(call.data.replace('get_my_config_', ''))
        history = users.get(user_id, {}).get('purchase_history', [])
        
        if 0 <= idx < len(history):
            item = history[idx]
            plan_key = item['plan_key']
            plan_name = plans_data.get(plan_key, {}).get('name', {}).get(lang, plan_key)
            
            bot.answer_callback_query(call.id, "Sending configuration..." if lang=='en' else "در حال ارسال کانفیگ...")
            
            for link in item['links']:
                send_config_with_qr(user_id, link, lang, plan_name=plan_name)
        else:
            bot.answer_callback_query(call.id, "Service not found." if lang=='en' else "سرویس پیدا نشد.")
    except Exception as e:
        print(f"Error in handle_get_my_config: {e}")
        bot.answer_callback_query(call.id, "Error occurred." if lang=='en' else "خطایی رخ داد.")

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['my_info'], LANGS['fa']['my_info']])
def show_my_info(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    
    # Check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    u = users.get(user_id, {})
    
    status = u.get('status', 'Active')
    user_type = u.get('user_type', 'new')
    trial = "✅ Used" if u.get('trial_used') else "❌ Not Used"
    ref_points = u.get('ref_points', 0)
    buy_count = u.get('buy_count', 0)
    balance = u.get('wallet_balance', 0)
    debt = u.get('debt', 0)
    
    if lang == 'fa':
        if user_type == 'trusted_seller':
            type_str = "همکار معتبر (پنل اعتباری)"
        else:
            type_str = "کاربر عادی" if user_type == 'new' else "کاربر وفادار (دسترسی به کارت)"
            
        info = f"👤 *پروفایل کاربری*\n\n"
        info += f"🆔 شناسه: `{user_id}`\n"
        info += f"🏅 سطح: *{type_str}*\n"
        if user_type == 'trusted_seller':
            info += f"🔴 بدهی فعلی: `{debt}` تومان\n"
        info += f"💰 موجودی کیف پول: `{balance}`\n"
        info += f"📊 وضعیت: `{status}`\n"
        info += f"🛒 تعداد خرید: `{buy_count}`\n"
        info += f"🎁 تست رایگان: {trial}\n"
        info += f"👥 امتیاز دعوت: `{ref_points}`"
    else:
        if user_type == 'trusted_seller':
            type_str = "Trusted Seller (Post-pay)"
        else:
            type_str = "Regular User" if user_type == 'new' else "Old User (Card Access)"

        info = f"👤 *User Profile*\n\n"
        info += f"🆔 ID: `{user_id}`\n"
        info += f"🏅 Tier: *{type_str}*\n"
        if user_type == 'trusted_seller':
            info += f"🔴 Current Debt: `{debt}`\n"
        info += f"💰 Wallet Balance: `{balance}`\n"
        info += f"📊 Status: `{status}`\n"
        info += f"🛒 Total Purchases: `{buy_count}`\n"
        info += f"🎁 Trial: {trial}\n"
        info += f"👥 Referral Points: `{ref_points}`"
    
    bot.send_message(message.chat.id, info, parse_mode='Markdown')

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['wallet'], LANGS['fa']['wallet']])
def wallet_menu(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    if not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    u = users.get(user_id, {})
    balance = u.get('wallet_balance', 0)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(LANGS[lang]['charge_wallet'], callback_data="wallet_charge"))
    
    bot.send_message(user_id, LANGS[lang]['wallet_balance_msg'].format(balance=balance), reply_markup=markup, parse_mode='Markdown')

@bot.callback_query_handler(func=lambda call: call.data == "wallet_charge")
def wallet_charge_callback(call):
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    update_user(user_id, user_state='waiting_for_charge_amount')
    bot.edit_message_text(LANGS[lang]['enter_amount'], user_id, call.message.message_id)
    bot.answer_callback_query(call.id)

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['prize_redeem_btn'], LANGS['fa']['prize_redeem_btn']])
def prize_redeem_start(message):
    lang = get_user_lang(message.chat.id)
    update_user(message.chat.id, user_state='waiting_for_prize_code')
    bot.send_message(message.chat.id, LANGS[lang]['enter_prize_code'], parse_mode='Markdown')

@bot.message_handler(commands=['addprize'], func=lambda m: is_admin(m.chat.id))
def admin_add_prize(message):
    try:
        # /addprize [code] [amount] [hours] [limit]
        parts = message.text.split()
        if len(parts) < 5:
            bot.reply_to(message, "Usage: `/addprize [code] [amount] [hours] [limit]`")
            return
        
        code = parts[1]
        amount = int(parts[2])
        hours = int(parts[3])
        limit = int(parts[4])
        
        prize_codes[code] = {
            'amount': amount,
            'expiry': time.time() + (hours * 3600),
            'limit': limit,
            'used_by': [],
            'created_at': time.time()
        }
        save_prize_codes()
        
        lang = get_user_lang(message.chat.id)
        bot.reply_to(message, LANGS[lang]['admin_prize_added'].format(code=code, amount=amount, hours=hours, limit=limit), parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(func=lambda m: m.text in [LANGS['en']['contact_admin'], LANGS['fa']['contact_admin']])
def contact_admin(message):
    lang = get_user_lang(message.chat.id)
    update_user(message.chat.id, user_state='waiting_for_admin_msg')
    bot.send_message(message.chat.id, LANGS[lang]['msg_to_admin_prompt'])

@bot.message_handler(func=lambda m: m.text and ("Language" in m.text or "تغییر زبان" in m.text))
def change_lang(message):
    print(f"DEBUG: Change language triggered by {message.chat.id}. Text: {message.text}")
    start(message, force_lang_select=True)

# Text and Media handling
@bot.message_handler(content_types=['photo', 'text', 'audio', 'voice', 'video', 'document'])
def handle_all_messages(message):
    user_id = str(message.chat.id)
    u = users.get(user_id, {})
    lang = get_user_lang(user_id)
    state = u.get('user_state')
    
    # Ignore commands
    if message.text and message.text.startswith('/'):
        return

    # Check subscription (except admin)
    if user_id != str(ADMIN_ID) and not is_subscribed(user_id):
        bot.send_message(user_id, LANGS[lang]['join_channel_prompt'].format(channel=CHANNEL_ID), reply_markup=get_join_markup(lang))
        return

    if state == 'waiting_for_trial_name':
        if not message.text: return
        chosen_name = message.text.strip().lower()
        if not re.match(r'^[a-z0-9]{3,15}$', chosen_name):
            bot.send_message(user_id, "❌ نام وارد شده نامعتبر است. فقط حروف انگلیسی و اعداد بین ۳ تا ۱۵ کاراکتر مجاز است." if lang=='fa' else "❌ Invalid name. Only alphanumeric English characters (3-15 chars) are allowed.")
            return
        if check_client_name_exists(chosen_name):
            bot.send_message(user_id, "❌ این نام قبلاً توسط کاربر دیگری انتخاب شده است. لطفاً نام دیگری ارسال کنید:" if lang=='fa' else "❌ This name already exists. Please choose a different name:")
            return
            
        update_user(user_id, user_state=None, trial_used=True, status='approved', last_plan=plan_key)
        
        plan_info = plans_data[plan_key]
        expiry_days = plan_info.get('expiry_days', 1)
        volume_gb = plan_info.get('volume_gb', 1)
        remark = f"trial-{user_id}"
        
        try:
            link = add_sui_client(remark, expiry_days, volume_gb, custom_name=chosen_name)
            add_purchase_to_history(user_id, plan_key, [link])
            plan_name = plan_info['name'].get(lang, plan_info['name']['en'])
            send_config_with_qr(user_id, link, lang, plan_name=plan_name)
        except Exception as e:
            print(f"Error creating trial client: {e}")
            bot.send_message(user_id, "⚠️ Error creating trial link.")
        return

    if state == 'waiting_for_purchase_name':
        if not message.text: return
        chosen_name = message.text.strip().lower()
        if not re.match(r'^[a-z0-9]{3,15}$', chosen_name):
            bot.send_message(user_id, "❌ نام وارد شده نامعتبر است. فقط حروف انگلیسی و اعداد بین ۳ تا ۱۵ کاراکتر مجاز است." if lang=='fa' else "❌ Invalid name. Only alphanumeric English characters (3-15 chars) are allowed.")
            return
        if check_client_name_exists(chosen_name):
            bot.send_message(user_id, "❌ این نام قبلاً توسط کاربر دیگری انتخاب شده است. لطفاً نام دیگری ارسال کنید:" if lang=='fa' else "❌ This name already exists. Please choose a different name:")
            return
            
        receipt_data = u.get('pending_receipt_data')
        receipt_type = u.get('pending_receipt_type')
        qty = u.get('pending_quantity', 1)
        
        update_user(user_id, user_state=None, pending_config_name=chosen_name, status='pending_approval')
        
        user_type = u.get('user_type', 'new')
        markup = types.InlineKeyboardMarkup()
        
        if plan_key.startswith('charge_wallet_'):
            amount = plan_key.replace('charge_wallet_', '')
            caption = f"💰 *Wallet Charge Receipt*\nUser: `{user_id}`\nAmount: `{amount}`\nUsername: @{message.from_user.username or '-'}"
            markup.add(types.InlineKeyboardButton(f"✅ Approve Charge", callback_data=f"admin_approve_{user_id}_{plan_key}"))
        else:
            plan_info = plans_data.get(plan_key)
            if not plan_info: return
            caption = f"💰 *Payment Receipt*\nUser: `{user_id}`\nType: `{user_type}`\nQty: `{qty}`\nUsername: @{message.from_user.username or '-'}\nPlan: {plan_info['name']['en']}\nDesired Config Name: `{chosen_name}`"
            markup.add(types.InlineKeyboardButton(f"✅ Approve & Send", callback_data=f"admin_approve_{user_id}_{plan_key}_0"))

        if user_type == 'new':
            markup.add(types.InlineKeyboardButton("⭐ Promote + Card Access", callback_data=f"admin_promote_{user_id}"))

        markup.add(types.InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user_id}"))

        if receipt_type == 'photo':
            bot.send_photo(ADMIN_ID, receipt_data, caption=caption, reply_markup=markup, parse_mode='Markdown')
        else:
            bot.send_message(ADMIN_ID, caption + f"\n\nText: {receipt_data}", reply_markup=markup, parse_mode='Markdown')

        bot.send_message(user_id, LANGS[lang]['receipt_received'])
        return

    # Handle Prize Codes
    if state == 'waiting_for_prize_code':
        if not message.text: return
        code = message.text.strip()
        now = time.time()
        
        if code in prize_codes:
            pc = prize_codes[code]
            if now < pc['expiry'] and len(pc['used_by']) < pc['limit']:
                if user_id not in pc['used_by']:
                    # Valid
                    amount = pc['amount']
                    pc['used_by'].append(user_id)
                    save_prize_codes()
                    
                    new_balance = u.get('wallet_balance', 0) + amount
                    update_user(user_id, wallet_balance=new_balance, user_state=None)
                    
                    bot.send_message(user_id, LANGS[lang]['prize_success'].format(amount=amount, balance=new_balance), parse_mode='Markdown')
                    return
                else:
                    bot.send_message(user_id, LANGS[lang]['prize_already_used'], parse_mode='Markdown')
                    update_user(user_id, user_state=None)
                    return
            else:
                # Expired or full
                bot.send_message(user_id, LANGS[lang]['prize_invalid'], parse_mode='Markdown')
                update_user(user_id, user_state=None)
                return
        else:
            bot.send_message(user_id, LANGS[lang]['prize_invalid'], parse_mode='Markdown')
            update_user(user_id, user_state=None)
            return

    # Handle Bale States
    if state == 'waiting_for_bale_id':
        if message.text:
            bale_id = message.text.strip()
            update_user(user_id, user_state='waiting_for_bale_media', bale_chat_id=bale_id)
            bot.send_message(user_id, LANGS[lang]['bale_media_prompt'], parse_mode='Markdown')
            return
    elif state == 'waiting_for_bale_media':
        bale_chat_id = u.get('bale_chat_id')
        if bale_chat_id:
            success = handle_bale_upload(bot, message, user_id, lang, bale_chat_id)
            if success:
                update_user(user_id, user_state=None)
            return

    # Handle Admin States
    if user_id == str(ADMIN_ID) and u.get('admin_state'):
        state = u.get('admin_state')
        
        if state.startswith("bulkadd_"):
            plan_key = state.replace("bulkadd_", "")
            links = [line.strip() for line in message.text.split('\n') if line.strip()]
            if links:
                plans_data[plan_key].setdefault('links', []).extend(links)
                save_all_plans()
                bot.send_message(ADMIN_ID, f"Added {len(links)} links. Total: {len(plans_data[plan_key]['links'])}")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("rename_tier_"):
            tier_key = state.replace("rename_tier_", "")
            if '|' in message.text:
                en_name, fa_name = [x.strip() for x in message.text.split('|', 1)]
                tiers_data[tier_key]['name'] = {'en': en_name, 'fa': fa_name}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Tier renamed for {tier_key}.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Name|Farsi_Name`")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("edit_tier_desc_"):
            tier_key = state.replace("edit_tier_desc_", "")
            if '|' in message.text:
                en_desc, fa_desc = [x.strip() for x in message.text.split('|', 1)]
                tiers_data[tier_key]['description'] = {'en': en_desc, 'fa': fa_desc}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Tier description updated for {tier_key}.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Desc|Farsi_Desc`")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("tier_add_plan_"):
            tier_key = state.replace("tier_add_plan_", "")
            plan_key = message.text.strip()
            if plan_key in plans_data:
                if 'plans' not in tiers_data[tier_key]:
                    tiers_data[tier_key]['plans'] = []
                if plan_key not in tiers_data[tier_key]['plans']:
                    tiers_data[tier_key]['plans'].append(plan_key)
                    save_all_plans()
                    bot.send_message(ADMIN_ID, f"✅ Plan `{plan_key}` added to Tier `{tier_key}`.")
                else:
                    bot.send_message(ADMIN_ID, "⚠️ Plan already in this tier.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Plan ID not found.")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state == "add_tier_id":
            tier_key = message.text.strip().lower().replace(" ", "_")
            if tier_key in tiers_data:
                bot.send_message(ADMIN_ID, "⚠️ Tier ID already exists.")
                return
            update_user(ADMIN_ID, admin_state=f"add_tier_name_{tier_key}")
            bot.send_message(ADMIN_ID, f"Tier ID `{tier_key}` set. Send NAME (Format: English_Name|Farsi_Name):")
            return

        elif state.startswith("add_tier_name_"):
            tier_key = state.replace("add_tier_name_", "")
            if '|' in message.text:
                en_name, fa_name = [x.strip() for x in message.text.split('|', 1)]
                tiers_data[tier_key] = {"name": {"en": en_name, "fa": fa_name}, "description": {"en": "None", "fa": "ندارد"}, "plans": []}
                update_user(ADMIN_ID, admin_state=f"add_tier_desc_{tier_key}")
                bot.send_message(ADMIN_ID, "Name set. Send DESCRIPTION (Format: English_Desc|Farsi_Desc):")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format.")
            return

        elif state.startswith("add_tier_desc_"):
            tier_key = state.replace("add_tier_desc_", "")
            if '|' in message.text:
                en_desc, fa_desc = [x.strip() for x in message.text.split('|', 1)]
                tiers_data[tier_key]['description'] = {'en': en_desc, 'fa': fa_desc}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Tier `{tier_key}` added!")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format.")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state == "add_plan_id":
            plan_key = message.text.strip().lower().replace(" ", "_")
            if plan_key in plans_data:
                bot.send_message(ADMIN_ID, "⚠️ Plan ID already exists. Try another one.")
                return
            update_user(ADMIN_ID, admin_state=f"add_plan_name_{plan_key}")
            bot.send_message(ADMIN_ID, f"Plan ID `{plan_key}` set. Now send the NAME (Format: English_Name|Farsi_Name):")
            return

        elif state.startswith("add_plan_name_"):
            plan_key = state.replace("add_plan_name_", "")
            if '|' in message.text:
                en_name, fa_name = [x.strip() for x in message.text.split('|', 1)]
                plans_data[plan_key] = {
                    "name": {"en": en_name, "fa": fa_name},
                    "price": {"en": "Not Set", "fa": "تنظیم نشده"},
                    "is_trial": False,
                    "links": []
                }
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Plan `{plan_key}` added! Please go to Manage Plans to set price and description.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Name|Farsi_Name`")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("edit_stars_"):
            plan_key = state.replace("edit_stars_", "")
            try:
                stars = int(message.text.strip())
                plans_data[plan_key]['stars_price'] = stars
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Stars price updated to {stars} for {plan_key}.")
            except ValueError:
                bot.send_message(ADMIN_ID, "⚠️ Invalid number. Please send an integer.")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("edit_price_"):
            plan_key = state.replace("edit_price_", "")
            if '|' in message.text:
                en_price, fa_price = [x.strip() for x in message.text.split('|', 1)]
                plans_data[plan_key]['price'] = {'en': en_price, 'fa': fa_price}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Price updated for {plan_key}.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Price|Farsi_Price`")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("edit_trusted_price_"):
            plan_key = state.replace("edit_trusted_price_", "")
            if '|' in message.text:
                en_price, fa_price = [x.strip() for x in message.text.split('|', 1)]
                plans_data[plan_key]['trusted_price'] = {'en': en_price, 'fa': fa_price}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Trusted price updated for {plan_key}.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Price|Farsi_Price`")
            update_user(ADMIN_ID, admin_state=None)
            admin_dashboard(message)
            return

        elif state.startswith("edit_desc_"):
            plan_key = state.replace("edit_desc_", "")
            if '|' in message.text:
                en_desc, fa_desc = [x.strip() for x in message.text.split('|', 1)]
                plans_data[plan_key]['description'] = {'en': en_desc, 'fa': fa_desc}
                save_all_plans()
                bot.send_message(ADMIN_ID, f"✅ Description updated for {plan_key}.")
            else:
                bot.send_message(ADMIN_ID, "⚠️ Invalid format. Use: `English_Desc|Farsi_Desc`")
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
    if u.get('user_state') == 'waiting_for_charge_amount':
        amount = message.text
        if not amount or not amount.isdigit():
            bot.send_message(user_id, LANGS[lang]['invalid_amount'])
            return
        
        update_user(user_id, user_state=None, pending_plan=f"charge_wallet_{amount}")
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_card_btn'], callback_data=f"pay_method_card_charge_wallet_{amount}"))
        markup.add(
            types.InlineKeyboardButton(LANGS[lang]['pay_crypto_btn'], callback_data=f"pay_method_crypto_charge_wallet_{amount}"),
            types.InlineKeyboardButton(LANGS[lang]['pay_usdt_btn'], callback_data=f"pay_method_usdt_charge_wallet_{amount}")
        )
        
        bot.send_message(user_id, LANGS[lang]['choose_payment_method'], reply_markup=markup)
        return

    if u.get('user_state') == 'waiting_for_admin_msg':
        update_user(user_id, user_state=None)
        user_type = u.get('user_type', 'new')
        caption = LANGS['en']['admin_new_msg'].format(user_id=user_id, username=message.from_user.username or 'N/A', text=message.text or '[Media]')
        caption += f"\n\n👤 Type: `{user_type}`"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(LANGS['en']['admin_reply_btn'], callback_data=f"admin_reply_user_{user_id}"))
        if user_type == 'new':
            markup.add(types.InlineKeyboardButton("⭐ Promote to Old User", callback_data=f"admin_promote_{user_id}"))
        bot.send_message(ADMIN_ID, caption, reply_markup=markup, parse_mode='Markdown')
        bot.send_message(user_id, LANGS[lang]['msg_sent_to_admin'])
        return

    # Handle Receipts
    plan_key = u.get('pending_plan')
    
    # Check if text is a main menu button to avoid treating it as a receipt
    main_menu_buttons = []
    for l in LANGS.values():
        main_menu_buttons.extend([
            l.get('show_plans'), l.get('view_tiers'), l.get('how_to_connect'), 
            l.get('my_info'), l.get('my_purchases'), l.get('wallet'), 
            l.get('referral'), l.get('server_status'), l.get('upload_bale'), 
            l.get('prize_redeem_btn'), l.get('contact_admin'), l.get('choose_lang_btn')
        ])

    if message.text in main_menu_buttons or message.text in ['👥 دعوت و کسب درآمد', '👥 زیر مجموعه گیری']:
        return

    if plan_key and (message.content_type == 'photo' or (message.text and not message.text.startswith('/'))):
        receipt_data = message.photo[-1].file_id if message.content_type == 'photo' else message.text
        receipt_type = 'photo' if message.content_type == 'photo' else 'text'
        
        # If wallet charge, we don't ask for a config name
        if plan_key.startswith('charge_wallet_'):
            update_user(user_id, status='pending_approval')
            markup = types.InlineKeyboardMarkup()
            amount = plan_key.replace('charge_wallet_', '')
            caption = f"💰 *Wallet Charge Receipt*\nUser: `{user_id}`\nAmount: `{amount}`\nUsername: @{message.from_user.username or '-'}"
            markup.add(types.InlineKeyboardButton(f"✅ Approve Charge", callback_data=f"admin_approve_{user_id}_{plan_key}"))
            markup.add(types.InlineKeyboardButton("❌ Reject", callback_data=f"admin_reject_{user_id}"))
            
            if receipt_type == 'photo':
                bot.send_photo(ADMIN_ID, receipt_data, caption=caption, reply_markup=markup, parse_mode='Markdown')
            else:
                bot.send_message(ADMIN_ID, caption + f"\n\nText: {receipt_data}", reply_markup=markup, parse_mode='Markdown')
                
            bot.send_message(user_id, LANGS[lang]['receipt_received'])
            return
            
        update_user(user_id, 
                    user_state='waiting_for_purchase_name', 
                    pending_receipt_data=receipt_data, 
                    pending_receipt_type=receipt_type)
                    
        bot.send_message(user_id, 
                         "✏️ *نام کانفیگ خود را وارد کنید:*\n\nلطفاً یک نام دلخواه به انگلیسی بین ۳ تا ۱۵ حرف/عدد وارد کنید (مثال: `myvpn`):" if lang=='fa' else 
                         "✏️ *Enter configuration name:*\n\nPlease enter an English name between 3 and 15 characters/digits (e.g. `myvpn`):", 
                         parse_mode='Markdown')
        return
@bot.callback_query_handler(func=lambda call: call.data.startswith('select_plan_'))
def select_plan_callback(call):
    if not check_sub_callback(call): return
    plan_key = call.data.replace('select_plan_', '')
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    
    if plan_key not in plans_data: return
    plan_info = plans_data[plan_key]
    
    if plan_info.get('is_trial'):
        if users.get(user_id, {}).get('trial_used'):
            bot.answer_callback_query(call.id, LANGS[lang]['already_trial'], show_alert=True)
            return
        
        update_user(user_id, user_state='waiting_for_trial_name', pending_plan=plan_key)
        bot.send_message(user_id, "✏️ *نام کانفیگ تستی خود را وارد کنید:*\n\nلطفاً یک نام دلخواه به انگلیسی بین ۳ تا ۱۵ حرف/عدد وارد کنید (مثال: `testali`):" if lang=='fa' else "✏️ *Enter configuration name:*\n\nPlease enter an English name between 3 and 15 characters/digits (e.g. `testali`):", parse_mode='Markdown')
        bot.answer_callback_query(call.id)
        return

    name = plan_info['name'].get(lang, plan_info['name']['en'])
    available_count = 999
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    btns = []
    for q in [1, 2, 3, 5, 10]:
        if q <= available_count:
            btns.append(types.InlineKeyboardButton(str(q), callback_data=f"set_qty_{plan_key}_{q}"))
        
    markup.add(*btns)
    
    bot.edit_message_text(LANGS[lang]['select_quantity'].format(plan=escape_md(name)), user_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('set_qty_'))
def select_quantity_callback(call):
    if not check_sub_callback(call): return
    # data: set_qty_{plan_key}_{qty}
    data = call.data.split('_')
    plan_key = "_".join(data[2:-1])
    qty = int(data[-1])
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)
    
    if plan_key not in plans_data: return
    
    update_user(user_id, pending_plan=plan_key, pending_quantity=qty, user_state=None)
    user_type = users.get(user_id, {}).get('user_type', 'new')
    
    markup = types.InlineKeyboardMarkup()
    
    if user_type == 'trusted_seller':
        markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_trusted_btn'], callback_data=f"pay_method_trusted_{plan_key}"))

    markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_wallet_btn'], callback_data=f"pay_method_wallet_{plan_key}"))

    if user_type == 'old':
        markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_card_btn'], callback_data=f"pay_method_card_{plan_key}"))
    
    markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_crypto_btn'], callback_data=f"pay_method_crypto_{plan_key}"))
    markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_usdt_btn'], callback_data=f"pay_method_usdt_{plan_key}"))
    
    if plans_data[plan_key].get('stars_price'):
        markup.add(types.InlineKeyboardButton(LANGS[lang]['pay_stars_btn'], callback_data=f"pay_method_stars_{plan_key}"))
        
    bot.edit_message_text(LANGS[lang]['choose_payment_method'], user_id, call.message.message_id, reply_markup=markup)
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_method_'))
def pay_method_callback(call):
    if not check_sub_callback(call): return
    data = call.data.split('_')
    method = data[2]
    plan_key = "_".join(data[3:])
    user_id = str(call.message.chat.id)
    lang = get_user_lang(user_id)

    if plan_key.startswith('charge_wallet_'):
        amount = plan_key.replace('charge_wallet_', '')
        if method == 'card':
            msg = LANGS[lang]['charge_summary'].format(amount=amount, card=CARD_NUMBER)
        elif method == 'crypto':
            msg = LANGS[lang]['charge_summary_crypto'].format(amount=amount, ton=TON_ADDRESS)
        elif method == 'usdt':
            msg = LANGS[lang]['charge_summary_usdt'].format(amount=amount, address=USDT_ERC20_ADDRESS)

        bot.edit_message_text(msg, user_id, call.message.message_id, parse_mode='Markdown')
        update_user(user_id, pending_plan=plan_key, user_state=None)
        bot.answer_callback_query(call.id)
        return

    if plan_key not in plans_data: return
    plan_info = plans_data[plan_key]
    name = plan_info['name'].get(lang, plan_info['name']['en'])
    
    # Extract numeric price (preferring Farsi/Toman as base for wallet/debt)
    u = users.get(user_id, {})
    user_type = u.get('user_type', 'new')
    
    # Use trusted_price if user is a trusted seller
    if user_type == 'trusted_seller':
        price_fa = plan_info.get('trusted_price', plan_info['price']).get('fa', '0')
        price_lang = plan_info.get('trusted_price', plan_info['price']).get(lang, '0')
    else:
        price_fa = plan_info['price'].get('fa', '0')
        price_lang = plan_info['price'].get(lang, '0')

    price_digits = "".join(re.findall(r'\d+', price_fa))
    price_num = int(price_digits) if price_digits else 0

    qty = u.get('pending_quantity', 1)
    total_price_num = price_num * qty

    if method == 'trusted':
        if user_type != 'trusted_seller':
            bot.answer_callback_query(call.id, "Access Denied.")
            return

        if plan_key in plans_data:
            sent_links = []
            expiry_days = plans_data[plan_key].get('expiry_days', 30)
            volume_gb = plans_data[plan_key].get('volume_gb', 0)
            
            for i in range(qty):
                remark = f"trusted-{user_id}-{i+1}"
                try:
                    link = add_sui_client(remark, expiry_days, volume_gb)
                    if link:
                        sent_links.append(link)
                except Exception as e:
                    print(f"Error creating client: {e}")

            if sent_links:
                # Record debt and purchase
                current_debt = u.get('debt', 0)
                new_debt = current_debt + total_price_num
                
                # Add to purchase history and debt record
                add_purchase_to_history(user_id, plan_key, sent_links)
                
                update_user(user_id, debt=new_debt, status='approved', last_plan=plan_key, pending_plan=None, pending_quantity=1)
                
                bot.edit_message_text(LANGS[lang]['trusted_payment_received'], user_id, call.message.message_id, parse_mode='Markdown')
                plan_name = plans_data[plan_key]['name'].get(lang, plans_data[plan_key]['name']['en'])
                for link in sent_links:
                    send_config_with_qr(user_id, link, lang, plan_name=plan_name)

                # Notify Admin
                bot.send_message(ADMIN_ID, f"🤝 *Trusted Seller Order!*\nUser: `{user_id}` (@{u.get('username')})\nPlan: {plan_key}\nQty: {qty}\nPrice: {total_price_num}\nNew Total Debt: `{new_debt}`")
            else:
                bot.send_message(user_id, "❌ Error: Failed to generate configuration links.")
        else:
            bot.send_message(user_id, "❌ Error: Plan not found.")
        return

    price = price_lang

    desc_data = plan_info.get('description', {})
    desc = desc_data.get(lang, desc_data.get('en', ''))
    if desc:
        desc = f"\n📝 {desc}\n"
    else:
        desc = ""

    total_price_text = f"{price} x {qty}"

    if method == 'wallet':
        u = users.get(user_id, {})
        balance = u.get('wallet_balance', 0)
        if balance >= total_price_num:
            # Process Payment Immediately
            new_balance = balance - total_price_num
            update_user(user_id, wallet_balance=new_balance)

            # Send config
            if plan_key in plans_data:
                sent_links = []
                expiry_days = plans_data[plan_key].get('expiry_days', 30)
                volume_gb = plans_data[plan_key].get('volume_gb', 0)
                
                for i in range(qty):
                    remark = f"wallet-{user_id}-{i+1}"
                    try:
                        link = add_sui_client(remark, expiry_days, volume_gb)
                        if link:
                            sent_links.append(link)
                    except Exception as e:
                        print(f"Error creating client: {e}")

                if sent_links:
                    update_user(user_id, status='approved', last_plan=plan_key, pending_plan=None, pending_quantity=1)
                    add_purchase_to_history(user_id, plan_key, sent_links)

                    bot.edit_message_text(LANGS[lang]['wallet_payment_success'].format(amount=total_price_num), user_id, call.message.message_id, parse_mode='Markdown')
                    plan_name = plans_data[plan_key]['name'].get(lang, plans_data[plan_key]['name']['en'])
                    for link in sent_links:
                        send_config_with_qr(user_id, link, lang, plan_name=plan_name)

                    # Notify Admin
                    bot.send_message(ADMIN_ID, f"💰 *Wallet Payment Received!*\nUser: `{user_id}`\nPlan: {plan_key}\nQty: {qty}\nAmount: {total_price_num}\nLinks sent automatically.")
                else:
                    bot.send_message(user_id, "❌ Error: Failed to generate configuration links.")
            else:
                bot.send_message(user_id, "❌ Error: Plan not found.")
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(LANGS[lang]['charge_wallet'], callback_data="wallet_charge"))
            bot.edit_message_text(LANGS[lang]['insufficient_balance'], user_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
        return

    if method == 'card':
        msg = LANGS[lang]['after_choose_plan'].format(plan=escape_md(name), price=escape_md(price), qty=qty, total_price=escape_md(total_price_text), desc=escape_md(desc), card=escape_md(CARD_NUMBER))
        bot.edit_message_text(msg, user_id, call.message.message_id, parse_mode='Markdown')
        update_user(user_id, pending_plan=plan_key, user_state=None)
    elif method == 'crypto':
        msg = LANGS[lang]['after_choose_plan_crypto'].format(plan=escape_md(name), price=escape_md(price), qty=qty, total_price=escape_md(total_price_text), desc=escape_md(desc), ton=escape_md(TON_ADDRESS))
        bot.edit_message_text(msg, user_id, call.message.message_id, parse_mode='Markdown')
        update_user(user_id, pending_plan=plan_key, user_state=None)
    elif method == 'usdt':
        msg = LANGS[lang]['after_choose_plan_usdt'].format(plan=escape_md(name), price=escape_md(price), qty=qty, total_price=escape_md(total_price_text), desc=escape_md(desc), address=escape_md(USDT_ERC20_ADDRESS))
        bot.edit_message_text(msg, user_id, call.message.message_id, parse_mode='Markdown')
        update_user(user_id, pending_plan=plan_key, user_state=None)
    elif method == 'stars':
        stars_price = plan_info.get('stars_price')
        if not stars_price:
            bot.answer_callback_query(call.id, "Stars payment not available for this plan.")
            return
        
        total_stars = stars_price * qty
        bot.delete_message(user_id, call.message.message_id)
        bot.send_invoice(
            chat_id=user_id,
            title=f"{name} x{qty}",
            description=desc[:255] if desc else f"VPN Plan: {name} x{qty}",
            invoice_payload=f"pay_stars_{plan_key}_{qty}",
            provider_token="", 
            currency="XTR",
            prices=[types.LabeledPrice(label=f"{name} x{qty}", amount=total_stars)],
            start_parameter="vpn_plan_payment"
        )
    
    bot.answer_callback_query(call.id)

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    user_id = str(message.chat.id)
    lang = get_user_lang(user_id)
    payload = message.successful_payment.invoice_payload
    # payload: pay_stars_{plan_key}_{qty}
    parts = payload.split('_')
    plan_key = "_".join(parts[2:-1])
    qty = int(parts[-1])
    
    if plan_key in plans_data:
        sent_links = []
        expiry_days = plans_data[plan_key].get('expiry_days', 30)
        volume_gb = plans_data[plan_key].get('volume_gb', 0)
        
        for i in range(qty):
            remark = f"stars-{user_id}-{i+1}"
            try:
                link = add_sui_client(remark, expiry_days, volume_gb)
                if link:
                    sent_links.append(link)
            except Exception as e:
                print(f"Error creating client: {e}")

        if sent_links:
            update_user(user_id, status='approved', last_plan=plan_key, pending_plan=None, pending_quantity=1)
            add_purchase_to_history(user_id, plan_key, sent_links)
            
            bot.send_message(user_id, LANGS[lang]['stars_payment_received'])
            plan_name = plans_data[plan_key]['name'].get(lang, plans_data[plan_key]['name']['en'])
            for link in sent_links:
                send_config_with_qr(user_id, link, lang, plan_name=plan_name)
            
            # Notify Admin
            bot.send_message(ADMIN_ID, f"⭐️ *Stars Payment Received!*\nUser: `{user_id}`\nPlan: {plan_key}\nQty: {qty}\nLinks sent automatically.")
        else:
            bot.send_message(user_id, "❌ Error: Failed to generate configuration links.")
    else:
        bot.send_message(user_id, "❌ Error: Plan not found.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_promote_'))
def admin_promote_user(call):
    target_uid = call.data.replace('admin_promote_', '')
    update_user(target_uid, user_type='old')
    bot.answer_callback_query(call.id, "User promoted to OLD.")
    bot.send_message(ADMIN_ID, f"✅ User {target_uid} is now an OLD user (Can use card).")
    # Update the message markup to remove the promote button
    bot.edit_message_reply_markup(ADMIN_ID, call.message.message_id, reply_markup=None)

def get_jwt_secret():
    try:
        # Check both local Windows developer path and remote Linux path
        paths = ["/root/shipien/web/.env.local", "./web/.env.local"]
        for p in paths:
            if os.path.exists(p):
                with open(p, "r") as f:
                    for line in f:
                        if line.startswith("JWT_SECRET="):
                            return line.split("=")[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "shipien-jwt-secret-key-2026-change-this-now!"

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_approve_web_') or call.data.startswith('admin_reject_web_'))
def admin_process_web_receipt(call):
    is_approve = call.data.startswith('admin_approve_web_')
    sub_id = call.data.replace('admin_approve_web_', '').replace('admin_reject_web_', '')
    
    import requests
    jwt_secret = get_jwt_secret()
    headers = {"Authorization": f"Bearer {jwt_secret}", "Content-Type": "application/json"}
    
    try:
        r = requests.post("https://shipien-web.vercel.app/api/internal/subscription", json={"subscriptionId": sub_id}, headers=headers, timeout=15)
        if r.status_code != 200:
            bot.answer_callback_query(call.id, f"Error: API returned status {r.status_code}")
            return
        res = r.json()
        if not res.get("success"):
            bot.answer_callback_query(call.id, "Error: Subscription not found on web API")
            return
        sub = res["subscription"]
    except Exception as e:
        bot.answer_callback_query(call.id, f"Network Error: {str(e)}")
        return

    if not is_approve:
        try:
            r = requests.post("https://shipien-web.vercel.app/api/internal/subscription/reject", json={"subscriptionId": sub_id}, headers=headers, timeout=15)
            if r.status_code == 200:
                bot.answer_callback_query(call.id, "Subscription Rejected")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(ADMIN_ID, f"❌ Rejected web subscription for user {sub['username']}.")
            else:
                bot.answer_callback_query(call.id, "Failed to reject on Web DB")
        except Exception as e:
            bot.answer_callback_query(call.id, f"Network Error: {str(e)}")
        return

    remark = f"web-{sub['username']}"
    expiry_days = sub["duration"]
    
    vol_str = sub["bandwidth"].upper()
    if "UNLIMITED" in vol_str:
        volume_gb = 0
    else:
        vol_match = re.search(r'\d+', vol_str)
        volume_gb = int(vol_match.group()) if vol_match else 50
        
    try:
        custom_name = sub.get("configName")
        link = add_sui_client(remark, expiry_days, volume_gb, custom_name=custom_name)
        if not link:
            raise Exception("add_sui_client returned empty link")
    except Exception as e:
        bot.answer_callback_query(call.id, f"S-UI Client Error: {str(e)}")
        return
        
    parsed = parse_anytls_link(link)
    client_name = None
    if parsed:
        password, server, port, sni, node_tag = parsed
        client_name = get_client_name_by_password(password)

    try:
        r = requests.post(
            "https://shipien-web.vercel.app/api/internal/subscription/activate",
            json={"subscriptionId": sub_id, "configLink": link, "clientName": client_name},
            headers=headers,
            timeout=15
        )
        if r.status_code == 200:
            bot.answer_callback_query(call.id, "Approved and Activated!")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(ADMIN_ID, f"✅ Approved web subscription for {sub['username']}. Generated anytls configuration sent to web dashboard.")
        else:
            bot.answer_callback_query(call.id, f"API activation failed with status {r.status_code}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Network Error: {str(e)}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('admin_approve_') or call.data.startswith('admin_reject_'))
def admin_process_receipt(call):
    data = call.data.split('_')
    action = data[1]
    target_uid = data[2]
    lang = get_user_lang(target_uid)
    
    if action == 'approve':
        # Check if it's a wallet charge
        if 'charge_wallet_' in call.data:
            # Format: admin_approve_{user_id}_charge_wallet_{amount}
            amount = int(data[-1])
            u = users.get(target_uid, {})
            current_balance = u.get('wallet_balance', 0)
            new_balance = current_balance + amount
            update_user(target_uid, wallet_balance=new_balance, status='approved', pending_plan=None)
            
            bot.send_message(target_uid, LANGS[lang]['wallet_charged_success'].format(amount=amount, balance=new_balance), parse_mode='Markdown')
            bot.answer_callback_query(call.id, f"Approved! User's new balance: {new_balance}")
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
            bot.send_message(ADMIN_ID, f"✅ User {target_uid} wallet charged with {amount}. New balance: {new_balance}")
            return

        # data format: admin_approve_{user_id}_{plan_key}_{idx}
        idx = int(data[-1])
        plan_key = "_".join(data[3:-1])
        u = users.get(target_uid, {})
        qty = u.get('pending_quantity', 1)

        if plan_key in plans_data:
            sent_links = []
            expiry_days = plans_data[plan_key].get('expiry_days', 30)
            volume_gb = plans_data[plan_key].get('volume_gb', 0)
            
            custom_name = u.get('pending_config_name')
            for i in range(qty):
                remark = f"user-{target_uid}-{i+1}"
                name_to_use = custom_name if i == 0 else f"{custom_name}{i+1}" if custom_name else None
                try:
                    link = add_sui_client(remark, expiry_days, volume_gb, custom_name=name_to_use)
                    if link:
                        sent_links.append(link)
                except Exception as e:
                    print(f"Error creating client: {e}")
            
            if sent_links:
                update_user(target_uid, status='approved', last_plan=plan_key, pending_plan=None, pending_quantity=1)
                add_purchase_to_history(target_uid, plan_key, sent_links)
                
                plan_name = plans_data[plan_key]['name'].get(lang, plans_data[plan_key]['name']['en'])
                for link in sent_links:
                    send_config_with_qr(target_uid, link, lang, plan_name=plan_name)
                
                bot.answer_callback_query(call.id, f"Approved and sent {qty} links!")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                bot.send_message(ADMIN_ID, f"✅ User {target_uid} approved for {qty} x {plan_key}.")
            else:
                bot.answer_callback_query(call.id, "Error: Failed to generate configuration links!")
        else:
            bot.answer_callback_query(call.id, "Error: Plan not found!")
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
        save_all_plans()
        admin_list_links(call)
    bot.answer_callback_query(call.id, "Deleted.")

print("Deleting webhook (in case of conflicts)...")
bot.delete_webhook()
print("Bot is running...")
bot.infinity_polling()

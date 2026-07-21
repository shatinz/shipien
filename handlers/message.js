/**
 * Telegram Serverless Handler: message.js
 * Processes text commands, starting flow, plan selection, and payment requests.
 */

import { CONFIG } from '../lib/config.js';
import { getDb, registerUser } from '../lib/db.js';

export default async function handleMessage(update, context) {
  const message = update.message || update.edited_message;
  if (!message) return;

  const chatId = message.chat.id;
  const user = message.from;
  const text = message.text || '';
  const db = await getDb(context);

  if (user) {
    await registerUser(db, user);
  }

  // Handle /start command
  if (text.startsWith('/start')) {
    const welcomeMsg = `🚀 **به ربات شیپین خوش آمدید!**\n\n` +
      `ارائه‌دهنده سرویس‌های باکیفیت و پرسرعت V2Ray / Hysteria.\n\n` +
      `📌 از منوی زیر می‌توانید سرویس مورد نظر خود را انتخاب و خریداری نمایید:`;

    const inlineKeyboard = {
      inline_keyboard: [
        [{ text: "🛍 خرید سرویس جدید", callback_data: "menu_buy" }],
        [{ text: "📋 سرویس‌های من", callback_data: "menu_my_services" }, { text: "💳 شارژ حساب", callback_data: "menu_recharge" }],
        [{ text: "📢 کانال اطلاع‌رسانی", url: `https://t.me/${CONFIG.CHANNEL_ID.replace('@', '')}` }, { text: "📞 پشتیبانی", callback_data: "menu_support" }]
      ]
    };

    await context.telegram.sendMessage(chatId, welcomeMsg, {
      parse_mode: 'Markdown',
      reply_markup: inlineKeyboard
    });
    return;
  }

  // Handle /help command
  if (text.startsWith('/help')) {
    const helpMsg = `ℹ️ **راهنمای استفاده از ربات شیپین:**\n\n` +
      `/start - شروع مجدد ربات و نمایش منوی اصلی\n` +
      `/buy - مشاهده پلن‌ها و خرید مستقیم\n` +
      `/status - وضعیت حساب کاربری\n` +
      `/help - دریافت راهنما`;

    await context.telegram.sendMessage(chatId, helpMsg, { parse_mode: 'Markdown' });
    return;
  }

  // Handle /buy command
  if (text.startsWith('/buy') || text.startsWith('/plans')) {
    const plansMsg = `⚡ **پلن‌های فعال شیپین:**\n\n` +
      CONFIG.DEFAULT_PLANS.map(p => `• **${p.title}**: ${p.price_toman.toLocaleString()} تومان`).join('\n') +
      `\n\nلطفاً پلن مورد نظر خود را برای شروع روند خرید انتخاب کنید:`;

    const planButtons = CONFIG.DEFAULT_PLANS.map(p => ([
      { text: `🛍 ${p.title} - ${p.price_toman.toLocaleString()} تومان`, callback_data: `buy_${p.id}` }
    ]));

    await context.telegram.sendMessage(chatId, plansMsg, {
      parse_mode: 'Markdown',
      reply_markup: { inline_keyboard: planButtons }
    });
    return;
  }

  // Handle Photo / Payment Receipt submission
  if (message.photo && message.photo.length > 0) {
    const photo = message.photo[message.photo.length - 1];
    const fileId = photo.file_id;

    // Send acknowledgement to user
    await context.telegram.sendMessage(chatId, "✅ رسید پرداخت شما دریافت شد و جهت بررسی برای مدیریت ارسال گردید.", { parse_mode: 'Markdown' });

    // Notify admin
    const adminMsg = `📩 **رسید جدید دریافت شد!**\n\n👤 کاربر: [${user.first_name}](tg://user?id=${user.id}) (ID: \`${user.id}\`)\n` +
      `` + (user.username ? `@${user.username}` : 'بدون یوزرنیم') + `\n\nلطفاً رسید زیر را تایید یا رد کنید:`;

    const adminKeyboard = {
      inline_keyboard: [
        [
          { text: "✅ تایید پرداخت", callback_data: `admin_approve_${user.id}_${fileId}` },
          { text: "❌ رد پرداخت", callback_data: `admin_reject_${user.id}_${fileId}` }
        ]
      ]
    };

    await context.telegram.sendPhoto(CONFIG.ADMIN_ID, fileId, {
      caption: adminMsg,
      parse_mode: 'Markdown',
      reply_markup: adminKeyboard
    });
    return;
  }

  // Default fallback response
  await context.telegram.sendMessage(chatId, "جهت مشاهده گزینه‌ها دستور /start یا /buy را ارسال کنید.");
}

import { api, db } from 'sdk';
import { users, payments } from 'schema';
import { CONFIG } from '../lib/config.js';

export default async function (message, ctx) {
  const chatId = message.chat.id;
  const fromUser = message.from;
  const text = message.text || '';

  // Register or update user in Telegram Serverless SQLite database
  if (fromUser) {
    await db.insert(users)
      .values({
        id: fromUser.id,
        username: fromUser.username || '',
        firstName: fromUser.first_name || ''
      })
      .onConflictDoUpdate({
        target: users.id,
        set: {
          username: fromUser.username || '',
          firstName: fromUser.first_name || ''
        }
      })
      .run();
  }

  // Handle /start command
  if (text.startsWith('/start')) {
    const welcomeMsg = `🚀 **به ربات شیپین (@${CONFIG.BOT_USERNAME}) خوش آمدید!**\n\n` +
      `ارائه‌دهنده سرویس‌های باکیفیت و پرسرعت V2Ray / Hysteria (پسرگارد).\n\n` +
      `📌 از منوی زیر می‌توانید سرویس مورد نظر خود را انتخاب کنید:`;

    const inlineKeyboard = {
      inline_keyboard: [
        [{ text: "🛍 خرید سرویس جدید", callback_data: "menu_buy" }],
        [{ text: "📱 نرم‌افزارهای سازگار", callback_data: "menu_apps" }],
        [{ text: "📢 کانال اطلاع‌رسانی", url: `https://t.me/${CONFIG.CHANNEL_ID.replace('@', '')}` }]
      ]
    };

    await api.sendMessage({
      chat_id: chatId,
      text: welcomeMsg,
      parse_mode: 'Markdown',
      reply_markup: inlineKeyboard
    });
    return;
  }

  // Handle /apps command
  if (text.startsWith('/apps')) {
    const appsMsg = `📱 **نرم‌افزارهای سازگار با کانفیگ‌های جدید شیپین:**\n\n` +
      `🤖 **اندروید (Android):**\n• v2rayNG\n• Hiddify\n\n` +
      `🍎 **آیفون (iOS):**\n• FairVPN\n• Hiddify\n\n` +
      `💻 **ویندوز (Windows):**\n• v2rayNG\n• Hiddify\n• Netch\n\n` +
      `🍏 **مک (macOS):**\n• Clash Verge\n\n` +
      `🐧 **لینوکس (Linux):**\n• Clash Verge`;

    await api.sendMessage({
      chat_id: chatId,
      text: appsMsg,
      parse_mode: 'Markdown'
    });
    return;
  }

  // Handle /buy or /plans command
  if (text.startsWith('/buy') || text.startsWith('/plans')) {
    const plansMsg = `⚡ **پلن‌های فعال شیپین:**\n\n` +
      CONFIG.DEFAULT_PLANS.map(p => `• **${p.title}**: ${p.price_toman.toLocaleString()} تومان`).join('\n') +
      `\n\nلطفاً پلن مورد نظر خود را برای شروع روند خرید انتخاب کنید:`;

    const planButtons = CONFIG.DEFAULT_PLANS.map(p => ([
      { text: `🛍 ${p.title} - ${p.price_toman.toLocaleString()} تومان`, callback_data: `buy_${p.id}` }
    ]));

    await api.sendMessage({
      chat_id: chatId,
      text: plansMsg,
      parse_mode: 'Markdown',
      reply_markup: { inline_keyboard: planButtons }
    });
    return;
  }

  // Handle photo / payment receipt submission
  if (message.photo && message.photo.length > 0) {
    const photo = message.photo[message.photo.length - 1];
    const fileId = photo.file_id;

    // Save payment receipt to database
    await db.insert(payments)
      .values({
        userId: fromUser.id,
        fileId: fileId,
        status: 'pending'
      })
      .run();

    await api.sendMessage({
      chat_id: chatId,
      text: "✅ رسید پرداخت شما دریافت شد و جهت بررسی برای مدیریت ارسال گردید.",
      parse_mode: 'Markdown'
    });

    // Send receipt to Admin
    const adminMsg = `📩 **رسید جدید دریافت شد!**\n\n👤 کاربر: [${fromUser.first_name}](tg://user?id=${fromUser.id}) (ID: \`${fromUser.id}\`)\n` +
      (fromUser.username ? `@${fromUser.username}` : 'بدون یوزرنیم') + `\n\nلطفاً رسید زیر را تایید یا رد کنید:`;

    const adminKeyboard = {
      inline_keyboard: [
        [
          { text: "✅ تایید پرداخت", callback_data: `admin_approve_${fromUser.id}_${fileId}` },
          { text: "❌ رد پرداخت", callback_data: `admin_reject_${fromUser.id}_${fileId}` }
        ]
      ]
    };

    await api.sendPhoto({
      chat_id: CONFIG.ADMIN_ID,
      photo: fileId,
      caption: adminMsg,
      parse_mode: 'Markdown',
      reply_markup: adminKeyboard
    });
    return;
  }

  // Default fallback response
  await api.sendMessage({
    chat_id: chatId,
    text: "جهت مشاهده گزینه‌ها دستور /start را ارسال کنید."
  });
}

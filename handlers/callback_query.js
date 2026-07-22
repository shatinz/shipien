import { api } from 'sdk';
import { CONFIG } from '../lib/config.js';

export default async function (callbackQuery, ctx) {
  const data = callbackQuery.data || '';
  const chatId = callbackQuery.message?.chat.id;
  const messageId = callbackQuery.message?.message_id;

  await api.answerCallbackQuery({ callback_query_id: callbackQuery.id });

  if (data === "menu_buy") {
    const plansMsg = `⚡ **انتخاب پلن اشتراک:**\n\nلطفاً یکی از سرویس‌های زیر را انتخاب کنید:`;
    const planButtons = CONFIG.DEFAULT_PLANS.map(p => ([
      { text: `🛍 ${p.title} (${p.price_toman.toLocaleString()} تومان)`, callback_data: `buy_${p.id}` }
    ]));
    planButtons.push([{ text: "🔙 بازگشت به منوی اصلی", callback_data: "menu_main" }]);

    await api.editMessageText({
      chat_id: chatId,
      message_id: messageId,
      text: plansMsg,
      parse_mode: 'Markdown',
      reply_markup: { inline_keyboard: planButtons }
    });
    return;
  }

  if (data === "menu_main") {
    const welcomeMsg = `🚀 **منوی اصلی شیپین (@${CONFIG.BOT_USERNAME}):**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب نمایید:`;
    const inlineKeyboard = {
      inline_keyboard: [
        [{ text: "🛍 خرید سرویس جدید", callback_data: "menu_buy" }],
        [{ text: "📱 نرم‌افزارهای سازگار", callback_data: "menu_apps" }],
        [{ text: "📢 کانال اطلاع‌رسانی", url: `https://t.me/${CONFIG.CHANNEL_ID.replace('@', '')}` }]
      ]
    };

    await api.editMessageText({
      chat_id: chatId,
      message_id: messageId,
      text: welcomeMsg,
      parse_mode: 'Markdown',
      reply_markup: inlineKeyboard
    });
    return;
  }

  if (data === "menu_apps") {
    const appsMsg = `📱 **نرم‌افزارهای سازگار با کانفیگ‌های جدید شیپین:**\n\n` +
      `🤖 **اندروید (Android):**\n• v2rayNG\n• Hiddify\n\n` +
      `🍎 **آیفون (iOS):**\n• FairVPN\n• Hiddify\n\n` +
      `💻 **ویندوز (Windows):**\n• v2rayNG\n• Hiddify\n• Netch\n\n` +
      `🍏 **مک (macOS):**\n• Clash Verge\n\n` +
      `🐧 **لینوکس (Linux):**\n• Clash Verge`;

    await api.editMessageText({
      chat_id: chatId,
      message_id: messageId,
      text: appsMsg,
      parse_mode: 'Markdown',
      reply_markup: {
        inline_keyboard: [
          [{ text: "🔙 بازگشت به منوی اصلی", callback_data: "menu_main" }]
        ]
      }
    });
    return;
  }

  if (data.startsWith("buy_")) {
    const planId = data.replace("buy_", "");
    const plan = CONFIG.DEFAULT_PLANS.find(p => p.id === planId);
    if (!plan) return;

    const payMsg = `💳 **پرداخت پلن ${plan.title}**\n\n` +
      `مبلغ: **${plan.price_toman.toLocaleString()} تومان**\n\n` +
      `لطفاً مبلغ فوق را به شماره کارت زیر واریز نموده و تصویر فیش را ارسال نمایید:\n\n` +
      `💳 **شماره کارت:**\n\`${CONFIG.CARD_NUMBER}\`\n\n` +
      `💎 **پرداخت TON:**\nآدرس: \`${CONFIG.TON_ADDRESS}\`\nکامنت: \`${CONFIG.TON_COMMENT}\`\n\n` +
      `پس از واریز، عکس فیش را همینجا ارسال نمایید.`;

    await api.sendMessage({
      chat_id: chatId,
      text: payMsg,
      parse_mode: 'Markdown',
      reply_markup: {
        inline_keyboard: [
          [{ text: "🔙 انصراف و بازگشت", callback_data: "menu_buy" }]
        ]
      }
    });
    return;
  }

  if (data.startsWith("admin_approve_")) {
    const parts = data.split("_");
    const targetUserId = parts[2];

    await api.sendMessage({
      chat_id: targetUserId,
      text: "🎉 **پرداخت شما تایید شد!**\n\nسرویس شما به زودی آماده و ارسال خواهد شد.",
      parse_mode: 'Markdown'
    });
    await api.editMessageCaption({
      chat_id: chatId,
      message_id: messageId,
      caption: "✅ **تایید شد.**",
      reply_markup: { inline_keyboard: [] }
    });
    return;
  }

  if (data.startsWith("admin_reject_")) {
    const parts = data.split("_");
    const targetUserId = parts[2];

    await api.sendMessage({
      chat_id: targetUserId,
      text: "❌ **پرداخت شما تایید نشد.**\n\nلطفاً در صورت وجود مشکل با پشتیبانی تماس بگیرید.",
      parse_mode: 'Markdown'
    });
    await api.editMessageCaption({
      chat_id: chatId,
      message_id: messageId,
      caption: "❌ **رد شد.**",
      reply_markup: { inline_keyboard: [] }
    });
    return;
  }
}

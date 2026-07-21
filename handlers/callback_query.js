/**
 * Telegram Serverless Handler: callback_query.js
 * Processes inline button interactions, plan choices, payments, and admin actions.
 */

import { CONFIG } from '../lib/config.js';
import { getDb } from '../lib/db.js';

export default async function handleCallbackQuery(update, context) {
  const query = update.callback_query;
  if (!query) return;

  const data = query.data || '';
  const chatId = query.message?.chat.id;
  const messageId = query.message?.message_id;
  const user = query.from;

  await context.telegram.answerCallbackQuery(query.id);

  // Main menu handlers
  if (data === "menu_buy") {
    const plansMsg = `⚡ **انتخاب پلن اشتراک:**\n\nلطفاً یکی از سرویس‌های زیر را انتخاب کنید:`;
    const planButtons = CONFIG.DEFAULT_PLANS.map(p => ([
      { text: `🛍 ${p.title} (${p.price_toman.toLocaleString()} تومان)`, callback_data: `buy_${p.id}` }
    ]));
    planButtons.push([{ text: "🔙 بازگشت به منوی اصلی", callback_data: "menu_main" }]);

    await context.telegram.editMessageText(chatId, messageId, plansMsg, {
      parse_mode: 'Markdown',
      reply_markup: { inline_keyboard: planButtons }
    });
    return;
  }

  if (data === "menu_main") {
    const welcomeMsg = `🚀 **منوی اصلی شیپین:**\n\nلطفاً یکی از گزینه‌های زیر را انتخاب نمایید:`;
    const inlineKeyboard = {
      inline_keyboard: [
        [{ text: "🛍 خرید سرویس جدید", callback_data: "menu_buy" }],
        [{ text: "📋 سرویس‌های من", callback_data: "menu_my_services" }, { text: "💳 شارژ حساب", callback_data: "menu_recharge" }],
        [{ text: "📢 کانال اطلاع‌رسانی", url: `https://t.me/${CONFIG.CHANNEL_ID.replace('@', '')}` }, { text: "📞 پشتیبانی", callback_data: "menu_support" }]
      ]
    };

    await context.telegram.editMessageText(chatId, messageId, welcomeMsg, {
      parse_mode: 'Markdown',
      reply_markup: inlineKeyboard
    });
    return;
  }

  // Buying a specific plan
  if (data.startsWith("buy_")) {
    const planId = data.replace("buy_", "");
    const plan = CONFIG.DEFAULT_PLANS.find(p => p.id === planId);
    if (!plan) return;

    const payMsg = `💳 **پرداخت پلن ${plan.title}**\n\n` +
      `مبلغ: **${plan.price_toman.toLocaleString()} تومان**\n\n` +
      `لطفاً مبلغ فوق را به شماره کارت زیر واریز نموده و تصویر فیش یا شماره پیگیری را ارسال نمایید:\n\n` +
      `💳 **شماره کارت:**\n\`${CONFIG.CARD_NUMBER}\`\n\n` +
      `💎 **پرداخت TON:**\nآدرس: \`${CONFIG.TON_ADDRESS}\`\nکامنت: \`${CONFIG.TON_COMMENT}\`\n\n` +
      `پس از واریز، عکس فیش را همینجا ارسال نمایید.`;

    await context.telegram.sendMessage(chatId, payMsg, {
      parse_mode: 'Markdown',
      reply_markup: {
        inline_keyboard: [
          [{ text: "🔙 انصراف و بازگشت", callback_data: "menu_buy" }]
        ]
      }
    });
    return;
  }

  // Admin approval flow
  if (data.startsWith("admin_approve_")) {
    const parts = data.split("_");
    const targetUserId = parts[2];

    await context.telegram.sendMessage(targetUserId, "🎉 **پرداخت شما تایید شد!**\n\nسرویس شما به زودی آماده و ارسال خواهد شد.", { parse_mode: 'Markdown' });
    await context.telegram.editMessageCaption(chatId, messageId, "✅ **تایید شد.**", { reply_markup: { inline_keyboard: [] } });
    return;
  }

  if (data.startsWith("admin_reject_")) {
    const parts = data.split("_");
    const targetUserId = parts[2];

    await context.telegram.sendMessage(targetUserId, "❌ **پرداخت شما تایید نشد.**\n\nلطفاً در صورت وجود مشکل با پشتیبانی تماس بگیرید.", { parse_mode: 'Markdown' });
    await context.telegram.editMessageCaption(chatId, messageId, "❌ **رد شد.**", { reply_markup: { inline_keyboard: [] } });
    return;
  }
}

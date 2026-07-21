const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN!;
const TELEGRAM_ADMIN_ID = process.env.TELEGRAM_ADMIN_ID!;
const TELEGRAM_API = `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}`;

export interface TelegramResult {
  ok: boolean;
  result?: { message_id: number };
}

export async function sendAdminMessage(text: string): Promise<TelegramResult> {
  const res = await fetch(`${TELEGRAM_API}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_ADMIN_ID,
      text,
      parse_mode: 'HTML',
    }),
  });
  return res.json();
}

export async function sendAdminPhoto(
  photoBase64: string,
  caption: string
): Promise<TelegramResult> {
  // Convert base64 to blob and send as form data
  const matches = photoBase64.match(/^data:([A-Za-z-+/]+);base64,(.+)$/);
  if (!matches) {
    return sendAdminMessage(caption);
  }

  const mimeType = matches[1];
  const base64Data = matches[2];
  const buffer = Buffer.from(base64Data, 'base64');
  const blob = new Blob([buffer], { type: mimeType });

  const formData = new FormData();
  formData.append('chat_id', TELEGRAM_ADMIN_ID);
  formData.append('photo', blob, 'receipt.jpg');
  formData.append('caption', caption);
  formData.append('parse_mode', 'HTML');

  const res = await fetch(`${TELEGRAM_API}/sendPhoto`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

export async function sendAdminReceiptWithButtons(
  subscriptionId: string,
  username: string,
  planName: string,
  receiptData: string,
  receiptType: string,
  configName?: string
): Promise<TelegramResult> {
  const caption = `📋 <b>New Payment Receipt</b>\n\n👤 User: <b>${username}</b>\n📦 Plan: <b>${planName}</b>\n🆔 Sub ID: <code>${subscriptionId}</code>\n📝 Desired Name: <b>${configName || 'Auto-generated'}</b>\n\n⏳ Waiting for your approval...`;

  const inlineKeyboard = {
    inline_keyboard: [
      [
        { text: '✅ Approve', callback_data: `admin_approve_web_${subscriptionId}` },
        { text: '❌ Reject', callback_data: `admin_reject_web_${subscriptionId}` },
      ],
    ],
  };

  if (receiptType === 'image') {
    const matches = receiptData.match(/^data:([A-Za-z-+/]+);base64,(.+)$/);
    if (matches) {
      const base64Data = matches[2];
      const buffer = Buffer.from(base64Data, 'base64');
      const blob = new Blob([buffer], { type: matches[1] });

      const formData = new FormData();
      formData.append('chat_id', TELEGRAM_ADMIN_ID);
      formData.append('photo', blob, 'receipt.jpg');
      formData.append('caption', caption);
      formData.append('parse_mode', 'HTML');
      formData.append('reply_markup', JSON.stringify(inlineKeyboard));

      const res = await fetch(`${TELEGRAM_API}/sendPhoto`, {
        method: 'POST',
        body: formData,
      });
      return res.json();
    }
  }

  // Text receipt or fallback
  const textMsg = caption + (receiptType === 'text' ? `\n\n📝 Receipt note: ${receiptData}` : '');
  const res = await fetch(`${TELEGRAM_API}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_ADMIN_ID,
      text: textMsg,
      parse_mode: 'HTML',
      reply_markup: inlineKeyboard,
    }),
  });
  return res.json();
}

export async function editMessageReplyMarkup(
  messageId: number,
  text: string
): Promise<void> {
  await fetch(`${TELEGRAM_API}/editMessageText`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: TELEGRAM_ADMIN_ID,
      message_id: messageId,
      text,
      parse_mode: 'HTML',
    }),
  });
}

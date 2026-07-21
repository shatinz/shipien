/**
 * ShipienBot Serverless Configuration
 */

export const CONFIG = {
  TOKEN: process.env.BOT_TOKEN || "7344235764:AAG4nXM1SOSnObMXKnjO6aJBDoQVAkMdP4k",
  ADMIN_ID: parseInt(process.env.ADMIN_ID || "8373593549", 10),
  CARD_NUMBER: "6037 9981 7457 8640",
  TON_ADDRESS: "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMg7",
  TON_COMMENT: "Deposit",
  USDT_ERC20_ADDRESS: "0x0000000000000000000000000000000000000000",
  CHANNEL_ID: "@shipien",
  DEFAULT_PLANS: [
    { id: "plan_1m_30g", title: "1 Month - 30 GB", volume_gb: 30, duration_days: 30, price_toman: 150000 },
    { id: "plan_1m_50g", title: "1 Month - 50 GB", volume_gb: 50, duration_days: 30, price_toman: 220000 },
    { id: "plan_3m_100g", title: "3 Months - 100 GB", volume_gb: 100, duration_days: 90, price_toman: 400000 }
  ]
};

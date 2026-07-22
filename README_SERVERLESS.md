# Telegram Serverless Deployment Guide for ShipienBot (@shipien_bot)

This guide explains how to deploy **ShipienBot** (`@shipien_bot`) directly onto Telegram's native **Serverless Platform** (`tgcloud`).

---

## 1. Prerequisites & BotFather Activation

1. Open Telegram and message **[@BotFather](https://t.me/BotFather)**.
2. Send command `/mybots` and select your bot (`@shipien_bot`).
3. Click on **Bot Settings** -> **Serverless**.
4. Click **Activate** to enable native serverless hosting for your bot.

---

## 2. Project Setup & Local Synchronization

Ensure you have **Node.js 18+** installed.

To verify your local project status against Telegram Cloud:
```bash
npx tgcloud status
```

---

## 3. Deploying Code & Database Schema

To push all handlers (`handlers/message.js`, `handlers/callback_query.js`), configs, and database schemas (`schema.js`) directly to Telegram's infrastructure:

```bash
npx tgcloud push
```

To run database migrations on Telegram Serverless SQLite:
```bash
npx tgcloud migrate
```

---

## 4. Architecture Summary

| Component | Telegram Serverless Implementation |
|---|---|
| **Bot Username** | `@shipien_bot` |
| **Hosting** | Native Telegram Infrastructure (V8 Isolated Sandbox) |
| **Management Panel** | PasarGuard (`https://vip-03.fl-sub.site:2096/dashboard`) |
| **CLI** | `tgcloud` / `npx tgcloud push` |
| **Database** | Built-in Telegram Serverless SQLite (`schema.js`) |
| **Handlers** | `handlers/message.js` & `handlers/callback_query.js` |
| **Config** | `tgcloud.config.json` & `lib/config.js` |

---

For further details, consult [Telegram Bot Serverless Documentation](https://core.telegram.org/bots/serverless).

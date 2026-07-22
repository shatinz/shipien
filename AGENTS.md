# Telegram Serverless AGENTS.md

This repository contains **ShipienBot** (`@shipien_bot`), configured to run on Telegram's native **Telegram Serverless Platform** (`tgcloud`).

## Architecture & Infrastructure

- **Bot Username:** `@shipien_bot`
- **Platform:** Native Telegram Serverless (`tgcloud` CLI / `@tgcloud/bot`).
- **Runtime:** Isolated V8 engine hosted directly on Telegram's infrastructure.
- **Database:** Built-in SQLite managed via `schema.js`.
- **Config:** `tgcloud.config.json` defines handlers and entry points.
- **Management Panel:** PasarGuard (`https://vip-03.fl-sub.site:2096/dashboard`)

## Project Structure

- `schema.js`: Contains table definitions for `users`, `plans`, `orders`, and `payments`.
- `handlers/message.js`: Entry point for text messages, commands, and image/receipt submissions.
- `handlers/callback_query.js`: Entry point for inline keyboard interactions and app compatibility guides.
- `lib/config.js`: Central configuration file for Bot Tokens, Admin ID, PasarGuard Panel, payment details, and app compatibility.
- `lib/db.js`: Database abstraction layer for Telegram Serverless.

## Compatible Client Applications
- **Android:** v2rayNG, Hiddify
- **iOS:** FairVPN, Hiddify
- **Windows:** v2rayNG, Hiddify, Netch
- **macOS:** Clash Verge
- **Linux:** Clash Verge

## Deployment Commands

- `npx tgcloud push`: Deploy local code to Telegram Serverless Platform.
- `npx tgcloud status`: View deployment and sync status.
- `npx tgcloud migrate`: Apply database schema changes.
- `npx tgcloud run`: Test handlers locally against the serverless environment.


# Telegram Serverless AGENTS.md

This repository contains **ShipienBot**, configured to run on Telegram's native **Telegram Serverless Platform** (`tgcloud`).

## Architecture & Infrastructure

- **Platform:** Native Telegram Serverless (`tgcloud` CLI / `@tgcloud/bot`).
- **Runtime:** Isolated V8 engine hosted directly on Telegram's infrastructure.
- **Database:** Built-in SQLite managed via `schema.js`.
- **Config:** `tgcloud.config.json` defines handlers and entry points.

## Project Structure

- `schema.js`: Contains table definitions for `users`, `plans`, `orders`, and `payments`.
- `handlers/message.js`: Entry point for text messages and image/receipt submissions.
- `handlers/callback_query.js`: Entry point for inline keyboard interactions.
- `lib/config.js`: Central configuration file for Bot Tokens, Admin ID, payment details.
- `lib/db.js`: Database abstraction layer for Telegram Serverless.

## Deployment Commands

- `npx tgcloud push`: Deploy local code to Telegram Serverless Platform.
- `npx tgcloud status`: View deployment and sync status.
- `npx tgcloud migrate`: Apply database schema changes.
- `npx tgcloud run`: Test handlers locally against the serverless environment.

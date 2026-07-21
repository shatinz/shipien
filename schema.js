/**
 * Telegram Serverless Database Schema (schema.js)
 * Native SQLite schema definitions managed by Telegram Cloud
 */

export const tables = {
  users: `
    CREATE TABLE IF NOT EXISTS users (
      user_id INTEGER PRIMARY KEY,
      username TEXT,
      first_name TEXT,
      last_name TEXT,
      balance REAL DEFAULT 0.0,
      joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      is_admin INTEGER DEFAULT 0
    );
  `,
  plans: `
    CREATE TABLE IF NOT EXISTS plans (
      plan_id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      volume_gb REAL NOT NULL,
      duration_days INTEGER NOT NULL,
      price_toman REAL NOT NULL,
      is_active INTEGER DEFAULT 1
    );
  `,
  orders: `
    CREATE TABLE IF NOT EXISTS orders (
      order_id TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      plan_id TEXT NOT NULL,
      config_name TEXT,
      config_link TEXT,
      status TEXT DEFAULT 'pending',
      amount_toman REAL NOT NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY (user_id) REFERENCES users(user_id)
    );
  `,
  payments: `
    CREATE TABLE IF NOT EXISTS payments (
      payment_id TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      amount REAL NOT NULL,
      method TEXT NOT NULL, -- 'card', 'ton', 'usdt'
      ref_number TEXT,
      photo_file_id TEXT,
      status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
  `
};

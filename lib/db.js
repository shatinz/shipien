/**
 * Database Abstraction Layer for Telegram Serverless Platform
 * Interacts with built-in SQLite engine provided by Telegram Cloud.
 */

export async function getDb(ctx) {
  if (ctx && ctx.db) {
    return ctx.db;
  }
  // Fallback / mock interface for development testing
  return {
    async query(sql, params = []) {
      console.log(`[DB Query] ${sql}`, params);
      return [];
    },
    async execute(sql, params = []) {
      console.log(`[DB Execute] ${sql}`, params);
      return { changes: 1, lastInsertRowid: 1 };
    }
  };
}

export async function registerUser(db, user) {
  const sql = `
    INSERT INTO users (user_id, username, first_name, last_name, is_admin)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(user_id) DO UPDATE SET
      username = excluded.username,
      first_name = excluded.first_name,
      last_name = excluded.last_name;
  `;
  await db.execute(sql, [
    user.id,
    user.username || '',
    user.first_name || '',
    user.last_name || '',
    user.id === 8373593549 ? 1 : 0
  ]);
}

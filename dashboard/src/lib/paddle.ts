/**
 * Paddle subscription status per user. Only users with an active subscription can use all features.
 *
 * PAUSED: This feature is currently disabled. To re-enable later:
 * 1. Set PADDLE_BILLING_ENABLED = true in middleware.ts
 * 2. Configure Paddle env vars (see .env.example) and Paddle dashboard (webhook, client token, price)
 * 3. Ensure /api/webhooks/paddle and /pricing work as expected
 */

import Database from "better-sqlite3";
import path from "node:path";

const dbPath = path.join(process.cwd(), "connections.db");
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS paddle_subscriptions (
    user_id TEXT PRIMARY KEY,
    paddle_subscription_id TEXT NOT NULL,
    status TEXT NOT NULL,
    updated_at INTEGER NOT NULL
  );
`);

const ACTIVE_STATUSES = ["active", "trialing"];

export function isPayer(userId: string): boolean {
  const row = db
    .prepare(
      "SELECT status FROM paddle_subscriptions WHERE user_id = ? AND status IN (" +
        ACTIVE_STATUSES.map(() => "?").join(",") +
        ")"
    )
    .get(userId, ...ACTIVE_STATUSES) as { status: string } | undefined;
  return !!row;
}

export function setSubscription(
  userId: string,
  paddleSubscriptionId: string,
  status: string
): void {
  const now = Math.floor(Date.now() / 1000);
  db.prepare(
    `INSERT INTO paddle_subscriptions (user_id, paddle_subscription_id, status, updated_at)
     VALUES (?, ?, ?, ?)
     ON CONFLICT(user_id) DO UPDATE SET
       paddle_subscription_id = excluded.paddle_subscription_id,
       status = excluded.status,
       updated_at = excluded.updated_at`
  ).run(userId, paddleSubscriptionId, status, now);
}

export function revokeSubscription(userId: string): void {
  db.prepare("DELETE FROM paddle_subscriptions WHERE user_id = ?").run(userId);
}

export function revokeByPaddleSubscriptionId(paddleSubscriptionId: string): void {
  db.prepare(
    "DELETE FROM paddle_subscriptions WHERE paddle_subscription_id = ?"
  ).run(paddleSubscriptionId);
}

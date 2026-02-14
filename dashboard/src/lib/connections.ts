/**
 * Store connections per user (Shopify / WooCommerce).
 * SQLite DB for persistence.
 */

import Database from "better-sqlite3";
import path from "node:path";

const dbPath = path.join(process.cwd(), "connections.db");
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS store_connections (
    user_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,
    shop_domain TEXT,
    access_token TEXT,
    wc_site_url TEXT,
    wc_consumer_key TEXT,
    wc_consumer_secret TEXT,
    created_at INTEGER NOT NULL
  );
  CREATE TABLE IF NOT EXISTS oauth_state (
    state TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at INTEGER NOT NULL
  );
`);

export type StoreConnection =
  | {
      platform: "shopify";
      shop_domain: string;
      access_token: string;
      created_at: number;
    }
  | {
      platform: "woocommerce";
      wc_site_url: string;
      wc_consumer_key: string;
      wc_consumer_secret: string;
      created_at: number;
    };

export function getConnection(userId: string): StoreConnection | null {
  const row = db
    .prepare(
      "SELECT platform, shop_domain, access_token, wc_site_url, wc_consumer_key, wc_consumer_secret, created_at FROM store_connections WHERE user_id = ?"
    )
    .get(userId) as
    | {
      platform: string;
      shop_domain: string | null;
      access_token: string | null;
      wc_site_url: string | null;
      wc_consumer_key: string | null;
      wc_consumer_secret: string | null;
      created_at: number;
    }
    | undefined;
  if (!row) return null;
  if (row.platform === "shopify" && row.shop_domain && row.access_token) {
    return {
      platform: "shopify",
      shop_domain: row.shop_domain,
      access_token: row.access_token,
      created_at: row.created_at,
    };
  }
  if (
    row.platform === "woocommerce" &&
    row.wc_site_url &&
    row.wc_consumer_key &&
    row.wc_consumer_secret
  ) {
    return {
      platform: "woocommerce",
      wc_site_url: row.wc_site_url,
      wc_consumer_key: row.wc_consumer_key,
      wc_consumer_secret: row.wc_consumer_secret,
      created_at: row.created_at,
    };
  }
  return null;
}

export function setShopifyConnection(
  userId: string,
  shopDomain: string,
  accessToken: string
): void {
  const now = Math.floor(Date.now() / 1000);
  db.prepare(
    `INSERT INTO store_connections (user_id, platform, shop_domain, access_token, created_at)
     VALUES (?, 'shopify', ?, ?, ?)
     ON CONFLICT(user_id) DO UPDATE SET
       platform = 'shopify',
       shop_domain = excluded.shop_domain,
       access_token = excluded.access_token,
       wc_site_url = NULL, wc_consumer_key = NULL, wc_consumer_secret = NULL,
       created_at = excluded.created_at`
  ).run(userId, shopDomain, accessToken, now);
}

export function setWooCommerceConnection(
  userId: string,
  siteUrl: string,
  consumerKey: string,
  consumerSecret: string
): void {
  const now = Math.floor(Date.now() / 1000);
  db.prepare(
    `INSERT INTO store_connections (user_id, platform, wc_site_url, wc_consumer_key, wc_consumer_secret, created_at)
     VALUES (?, 'woocommerce', ?, ?, ?, ?)
     ON CONFLICT(user_id) DO UPDATE SET
       platform = 'woocommerce',
       shop_domain = NULL, access_token = NULL,
       wc_site_url = excluded.wc_site_url,
       wc_consumer_key = excluded.wc_consumer_key,
       wc_consumer_secret = excluded.wc_consumer_secret,
       created_at = excluded.created_at`
  ).run(userId, siteUrl, consumerKey, consumerSecret, now);
}

// OAuth state for Shopify (state -> userId)
export function setOAuthState(state: string, userId: string): void {
  const now = Math.floor(Date.now() / 1000);
  db.prepare(
    "INSERT OR REPLACE INTO oauth_state (state, user_id, created_at) VALUES (?, ?, ?)"
  ).run(state, userId, now);
}

export function consumeOAuthState(state: string): string | null {
  const row = db
    .prepare("SELECT user_id FROM oauth_state WHERE state = ?")
    .get(state) as { user_id: string } | undefined;
  if (!row) return null;
  db.prepare("DELETE FROM oauth_state WHERE state = ?").run(state);
  return row.user_id;
}

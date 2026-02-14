/**
 * Optional Redis client for Better Auth session storage.
 * When REDIS_URL is set, sessions are stored in Redis so they persist
 * across server restarts and returning users stay logged in.
 */

import { createClient, type RedisClientType } from "redis";

let client: RedisClientType | null = null;
let connectPromise: Promise<void> | null = null;

const PREFIX = "reorder-auth:";

function getClient(): RedisClientType | null {
  const url = process.env.REDIS_URL;
  if (!url) return null;
  if (!client) {
    client = createClient({ url });
    client.on("error", (err) => console.error("[Redis]", err.message));
    connectPromise = client.connect();
  }
  return client;
}

async function ensureConnected(): Promise<RedisClientType | null> {
  const c = getClient();
  if (!c) return null;
  if (connectPromise) await connectPromise;
  return c;
}

export async function redisGet(key: string): Promise<string | null> {
  const c = await ensureConnected();
  if (!c) return null;
  return c.get(PREFIX + key);
}

export async function redisSet(key: string, value: string, ttlSeconds?: number): Promise<void> {
  const c = await ensureConnected();
  if (!c) return;
  if (ttlSeconds != null && ttlSeconds > 0) {
    await c.set(PREFIX + key, value, { EX: ttlSeconds });
  } else {
    await c.set(PREFIX + key, value);
  }
}

export async function redisDelete(key: string): Promise<void> {
  const c = await ensureConnected();
  if (!c) return;
  await c.del(PREFIX + key);
}

export function isRedisConfigured(): boolean {
  return Boolean(process.env.REDIS_URL);
}

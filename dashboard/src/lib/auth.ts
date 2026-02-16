import { betterAuth } from "better-auth";
import Database from "better-sqlite3";
import path from "node:path";
import { redisGet, redisSet, redisDelete, isRedisConfigured } from "./redis";

const dbPath = path.join(process.cwd(), "auth.db");

const THIRTY_DAYS = 30 * 24 * 60 * 60; // seconds

export const auth = betterAuth({
  database: new Database(dbPath),
  secret: process.env.BETTER_AUTH_SECRET,
  baseURL: process.env.BETTER_AUTH_URL ?? "http://localhost:4321",
  emailAndPassword: {
    enabled: true,
  },
  trustedOrigins: [
    "http://localhost:4321",
    "http://127.0.0.1:4321",
    process.env.BETTER_AUTH_URL ?? "",
  ].filter(Boolean),
  // Longer session + cookie cache so returning users stay logged in
  session: {
    expiresIn: THIRTY_DAYS,
    updateAge: 24 * 60 * 60, // refresh expiry every 1 day when used
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24, // 1 day cache in cookie; then revalidate from DB/Redis
    },
    // When using Redis, still store in DB so session ID is available (Better Auth requirement)
    ...(isRedisConfigured() && { storeSessionInDatabase: true }),
  },
  // Optional: Redis for session storage so sessions survive restarts and users stay logged in
  ...(isRedisConfigured() && {
    secondaryStorage: {
      get: redisGet,
      set: redisSet,
      delete: redisDelete,
    },
  }),
});

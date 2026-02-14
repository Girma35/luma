/**
 * Paddle webhook: subscription.created/activated → set payer; canceled/past_due/updated → revoke.
 * PAUSED: Billing is disabled (PADDLE_BILLING_ENABLED = false in middleware). Re-enable when ready.
 */

import type { APIRoute } from "astro";
import { createHmac, timingSafeEqual } from "crypto";
import {
  setSubscription,
  revokeSubscription,
  revokeByPaddleSubscriptionId,
} from "../../../lib/paddle";

export const prerender = false;

const FIVE_SECONDS = 5;

function verifySignature(
  rawBody: string,
  signatureHeader: string | null,
  secret: string
): boolean {
  if (!signatureHeader || !secret) return false;
  const parts: Record<string, string> = {};
  for (const part of signatureHeader.split(";")) {
    const [k, v] = part.split("=");
    if (k && v) parts[k.trim()] = v.trim();
  }
  const ts = parts.ts;
  const h1 = parts.h1;
  if (!ts || !h1) return false;
  const timestamp = parseInt(ts, 10);
  if (Number.isNaN(timestamp)) return false;
  if (Math.abs(Date.now() / 1000 - timestamp) > FIVE_SECONDS) return false;
  const signedPayload = `${ts}:${rawBody}`;
  const expected = createHmac("sha256", secret)
    .update(signedPayload)
    .digest("hex");
  try {
    return timingSafeEqual(Buffer.from(h1, "hex"), Buffer.from(expected, "hex"));
  } catch {
    return false;
  }
}

export const POST: APIRoute = async ({ request }) => {
  const secret = process.env.PADDLE_WEBHOOK_SECRET;
  if (!secret) {
    return new Response(JSON.stringify({ error: "Webhook not configured" }), {
      status: 500,
      headers: { "Content-Type": "application/json" },
    });
  }

  let rawBody: string;
  try {
    rawBody = await request.text();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid body" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const signature = request.headers.get("paddle-signature");
  if (!verifySignature(rawBody, signature, secret)) {
    return new Response(JSON.stringify({ error: "Invalid signature" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  let payload: {
    event_type?: string;
    data?: {
      id?: string;
      status?: string;
      custom_data?: { user_id?: string };
    };
  };
  try {
    payload = JSON.parse(rawBody);
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const eventType = payload.event_type;
  const data = payload.data;

  if (eventType === "subscription.created" || eventType === "subscription.activated") {
    const userId = data?.custom_data?.user_id;
    const subId = data?.id;
    const status = data?.status ?? "active";
    if (userId && subId) {
      setSubscription(userId, subId, status);
    }
  } else if (
    eventType === "subscription.canceled" ||
    eventType === "subscription.past_due"
  ) {
    const userId = data?.custom_data?.user_id;
    const subId = data?.id;
    if (userId) revokeSubscription(userId);
    else if (subId) revokeByPaddleSubscriptionId(subId);
  } else if (eventType === "subscription.updated") {
    const status = data?.status;
    if (status === "canceled" || status === "past_due") {
      const userId = data?.custom_data?.user_id;
      const subId = data?.id;
      if (userId) revokeSubscription(userId);
      else if (subId) revokeByPaddleSubscriptionId(subId);
    }
  }

  return new Response(JSON.stringify({ received: true }), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
};

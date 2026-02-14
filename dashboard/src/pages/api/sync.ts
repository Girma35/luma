import type { APIRoute } from "astro";
import { auth } from "../../lib/auth";
import { getConnection } from "../../lib/connections";

export const prerender = false;

const API_BASE =
  (typeof process !== "undefined" && process.env.PUBLIC_API_URL) ||
  "http://localhost:8000";

export const POST: APIRoute = async ({ request }) => {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session?.user) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  const connection = getConnection(session.user.id);
  if (!connection) {
    return new Response(
      JSON.stringify({ error: "No store connected. Connect your store first." }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  let body: { platform?: string; full_sync?: boolean };
  try {
    body = await request.json();
  } catch {
    body = {};
  }
  const platform = body.platform ?? connection.platform;
  const full_sync = body.full_sync ?? false;

  const payload =
    connection.platform === "shopify"
      ? {
          platform: "shopify",
          full_sync,
          shop_domain: connection.shop_domain,
          access_token: connection.access_token,
        }
      : {
          platform: "woocommerce",
          full_sync,
          wc_site_url: connection.wc_site_url,
          wc_consumer_key: connection.wc_consumer_key,
          wc_consumer_secret: connection.wc_consumer_secret,
        };

  try {
    const res = await fetch(`${API_BASE}/sync/with-credentials`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json().catch(() => ({}));
    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { "Content-Type": "application/json" },
    });
  } catch (e) {
    return new Response(
      JSON.stringify({
        error: "Sync service unavailable. Is the API running?",
      }),
      { status: 502, headers: { "Content-Type": "application/json" } }
    );
  }
};

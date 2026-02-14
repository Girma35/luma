import type { APIRoute } from "astro";
import { auth } from "../../../lib/auth";
import { setWooCommerceConnection } from "../../../lib/connections";

export const prerender = false;

export const POST: APIRoute = async ({ request }) => {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session?.user) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: { "Content-Type": "application/json" },
    });
  }

  let body: { siteUrl?: string; consumerKey?: string; consumerSecret?: string };
  try {
    body = await request.json();
  } catch {
    return new Response(JSON.stringify({ error: "Invalid JSON" }), {
      status: 400,
      headers: { "Content-Type": "application/json" },
    });
  }

  const siteUrl = body.siteUrl?.trim()?.replace(/\/$/, "");
  const consumerKey = body.consumerKey?.trim();
  const consumerSecret = body.consumerSecret?.trim();

  if (!siteUrl || !consumerKey || !consumerSecret) {
    return new Response(
      JSON.stringify({ error: "Missing siteUrl, consumerKey, or consumerSecret" }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  const apiUrl = `${siteUrl}/wp-json/wc/v3/system_status`;
  const authHeader =
    "Basic " +
    Buffer.from(`${consumerKey}:${consumerSecret}`).toString("base64");

  try {
    const res = await fetch(apiUrl, {
      headers: { Authorization: authHeader },
    });
    if (!res.ok) {
      const text = await res.text();
      return new Response(
        JSON.stringify({
          error: "WooCommerce connection failed. Check URL and API keys.",
          detail: res.status,
        }),
        { status: 400, headers: { "Content-Type": "application/json" } }
      );
    }
  } catch (e) {
    return new Response(
      JSON.stringify({
        error: "Could not reach store. Check the store URL and try again.",
      }),
      { status: 400, headers: { "Content-Type": "application/json" } }
    );
  }

  setWooCommerceConnection(
    session.user.id,
    siteUrl,
    consumerKey,
    consumerSecret
  );

  return new Response(
    JSON.stringify({ success: true, redirect: "/" }),
    { status: 200, headers: { "Content-Type": "application/json" } }
  );
};

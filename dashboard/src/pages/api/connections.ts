import type { APIRoute } from "astro";
import { auth } from "../../lib/auth";
import { getConnection } from "../../lib/connections";

export const prerender = false;

export const GET: APIRoute = async ({ request }) => {
  const session = await auth.api.getSession({ headers: request.headers });
  if (!session?.user) {
    return new Response(JSON.stringify({ connection: null }), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  }
  const connection = getConnection(session.user.id);
  return new Response(
    JSON.stringify({
      connection: connection
        ? {
            platform: connection.platform,
            ...(connection.platform === "shopify"
              ? { shop_domain: connection.shop_domain }
              : {
                  wc_site_url: connection.wc_site_url,
                }),
          }
        : null,
    }),
    {
      status: 200,
      headers: { "Content-Type": "application/json" },
    }
  );
};

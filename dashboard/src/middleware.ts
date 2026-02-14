import { auth } from "./lib/auth";
import { getConnection } from "./lib/connections";
import { isPayer } from "./lib/paddle";
import { defineMiddleware } from "astro:middleware";

/** PAUSED: Set to true to require Paddle subscription for full access (see src/lib/paddle.ts and README). */
const PADDLE_BILLING_ENABLED = false;

const PUBLIC_PATHS = ["/", "/login", "/signup", "/api/auth"];
const CONNECT_PATHS = ["/connect", "/api/connect", "/api/connections"];
const PAYWALL_ALLOWED = ["/pricing", "/api/webhooks/paddle"];
const REDIRECT_TO = "/login";

function isPublic(pathname: string): boolean {
  return PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

function isConnectPath(pathname: string): boolean {
  return CONNECT_PATHS.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

function isPaywallAllowed(pathname: string): boolean {
  return PAYWALL_ALLOWED.some((p) => pathname === p || pathname.startsWith(p + "/"));
}

export const onRequest = defineMiddleware(async (context, next) => {
  const { pathname } = context.url;

  const session = await auth.api.getSession({
    headers: context.request.headers,
  });

  if (session) {
    context.locals.user = session.user;
    context.locals.session = session.session;
    // When Paddle billing is disabled, treat everyone as payer so all features stay accessible
    context.locals.isPayer = PADDLE_BILLING_ENABLED ? isPayer(session.user.id) : true;
    if (pathname === "/") return context.redirect("/dashboard");
    if (pathname === "/login" || pathname === "/signup") {
      return context.redirect("/dashboard");
    }
    if (!isConnectPath(pathname)) {
      const connection = getConnection(session.user.id);
      if (!connection) {
        return context.redirect("/connect");
      }
    }
    if (PADDLE_BILLING_ENABLED && !context.locals.isPayer && !isPaywallAllowed(pathname)) {
      return context.redirect("/pricing");
    }
    return next();
  }

  context.locals.user = null;
  context.locals.session = null;
  context.locals.isPayer = false;
  if (isPublic(pathname)) {
    return next();
  }
  return context.redirect(REDIRECT_TO);
});

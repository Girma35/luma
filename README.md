# ReOrder AI

Supply chain forecasting and inventory optimization for Shopify and WooCommerce. The dashboard answers: **What is about to run out?** **How much should I buy?** **What is burning my cash?**

## Quick Start

**1. Backend (API)**

```bash
# Optional: copy env and set CORS if needed
cp .env.example .env

# Run API (serves at http://localhost:8000, demo data included)
uvicorn src.api.main:app --reload --port 8000
```

**2. Dashboard**

```bash
cd dashboard
npm install
npm run dev
```

Open **http://localhost:4321**. The dashboard uses the API at `http://localhost:8000` by default. To point elsewhere, set `PUBLIC_API_URL` in `dashboard/.env` (see `dashboard/.env.example`).

**3. Authentication (Better Auth)**

The dashboard is protected by [Better Auth](https://www.better-auth.com/) (free, open-source). Email/password sign-up and sign-in are enabled.

```bash
cd dashboard
cp .env.example .env
# Edit .env and set BETTER_AUTH_SECRET (min 32 chars). Generate with: openssl rand -base64 32
npx @better-auth/cli migrate   # create auth tables (SQLite auth.db)
npm run dev
```

Then open **http://localhost:4321** — you’ll be redirected to **/login**. Sign up at **/signup**, then sign in.

**4. User journey — Connect your store**

After login you’re sent to **Connect your store**:

1. **Enter store platform** — Choose **Shopify** or **WooCommerce**.
2. **Click connect**  
   - **Shopify:** Enter your store domain (e.g. `mystore.myshopify.com`), then **Connect Shopify**. You’re redirected to Shopify to approve the app (set `SHOPIFY_CLIENT_ID` and `SHOPIFY_CLIENT_SECRET` from your Shopify app).  
   - **WooCommerce:** Enter store URL and REST API consumer key + secret (from WooCommerce → Settings → Advanced → REST API).
3. **Approve access** — Shopify: approve in the Shopify screen. WooCommerce: we validate the keys and save.
4. **Dashboard** — After a store is connected you can use the dashboard, Inventory, Orders, Analytics, etc.

Sessions last 30 days and are cached in cookies so **returning users stay logged in** without signing in again. Optional: set `REDIS_URL=redis://localhost:6379` in `dashboard/.env` to store sessions in Redis (persists across server restarts).

**5. Paddle billing (paused — code in place for future use)**

Paddle-only billing is currently **disabled**: all logged-in users with a connected store have full access. The implementation is left in place so it can be re-enabled later.

- **To re-enable:** set `PADDLE_BILLING_ENABLED = true` in `dashboard/src/middleware.ts`, then configure Paddle (see `dashboard/.env.example` and comments in `dashboard/src/lib/paddle.ts`).
- **What’s in place:** `dashboard/src/lib/paddle.ts` (payer status), `dashboard/src/pages/api/webhooks/paddle.ts` (webhook), `dashboard/src/pages/pricing.astro` (checkout), middleware paywall when enabled.
- **Paddle setup when enabling:** client-side token, price ID, notification destination `{BETTER_AUTH_URL}/api/webhooks/paddle` for `subscription.created`, `subscription.activated`, `subscription.updated`, `subscription.canceled`, `subscription.past_due`; checkout uses `custom_data.user_id` to link subscriptions to users.

**Docker (API only)**

```bash
cp .env.example .env
docker compose up --build
# API at http://localhost:8000; run the dashboard locally with npm as above.
```

- **API docs:** http://localhost:8000/docs  
- **Health:** http://localhost:8000/health  

## Data normalization pipeline

The backend includes a **Step 4 — Data normalization pipeline** that turns raw store data into clean time-series:

1. **Timezone normalization** — order timestamps to UTC, `series_date` for grouping.
2. **Currency normalization** — all amounts to base currency (per-store config).
3. **SKU deduplication** — raw SKU → canonical SKU via `sku_mappings` table.
4. **Variant rollups** — aggregate to daily (store, SKU, category) with quantity and revenue.
5. **Refund adjustments** — subtract refunds from order revenue before rollup.
6. **Outlier detection** — IQR-based cap or flag of extreme values.
7. **Missing data interpolation** — fill gaps with zero (or linear) for continuous series.

**Output:** `normalized_series` table — clean time-series per SKU / category / store.

- **DB:** SQLAlchemy models in `src/db/` (pipeline_store_config, raw_orders, raw_refunds, raw_products, sku_mappings, normalized_series).
- **Pipeline:** `src/pipeline/` — stages in `stages/`, orchestrator in `runner.py`.
- **API:** `POST /pipeline/{store_id}/run`, `GET /pipeline/{store_id}/series`, `POST /pipeline/ingest/orders`, `POST /pipeline/store-config`.

Set store config (timezone, base currency) via `POST /pipeline/store-config`, ingest raw orders via `POST /pipeline/ingest/orders`, then `POST /pipeline/{store_id}/run`. Query clean series with `GET /pipeline/{store_id}/series`.

## Project Structure

- `src/api/`: FastAPI backend for data ingestion and AI orchestration.
- `src/core/`: In-memory store (seed data), config, and forecasting hooks.
- `src/db/`: SQLAlchemy models and session for pipeline DB.
- `src/pipeline/`: Data normalization pipeline (stages + runner).
- `src/integrations/`: Shopify and WooCommerce API clients.
- `dashboard/`: Astro frontend (Dashboard, Inventory, Orders, Analytics, Simulator, Suppliers, SKU detail).

---

## Phase 1: The Technical Blueprint

We are building a data pipeline that looks like this:

* **Data Ingestion:** Use the **Shopify Admin API (GraphQL)** and **WooCommerce REST API** to pull three specific things:
  1. **Historical Sales:** At least 12–24 months of SKU-level data to catch seasonality.
  2. **Current Inventory:** Real-time stock levels across all locations.
  3. **Product Metadata:** Categories, tags, and supplier lead times.

* **The "Brain" (The AI):** Leveraging **Amazon Forecast** or **Google Vertex AI**. We feed in CSV/JSON data, and they provide predicted sales for the next 30/60/90 days.

* **The Dashboard:** Built with **Astro**. It provides incredible performance and handles "Islands of Interactivity" perfectly for complex data visualizations.

---

## Phase 2: The "ReOrder" Feature Set

The dashboard answers three questions instantly:

1. **"What is about to run out?"** (The Reorder Point).
2. **"How much should I buy?"** (The Economic Order Quantity).
3. **"What is burning my cash?"** (The Dead Stock Alert—items that haven't sold in 60+ days).



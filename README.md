# ReOrder AI

Supply chain forecasting and inventory optimization for Shopify and WooCommerce. The dashboard shows KPIs, risk alerts, reorder suggestions, and SKU-level detail—powered by a FastAPI backend with optional live integrations.

---

## Quick start

**1. Backend (API)**

```bash
# From repo root
cp .env.example .env   # optional: edit for Shopify/WooCommerce
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

API: **http://localhost:8000** — Docs: http://localhost:8000/docs

**2. Dashboard**

```bash
cd dashboard
npm install
npm run dev
```

Dashboard: **http://localhost:4321**

The dashboard uses the API at `http://localhost:8000` by default. To point at another host, set `PUBLIC_API_URL` in `dashboard/.env` (e.g. `PUBLIC_API_URL=https://api.example.com`).

**3. Run both with Docker**

```bash
docker-compose up --build
```

API on port 8000; serve the dashboard separately or build and host the `dashboard` static build elsewhere.

---

## Project Structure

- `src/api/`: FastAPI backend for data ingestion and AI orchestration.
- `src/core/`: Forecasting logic and integration with Amazon Forecast/Vertex AI.
- `src/integrations/`: Shopify and WooCommerce API clients.
- `dashboard/`: Astro frontend (The 2026 standard for high-performance SaaS).

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



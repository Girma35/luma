# ReOrder AI

That is a fantastic choice. **ReOrder AI** is a "pain-killer" product because it directly impacts a business owner's bank account. In 2026, the gap between "data" and "decision" is where the most money is made.

To get this off the ground, we focus on the **"Minimum Viable Data"**—getting the right info out of Shopify and WooCommerce so our AI can actually make a prediction.

## Project Structure (Target)

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



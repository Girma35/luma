/**
 * ReOrder AI — API client for the FastAPI backend.
 * Uses PUBLIC_API_URL in .env or defaults to http://localhost:8000.
 */

const API_BASE =
  typeof import.meta.env !== "undefined" && import.meta.env?.PUBLIC_API_URL
    ? (import.meta.env as { PUBLIC_API_URL?: string }).PUBLIC_API_URL
    : "http://localhost:8000";

export type KPI = { label: string; value: string; trend: string; status: string };
export type { KPI as DashboardKPI };
export type Alert = {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  sku?: string;
  created_at: string;
  resolved?: boolean;
};
export type ReorderSuggestion = {
  sku: string;
  product_name: string;
  current_stock: number;
  predicted_demand_30d: number;
  suggested_order_qty: number;
  estimated_cost: number;
  days_until_stockout: number;
};
export type RecommendedAction = {
  skus_count: number;
  total_value: string;
  message: string;
  items: ReorderSuggestion[];
};
export type DashboardResponse = {
  kpis: KPI[];
  alerts: Alert[];
  health_score: number;
  recommended_action: RecommendedAction | null;
  total_items: number;
  total_inventory_value: number;
};
export type TrendDataPoint = { label: string; actual: number; projected: number; category: string };
export type TrendsResponse = {
  period: string;
  data: TrendDataPoint[];
  categories: string[];
  summary: Record<string, number>;
};
export type InventoryItem = {
  id: string;
  sku: string;
  product_name: string;
  platform: string;
  current_stock: number;
  unit_cost: number;
  retail_price: number;
  predicted_demand_30d?: number;
  reorder_point?: number;
  lead_time_days: number;
  safety_stock: number;
  status: string;
  category: string;
  last_sold_at?: string;
  last_synced_at?: string;
};

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export async function getDashboard(): Promise<DashboardResponse> {
  return fetchApi<DashboardResponse>("/dashboard");
}

export async function getTrends(period: "weekly" | "monthly" = "weekly", category?: string): Promise<TrendsResponse> {
  const q = new URLSearchParams({ period });
  if (category && category !== "All") q.set("category", category);
  return fetchApi<TrendsResponse>(`/dashboard/trends?${q}`);
}

export async function getInventory(params?: {
  status?: string;
  platform?: string;
  category?: string;
  search?: string;
}): Promise<InventoryItem[]> {
  const q = new URLSearchParams();
  if (params?.status) q.set("status", params.status);
  if (params?.platform) q.set("platform", params.platform);
  if (params?.category) q.set("category", params.category);
  if (params?.search) q.set("search", params.search);
  const suffix = q.toString() ? `?${q}` : "";
  return fetchApi<InventoryItem[]>(`/inventory${suffix}`);
}

export async function getInventoryBySku(sku: string): Promise<InventoryItem | null> {
  const res = await fetch(`${API_BASE}/inventory/sku/${encodeURIComponent(sku)}`);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(`API ${res.status}`);
  return res.json() as Promise<InventoryItem>;
}

export { API_BASE };

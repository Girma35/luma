/**
 * ReOrder AI — API client for dashboard
 * Uses PUBLIC_API_URL (e.g. http://localhost:8000) with fallback.
 */

const BASE =
  (typeof import.meta !== "undefined" && (import.meta as unknown as { env?: { PUBLIC_API_URL?: string } }).env?.PUBLIC_API_URL) ||
  "http://localhost:8000";

export type KPI = { label: string; value: string; trend: string; status: string };
export type Alert = {
  id: string;
  type: string;
  title: string;
  message: string;
  severity: string;
  created_at?: string;
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

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`);
  return res.json() as Promise<T>;
}

export async function getDashboard(): Promise<DashboardResponse | null> {
  try {
    return await get<DashboardResponse>("/dashboard");
  } catch {
    return null;
  }
}

export async function getTrends(period: "weekly" | "monthly" = "weekly", category?: string): Promise<TrendsResponse | null> {
  try {
    const q = new URLSearchParams({ period });
    if (category && category !== "All") q.set("category", category);
    return await get<TrendsResponse>(`/dashboard/trends?${q}`);
  } catch {
    return null;
  }
}

export async function getInventory(params?: {
  status?: string;
  platform?: string;
  category?: string;
  search?: string;
}): Promise<InventoryItem[]> {
  try {
    const q = params ? new URLSearchParams(params as Record<string, string>) : "";
    return await get<InventoryItem[]>(`/inventory${q ? `?${q}` : ""}`);
  } catch {
    return [];
  }
}

export async function getInventoryItem(id: string): Promise<InventoryItem | null> {
  try {
    return await get<InventoryItem>(`/inventory/${id}`);
  } catch {
    return null;
  }
}

export async function getHealth(): Promise<{ status: string } | null> {
  try {
    return await get<{ status: string }>("/health");
  } catch {
    return null;
  }
}

import React from "react";
import type { InventoryItem } from "../../lib/api";

const statusClass: Record<string, string> = {
    OK: "bg-success/10 text-success",
    LOW_STOCK: "bg-amber-100 text-amber-800",
    REORDER_NOW: "bg-accent/10 text-accent",
    OUT_OF_STOCK: "bg-accent text-white",
    DEAD_STOCK: "bg-slate-200 text-slate-600",
};

export const SkuDetailFromApi: React.FC<{ item: InventoryItem }> = ({ item }) => {
    const runway = item.predicted_demand_30d
        ? Math.floor(item.current_stock / (item.predicted_demand_30d / 30))
        : null;
    const reorderDate = item.predicted_demand_30d
        ? (() => {
            const d = new Date();
            d.setDate(d.getDate() + (runway ?? 0) - item.lead_time_days);
            return d.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
        })()
        : "—";

    return (
        <>
            <nav className="flex flex-wrap gap-2 mb-4 items-center">
                <a className="text-primary/70 text-sm font-medium hover:text-primary" href="/">Dashboard</a>
                <span className="material-symbols-outlined text-xs text-primary/40">chevron_right</span>
                <a className="text-primary/70 text-sm font-medium hover:text-primary" href="/inventory">Inventory</a>
                <span className="material-symbols-outlined text-xs text-primary/40">chevron_right</span>
                <span className="text-[#131616] text-sm font-semibold">SKU: {item.sku}</span>
            </nav>

            <div className="bg-primary rounded-xl p-8 mb-8 text-white shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-3 flex-wrap">
                        <h1 className="text-3xl sm:text-4xl font-black tracking-tight">SKU: {item.sku}</h1>
                        <span className="bg-white/20 text-white text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider">
                            {item.status.replace("_", " ")}
                        </span>
                    </div>
                    <p className="text-white/80 text-base font-medium">
                        {item.product_name} • {item.category} • Last synced: {item.last_synced_at ? new Date(item.last_synced_at).toLocaleDateString() : "—"}
                    </p>
                </div>
                <div className="flex gap-3">
                    <a href={`/inventory?highlight=${item.id}`} className="flex items-center gap-2 px-5 py-2.5 bg-white/10 hover:bg-white/20 border border-white/30 rounded-lg text-white text-sm font-bold transition-all">
                        <span className="material-symbols-outlined text-lg">edit_note</span>
                        Edit
                    </a>
                    <a href="/forecasts" className="flex items-center gap-2 px-6 py-2.5 bg-white text-primary hover:bg-cream rounded-lg text-sm font-bold shadow-md">
                        <span className="material-symbols-outlined text-lg">trending_up</span>
                        Analytics
                    </a>
                </div>
            </div>

            {["REORDER_NOW", "OUT_OF_STOCK", "LOW_STOCK"].includes(item.status) && (
                <div className="bg-accent/10 border-l-4 border-accent p-5 rounded-lg mb-8 flex items-start gap-4">
                    <span className="material-symbols-outlined text-accent text-3xl">warning</span>
                    <div className="flex-1">
                        <h3 className="text-accent text-lg font-bold">Stock alert</h3>
                        <p className="text-slate-600 text-sm mt-1">
                            Current stock {item.current_stock} • Predicted demand 30d: {item.predicted_demand_30d ?? "—"} • Runway: {runway != null ? `${runway} days` : "—"}
                        </p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-cream p-6 rounded-xl border border-primary/10 shadow-sm">
                    <p className="text-[#6a7b7c] text-sm font-semibold uppercase tracking-wider">Current Stock</p>
                    <p className="text-primary text-3xl font-black mt-1">{item.current_stock} <span className="text-base text-[#6a7b7c]">units</span></p>
                    <p className="text-[#6a7b7c] text-xs mt-2">Runway: {runway != null ? `${runway} days` : "—"}</p>
                </div>
                <div className="bg-cream p-6 rounded-xl border border-primary/10 shadow-sm">
                    <p className="text-[#6a7b7c] text-sm font-semibold uppercase tracking-wider">Lead Time</p>
                    <p className="text-primary text-3xl font-black mt-1">{item.lead_time_days} <span className="text-base text-[#6a7b7c]">days</span></p>
                </div>
                <div className="bg-cream p-6 rounded-xl border border-primary/10 shadow-sm">
                    <p className="text-[#6a7b7c] text-sm font-semibold uppercase tracking-wider">Predicted demand (30d)</p>
                    <p className="text-primary text-3xl font-black mt-1">{item.predicted_demand_30d ?? "—"} <span className="text-base text-[#6a7b7c]">units</span></p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
                <div className="lg:col-span-2 bg-cream rounded-xl border border-primary/10 p-6 shadow-sm">
                    <div className="flex items-center gap-2 border-b border-primary/10 pb-4">
                        <span className="material-symbols-outlined text-primary">factory</span>
                        <h3 className="text-lg font-bold">Platform & cost</h3>
                    </div>
                    <div className="flex flex-col gap-4 mt-4">
                        <p className="text-sm"><span className="font-bold text-[#6a7b7c]">Platform</span> <span className="font-bold text-primary capitalize">{item.platform}</span></p>
                        <p className="text-sm"><span className="font-bold text-[#6a7b7c]">Unit cost</span> <span className="font-bold text-primary">${item.unit_cost.toFixed(2)}</span></p>
                        <p className="text-sm"><span className="font-bold text-[#6a7b7c]">Retail price</span> <span className="font-bold text-primary">${item.retail_price.toFixed(2)}</span></p>
                        <p className="text-sm"><span className="font-bold text-[#6a7b7c]">Safety stock</span> <span className="font-bold text-primary">{item.safety_stock}</span></p>
                    </div>
                </div>
                <div className="lg:col-span-3 bg-cream rounded-xl border border-primary/10 p-6 shadow-sm">
                    <div className="flex items-center gap-2 border-b border-primary/10 pb-4">
                        <span className="material-symbols-outlined text-primary">query_stats</span>
                        <h3 className="text-lg font-bold">Forecast</h3>
                    </div>
                    <div className="grid grid-cols-2 gap-4 mt-4">
                        <div className="bg-secondary p-3 rounded-lg">
                            <p className="text-xs font-bold text-[#6a7b7c]">OPTIMAL REORDER DATE</p>
                            <p className="text-lg font-black text-[#131616]">{reorderDate}</p>
                        </div>
                        <div className="bg-secondary p-3 rounded-lg">
                            <p className="text-xs font-bold text-[#6a7b7c]">REORDER POINT</p>
                            <p className="text-lg font-black text-[#131616]">{item.reorder_point ?? "—"}</p>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

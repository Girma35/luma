import { useEffect, useState } from 'react';
import { fetchInventory, type InventoryItem } from '../lib/api';

function StatusBadge({ status }: { status: string }) {
  const styles: Record<string, string> = {
    REORDER_NOW: 'bg-red-500/20 text-red-400 border-red-500/50',
    DEAD_STOCK: 'bg-amber-500/20 text-amber-400 border-amber-500/50',
    OK: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/50',
  };
  const label = status === 'REORDER_NOW' ? 'Reorder now' : status === 'DEAD_STOCK' ? 'Dead stock' : 'Healthy';
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold border ${styles[status] || 'bg-white/10'}`}>
      {label}
    </span>
  );
}

export default function InventoryTable() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInventory()
      .then(setItems)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'))
      .finally(() => setLoading(false));
  }, []);

  if (error) {
    return (
      <div className="rounded-2xl p-6 border border-red-500/30 bg-red-500/5 text-red-400">
        <p>{error}</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="rounded-2xl border border-white/10 bg-white/5 p-8 animate-pulse">
        <div className="h-8 w-48 bg-white/10 rounded mb-6" />
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="h-12 bg-white/10 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="border-b border-white/10 text-white/60 text-sm font-semibold">
              <th className="p-4">SKU</th>
              <th className="p-4">Product</th>
              <th className="p-4">Stock</th>
              <th className="p-4">Reorder at</th>
              <th className="p-4">Demand (30d)</th>
              <th className="p-4">Status</th>
            </tr>
          </thead>
          <tbody>
            {items.map((row) => (
              <tr key={row.sku} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                <td className="p-4 font-mono text-sm">{row.sku}</td>
                <td className="p-4 font-medium">{row.product_name}</td>
                <td className="p-4">{row.current_stock}</td>
                <td className="p-4">{row.reorder_point ?? '—'}</td>
                <td className="p-4">{row.predicted_demand_30d != null ? row.predicted_demand_30d.toFixed(1) : '—'}</td>
                <td className="p-4">
                  <StatusBadge status={row.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

import React, { useEffect, useState } from 'react';
import { getInventory, type InventoryItem } from '../lib/api';

const STATUS_STYLES: Record<string, string> = {
  OK: 'bg-success/10 text-success',
  LOW_STOCK: 'bg-accent/10 text-accent',
  REORDER_NOW: 'bg-accent text-white',
  OUT_OF_STOCK: 'bg-accent text-white',
  DEAD_STOCK: 'bg-slate-200 text-slate-600 dark:bg-white/10 dark:text-slate-400',
};

export const InventoryTable: React.FC = () => {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'risk'>('all');

  useEffect(() => {
    getInventory()
      .then(setItems)
      .catch(() => setItems([]))
      .finally(() => setLoading(false));
  }, []);

  const riskStatuses = ['REORDER_NOW', 'LOW_STOCK', 'OUT_OF_STOCK', 'DEAD_STOCK'];
  const filtered = filter === 'risk' ? items.filter((i) => riskStatuses.includes(i.status)) : items;

  if (loading) {
    return (
      <div className="bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded overflow-hidden">
        <div className="p-8 text-center text-slate-500">Loading inventory…</div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded p-8 text-center text-slate-500">
        No inventory data. Start the API or sync from Shopify/WooCommerce.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-black text-black dark:text-white uppercase tracking-tighter">Asset Breakdown</h3>
        <div className="flex gap-2">
          <button
            className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest ${filter === 'all' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white dark:bg-white/10 border border-slate-200 dark:border-white/20 text-slate-400 dark:text-slate-400'}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`px-4 py-1.5 text-[10px] font-black uppercase tracking-widest ${filter === 'risk' ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-white dark:bg-white/10 border border-slate-200 dark:border-white/20 text-slate-400 dark:text-slate-400'}`}
            onClick={() => setFilter('risk')}
          >
            Risk Only
          </button>
        </div>
      </div>
      <div className="bg-white dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-black text-white text-[10px] font-black uppercase tracking-widest">
                <th className="px-6 py-4">SKU / Product</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Stock</th>
                <th className="px-6 py-4">Status</th>
                <th className="px-6 py-4">Value</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-white/10">
              {filtered.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4">
                    <a href={`/sku/${item.sku}`} className="block group">
                      <span className="font-black text-black dark:text-white text-sm uppercase tracking-tighter group-hover:underline">{item.product_name}</span>
                      <span className="text-[9px] text-slate-400 font-bold tracking-widest uppercase block">{item.sku}</span>
                    </a>
                  </td>
                  <td className="px-6 py-4 text-[11px] font-bold text-slate-500 dark:text-slate-400 uppercase">{item.category}</td>
                  <td className="px-6 py-4 text-sm font-bold text-black dark:text-white">{item.current_stock}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${STATUS_STYLES[item.status] ?? 'bg-slate-100 text-slate-600'}`}>
                      {item.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm font-black text-black dark:text-white">${(item.current_stock * item.unit_cost).toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <a href={`/sku/${item.sku}`} className="inline-block bg-black dark:bg-white text-white dark:text-black px-4 py-1.5 rounded text-[9px] font-black uppercase tracking-widest hover:opacity-90 transition-all">
                      View
                    </a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

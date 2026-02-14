import React, { useEffect, useState } from 'react';
import { getInventory, type InventoryItem } from '../lib/api';

const statusClass: Record<string, string> = {
    OK: 'bg-slate-100 text-slate-600',
    LOW_STOCK: 'bg-amber-100 text-amber-800',
    REORDER_NOW: 'bg-accent/10 text-accent',
    OUT_OF_STOCK: 'bg-accent text-white',
    DEAD_STOCK: 'bg-slate-200 text-slate-600',
};

export const InventoryList: React.FC = () => {
    const [items, setItems] = useState<InventoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('');

    useEffect(() => {
        getInventory().then((list) => {
            setItems(list);
            setLoading(false);
        });
    }, []);

    const filtered = filter
        ? items.filter(
            (i) =>
                i.sku.toLowerCase().includes(filter.toLowerCase()) ||
                i.product_name.toLowerCase().includes(filter.toLowerCase())
        )
        : items;

    if (loading) {
        return (
            <div className="bg-white border border-slate-200 rounded-lg p-12 text-center text-slate-500 font-medium">
                Loading inventory…
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-4">
                <input
                    type="search"
                    placeholder="Search SKU or product name..."
                    className="bg-slate-50 border border-slate-200 rounded pl-10 pr-4 py-2 text-sm font-medium placeholder:text-slate-400 max-w-xs"
                    value={filter}
                    onChange={(e) => setFilter(e.target.value)}
                />
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                    {filtered.length} item{filtered.length !== 1 ? 's' : ''}
                </span>
            </div>
            <div className="bg-white border border-slate-200 shadow-sm overflow-hidden rounded-lg">
                <table className="w-full text-left border-collapse">
                    <thead>
                        <tr className="bg-slate-50 border-b border-slate-200 text-[10px] font-black uppercase tracking-widest text-slate-500">
                            <th className="px-6 py-4">SKU / Product</th>
                            <th className="px-6 py-4">Category</th>
                            <th className="px-6 py-4">Stock</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Value</th>
                            <th className="px-6 py-4 text-right">Action</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filtered.map((item) => (
                            <tr key={item.id} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="font-bold text-black text-sm">{item.product_name}</div>
                                    <div className="text-[9px] text-slate-400 font-bold uppercase tracking-widest">{item.sku}</div>
                                </td>
                                <td className="px-6 py-4 text-sm text-slate-600">{item.category}</td>
                                <td className="px-6 py-4 font-bold text-black">{item.current_stock}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${statusClass[item.status] ?? 'bg-slate-100 text-slate-600'}`}>
                                        {item.status.replace('_', ' ')}
                                    </span>
                                </td>
                                <td className="px-6 py-4 font-bold text-black">${(item.current_stock * item.unit_cost).toLocaleString()}</td>
                                <td className="px-6 py-4 text-right">
                                    <a
                                        href={`/sku/${item.id}`}
                                        className="inline-flex items-center gap-1 bg-black text-white px-4 py-1.5 rounded text-[9px] font-black uppercase tracking-widest hover:bg-slate-800 transition-all"
                                    >
                                        View
                                    </a>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {filtered.length === 0 && (
                    <div className="px-6 py-12 text-center text-slate-500 font-medium">
                        {items.length === 0 ? 'No inventory yet. Connect a store or add items via the API.' : 'No items match your search.'}
                    </div>
                )}
            </div>
        </div>
    );
};

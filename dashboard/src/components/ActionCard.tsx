import React, { useEffect, useState } from 'react';
import { dashboardData } from '../data/mockData';
import { getDashboard, type RecommendedAction } from '../lib/api';

export const ActionCard: React.FC = () => {
    const [action, setAction] = useState<RecommendedAction>(dashboardData.recommendedAction as unknown as RecommendedAction);

    useEffect(() => {
        getDashboard().then((d) => {
            if (d?.recommended_action) {
                setAction({
                    skus_count: d.recommended_action.skus_count,
                    total_value: d.recommended_action.total_value,
                    message: d.recommended_action.message,
                    items: d.recommended_action.items || [],
                });
            }
        });
    }, []);

    return (
        <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-xl p-8 relative overflow-hidden">
            <div className="absolute right-0 top-0 h-full w-px bg-slate-200 pointer-events-none"></div>
            <div className="flex justify-between items-center relative z-10">
                <div className="max-w-xl">
                    <div className="flex items-center gap-2 mb-4">
                        <span className="bg-black text-white px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest">Priority AI Action</span>
                        <span className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">• {action.skus_count} SKUs Pending</span>
                    </div>
                    <h3 className="text-3xl font-black text-black tracking-tighter mb-3 uppercase">Inventory Optimization Required</h3>
                    <p className="text-slate-500 font-medium text-sm leading-snug mb-6 max-w-lg">
                        {action.message}
                    </p>
                    <div className="flex items-baseline gap-2 mb-6 border-b border-slate-100 pb-4">
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Est. Liquidity Requirement:</span>
                        <span className="text-2xl font-black text-black">{action.total_value}</span>
                    </div>
                    <div className="flex gap-4">
                        <a href="/inventory/buying" className="bg-black hover:bg-slate-800 text-white font-black px-8 py-3 rounded text-[10px] uppercase tracking-widest transition-all shadow-lg flex items-center gap-2 inline-flex">
                            <span>Execute Order</span>
                            <span className="material-symbols-outlined text-sm">bolt</span>
                        </a>
                        <a href="/forecasts" className="bg-white border border-slate-300 text-black font-black px-6 py-3 rounded text-[10px] uppercase tracking-widest hover:bg-slate-50 transition-all inline-flex">
                            Analysis Breakdown
                        </a>
                    </div>
                </div>
                <div className="hidden lg:block text-slate-100 transition-transform hover:scale-110">
                    <span className="material-symbols-outlined text-[120px]">verified</span>
                </div>
            </div>
        </div>
    );
};

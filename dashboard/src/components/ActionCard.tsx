import React, { useEffect, useState } from 'react';
import { getDashboard, type RecommendedAction } from '../lib/api';
import { dashboardData } from '../data/mockData';

export const ActionCard: React.FC = () => {
    const [action, setAction] = useState<RecommendedAction>(dashboardData.recommendedAction as unknown as RecommendedAction);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getDashboard()
            .then((d) => {
                if (d.recommended_action)
                    setAction(d.recommended_action);
            })
            .catch(() => { /* keep mock */ })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-xl p-8 relative overflow-hidden animate-pulse">
                <div className="h-6 bg-slate-200 rounded w-48 mb-4" />
                <div className="h-8 bg-slate-200 rounded w-3/4 mb-3" />
                <div className="h-4 bg-slate-100 rounded w-full mb-6" />
                <div className="h-10 bg-slate-200 rounded w-32" />
            </div>
        );
    }

    return (
        <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-xl p-8 relative overflow-hidden">
            <div className="absolute right-0 top-0 h-full w-px bg-slate-200 pointer-events-none"></div>
            <div className="flex justify-between items-center relative z-10">
                <div className="max-w-xl">
                    <div className="flex items-center gap-2 mb-4">
                        <span className="bg-black text-white px-3 py-1 rounded text-[9px] font-black uppercase tracking-widest">Priority AI Action</span>
                        <span className="text-slate-400 text-[10px] font-bold uppercase tracking-widest">• {action.skus_count} SKUs Pending</span>
                    </div>
                    <h3 className="text-3xl font-black text-black dark:text-white tracking-tighter mb-3 uppercase">Inventory Optimization Required</h3>
                    <p className="text-slate-500 dark:text-slate-400 font-medium text-sm leading-snug mb-6 max-w-lg">
                        {action.message}
                    </p>
                    <div className="flex items-baseline gap-2 mb-6 border-b border-slate-100 dark:border-white/10 pb-4">
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-400">Est. Liquidity Requirement:</span>
                        <span className="text-2xl font-black text-black dark:text-white">{action.total_value}</span>
                    </div>
                    <div className="flex gap-4">
                        <a href="/inventory/buying" className="bg-black hover:bg-slate-800 text-white font-black px-8 py-3 rounded text-[10px] uppercase tracking-widest transition-all shadow-lg flex items-center gap-2 inline-flex">
                            <span>Execute Order</span>
                            <span className="material-symbols-outlined text-sm">bolt</span>
                        </a>
                        <a href="/inventory/health" className="bg-white dark:bg-white/10 border border-slate-300 dark:border-white/20 text-black dark:text-white font-black px-6 py-3 rounded text-[10px] uppercase tracking-widest hover:bg-slate-50 dark:hover:bg-white/20 transition-all inline-flex">
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

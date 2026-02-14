import React, { useEffect, useState } from 'react';
import { getDashboard } from '../lib/api';
import { dashboardData } from '../data/mockData';

type KPI = { label: string; value: string; trend: string; status: string };

export const KPICards: React.FC = () => {
    const [kpis, setKpis] = useState<KPI[]>(dashboardData.kpis);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getDashboard()
            .then((d) => setKpis(d.kpis))
            .catch(() => { /* keep mock */ })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="bg-white dark:bg-background-dark p-6 rounded border border-slate-200 shadow-sm animate-pulse">
                        <div className="h-3 bg-slate-200 rounded w-1/2 mb-4" />
                        <div className="h-8 bg-slate-200 rounded w-2/3 mb-2" />
                        <div className="h-3 bg-slate-100 rounded w-3/4" />
                    </div>
                ))}
            </div>
        );
    }

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpis.map((kpi, index) => (
                <div key={index} className="bg-white dark:bg-background-dark p-6 rounded border border-slate-200 shadow-sm">
                    <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">{kpi.label}</p>
                    <h3 className="text-3xl font-black text-black dark:text-white tracking-tighter">{kpi.value}</h3>
                    <div className={`mt-2 flex items-center text-xs font-bold ${kpi.status === 'up' ? 'text-success' :
                        kpi.status === 'down' ? 'text-accent' :
                            'text-slate-400'
                        }`}>
                        <span className="material-symbols-outlined text-[16px] mr-1">
                            {kpi.status === 'up' ? 'trending_up' :
                                kpi.status === 'down' ? 'warning' :
                                    kpi.status === 'neutral' ? 'check_circle' : 'inventory'}
                        </span>
                        <span>{kpi.trend}</span>
                    </div>
                </div>
            ))}
        </div>
    );
};

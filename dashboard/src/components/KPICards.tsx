import React, { useEffect, useState } from 'react';
import { dashboardData } from '../data/mockData';
import { getDashboard, type KPI } from '../lib/api';

export const KPICards: React.FC = () => {
    const [kpis, setKpis] = useState<KPI[]>(dashboardData.kpis);

    useEffect(() => {
        getDashboard().then((d) => {
            if (d?.kpis?.length) setKpis(d.kpis);
        });
    }, []);

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpis.map((kpi, index) => (
                <div key={index} className="bg-white dark:bg-background-dark p-6 rounded border border-slate-200 shadow-sm">
                    <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest mb-1">{kpi.label}</p>
                    <h3 className="text-3xl font-black text-black tracking-tighter">{kpi.value}</h3>
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

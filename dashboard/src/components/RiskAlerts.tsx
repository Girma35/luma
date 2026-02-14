import React, { useEffect, useState } from 'react';
import { getDashboard, type Alert } from '../lib/api';
import { dashboardData } from '../data/mockData';

function formatTime(createdAt: string): string {
    try {
        const d = new Date(createdAt);
        const now = new Date();
        const mins = Math.floor((now.getTime() - d.getTime()) / 60000);
        if (mins < 60) return `${mins} mins ago`;
        const hours = Math.floor(mins / 60);
        if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        const days = Math.floor(hours / 24);
        return days === 1 ? 'Yesterday' : `${days} days ago`;
    } catch {
        return '';
    }
}

export const RiskAlerts: React.FC = () => {
    const [alerts, setAlerts] = useState(dashboardData.alerts as { id: number | string; type: string; title: string; message: string; time: string; severity: string }[]);
    const [unresolvedCount, setUnresolvedCount] = useState(3);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getDashboard()
            .then((d) => {
                setAlerts(d.alerts.map((a: Alert) => ({
                    id: a.id,
                    type: a.type,
                    title: a.title,
                    message: a.message,
                    time: formatTime(a.created_at),
                    severity: a.severity,
                })));
                setUnresolvedCount(d.alerts.filter((a: Alert) => !a.resolved).length);
            })
            .catch(() => { /* keep mock */ })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-sm p-6 flex flex-col h-full">
                <div className="flex items-center justify-between mb-6">
                    <h3 className="font-bold text-sm uppercase tracking-tighter text-black dark:text-white">Risk Management</h3>
                    <span className="h-5 w-16 bg-slate-200 rounded animate-pulse" />
                </div>
                <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-20 bg-slate-100 dark:bg-white/5 rounded animate-pulse" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-sm p-6 flex flex-col h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-sm uppercase tracking-tighter text-black dark:text-white">Risk Management</h3>
                <span className="bg-accent text-white text-[9px] font-black px-2 py-0.5 rounded">{unresolvedCount} ACTIVE</span>
            </div>
            <div className="space-y-6 flex-1 overflow-y-auto">
                {alerts.map((alert) => (
                    <div key={String(alert.id)} className="group cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                            <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${alert.severity === 'high' ? 'bg-accent text-white' :
                                alert.severity === 'medium' ? 'bg-black text-white' :
                                    'bg-slate-200 text-black dark:bg-white/20 dark:text-white'
                                }`}>
                                {alert.type}
                            </span>
                            <span className="text-[10px] text-slate-400 font-bold uppercase">{alert.time}</span>
                        </div>
                        <h4 className="text-sm font-bold text-black dark:text-white group-hover:underline transition-all leading-tight">
                            {alert.title}
                        </h4>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 leading-snug font-medium">
                            {alert.message}
                        </p>
                    </div>
                ))}
            </div>
            <a href="/inventory/health" className="w-full mt-8 py-2 border border-black dark:border-white text-black dark:text-white font-black text-[10px] uppercase tracking-widest hover:bg-black hover:text-white dark:hover:bg-white dark:hover:text-black transition-all text-center block rounded">
                Full System Log
            </a>
        </div>
    );
};

export const HealthScore: React.FC = () => {
    const [healthScore, setHealthScore] = useState(dashboardData.healthScore);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getDashboard()
            .then((d) => setHealthScore(d.health_score))
            .catch(() => { /* keep mock */ })
            .finally(() => setLoading(false));
    }, []);

    if (loading) {
        return (
            <div className="bg-black text-white rounded p-6 shadow-xl">
                <div className="flex justify-between items-center mb-4">
                    <span className="text-[10px] font-black uppercase tracking-widest">Health Index</span>
                    <span className="material-symbols-outlined text-sm">shield</span>
                </div>
                <div className="h-12 w-24 bg-white/20 rounded animate-pulse" />
                <div className="w-full bg-white/10 h-1 rounded-full mt-6 animate-pulse" />
            </div>
        );
    }

    return (
        <div className="bg-black text-white rounded p-6 shadow-xl">
            <div className="flex justify-between items-center mb-4">
                <span className="text-[10px] font-black uppercase tracking-widest">Health Index</span>
                <span className="material-symbols-outlined text-sm">shield</span>
            </div>
            <div className="flex items-end gap-3">
                <div className="text-5xl font-black tracking-tighter">{healthScore}</div>
                <div className="text-[10px] uppercase font-bold text-success mb-1 tracking-widest flex items-center">
                    <span className="material-symbols-outlined text-sm mr-1">trending_up</span>
                    Stable
                </div>
            </div>
            <div className="w-full bg-white/10 h-1 rounded-full mt-6">
                <div className="bg-success h-full rounded-full transition-all duration-1000" style={{ width: `${Math.min(100, healthScore)}%` }}></div>
            </div>
        </div>
    );
};

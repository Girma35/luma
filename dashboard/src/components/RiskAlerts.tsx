import React, { useEffect, useState } from 'react';
import { dashboardData } from '../data/mockData';
import { getDashboard, type Alert } from '../lib/api';

function formatTimeAgo(createdAt: string | undefined): string {
    if (!createdAt) return '';
    const d = new Date(createdAt);
    const now = new Date();
    const mins = Math.floor((now.getTime() - d.getTime()) / 60000);
    if (mins < 60) return `${mins} mins ago`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    const days = Math.floor(hours / 24);
    return days === 1 ? 'Yesterday' : `${days} days ago`;
}

export const RiskAlerts: React.FC = () => {
    const [alerts, setAlerts] = useState<Alert[]>(dashboardData.alerts as unknown as Alert[]);
    const [unresolvedCount, setUnresolvedCount] = useState(3);

    useEffect(() => {
        getDashboard().then((d) => {
            if (d?.alerts?.length !== undefined) {
                const active = d.alerts.filter((a) => !a.resolved);
                setAlerts(d.alerts);
                setUnresolvedCount(active.length);
            }
        });
    }, []);

    return (
        <div className="bg-white dark:bg-background-dark rounded border border-slate-200 shadow-sm p-6 flex flex-col h-full">
            <div className="flex items-center justify-between mb-6">
                <h3 className="font-bold text-sm uppercase tracking-tighter text-black">Risk Management</h3>
                <span className="bg-accent text-white text-[9px] font-black px-2 py-0.5 rounded">{unresolvedCount} ACTIVE</span>
            </div>
            <div className="space-y-6 flex-1 overflow-y-auto">
                {alerts.map((alert) => (
                    <div key={alert.id} className="group cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                            <span className={`px-2 py-0.5 rounded text-[9px] font-black uppercase tracking-widest ${alert.severity === 'high' ? 'bg-accent text-white' :
                                alert.severity === 'medium' ? 'bg-black text-white' :
                                    'bg-slate-200 text-black'
                                }`}>
                                {alert.type}
                            </span>
                            <span className="text-[10px] text-slate-400 font-bold uppercase">
                                {('time' in alert && typeof (alert as { time?: string }).time === 'string')
                                    ? (alert as { time: string }).time
                                    : formatTimeAgo(alert.created_at)}
                            </span>
                        </div>
                        <h4 className="text-sm font-bold text-black dark:text-white group-hover:underline transition-all leading-tight">
                            {alert.title}
                        </h4>
                        <p className="text-xs text-slate-500 mt-1 leading-snug font-medium">
                            {alert.message}
                        </p>
                    </div>
                ))}
            </div>
            <a href="/inventory/health" className="w-full mt-8 py-2 border border-black text-black font-black text-[10px] uppercase tracking-widest hover:bg-black hover:text-white transition-all block text-center">
                Full System Log
            </a>
        </div>
    );
};

export const HealthScore: React.FC = () => {
    const [score, setScore] = useState(dashboardData.healthScore);

    useEffect(() => {
        getDashboard().then((d) => {
            if (d != null && typeof d.health_score === 'number') setScore(d.health_score);
        });
    }, []);

    return (
        <div className="bg-black text-white rounded p-6 shadow-xl">
            <div className="flex justify-between items-center mb-4">
                <span className="text-[10px] font-black uppercase tracking-widest">Health Index</span>
                <span className="material-symbols-outlined text-sm">shield</span>
            </div>
            <div className="flex items-end gap-3">
                <div className="text-5xl font-black tracking-tighter">{score}</div>
                <div className="text-[10px] uppercase font-bold text-success mb-1 tracking-widest flex items-center">
                    <span className="material-symbols-outlined text-sm mr-1">trending_up</span>
                    {score >= 80 ? 'Stable' : score >= 60 ? 'Monitor' : 'At Risk'}
                </div>
            </div>
            <div className="w-full bg-white/10 h-1 rounded-full mt-6">
                <div className="bg-success h-full rounded-full transition-all duration-1000" style={{ width: `${Math.min(100, score)}%` }}></div>
            </div>
        </div>
    );
};

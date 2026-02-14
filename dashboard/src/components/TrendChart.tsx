import React, { useEffect, useState } from 'react';
import { getTrends, type TrendsResponse } from '../lib/api';

export const TrendChart: React.FC = () => {
    const [period, setPeriod] = useState<'weekly' | 'monthly'>('weekly');
    const [data, setData] = useState<TrendsResponse | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getTrends(period)
            .then(setData)
            .catch(() => setData(null))
            .finally(() => setLoading(false));
    }, [period]);

    const points = data?.data ?? [];
    const maxVal = Math.max(1, ...points.map((d) => d.actual), ...points.map((d) => d.projected));

    return (
        <div className="bg-white dark:bg-background-dark p-6 rounded border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h3 className="text-sm font-black uppercase tracking-tighter text-black dark:text-white">Inventory Velocity</h3>
                    <p className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mt-1">Real-time Performance Metrics</p>
                </div>
                <div className="flex bg-slate-100 p-1 rounded">
                    <button
                        className={`px-4 py-1 text-[10px] font-black uppercase ${period === 'weekly' ? 'bg-white shadow-sm border border-slate-200' : 'text-slate-400'}`}
                        onClick={() => setPeriod('weekly')}
                    >
                        Weekly
                    </button>
                    <button
                        className={`px-4 py-1 text-[10px] font-bold uppercase ${period === 'monthly' ? 'bg-white shadow-sm border border-slate-200' : 'text-slate-400'}`}
                        onClick={() => setPeriod('monthly')}
                    >
                        Monthly
                    </button>
                </div>
            </div>
            <div className="h-64 w-full bg-slate-50 dark:bg-white/5 rounded flex items-end justify-between gap-1 p-6 overflow-hidden relative border border-slate-100">
                {loading ? (
                    <div className="w-full flex items-center justify-center text-slate-400 text-sm">Loading…</div>
                ) : points.length === 0 ? (
                    <div className="w-full flex items-end justify-between gap-1">
                        {[0.6, 0.75, 0.5, 0.8, 0.3, 0.5, 1, 0.6, 0.5, 0.75].map((height, i) => (
                            <div
                                key={i}
                                className="flex-1 rounded-t min-w-[8px] transition-all duration-300"
                                style={{ height: `${height * 100}%`, backgroundColor: i === 6 ? '#16a34a' : '#00000022' }}
                            />
                        ))}
                    </div>
                ) : (
                    <>
                        {points.map((d, i) => (
                            <div key={d.label} className="flex-1 flex flex-col items-center gap-1 min-w-0">
                                <div
                                    className="w-full rounded-t transition-all duration-300 bg-black/20 dark:bg-white/20"
                                    style={{ height: `${(d.actual / maxVal) * 100}%`, minHeight: '4px' }}
                                />
                                <div
                                    className="w-full rounded-t transition-all duration-300 bg-success/80"
                                    style={{ height: `${(d.projected / maxVal) * 100}%`, minHeight: '2px' }}
                                />
                            </div>
                        ))}
                    </>
                )}
            </div>
            <div className="mt-4 flex justify-between text-[8px] font-black uppercase tracking-widest text-slate-400">
                {points.length > 0 ? (
                    <>
                        <span>{points[0]?.label}</span>
                        <span>{points[Math.floor(points.length / 2)]?.label}</span>
                        <span>{points[points.length - 1]?.label}</span>
                    </>
                ) : (
                    <>
                        <span>Oct 01</span>
                        <span>Oct 15</span>
                        <span>Oct 31</span>
                    </>
                )}
            </div>
        </div>
    );
};

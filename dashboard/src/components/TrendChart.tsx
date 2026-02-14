import React, { useEffect, useState } from 'react';
import { getTrends, type TrendDataPoint } from '../lib/api';

export const TrendChart: React.FC = () => {
    const [period, setPeriod] = useState<'weekly' | 'monthly'>('weekly');
    const [data, setData] = useState<TrendDataPoint[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getTrends(period).then((res) => {
            if (res?.data?.length) {
                setData(res.data);
            } else {
                // Fallback mock bars when API has no data
                setData([
                    { label: 'W1', actual: 60, projected: 58, category: 'All' },
                    { label: 'W2', actual: 75, projected: 72, category: 'All' },
                    { label: 'W3', actual: 50, projected: 55, category: 'All' },
                    { label: 'W4', actual: 80, projected: 78, category: 'All' },
                    { label: 'W5', actual: 30, projected: 35, category: 'All' },
                    { label: 'W6', actual: 50, projected: 52, category: 'All' },
                    { label: 'W7', actual: 100, projected: 95, category: 'All' },
                    { label: 'W8', actual: 60, projected: 62, category: 'All' },
                    { label: 'W9', actual: 50, projected: 48, category: 'All' },
                    { label: 'W10', actual: 75, projected: 78, category: 'All' },
                ]);
            }
            setLoading(false);
        });
    }, [period]);

    const maxVal = Math.max(...data.map((d) => d.actual), 1);

    return (
        <div className="bg-white dark:bg-background-dark p-6 rounded border border-slate-200 shadow-sm">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h3 className="text-sm font-black uppercase tracking-tighter text-black">Inventory Velocity</h3>
                    <p className="text-[10px] uppercase font-bold text-slate-400 tracking-widest mt-1">Real-time Performance Metrics</p>
                </div>
                <div className="flex bg-slate-100 p-1 rounded">
                    <button
                        onClick={() => setPeriod('weekly')}
                        className={`px-4 py-1 text-[10px] font-black uppercase ${period === 'weekly' ? 'bg-white shadow-sm border border-slate-200' : 'text-slate-400'}`}
                    >
                        Weekly
                    </button>
                    <button
                        onClick={() => setPeriod('monthly')}
                        className={`px-4 py-1 text-[10px] font-bold uppercase ${period === 'monthly' ? 'bg-white shadow-sm border border-slate-200' : 'text-slate-400'}`}
                    >
                        Monthly
                    </button>
                </div>
            </div>
            <div className="h-64 w-full bg-slate-50 dark:bg-white/5 rounded flex items-end justify-between p-6 overflow-hidden relative border border-slate-100 gap-1">
                {loading ? (
                    <div className="flex items-center justify-center w-full text-slate-400 text-sm">Loading…</div>
                ) : (
                    data.map((d, i) => (
                        <div
                            key={d.label}
                            className="flex-1 rounded-t transition-all duration-500 min-w-0"
                            style={{
                                height: `${(d.actual / maxVal) * 100}%`,
                                backgroundColor: i === data.length - 2 ? '#16a34a' : 'rgba(0,0,0,0.13)',
                            }}
                            title={`${d.label}: ${d.actual} actual, ${d.projected} projected`}
                        />
                    ))
                )}
            </div>
            <div className="mt-4 flex items-center justify-between text-[8px] font-black uppercase tracking-widest text-slate-400">
                <span>{data[0]?.label ?? '—'}</span>
                <span>{data[Math.floor(data.length / 2)]?.label ?? '—'}</span>
                <span>{data[data.length - 1]?.label ?? '—'}</span>
            </div>
        </div>
    );
};

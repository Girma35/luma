import { useEffect, useState } from 'react';
import { fetchInsights, type InsightsSummary } from '../lib/api';

export default function InsightsCards() {
  const [data, setData] = useState<InsightsSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load'));
  }, []);

  if (error) {
    return (
      <div className="rounded-3xl p-8 border border-red-500/30 bg-red-500/5 text-red-400">
        <p className="font-semibold">Cannot reach API</p>
        <p className="text-sm mt-1 opacity-80">{error}</p>
        <p className="text-sm mt-2">Start the backend with: <code className="bg-black/30 px-1 rounded">uvicorn src.api.main:app --reload</code></p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-white/5 border border-white/10 rounded-3xl p-8 animate-pulse">
        <div className="h-6 w-32 bg-white/10 rounded mb-6" />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-white/10 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white/5 border border-white/10 rounded-3xl p-8 shadow-inner overflow-hidden">
      <div className="flex justify-between items-center mb-8">
        <h3 className="text-xl font-bold">Inventory Health</h3>
        <span className="text-emerald-400 text-sm font-bold">Live</span>
      </div>
      <div className="space-y-4">
        <div className="p-5 rounded-2xl bg-black/40 border-l-4 border-red-500">
          <span className="text-sm text-white/40 block mb-1">Ready to Reorder</span>
          <span className="text-3xl font-black">{data.reorder_now} items</span>
        </div>
        <div className="p-5 rounded-2xl bg-black/40 border-l-4 border-amber-500">
          <span className="text-sm text-white/40 block mb-1">Dead Stock</span>
          <span className="text-3xl font-black">{data.dead_stock} items</span>
        </div>
        <div className="p-5 rounded-2xl bg-black/40 border-l-4 border-emerald-500">
          <span className="text-sm text-white/40 block mb-1">Healthy</span>
          <span className="text-3xl font-black">{data.healthy} items</span>
        </div>
      </div>
    </div>
  );
}

import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

export const ForecastChart: React.FC = () => {
    const { forecast } = skuDetailData;

    return (
        <div className="lg:col-span-3 bg-cream rounded-xl border border-primary/10 p-6 flex flex-col gap-4 shadow-sm">
            <div className="flex justify-between items-center border-b border-primary/10 pb-4">
                <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-primary">query_stats</span>
                    <h3 className="text-lg font-bold">Inventory Forecast (AI Model v4)</h3>
                </div>
                <div className="flex gap-2">
                    <button className="px-3 py-1 bg-primary/10 text-primary text-xs font-bold rounded transition-colors">
                        30 Days
                    </button>
                    <button className="px-3 py-1 hover:bg-primary/5 text-[#6a7b7c] text-xs font-bold rounded transition-colors">
                        90 Days
                    </button>
                </div>
            </div>

            {/* Forecast Chart Visualization */}
            <div className="flex-1 min-h-[250px] relative bg-primary/5 rounded-lg overflow-hidden border border-dashed border-primary/20 flex items-center justify-center">
                <svg
                    className="absolute inset-0 w-full h-full"
                    preserveAspectRatio="none"
                    viewBox="0 0 400 200"
                    xmlns="http://www.w3.org/2000/svg"
                >
                    {/* Projected line (dashed) */}
                    <path
                        d="M0 150 Q 50 140, 100 160 T 200 130 T 300 180 T 400 140"
                        fill="none"
                        opacity="0.4"
                        stroke="var(--color-primary, #7baaac)"
                        strokeDasharray="10 5"
                        strokeWidth="3"
                    />
                    {/* Actual line (solid) */}
                    <path
                        d="M0 160 Q 50 150, 100 170 T 200 120 T 300 190 T 400 110"
                        fill="none"
                        stroke="var(--color-primary, #7baaac)"
                        strokeWidth="4"
                    />
                    {/* Reorder point indicator */}
                    <circle cx="200" cy="120" fill="var(--color-primary, #7baaac)" r="5" />
                    <rect
                        fill="var(--color-primary, #7baaac)"
                        height="30"
                        rx="4"
                        width="40"
                        x="180"
                        y="80"
                    />
                    <text fill="white" fontSize="10" fontWeight="bold" textAnchor="middle" x="200" y="100">
                        REORDER
                    </text>
                </svg>
                <p className="text-primary/40 text-sm font-bold z-10">
                    Real-time depletion forecast visualization
                </p>
            </div>

            {/* Forecast Stats */}
            <div className="grid grid-cols-2 gap-4">
                <div className="bg-secondary p-3 rounded-lg">
                    <p className="text-xs font-bold text-[#6a7b7c]">EST. OUT OF STOCK</p>
                    <p className="text-lg font-black text-accent">{forecast.estOutOfStock}</p>
                </div>
                <div className="bg-secondary p-3 rounded-lg">
                    <p className="text-xs font-bold text-[#6a7b7c]">OPTIMAL REORDER DATE</p>
                    <p className="text-lg font-black text-[#131616]">{forecast.optimalReorderDate}</p>
                </div>
            </div>
        </div>
    );
};

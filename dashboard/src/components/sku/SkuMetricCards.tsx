import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

interface MetricCardProps {
    icon: string;
    label: string;
    value: number;
    unit: string;
    trend: number;
    description: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, unit, trend, description }) => {
    const isPositive = trend > 0;
    const isNeutral = trend === 0;
    const isNegative = trend < 0;

    return (
        <div className="bg-cream p-6 rounded-xl border border-primary/10 shadow-sm flex flex-col gap-4">
            <div className="flex justify-between items-start">
                <div className="p-2 bg-primary/10 rounded-lg text-primary">
                    <span className="material-symbols-outlined">{icon}</span>
                </div>
                <span
                    className={`text-sm font-bold flex items-center px-2 py-0.5 rounded-full ${isPositive
                            ? "text-emerald-700 bg-emerald-100"
                            : isNegative
                                ? "text-accent bg-red-100"
                                : "text-[#6a7b7c] bg-gray-200"
                        }`}
                >
                    <span className="material-symbols-outlined text-xs">
                        {isPositive ? "north" : isNegative ? "south" : "remove"}
                    </span>{" "}
                    {Math.abs(trend)}%
                </span>
            </div>
            <div>
                <p className="text-[#6a7b7c] text-sm font-semibold uppercase tracking-wider">{label}</p>
                <p className="text-primary text-3xl font-black mt-1">
                    {value} <span className="text-base font-normal text-[#6a7b7c]">{unit}</span>
                </p>
            </div>
            <p className="text-[#6a7b7c] text-xs leading-normal">{description}</p>
        </div>
    );
};

export const SkuMetricCards: React.FC = () => {
    const { salesVelocity, avgLeadTime, currentStock } = skuDetailData;

    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <MetricCard
                icon="speed"
                label="Sales Velocity"
                value={salesVelocity.value}
                unit={salesVelocity.unit}
                trend={salesVelocity.trend}
                description="Above average performance for the current 30-day window."
            />
            <MetricCard
                icon="schedule"
                label="Avg Lead Time"
                value={avgLeadTime.value}
                unit={avgLeadTime.unit}
                trend={avgLeadTime.trend}
                description="Consistent performance across last 5 replenishment cycles."
            />
            <MetricCard
                icon="inventory_2"
                label="Current Stock"
                value={currentStock.value}
                unit={currentStock.unit}
                trend={currentStock.trend}
                description={`Runway estimate: ${currentStock.runway} days based on current velocity.`}
            />
        </div>
    );
};

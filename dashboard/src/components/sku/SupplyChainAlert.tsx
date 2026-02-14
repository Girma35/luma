import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

interface SupplyChainAlertProps {
    sku?: string;
}

export const SupplyChainAlert: React.FC<SupplyChainAlertProps> = () => {
    const alert = skuDetailData.alert;
    if (!alert) return null;

    return (
        <div className="bg-accent/10 border-l-4 border-accent p-5 rounded-lg mb-8 flex items-start gap-4">
            <div className="text-accent mt-1">
                <span className="material-symbols-outlined text-3xl font-bold">warning</span>
            </div>
            <div className="flex-1">
                <h3 className="text-accent text-lg font-bold leading-tight">{alert.title}</h3>
                <p className="text-[#4a3535] text-sm mt-1 leading-relaxed">{alert.message}</p>
                <div className="mt-3 flex items-center gap-4">
                    <a
                        className="text-accent font-bold text-sm underline underline-offset-4 hover:opacity-80 transition-opacity"
                        href="#"
                    >
                        View Mitigation Plan
                    </a>
                    <span className="text-[#4a3535]/60 text-xs font-medium italic">
                        Impact Probability: {alert.impactProbability}%
                    </span>
                </div>
            </div>
        </div>
    );
};

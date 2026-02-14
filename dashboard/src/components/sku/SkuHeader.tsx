import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

interface SkuHeaderProps {
    sku?: string;
}

export const SkuHeader: React.FC<SkuHeaderProps> = ({ sku: skuProp }) => {
    const data = skuDetailData;
    const sku = skuProp ?? data.sku;
    return (
        <>
            <nav className="flex flex-wrap gap-2 mb-4 items-center">
                <a className="text-primary/70 text-sm font-medium hover:text-primary transition-colors" href="/">
                    Dashboard
                </a>
                <span className="material-symbols-outlined text-xs text-primary/40">chevron_right</span>
                <a className="text-primary/70 text-sm font-medium hover:text-primary transition-colors" href="/inventory/health">
                    Inventory
                </a>
                <span className="material-symbols-outlined text-xs text-primary/40">chevron_right</span>
                <a className="text-primary/70 text-sm font-medium hover:text-primary transition-colors" href="/inventory/health">
                    {data.category}
                </a>
                <span className="material-symbols-outlined text-xs text-primary/40">chevron_right</span>
                <span className="text-[#131616] dark:text-white text-sm font-semibold">SKU: {sku}</span>
            </nav>

            <div className="bg-primary rounded-xl p-8 mb-8 text-white shadow-lg flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                <div className="flex flex-col gap-2">
                    <div className="flex items-center gap-3 flex-wrap">
                        <h1 className="text-3xl sm:text-4xl font-black tracking-tight">
                            SKU: {sku}
                        </h1>
                        <span className="bg-white/20 text-white text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider">
                            {data.status}
                        </span>
                    </div>
                    <p className="text-white/80 text-base font-medium">
                        Internal ID: {sku} • Last Restocked: {data.lastRestocked}
                    </p>
                </div>
                <div className="flex gap-3">
                    <button className="flex items-center gap-2 px-5 py-2.5 bg-white/10 hover:bg-white/20 border border-white/30 rounded-lg text-white text-sm font-bold transition-all backdrop-blur-sm">
                        <span className="material-symbols-outlined text-lg">edit_note</span>
                        <span>Edit Detail</span>
                    </button>
                    <button className="flex items-center gap-2 px-6 py-2.5 bg-white text-primary hover:bg-cream rounded-lg text-sm font-bold transition-all shadow-md">
                        <span className="material-symbols-outlined text-lg">trending_up</span>
                        <span>Adjust Forecast</span>
                    </button>
                </div>
            </div>
        </>
    );
};

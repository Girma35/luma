import React, { useEffect, useState } from "react";
import { getInventoryItem, type InventoryItem } from "../../lib/api";
import { SkuDetailFromApi } from "./SkuDetailFromApi";

export const SkuPageContent: React.FC<{ id: string }> = ({ id }) => {
    const [item, setItem] = useState<InventoryItem | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        if (!id) {
            setLoading(false);
            setError(true);
            return;
        }
        getInventoryItem(id).then((data) => {
            setItem(data ?? null);
            setError(!data);
            setLoading(false);
        });
    }, [id]);

    if (loading) {
        return (
            <div className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full px-4 sm:px-10 py-6">
                <div className="bg-slate-50 rounded-xl p-12 text-center text-slate-500 font-medium">
                    Loading SKU…
                </div>
            </div>
        );
    }

    if (error || !item) {
        return (
            <div className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full px-4 sm:px-10 py-6">
                <div className="bg-accent/10 border border-accent rounded-xl p-8 text-center">
                    <p className="font-bold text-accent mb-2">SKU not found</p>
                    <p className="text-slate-600 text-sm mb-4">The item may have been removed or the ID is invalid.</p>
                    <a href="/inventory" className="inline-flex items-center gap-2 bg-black text-white px-6 py-2.5 rounded text-sm font-bold hover:bg-slate-800">
                        Back to Inventory
                    </a>
                </div>
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col max-w-[1200px] mx-auto w-full px-4 sm:px-10 py-6 space-y-8">
            <SkuDetailFromApi item={item} />
        </div>
    );
};

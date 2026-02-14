import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

export const SupplierInfo: React.FC = () => {
    const { supplier } = skuDetailData;

    return (
        <div className="lg:col-span-2 bg-cream rounded-xl border border-primary/10 p-6 flex flex-col gap-6 shadow-sm">
            <div className="flex items-center gap-2 border-b border-primary/10 pb-4">
                <span className="material-symbols-outlined text-primary">factory</span>
                <h3 className="text-lg font-bold">Supplier Information</h3>
            </div>
            <div className="flex flex-col gap-5">
                <div className="flex items-center gap-4">
                    <div className="size-12 rounded-lg bg-primary/5 flex items-center justify-center text-primary font-bold text-xl">
                        {supplier.initials}
                    </div>
                    <div>
                        <p className="font-bold text-[#131616]">{supplier.name}</p>
                        <p className="text-sm text-[#6a7b7c]">{supplier.location}</p>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4 py-4 border-y border-primary/5">
                    <div>
                        <p className="text-xs font-semibold text-[#6a7b7c] uppercase">Reliability</p>
                        <div className="flex items-center gap-1 mt-1">
                            <span className="material-symbols-outlined text-primary text-base">star</span>
                            <span className="text-sm font-bold">{supplier.reliability} / 5.0</span>
                        </div>
                    </div>
                    <div>
                        <p className="text-xs font-semibold text-[#6a7b7c] uppercase">Contact</p>
                        <p className="text-sm font-bold mt-1 text-primary underline cursor-pointer">
                            {supplier.contact}
                        </p>
                    </div>
                </div>
                <div className="flex flex-col gap-3">
                    <p className="text-sm font-semibold">Active Purchase Orders</p>
                    {supplier.purchaseOrders.map((po) => (
                        <div
                            key={po.id}
                            className="flex justify-between items-center p-3 bg-primary/5 rounded-lg"
                        >
                            <span className="text-sm font-medium">{po.id}</span>
                            <span
                                className={`text-xs font-bold ${po.status === "In Transit" ? "text-primary" : "text-[#6a7b7c]"
                                    }`}
                            >
                                {po.status}
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

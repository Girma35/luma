import React from "react";
import { skuDetailData } from "../../data/skuDetailData";

export const TopNav: React.FC = () => {
    const data = skuDetailData;
    return (
        <header className="flex items-center justify-between whitespace-nowrap border-b border-primary/20 bg-cream/80 backdrop-blur-sm px-6 md:px-10 py-3 sticky top-0 z-50">
            <div className="flex items-center gap-8">
                <div className="flex items-center gap-3 text-primary">
                    <div className="size-6">
                        <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                            <path
                                clipRule="evenodd"
                                d="M12.0799 24L4 19.2479L9.95537 8.75216L18.04 13.4961L18.0446 4H29.9554L29.96 13.4961L38.0446 8.75216L44 19.2479L35.92 24L44 28.7521L38.0446 39.2479L29.96 34.5039L29.9554 44H18.0446L18.04 34.5039L9.95537 39.2479L4 28.7521L12.0799 24Z"
                                fill="currentColor"
                                fillRule="evenodd"
                            />
                        </svg>
                    </div>
                    <h2 className="text-[#131616] text-lg font-bold leading-tight tracking-tight">
                        ReOrder AI
                    </h2>
                </div>
                <nav className="hidden md:flex items-center gap-9">
                    <a
                        className="text-[#6a7b7c] text-sm font-medium leading-normal hover:text-primary transition-colors"
                        href="/"
                    >
                        Dashboard
                    </a>
                    <a
                        className="text-primary text-sm font-semibold leading-normal border-b-2 border-primary pb-1"
                        href="/inventory/health"
                    >
                        Inventory
                    </a>
                    <a
                        className="text-[#6a7b7c] text-sm font-medium leading-normal hover:text-primary transition-colors"
                        href="/inventory/buying"
                    >
                        Orders
                    </a>
                    <a
                        className="text-[#6a7b7c] text-sm font-medium leading-normal hover:text-primary transition-colors"
                        href="/suppliers"
                    >
                        Suppliers
                    </a>
                    <a
                        className="text-[#6a7b7c] text-sm font-medium leading-normal hover:text-primary transition-colors"
                        href="/forecasts"
                    >
                        Analytics
                    </a>
                </nav>
            </div>
            <div className="flex flex-1 justify-end gap-4 items-center">
                <label className="hidden sm:flex flex-col min-w-40 !h-9 max-w-64">
                    <div className="flex w-full flex-1 items-stretch rounded-lg h-full">
                        <div className="text-[#6a7b7c] flex border-none bg-primary/10 items-center justify-center pl-3 rounded-l-lg">
                            <span className="material-symbols-outlined text-sm">search</span>
                        </div>
                        <input
                            className="flex w-full min-w-0 flex-1 resize-none overflow-hidden rounded-lg text-[#131616] focus:outline-0 focus:ring-0 border-none bg-primary/10 h-full placeholder:text-[#6a7b7c] px-3 rounded-l-none pl-2 text-sm font-normal"
                            placeholder="Quick Search SKU..."
                        />
                    </div>
                </label>
                <div className="bg-primary/20 p-1 rounded-full text-primary cursor-pointer hover:bg-primary/30 transition-colors">
                    <span className="material-symbols-outlined block">notifications</span>
                </div>
                <div
                    className="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9 border-2 border-primary/20"
                    style={{ backgroundImage: `url('${data.avatarUrl}')` }}
                />
            </div>
        </header>
    );
};

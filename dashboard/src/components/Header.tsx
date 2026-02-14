import React from 'react';
import { dashboardData } from '../data/mockData';

export const Header: React.FC = () => {
    const { user } = dashboardData;
    return (
        <header className="h-16 bg-white dark:bg-background-dark/80 backdrop-blur-md border-b border-[#e2e8f0] px-8 flex items-center justify-between sticky top-0 z-10">
            <div className="flex items-center gap-6 flex-1">
                <h2 className="text-xl font-black tracking-tighter text-black uppercase">Dashboard</h2>
                <div className="relative w-full max-w-md">
                    <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">search</span>
                    <input
                        className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 rounded pl-10 pr-4 py-1.5 focus:ring-1 focus:ring-black text-xs font-medium placeholder:text-slate-400"
                        placeholder="Search system..."
                        type="text"
                    />
                </div>
            </div>
            <div className="flex items-center gap-4">
                <button className="size-8 flex items-center justify-center rounded text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5">
                    <span className="material-symbols-outlined text-[20px]">notifications</span>
                </button>
                <div className="h-6 w-px bg-slate-200"></div>
                <div className="flex items-center gap-3 pl-2">
                    <div className="text-right">
                        <p className="text-sm font-bold text-black">{user.name}</p>
                        <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">{user.role}</p>
                    </div>
                    <div
                        className="size-9 rounded-full bg-center bg-cover border border-slate-200"
                        style={{ backgroundImage: `url('${user.avatarUrl}')` }}
                        aria-label={user.name}
                    ></div>
                </div>
            </div>
        </header>
    );
};

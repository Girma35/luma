import React from 'react';

const NAV = [
  { href: '/dashboard', label: 'Dashboard', icon: 'dashboard' },
  { href: '/connect', label: 'Connect store', icon: 'link' },
  { href: '/inventory/health', label: 'Inventory', icon: 'inventory_2' },
  { href: '/inventory/buying', label: 'Orders', icon: 'shopping_cart' },
  { href: '/forecasts', label: 'Analytics', icon: 'monitoring' },
  { href: '/simulator', label: 'Simulator', icon: 'query_stats' },
  { href: '/suppliers', label: 'Suppliers', icon: 'group' },
] as const;

interface SidebarProps {
  currentPath?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPath = '/' }) => {
  return (
    <aside className="w-64 bg-white dark:bg-background-dark border-r border-[#e2e8f0] dark:border-white/10 flex flex-col justify-between py-6">
      <div>
        <div className="px-6 mb-10 flex items-center gap-3">
          <div className="size-10 rounded-lg bg-black flex items-center justify-center text-white">
            <span className="material-symbols-outlined">analytics</span>
          </div>
          <div>
            <h1 className="text-black dark:text-white font-black text-xl leading-tight tracking-tighter">REORDER AI</h1>
            <p className="text-slate-500 text-[9px] uppercase font-bold tracking-[0.2em]">Intelligence Suite</p>
          </div>
        </div>
        <nav className="space-y-1">
          {NAV.map(({ href, label, icon }) => {
            const isActive = currentPath === href || (href !== '/' && currentPath.startsWith(href));
            return (
              <a
                key={href}
                className={`flex items-center gap-3 px-6 py-3 font-semibold border-r-4 transition-colors ${
                  isActive
                    ? 'text-black dark:text-white border-black bg-slate-50 dark:bg-white/10'
                    : 'text-slate-500 hover:bg-slate-50 dark:hover:bg-white/5 hover:text-black dark:hover:text-white border-transparent'
                }`}
                href={href}
              >
                <span className="material-symbols-outlined text-[20px]">{icon}</span>
                <span>{label}</span>
              </a>
            );
          })}
        </nav>
      </div>
      <div className="px-6">
        <a href="/inventory/buying" className="block w-full bg-black hover:bg-slate-800 text-white font-bold py-2.5 rounded text-xs uppercase tracking-widest transition-all shadow-sm text-center">
          New Report
        </a>
      </div>
    </aside>
  );
};

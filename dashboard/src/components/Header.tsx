import React from 'react';
import { useSession, signOut } from '../lib/auth-client';

export const Header: React.FC = () => {
  const { data: session, isPending } = useSession();

  const user = session?.user;
  const name = user?.name ?? user?.email ?? "User";
  const role = "Dashboard";

  return (
    <header className="h-16 bg-white dark:bg-background-dark/80 backdrop-blur-md border-b border-[#e2e8f0] dark:border-white/10 px-8 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-6 flex-1">
        <h2 className="text-xl font-black tracking-tighter text-black dark:text-white uppercase">Dashboard</h2>
        <div className="relative w-full max-w-md">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-lg">search</span>
          <input
            className="w-full bg-slate-50 dark:bg-white/5 border border-slate-200 dark:border-white/10 rounded pl-10 pr-4 py-1.5 focus:ring-1 focus:ring-black dark:focus:ring-white text-xs font-medium placeholder:text-slate-400 text-black dark:text-white"
            placeholder="Search system..."
            type="text"
          />
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="size-8 flex items-center justify-center rounded text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5" type="button" aria-label="Notifications">
          <span className="material-symbols-outlined text-[20px]">notifications</span>
        </button>
        <div className="h-6 w-px bg-slate-200 dark:bg-white/10" />
        <div className="flex items-center gap-3 pl-2">
          {!isPending && (
            <>
              <div className="text-right">
                <p className="text-sm font-bold text-black dark:text-white">{name}</p>
                <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">{role}</p>
              </div>
              {user?.image ? (
                <img
                  src={user.image}
                  alt=""
                  className="size-9 rounded-full bg-slate-100 dark:bg-white/10 border border-slate-200 dark:border-white/10 object-cover"
                />
              ) : (
                <div
                  className="size-9 rounded-full bg-black dark:bg-white text-white dark:text-black flex items-center justify-center text-sm font-black"
                  aria-hidden
                >
                  {name.charAt(0).toUpperCase()}
                </div>
              )}
              <button
                type="button"
                onClick={async () => {
                  await signOut();
                  window.location.href = "/login";
                }}
                className="text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-accent transition-colors"
              >
                Sign out
              </button>
            </>
          )}
        </div>
      </div>
    </header>
  );
};

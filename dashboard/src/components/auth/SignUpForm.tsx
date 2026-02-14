import React, { useState } from "react";
import { signUp } from "../../lib/auth-client";

export const SignUpForm: React.FC = () => {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await signUp.email({
        name,
        email,
        password,
        callbackURL: "/",
      });
      if (result.error) {
        setError(result.error.message ?? "Sign up failed");
        setLoading(false);
        return;
      }
      window.location.href = result.data?.url ?? "/";
    } catch (err) {
      setError(err instanceof Error ? err.message : "Sign up failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="p-3 rounded-lg bg-accent/10 border border-accent text-accent text-sm font-medium">
          {error}
        </div>
      )}
      <div>
        <label htmlFor="name" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Name
        </label>
        <input
          id="name"
          type="text"
          autoComplete="name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
          placeholder="Your name"
        />
      </div>
      <div>
        <label htmlFor="email" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Email
        </label>
        <input
          id="email"
          type="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
          placeholder="you@company.com"
        />
      </div>
      <div>
        <label htmlFor="password" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Password
        </label>
        <input
          id="password"
          type="password"
          autoComplete="new-password"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
          placeholder="•••••••• (min 8 characters)"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-black dark:bg-white text-white dark:text-black font-black text-sm uppercase tracking-widest rounded-lg hover:bg-slate-800 dark:hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? "Creating account…" : "Create account"}
      </button>
    </form>
  );
};

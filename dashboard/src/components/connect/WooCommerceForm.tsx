import React, { useState } from "react";

export const WooCommerceForm: React.FC = () => {
  const [siteUrl, setSiteUrl] = useState("");
  const [consumerKey, setConsumerKey] = useState("");
  const [consumerSecret, setConsumerSecret] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await fetch("/api/connect/woocommerce", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          siteUrl: siteUrl.trim().replace(/\/$/, ""),
          consumerKey: consumerKey.trim(),
          consumerSecret: consumerSecret.trim(),
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        setError((data.error as string) || "Connection failed");
        setLoading(false);
        return;
      }
      window.location.href = (data.redirect as string) || "/";
    } catch {
      setError("Network error. Try again.");
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
        <label htmlFor="siteUrl" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Store URL
        </label>
        <input
          id="siteUrl"
          type="url"
          required
          value={siteUrl}
          onChange={(e) => setSiteUrl(e.target.value)}
          placeholder="https://yourstore.com"
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
        />
      </div>
      <div>
        <label htmlFor="consumerKey" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Consumer key
        </label>
        <input
          id="consumerKey"
          type="text"
          required
          value={consumerKey}
          onChange={(e) => setConsumerKey(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
        />
      </div>
      <div>
        <label htmlFor="consumerSecret" className="block text-[10px] font-black uppercase tracking-widest text-slate-500 dark:text-slate-400 mb-2">
          Consumer secret
        </label>
        <input
          id="consumerSecret"
          type="password"
          required
          value={consumerSecret}
          onChange={(e) => setConsumerSecret(e.target.value)}
          className="w-full px-4 py-3 rounded-lg border border-slate-200 dark:border-white/20 bg-white dark:bg-white/5 text-black dark:text-white text-sm font-medium focus:ring-2 focus:ring-black dark:focus:ring-white outline-none"
        />
      </div>
      <button
        type="submit"
        disabled={loading}
        className="w-full py-3 bg-purple-600 hover:bg-purple-700 text-white font-black text-sm uppercase tracking-widest rounded-lg transition-colors disabled:opacity-50"
      >
        {loading ? "Connecting…" : "Connect store"}
      </button>
    </form>
  );
};

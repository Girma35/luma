import { useState } from 'react';
import { syncShopify, syncWooCommerce } from '../lib/api';

interface Props {
  open: boolean;
  onClose: () => void;
}

type Platform = 'shopify' | 'woocommerce';

export default function ConnectStoreModal({ open, onClose }: Props) {
  const [platform, setPlatform] = useState<Platform>('shopify');
  const [shopUrl, setShopUrl] = useState('');
  const [accessToken, setAccessToken] = useState('');
  const [consumerKey, setConsumerKey] = useState('');
  const [consumerSecret, setConsumerSecret] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'ok' | 'err'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);
    try {
      if (platform === 'shopify') {
        const r = await syncShopify();
        setMessage({ type: 'ok', text: r.message });
      } else {
        const r = await syncWooCommerce();
        setMessage({ type: 'ok', text: r.message });
      }
      setTimeout(onClose, 1500);
    } catch (err) {
      setMessage({ type: 'err', text: err instanceof Error ? err.message : 'Sync failed' });
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[#0d0d1a] border border-white/10 rounded-2xl shadow-2xl max-w-md w-full p-8" onClick={(e) => e.stopPropagation()}>
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold">Connect Store</h2>
          <button type="button" onClick={onClose} className="text-white/50 hover:text-white text-2xl leading-none">&times;</button>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white/70 mb-2">Platform</label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value as Platform)}
              className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white focus:border-purple-500 outline-none"
            >
              <option value="shopify">Shopify</option>
              <option value="woocommerce">WooCommerce</option>
            </select>
          </div>
          {platform === 'shopify' && (
            <>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Shop URL</label>
                <input
                  type="url"
                  value={shopUrl}
                  onChange={(e) => setShopUrl(e.target.value)}
                  placeholder="https://your-store.myshopify.com"
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:border-purple-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Admin API access token</label>
                <input
                  type="password"
                  value={accessToken}
                  onChange={(e) => setAccessToken(e.target.value)}
                  placeholder="shpat_..."
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:border-purple-500 outline-none"
                />
              </div>
            </>
          )}
          {platform === 'woocommerce' && (
            <>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Site URL</label>
                <input
                  type="url"
                  value={shopUrl}
                  onChange={(e) => setShopUrl(e.target.value)}
                  placeholder="https://yoursite.com"
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white placeholder-white/30 focus:border-purple-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Consumer key</label>
                <input
                  type="text"
                  value={consumerKey}
                  onChange={(e) => setConsumerKey(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white focus:border-purple-500 outline-none"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/70 mb-2">Consumer secret</label>
                <input
                  type="password"
                  value={consumerSecret}
                  onChange={(e) => setConsumerSecret(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl bg-white/5 border border-white/10 text-white focus:border-purple-500 outline-none"
                />
              </div>
            </>
          )}
          {message && (
            <p className={message.type === 'ok' ? 'text-emerald-400 text-sm' : 'text-red-400 text-sm'}>{message.text}</p>
          )}
          <div className="flex gap-3 pt-2">
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-purple-600 text-white py-2.5 rounded-xl font-bold hover:bg-purple-500 disabled:opacity-50"
            >
              {loading ? 'Syncing…' : 'Sync now'}
            </button>
            <button type="button" onClick={onClose} className="px-6 py-2.5 rounded-xl border border-white/10 hover:bg-white/5">
              Cancel
            </button>
          </div>
        </form>
        <p className="text-white/40 text-xs mt-4">Credentials are not stored on our servers. Sync runs with demo data until you connect a real store.</p>
      </div>
    </div>
  );
}

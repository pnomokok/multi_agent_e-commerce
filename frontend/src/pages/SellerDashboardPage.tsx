import { useState } from 'react'
import { MOCK_SELLER } from '@/data/mockData'
import { formatPrice } from '@/utils/format'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  LineChart, Line, Legend,
} from 'recharts'

const weeklyData = [
  { day: 'Pzt', negotiations: 4, saved: 3, discount: 520 },
  { day: 'Sal', negotiations: 6, saved: 5, discount: 780 },
  { day: 'Çar', negotiations: 3, saved: 2, discount: 310 },
  { day: 'Per', negotiations: 8, saved: 7, discount: 1050 },
  { day: 'Cum', negotiations: 11, saved: 9, discount: 1420 },
  { day: 'Cmt', negotiations: 7, saved: 6, discount: 890 },
  { day: 'Paz', negotiations: 5, saved: 4, discount: 670 },
]

const recentLogs = [
  { time: '16:42:01', agent: 'Orkestratör', action: 'intent_detection', result: 'price_objection (0.94)', type: 'route' },
  { time: '16:42:01', agent: 'Orkestratör', action: 'ROUTE → Pazarlık Ajanı', result: '', type: 'route' },
  { time: '16:42:01', agent: 'Pazarlık Ajanı', action: 'get_product_data', result: '{ base_price: 950, margin: 0.18, stock: 47 }', type: 'data' },
  { time: '16:42:02', agent: 'Pazarlık Ajanı', action: 'get_customer_segment', result: '"new"', type: 'data' },
  { time: '16:42:02', agent: 'Pazarlık Ajanı', action: 'karar', result: 'indirim 150 TL + hediye kılıf', type: 'decision' },
  { time: '16:42:03', agent: 'Pazarlık Ajanı', action: 'response_ready → Eko', result: '', type: 'route' },
]

const logColors: Record<string, string> = {
  route: 'text-trust-blue',
  data: 'text-eco-green',
  decision: 'text-negotiation-gold',
}

interface PolicyState {
  max_discount_pct: number
  monthly_budget: number
  min_margin: number
  negotiation_enabled: boolean
  preferred_concessions: string[]
}

export default function SellerDashboardPage() {
  const seller = MOCK_SELLER
  const [policy, setPolicy] = useState<PolicyState>({
    max_discount_pct: 15,
    monthly_budget: 15000,
    min_margin: 15,
    negotiation_enabled: true,
    preferred_concessions: ['discount', 'gift'],
  })
  const [saved, setSaved] = useState(false)
  const budgetUsedPct = Math.round((seller.monthly_negotiation_spent / seller.monthly_negotiation_budget) * 100)

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const toggleConcession = (c: string) => {
    setPolicy((p) => ({
      ...p,
      preferred_concessions: p.preferred_concessions.includes(c)
        ? p.preferred_concessions.filter((x) => x !== c)
        : [...p.preferred_concessions, c],
    }))
  }

  return (
    <div className="min-h-screen bg-surface-bg font-sans">
      {/* Seller-specific header */}
      <header className="bg-on-background text-inverse-on-surface border-b border-on-surface/10 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="font-display text-xl font-bold text-primary-fixed-dim">Eko</span>
            <span className="text-on-surface/40">|</span>
            <span className="text-sm text-inverse-on-surface/70">Satıcı Paneli</span>
            <span className="text-sm font-semibold text-inverse-on-surface">{seller.name}</span>
          </div>

          {/* Eco Seller Badge */}
          {seller.eco_seller_badge && (
            <div className="flex items-center gap-2 bg-primary/20 border border-primary/40 px-3 py-1 rounded-full">
              <span className="material-symbols-outlined text-primary-fixed-dim text-sm"
                style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
              <span className="text-xs font-bold text-primary-fixed-dim uppercase tracking-wide font-mono">Eko Satıcı</span>
            </div>
          )}

          <div className="flex items-center gap-2 text-sm text-inverse-on-surface/60">
            <span className="w-2 h-2 bg-eco-green rounded-full animate-pulse" />
            Sistemler Aktif
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">

        {/* KPI Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              label: 'Bu Hafta Kapatılan Pazarlık',
              value: seller.weekly_negotiations_closed,
              unit: 'adet',
              icon: 'handshake',
              color: 'text-trust-blue',
              bg: 'bg-trust-blue/10',
            },
            {
              label: 'Verilen Toplam İndirim',
              value: formatPrice(seller.weekly_discount_given),
              unit: '',
              icon: 'local_offer',
              color: 'text-negotiation-gold',
              bg: 'bg-negotiation-gold/10',
            },
            {
              label: 'Kurtarılan Tahmini Sipariş',
              value: seller.estimated_saved_orders,
              unit: 'sipariş',
              icon: 'shopping_bag',
              color: 'text-eco-green',
              bg: 'bg-eco-green/10',
            },
            {
              label: 'Net ROI',
              value: `${seller.net_roi}x`,
              unit: '',
              icon: 'trending_up',
              color: 'text-primary',
              bg: 'bg-primary/10',
            },
          ].map((kpi) => (
            <div key={kpi.label} className="bg-surface-card rounded-xl border border-outline-variant p-4">
              <div className={`w-10 h-10 ${kpi.bg} rounded-lg flex items-center justify-center mb-3`}>
                <span className={`material-symbols-outlined ${kpi.color} text-xl`}
                  style={{ fontVariationSettings: "'FILL' 1" }}>{kpi.icon}</span>
              </div>
              <p className="text-xs text-text-secondary mb-1">{kpi.label}</p>
              <p className="font-display text-2xl font-bold text-text-primary">
                {kpi.value}<span className="text-sm font-normal text-text-secondary ml-1">{kpi.unit}</span>
              </p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left column — Charts + Logs */}
          <div className="lg:col-span-2 space-y-6">
            {/* Weekly negotiations chart */}
            <div className="bg-surface-card rounded-xl border border-outline-variant p-5">
              <h2 className="font-display text-base font-semibold text-text-primary mb-4">
                Haftalık Pazarlık & Dönüşüm
              </h2>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={weeklyData} barGap={4}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#bbcabf" />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(v, n) => [v, n === 'negotiations' ? 'Toplam' : 'Kazanılan']} />
                  <Legend formatter={(v) => v === 'negotiations' ? 'Pazarlık' : 'Dönüşüm'} />
                  <Bar dataKey="negotiations" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="saved" fill="#10b981" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            {/* Discount trend */}
            <div className="bg-surface-card rounded-xl border border-outline-variant p-5">
              <h2 className="font-display text-base font-semibold text-text-primary mb-4">
                Günlük İndirim Harcaması (TL)
              </h2>
              <ResponsiveContainer width="100%" height={160}>
                <LineChart data={weeklyData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#bbcabf" />
                  <XAxis dataKey="day" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(v) => [`${v} TL`]} />
                  <Line type="monotone" dataKey="discount" stroke="#006c49" strokeWidth={2} dot={{ r: 4, fill: '#006c49' }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Live agent log panel */}
            <div className="bg-inverse-surface rounded-xl border border-on-surface/10 p-5">
              <div className="flex items-center justify-between mb-3">
                <h2 className="font-display text-base font-semibold text-inverse-on-surface">
                  Canlı Ajan Log Paneli
                </h2>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 bg-eco-green rounded-full animate-pulse" />
                  <span className="text-xs text-inverse-on-surface/60 font-mono">CANLI</span>
                </div>
              </div>
              <div className="space-y-2 font-mono text-xs max-h-52 overflow-y-auto">
                {recentLogs.map((log, i) => (
                  <div key={i} className="flex gap-3 items-start">
                    <span className="text-inverse-on-surface/40 flex-shrink-0">[{log.time}]</span>
                    <span className={`font-semibold flex-shrink-0 ${logColors[log.type]}`}>{log.agent}</span>
                    <span className="text-inverse-on-surface/70">→ {log.action}</span>
                    {log.result && (
                      <span className="text-inverse-on-surface/50 truncate">{log.result}</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right column — Policy Editor */}
          <div className="space-y-4">
            {/* Budget progress */}
            <div className="bg-surface-card rounded-xl border border-outline-variant p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-text-primary">Aylık Pazarlık Bütçesi</h3>
                <span className="text-xs text-text-secondary font-mono">{budgetUsedPct}% kullanıldı</span>
              </div>
              <div className="w-full bg-surface-container rounded-full h-2.5 mb-2">
                <div
                  className="h-2.5 rounded-full bg-gradient-to-r from-eco-green to-primary transition-all"
                  style={{ width: `${budgetUsedPct}%` }}
                />
              </div>
              <div className="flex justify-between text-xs text-text-secondary">
                <span>{formatPrice(seller.monthly_negotiation_spent)} harcandı</span>
                <span>{formatPrice(seller.monthly_negotiation_budget)} toplam</span>
              </div>
            </div>

            {/* CO₂ stat */}
            <div className="bg-surface-bright border border-eco-green/30 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="material-symbols-outlined text-eco-green text-lg"
                  style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
                <span className="text-sm font-semibold text-primary">Karbon Tasarrufu</span>
              </div>
              <p className="font-display text-3xl font-bold text-eco-green">
                {seller.total_co2_saved_kg.toLocaleString('tr-TR')} <span className="text-base font-normal text-text-secondary">kg CO₂</span>
              </p>
              <p className="text-xs text-text-secondary mt-1">≈ {Math.round(seller.total_co2_saved_kg / 21)} ağaç-yıl karbon emilimi</p>
            </div>

            {/* Policy Editor */}
            <div className="bg-surface-card rounded-xl border border-outline-variant p-4">
              <h3 className="font-display text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
                <span className="material-symbols-outlined text-base text-on-surface-variant">tune</span>
                Pazarlık Politikası
              </h3>

              <div className="space-y-4">
                {/* Negotiation toggle */}
                <div className="flex items-center justify-between">
                  <span className="text-sm text-text-primary">Pazarlık Aktif</span>
                  <button
                    onClick={() => setPolicy((p) => ({ ...p, negotiation_enabled: !p.negotiation_enabled }))}
                    className={`w-11 h-6 rounded-full transition-colors relative ${
                      policy.negotiation_enabled ? 'bg-primary' : 'bg-outline'
                    }`}
                  >
                    <span className={`absolute top-0.5 w-5 h-5 bg-white rounded-full shadow transition-all ${
                      policy.negotiation_enabled ? 'left-5' : 'left-0.5'
                    }`} />
                  </button>
                </div>

                {/* Max discount */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-primary">Maks. İndirim</span>
                    <span className="font-semibold text-primary">{policy.max_discount_pct}%</span>
                  </div>
                  <input
                    type="range"
                    min={5} max={30} step={1}
                    value={policy.max_discount_pct}
                    onChange={(e) => setPolicy((p) => ({ ...p, max_discount_pct: +e.target.value }))}
                    className="w-full accent-primary"
                  />
                  <div className="flex justify-between text-xs text-text-secondary mt-0.5">
                    <span>5%</span><span>30%</span>
                  </div>
                </div>

                {/* Min margin */}
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-text-primary">Min. Kar Marjı</span>
                    <span className="font-semibold text-primary">{policy.min_margin}%</span>
                  </div>
                  <input
                    type="range"
                    min={5} max={40} step={1}
                    value={policy.min_margin}
                    onChange={(e) => setPolicy((p) => ({ ...p, min_margin: +e.target.value }))}
                    className="w-full accent-primary"
                  />
                </div>

                {/* Preferred concessions */}
                <div>
                  <p className="text-sm text-text-primary mb-2">Tercih Edilen Ödün Türleri</p>
                  <div className="flex flex-wrap gap-2">
                    {[
                      { key: 'discount', label: 'İndirim', icon: 'percent' },
                      { key: 'gift', label: 'Hediye', icon: 'redeem' },
                      { key: 'bundle', label: 'Bundle', icon: 'inventory_2' },
                      { key: 'shipping', label: 'Kargo', icon: 'local_shipping' },
                    ].map(({ key, label, icon }) => (
                      <button
                        key={key}
                        onClick={() => toggleConcession(key)}
                        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                          policy.preferred_concessions.includes(key)
                            ? 'bg-primary text-on-primary border-primary'
                            : 'bg-surface-bg text-text-secondary border-outline-variant hover:border-primary'
                        }`}
                      >
                        <span className="material-symbols-outlined text-xs">{icon}</span>
                        {label}
                      </button>
                    ))}
                  </div>
                </div>

                <button
                  onClick={handleSave}
                  className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center gap-1.5 ${
                    saved
                      ? 'bg-eco-green text-white'
                      : 'bg-primary text-on-primary hover:bg-on-primary-container'
                  }`}
                >
                  <span className="material-symbols-outlined text-base">
                    {saved ? 'check' : 'save'}
                  </span>
                  {saved ? 'Kaydedildi!' : 'Politikayı Kaydet'}
                </button>
              </div>
            </div>

            {/* Pause button */}
            <button className="w-full py-2.5 rounded-xl text-sm font-semibold border-2 border-danger-red text-danger-red hover:bg-danger-red hover:text-white transition-colors flex items-center justify-center gap-2">
              <span className="material-symbols-outlined text-base">pause_circle</span>
              Pazarlık Modunu Duraklat
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}

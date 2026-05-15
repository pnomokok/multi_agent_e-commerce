import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '@/components/shared/Header'
import ProductCard from '@/components/customer/ProductCard'
import { MOCK_PRODUCTS, CATEGORIES } from '@/data/mockData'

export default function CustomerPage() {
  const [activeCategory, setActiveCategory] = useState('Tümü')
  const navigate = useNavigate()

  const filtered = activeCategory === 'Tümü'
    ? MOCK_PRODUCTS
    : MOCK_PRODUCTS.filter((p) => p.category === activeCategory)

  return (
    <div className="min-h-screen bg-surface-bg">
      <Header />

      <main className="max-w-7xl mx-auto px-4 md:px-10 pb-16">
        {/* Category chips */}
        <div className="flex items-center gap-2 py-4 overflow-x-auto scrollbar-hide">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`flex-shrink-0 flex items-center gap-1.5 px-4 py-1.5 rounded-full border text-sm font-medium transition-colors ${
                activeCategory === cat
                  ? 'bg-primary text-on-primary border-primary'
                  : 'bg-surface-card text-on-surface-variant border-outline-variant hover:border-primary hover:text-primary'
              }`}
            >
              <span className="material-symbols-outlined text-base">
                {cat === 'Tümü' ? 'apps' : cat === 'Elektronik' ? 'devices' : cat === 'Giyim' ? 'checkroom' : cat === 'Ev' ? 'home' : 'menu_book'}
              </span>
              {cat}
            </button>
          ))}
        </div>

        {/* Hero banner */}
        <div className="relative rounded-2xl overflow-hidden mb-8 bg-gradient-to-br from-primary to-eco-green">
          <div className="px-8 py-10 md:py-14 md:px-14 max-w-xl relative z-10">
            <span className="inline-flex items-center gap-1.5 bg-white/20 text-white text-xs font-bold uppercase tracking-wider px-3 py-1 rounded-full mb-4 backdrop-blur-sm border border-white/30">
              <span className="material-symbols-outlined text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
              Yeni Nesil Alışveriş
            </span>
            <h1 className="font-display text-3xl md:text-4xl font-bold text-white leading-tight mb-3">
              Eko ile Tanışın: Hem Cüzdana Hem Dünyaya İyi Gelen Alışveriş
            </h1>
            <p className="text-white/80 text-sm md:text-base mb-6">
              Pazarlık yapın, en iyi fiyatı bulun ve her alışverişinizde karbon izinizi azaltın.
            </p>
            <button
              onClick={() => navigate('/cart')}
              className="inline-flex items-center gap-2 bg-white text-primary font-semibold px-6 py-3 rounded-full hover:bg-surface-container-low transition-colors shadow-lg"
            >
              <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
              Keşfetmeye Başla
            </button>
          </div>
          {/* Decorative circles */}
          <div className="absolute right-0 top-0 w-64 h-64 bg-white/10 rounded-full -translate-y-1/3 translate-x-1/4" />
          <div className="absolute right-20 bottom-0 w-32 h-32 bg-white/10 rounded-full translate-y-1/3" />
        </div>

        {/* Products */}
        <div className="flex items-center justify-between mb-4">
          <h2 className="font-display text-xl font-semibold text-text-primary">
            {activeCategory === 'Tümü' ? 'Sizin İçin Seçtiklerimiz' : activeCategory}
          </h2>
          <span className="text-sm text-text-secondary">{filtered.length} ürün</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {filtered.map((product) => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </main>
    </div>
  )
}

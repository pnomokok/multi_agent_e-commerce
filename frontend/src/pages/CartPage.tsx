import { useNavigate } from 'react-router-dom'
import Header from '@/components/shared/Header'
import EkoChat from '@/components/customer/EkoChat'
import { useCartStore } from '@/store/cartStore'
import { formatPrice } from '@/utils/format'

export default function CartPage() {
  const navigate = useNavigate()
  const { items, updateQty, removeItem, total } = useCartStore()
  const cartTotal = total()
  const shipping = cartTotal > 0 ? 49 : 0

  return (
    <div className="min-h-screen bg-surface-bg">
      <Header showSearch={false} />

      <main className="max-w-6xl mx-auto px-4 md:px-10 py-8 pb-24">
        <h1 className="font-display text-2xl font-bold text-text-primary mb-6">Sepetim</h1>

        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 gap-4">
            <div className="w-20 h-20 rounded-full bg-surface-container flex items-center justify-center">
              <span className="material-symbols-outlined text-4xl text-outline">shopping_cart</span>
            </div>
            <p className="text-text-secondary text-lg">Sepetiniz boş</p>
            <button
              onClick={() => navigate('/')}
              className="bg-primary text-on-primary px-6 py-2.5 rounded-full font-medium hover:bg-on-primary-container transition-colors"
            >
              Alışverişe Başla
            </button>
          </div>
        ) : (
          <div className="flex flex-col lg:flex-row gap-6">
            {/* Left — Cart items */}
            <div className="flex-1 flex flex-col gap-4">
              {/* Eco banner */}
              <div className="bg-surface-bright border border-eco-green/30 rounded-xl px-4 py-3 flex items-center gap-3">
                <span className="material-symbols-outlined text-eco-green text-xl flex-shrink-0"
                  style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
                <div>
                  <p className="text-sm font-semibold text-primary">Yeşil Teslimat Fırsatı</p>
                  <p className="text-xs text-on-surface-variant">Eko ile konuşarak siparişini birleştir, karbon tasarrufu yap ve ekstra indirim kazan.</p>
                </div>
              </div>

              {/* Items */}
              {items.map(({ product, quantity }) => (
                <div
                  key={product.id}
                  className="bg-surface-card rounded-xl border border-outline-variant p-4 flex gap-4 hover:shadow-md transition-shadow"
                >
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-24 h-24 object-cover rounded-lg bg-surface-container-low flex-shrink-0"
                  />
                  <div className="flex-1 min-w-0 flex flex-col justify-between">
                    <div className="flex justify-between items-start gap-2">
                      <div>
                        <p className="text-xs text-text-secondary mb-0.5">{product.category}</p>
                        <h3 className="text-sm font-semibold text-text-primary leading-snug line-clamp-2">
                          {product.name}
                        </h3>
                      </div>
                      <button
                        onClick={() => removeItem(product.id)}
                        className="text-text-secondary hover:text-danger-red transition-colors flex-shrink-0 p-1"
                      >
                        <span className="material-symbols-outlined text-lg">delete</span>
                      </button>
                    </div>

                    <div className="flex items-center justify-between mt-2">
                      {/* Qty control */}
                      <div className="flex items-center border border-outline-variant rounded-lg overflow-hidden bg-surface-bg">
                        <button
                          onClick={() => updateQty(product.id, -1)}
                          className="px-3 py-1.5 text-text-secondary hover:bg-surface-container transition-colors text-sm font-bold"
                        >
                          −
                        </button>
                        <span className="px-3 py-1.5 text-sm font-medium text-text-primary border-x border-outline-variant min-w-[2rem] text-center">
                          {quantity}
                        </span>
                        <button
                          onClick={() => updateQty(product.id, 1)}
                          className="px-3 py-1.5 text-text-secondary hover:bg-surface-container transition-colors text-sm font-bold"
                        >
                          +
                        </button>
                      </div>

                      <p className="text-base font-bold text-text-primary font-display">
                        {formatPrice(product.list_price * quantity)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Right — Order summary */}
            <div className="w-full lg:w-80 flex-shrink-0">
              <div className="bg-surface-card rounded-xl border border-outline-variant p-5 sticky top-24">
                <h2 className="font-display text-lg font-semibold text-text-primary mb-4 pb-3 border-b border-outline-variant">
                  Sipariş Özeti
                </h2>

                <div className="flex flex-col gap-2.5 mb-4 text-sm">
                  <div className="flex justify-between text-text-secondary">
                    <span>Ürünlerin Toplamı</span>
                    <span>{formatPrice(cartTotal)}</span>
                  </div>
                  <div className="flex justify-between text-text-secondary">
                    <span>Kargo Tutarı</span>
                    <span>{formatPrice(shipping)}</span>
                  </div>
                  <div className="flex justify-between text-eco-green font-medium">
                    <span>Yeşil Teslimat İndirimi</span>
                    <span className="text-eco-green">Eko ile kazan!</span>
                  </div>
                </div>

                <div className="flex justify-between items-center py-3 border-t border-outline-variant mb-4">
                  <span className="font-semibold text-text-primary">Toplam</span>
                  <span className="font-display text-xl font-bold text-primary">
                    {formatPrice(cartTotal + shipping)}
                  </span>
                </div>

                <button className="w-full bg-primary text-on-primary py-3 rounded-xl font-semibold hover:bg-on-primary-container transition-colors shadow-sm mb-3">
                  Siparişi Onayla
                </button>

                <button
                  onClick={() => navigate('/')}
                  className="w-full text-center text-sm text-primary hover:text-on-primary-container transition-colors"
                >
                  Alışverişe Devam Et
                </button>

                {/* Eco note */}
                <div className="mt-4 pt-4 border-t border-outline-variant flex items-start gap-2">
                  <span className="material-symbols-outlined text-eco-green text-base flex-shrink-0 mt-0.5"
                    style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
                  <p className="text-xs text-text-secondary">
                    Sağ alt köşedeki <strong className="text-primary">Eko</strong> butonuna tıklayarak fiyat pazarlığı yap veya yeşil teslimat seç!
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Eko Chat — FAB + slide-in panel */}
      <EkoChat />
    </div>
  )
}

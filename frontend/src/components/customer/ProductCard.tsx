import { useState } from 'react'
import { useCartStore } from '@/store/cartStore'
import { useChatStore } from '@/store/chatStore'
import { ECO_SELLER_PRODUCT_IDS } from '@/data/mockData'
import { formatPrice } from '@/utils/format'
import type { Product } from '@/api/products'
import { useNavigate } from 'react-router-dom'

interface ProductCardProps {
  product: Product
}

export default function ProductCard({ product }: ProductCardProps) {
  const addItem = useCartStore((s) => s.addItem)
  const openChat = useChatStore((s) => s.openChat)
  const [added, setAdded] = useState(false)
  const [wishlist, setWishlist] = useState(false)
  const navigate = useNavigate()
  const isEcoSeller = ECO_SELLER_PRODUCT_IDS.has(product.id)

  const handleAddToCart = (e: React.MouseEvent) => {
    e.stopPropagation()
    addItem(product)
    setAdded(true)
    setTimeout(() => setAdded(false), 1500)
  }

  const handleBargain = (e: React.MouseEvent) => {
    e.stopPropagation()
    addItem(product)
    navigate('/cart')
    setTimeout(() => openChat(), 100)
  }

  return (
    <div className="bg-surface-card rounded-xl border border-outline-variant overflow-hidden hover:shadow-lg transition-shadow cursor-pointer group">
      {/* Image */}
      <div className="relative aspect-square overflow-hidden bg-surface-container-low">
        <img
          src={product.image_url}
          alt={product.name}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          loading="lazy"
        />

        {/* Wishlist */}
        <button
          onClick={(e) => { e.stopPropagation(); setWishlist((v) => !v) }}
          className="absolute top-2 right-2 w-8 h-8 bg-white/80 backdrop-blur rounded-full flex items-center justify-center shadow-sm hover:bg-white transition-colors"
        >
          <span
            className={`material-symbols-outlined text-base ${wishlist ? 'text-danger-red' : 'text-text-secondary'}`}
            style={{ fontVariationSettings: wishlist ? "'FILL' 1" : "'FILL' 0" }}
          >
            favorite
          </span>
        </button>

        {/* Eco Seller badge */}
        {isEcoSeller && (
          <div className="absolute top-2 left-2 flex items-center gap-1 bg-white/90 backdrop-blur border border-eco-green/40 text-eco-green px-2 py-0.5 rounded-full shadow-sm">
            <span className="material-symbols-outlined text-xs" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
            <span className="text-xs font-bold uppercase tracking-wide font-mono">Eco Seller</span>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="p-3 flex flex-col gap-2">
        <div>
          <p className="text-xs text-text-secondary">{product.category}</p>
          <h3 className="text-sm font-semibold text-text-primary leading-snug line-clamp-2 mt-0.5">
            {product.name}
          </h3>
        </div>

        <p className="text-lg font-bold text-text-primary font-display">
          {formatPrice(product.list_price)}
        </p>

        {/* Buttons */}
        <div className="flex flex-col gap-1.5">
          <button
            onClick={handleAddToCart}
            className={`w-full py-2 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
              added
                ? 'bg-eco-green text-white'
                : 'bg-primary text-on-primary hover:bg-on-primary-container'
            }`}
          >
            <span className="material-symbols-outlined text-base">
              {added ? 'check' : 'shopping_cart'}
            </span>
            {added ? 'Eklendi!' : 'Sepete Ekle'}
          </button>

          {product.negotiation_enabled && (
            <button
              onClick={handleBargain}
              className="w-full py-2 rounded-lg text-sm font-medium border-2 border-eco-green text-eco-green hover:bg-surface-container-low transition-colors flex items-center justify-center gap-1.5"
            >
              <span className="material-symbols-outlined text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
                chat_bubble
              </span>
              Eko ile Pazarlık Yap
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

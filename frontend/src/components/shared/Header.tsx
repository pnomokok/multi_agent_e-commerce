import { useNavigate, useLocation } from 'react-router-dom'
import { useCartStore } from '@/store/cartStore'
import PersonaSelector from '@/components/customer/PersonaSelector'

interface HeaderProps {
  showSearch?: boolean
}

export default function Header({ showSearch = true }: HeaderProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const itemCount = useCartStore((s) => s.itemCount())

  const navLinks = ['Eco-Deals', 'Sürdürülebilirlik', 'Kategoriler', 'Flaş İndirim']

  return (
    <header className="sticky top-0 z-40 bg-surface border-b border-outline-variant shadow-sm">
      <div className="max-w-7xl mx-auto px-4 md:px-10 h-16 flex items-center gap-4">
        {/* Logo */}
        <button
          onClick={() => navigate('/')}
          className="font-display text-2xl font-bold text-primary tracking-tight flex-shrink-0"
        >
          Eko
        </button>

        {/* Search */}
        {showSearch && (
          <div className="flex-1 max-w-xl hidden md:flex relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary text-xl">
              search
            </span>
            <input
              type="text"
              placeholder="Ürün, kategori veya marka ara..."
              className="w-full pl-10 pr-4 py-2 bg-surface-container-low border border-outline-variant rounded-full text-sm focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors"
            />
          </div>
        )}

        {/* Nav links — desktop */}
        <nav className="hidden lg:flex items-center gap-6 ml-2">
          {navLinks.map((link) => (
            <a
              key={link}
              href="#"
              className="text-sm text-on-surface-variant hover:text-primary transition-colors font-medium"
            >
              {link}
            </a>
          ))}
        </nav>

        <div className="flex-1" />

        {/* Right icons */}
        <div className="flex items-center gap-2">
          {/* Persona selector */}
          <PersonaSelector />

          <button className="p-2 text-on-surface-variant hover:text-primary hover:bg-surface-container-low rounded-full transition-colors">
            <span className="material-symbols-outlined text-xl">favorite</span>
          </button>

          {/* Cart */}
          <button
            onClick={() => navigate('/cart')}
            className={`relative p-2 rounded-full transition-colors ${
              location.pathname === '/cart'
                ? 'text-primary bg-surface-container'
                : 'text-on-surface-variant hover:text-primary hover:bg-surface-container-low'
            }`}
          >
            <span className="material-symbols-outlined text-xl">shopping_cart</span>
            {itemCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-5 h-5 bg-primary-container text-on-primary-container text-xs font-bold rounded-full flex items-center justify-center">
                {itemCount > 9 ? '9+' : itemCount}
              </span>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}

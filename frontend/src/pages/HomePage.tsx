import { useNavigate } from 'react-router-dom'
import { ShoppingCart, Store, Leaf } from 'lucide-react'

export default function HomePage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-gradient-to-br from-violet-50 to-green-50 flex flex-col items-center justify-center px-4">
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-2 mb-4">
          <Leaf className="w-10 h-10 text-green-500" />
          <h1 className="text-5xl font-bold text-gray-900">Eko</h1>
        </div>
        <p className="text-xl text-gray-600 max-w-md mx-auto">
          Cüzdana iyi, dünyaya iyi — akıllı sepet asistanı
        </p>
      </div>

      <div className="flex gap-6 flex-wrap justify-center">
        <button
          onClick={() => navigate('/shop')}
          className="flex flex-col items-center gap-3 bg-white rounded-2xl shadow-lg px-10 py-8 hover:shadow-xl transition-shadow border border-gray-100 cursor-pointer"
        >
          <ShoppingCart className="w-10 h-10 text-violet-600" />
          <span className="text-lg font-semibold text-gray-800">Müşteri Ekranı</span>
          <span className="text-sm text-gray-500">Eko ile alışveriş yap</span>
        </button>

        <button
          onClick={() => navigate('/seller')}
          className="flex flex-col items-center gap-3 bg-white rounded-2xl shadow-lg px-10 py-8 hover:shadow-xl transition-shadow border border-gray-100 cursor-pointer"
        >
          <Store className="w-10 h-10 text-green-600" />
          <span className="text-lg font-semibold text-gray-800">Satıcı Paneli</span>
          <span className="text-sm text-gray-500">ROI ve pazarlık istatistikleri</span>
        </button>
      </div>
    </div>
  )
}

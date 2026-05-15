import { BrowserRouter, Routes, Route } from 'react-router-dom'
import CustomerPage from '@/pages/CustomerPage'
import CartPage from '@/pages/CartPage'
import SellerDashboardPage from '@/pages/SellerDashboardPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Müşteri tarafı — e-ticaret ana sayfası */}
        <Route path="/" element={<CustomerPage />} />
        <Route path="/cart" element={<CartPage />} />
        {/* Satıcı paneli — tamamen izole */}
        <Route path="/seller" element={<SellerDashboardPage />} />
      </Routes>
    </BrowserRouter>
  )
}

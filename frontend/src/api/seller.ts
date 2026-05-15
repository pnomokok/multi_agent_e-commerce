import client from './client'

export interface SellerDashboard {
  seller_id: string
  seller_name: string
  eco_seller_badge: boolean
  total_co2_saved_kg: number
  weekly_negotiations_closed: number
  weekly_discount_given: number
  estimated_saved_orders: number
  net_roi: number
}

export interface SellerPolicy {
  monthly_negotiation_budget: number
  monthly_negotiation_spent: number
  min_margin_target: number
}

export const getSellerDashboard = (sellerId: string) =>
  client.get<SellerDashboard>(`/seller/${sellerId}/dashboard`).then((r) => r.data)

export const getSellerPolicy = (sellerId: string) =>
  client.get<SellerPolicy>(`/seller/${sellerId}/policy`).then((r) => r.data)

export const updateSellerPolicy = (sellerId: string, policy: Partial<SellerPolicy>) =>
  client.put(`/seller/${sellerId}/policy`, policy).then((r) => r.data)

export const getSellerStats = (sellerId: string) =>
  client.get(`/seller/${sellerId}/stats`).then((r) => r.data)

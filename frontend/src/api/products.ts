import client from './client'

export interface Product {
  id: string
  seller_id: string
  name: string
  category: string
  list_price: number
  image_url: string
  weight_kg: number
  negotiation_enabled: boolean
  stock: number
}

export const getProducts = () =>
  client.get<Product[]>('/products').then((r) => r.data)

export const getPersonas = () =>
  client.get<Persona[]>('/personas').then((r) => r.data)

export interface Persona {
  id: string
  name: string
  segment: 'new' | 'loyal' | 'bargain_hunter'
  address: string
  total_co2_saved_kg: number
  eco_customer_badge: boolean
}

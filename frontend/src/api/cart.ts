import client from './client'

export interface CartItem {
  product_id: string
  product_name: string
  quantity: number
  unit_price: number
  total_price: number
  image_url: string
}

export interface CartResponse {
  session_id: string
  items: CartItem[]
  total: number
  item_count: number
}

export const getCart = (sessionId: string) =>
  client.get<CartResponse>(`/cart/${sessionId}`).then((r) => r.data)

export const addToCart = (sessionId: string, productId: string, quantity = 1) =>
  client
    .post(`/cart/${sessionId}/add`, { product_id: productId, quantity })
    .then((r) => r.data)

export const removeFromCart = (sessionId: string, productId: string) =>
  client
    .post(`/cart/${sessionId}/remove`, { product_id: productId })
    .then((r) => r.data)

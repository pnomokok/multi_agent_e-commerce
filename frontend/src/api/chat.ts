import client from './client'

export interface AgentLog {
  timestamp: string
  agent_name: string
  action: string
  payload: Record<string, unknown>
}

export interface OfferDetails {
  original_price: number
  offered_price: number
  discount_amount: number
  gifts: string[]
  free_shipping: boolean
  is_final: boolean
}

export interface CarbonData {
  discount_amount: number
  co2_saved_kg: number
  tree_equivalent: string
  express_date: string
  consolidated_date: string
}

export interface ChatResponse {
  response_text: string
  agent_used: string
  offer_details: OfferDetails | null
  carbon_data: CarbonData | null
  agent_logs: AgentLog[]
}

export const sendMessage = (sessionId: string, message: string) =>
  client
    .post<ChatResponse>(`/chat/${sessionId}`, { message })
    .then((r) => r.data)

export const startSession = (customerId: string) =>
  client
    .post<{ session_id: string }>('/session/start', { customer_id: customerId })
    .then((r) => r.data)

export const checkout = (sessionId: string, deliveryPreference: 'express' | 'consolidated') =>
  client
    .post(`/checkout/${sessionId}`, { delivery_preference: deliveryPreference })
    .then((r) => r.data)

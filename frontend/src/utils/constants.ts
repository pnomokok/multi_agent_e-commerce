export const API_BASE = '/api'
export const WS_BASE = `ws://${window.location.host}/ws`

export const CUSTOMER_SEGMENTS = {
  new: 'Yeni Müşteri',
  loyal: 'Sadık Müşteri',
  bargain_hunter: 'Pazarlık Avcısı',
} as const

export const DELIVERY_OPTIONS = {
  express: 'Hızlı Teslimat',
  consolidated: 'Konsolide Teslimat',
} as const

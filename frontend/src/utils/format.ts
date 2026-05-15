export function formatPrice(amount: number): string {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    minimumFractionDigits: 0,
  }).format(amount)
}

export function formatCO2(kg: number): string {
  if (kg < 1) return `${(kg * 1000).toFixed(0)} g CO₂`
  return `${kg.toFixed(1)} kg CO₂`
}

export function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    day: 'numeric',
    month: 'long',
    weekday: 'short',
  })
}

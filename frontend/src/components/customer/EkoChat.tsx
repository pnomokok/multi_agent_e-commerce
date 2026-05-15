import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useChatStore, type ChatMessage } from '@/store/chatStore'
import { useCartStore } from '@/store/cartStore'
import { useSessionStore } from '@/store/sessionStore'
import { sendMessage, startSession } from '@/api/chat'
import { formatPrice, formatCO2 } from '@/utils/format'
import type { OfferDetails, CarbonData } from '@/api/chat'

function OfferCard({ offer, onAccept }: { offer: OfferDetails; onAccept: () => void }) {
  return (
    <div className="bg-surface-card border border-negotiation-gold/40 rounded-xl p-3 mt-2 shadow-sm">
      <div className="flex items-center gap-1.5 mb-2">
        <span className="material-symbols-outlined text-negotiation-gold text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
          local_offer
        </span>
        <span className="text-sm font-semibold text-text-primary">Eko Teklifi</span>
      </div>
      <div className="flex items-baseline gap-2 mb-1">
        <span className="text-xs text-text-secondary line-through">{formatPrice(offer.original_price)}</span>
        <span className="text-lg font-bold text-primary">{formatPrice(offer.offered_price)}</span>
      </div>
      {offer.gifts.length > 0 && (
        <p className="text-xs text-eco-green mb-2">🎁 Hediye: {offer.gifts.join(', ')}</p>
      )}
      {offer.free_shipping && (
        <p className="text-xs text-eco-green mb-2">🚚 Ücretsiz kargo</p>
      )}
      <div className="flex gap-2">
        <button onClick={onAccept} className="flex-1 bg-primary text-on-primary text-sm py-1.5 rounded-lg font-medium hover:bg-on-primary-container transition-colors">
          Kabul Et
        </button>
        <button className="flex-1 bg-surface-container text-text-secondary text-sm py-1.5 rounded-lg font-medium hover:bg-surface-container-high transition-colors">
          Reddediyorum
        </button>
      </div>
    </div>
  )
}

function CarbonCard({ data, onAccept, onDecline }: { data: CarbonData; onAccept: () => void; onDecline: () => void }) {
  return (
    <div className="bg-surface-bright border border-eco-green/40 rounded-xl p-3 mt-2 shadow-sm">
      <div className="flex items-center gap-1.5 mb-2">
        <span className="material-symbols-outlined text-eco-green text-base" style={{ fontVariationSettings: "'FILL' 1" }}>
          local_shipping
        </span>
        <span className="text-sm font-semibold text-primary">Yeşil Teslimat Fırsatı</span>
      </div>
      <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
        <div className="bg-surface-card rounded-lg p-2 text-center">
          <p className="text-text-secondary">İndirim</p>
          <p className="font-bold text-primary text-base">{formatPrice(data.discount_amount)}</p>
        </div>
        <div className="bg-surface-card rounded-lg p-2 text-center">
          <p className="text-text-secondary">CO₂ Tasarrufu</p>
          <p className="font-bold text-eco-green text-base">{formatCO2(data.co2_saved_kg)}</p>
        </div>
      </div>
      <p className="text-xs text-text-secondary mb-2">🌳 {data.tree_equivalent}</p>
      <div className="flex gap-2">
        <button onClick={onAccept} className="flex-1 bg-eco-green text-white text-sm py-1.5 rounded-lg font-medium hover:bg-primary transition-colors">
          Yeşil Teslimat Seç
        </button>
        <button onClick={onDecline} className="flex-1 bg-surface-container text-text-secondary text-sm py-1.5 rounded-lg font-medium hover:bg-surface-container-high transition-colors">
          Hızlı Teslimat
        </button>
      </div>
    </div>
  )
}

function MessageBubble({ msg, onAccept }: { msg: ChatMessage; onAccept: (type: string) => void }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-2 items-end ${isUser ? 'flex-row-reverse' : ''}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-surface-container flex-shrink-0 flex items-center justify-center border border-eco-green/30">
          <span className="material-symbols-outlined text-eco-green text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
        </div>
      )}
      <div className={`max-w-[82%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div className={`px-3 py-2 rounded-2xl text-sm leading-relaxed ${
          isUser
            ? 'bg-primary text-on-primary rounded-br-sm'
            : 'bg-surface-card border border-outline-variant text-text-primary rounded-bl-sm shadow-sm'
        }`}>
          {msg.text}
        </div>
        {msg.offer && (
          <OfferCard offer={msg.offer} onAccept={() => onAccept('offer')} />
        )}
        {msg.carbon && (
          <CarbonCard
            data={msg.carbon}
            onAccept={() => onAccept('green')}
            onDecline={() => onAccept('express')}
          />
        )}
        <span className="text-xs text-text-secondary mt-1 px-1">
          {msg.timestamp.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  )
}

export default function EkoChat() {
  const { isOpen, messages, isLoading, addMessage, setLoading, toggleChat, openChat, reset } = useChatStore()
  const { sessionId, persona, setSession } = useSessionStore()
  const cartTotal = useCartStore((s) => s.total())
  const items = useCartStore((s) => s.items)
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Greet when chat opens for first time
  useEffect(() => {
    if (isOpen && messages.length === 0 && items.length > 0) {
      addMessage({
        role: 'assistant',
        text: `Merhaba ${persona.name}! 👋 Sepetindeki ${items.length} ürün için toplam ${new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 0 }).format(cartTotal)} ödenecek. Fiyat konusunda yardımcı olmamı ister misin? Ya da yeşil teslimat seçeneklerine bakalım mı?`,
      })
    }
  }, [isOpen])

  const initSession = async () => {
    if (sessionId) return sessionId
    try {
      const { session_id } = await startSession(persona.id)
      setSession(session_id)
      return session_id
    } catch {
      // Backend not ready — use mock session
      const mockId = `mock-${Date.now()}`
      setSession(mockId)
      return mockId
    }
  }

  const handleSend = async () => {
    const text = input.trim()
    if (!text || isLoading) return
    setInput('')

    addMessage({ role: 'user', text })
    setLoading(true)

    try {
      const sid = await initSession()
      if (sid.startsWith('mock-')) {
        // Mock response when backend isn't ready
        await new Promise((r) => setTimeout(r, 1200))
        const mockReply = getMockReply(text, cartTotal)
        addMessage(mockReply)
      } else {
        const res = await sendMessage(sid, text)
        addMessage({
          role: 'assistant',
          text: res.response_text,
          offer: res.offer_details ?? undefined,
          carbon: res.carbon_data ?? undefined,
        })
      }
    } catch {
      addMessage({ role: 'assistant', text: 'Bir sorun oluştu, lütfen tekrar dene.' })
    } finally {
      setLoading(false)
    }
  }

  const handleAccept = (type: string) => {
    if (type === 'offer') {
      addMessage({ role: 'assistant', text: '✅ Harika! Teklif uygulandı. Sepetini onaylayabilirsin.' })
    } else if (type === 'green') {
      addMessage({ role: 'assistant', text: '🌱 Yeşil teslimatı seçtin! Hem cüzdanın hem de dünya teşekkür eder. Sipariş onayına geçebilirsin.' })
    } else {
      addMessage({ role: 'assistant', text: 'Hızlı teslimat seçildi. İyi alışverişler!' })
    }
  }

  return (
    <>
      {/* FAB Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            onClick={() => openChat()}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-primary text-on-primary rounded-full shadow-xl flex items-center justify-center hover:bg-on-primary-container transition-colors group"
          >
            <span className="material-symbols-outlined text-2xl group-hover:scale-110 transition-transform"
              style={{ fontVariationSettings: "'FILL' 1" }}>
              chat_bubble
            </span>
            {/* Pulse ring */}
            <span className="absolute inset-0 rounded-full bg-primary animate-ping opacity-20" />
            {/* Label */}
            <span className="absolute right-full mr-3 whitespace-nowrap bg-text-primary text-white text-xs px-3 py-1.5 rounded-full opacity-0 group-hover:opacity-100 transition-opacity font-medium">
              Eko ile Konuş
            </span>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Overlay backdrop */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={toggleChat}
            className="fixed inset-0 bg-black/20 z-40 md:hidden"
          />
        )}
      </AnimatePresence>

      {/* Slide-in chat panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 28, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 z-50 w-full max-w-sm bg-surface-card border-l border-outline-variant shadow-2xl flex flex-col"
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-outline-variant bg-surface-bright">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-full bg-surface-container flex items-center justify-center border border-eco-green/30">
                  <span className="material-symbols-outlined text-eco-green text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>
                    eco
                  </span>
                </div>
                <div>
                  <p className="text-sm font-semibold text-primary font-display">Eko Asistan</p>
                  <div className="flex items-center gap-1">
                    <span className="w-1.5 h-1.5 bg-eco-green rounded-full animate-pulse" />
                    <span className="text-xs text-eco-green font-mono">Çevrimiçi</span>
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={reset}
                  className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface-container rounded-full transition-colors"
                  title="Sohbeti sıfırla"
                >
                  <span className="material-symbols-outlined text-base">refresh</span>
                </button>
                <button
                  onClick={toggleChat}
                  className="p-1.5 text-text-secondary hover:text-text-primary hover:bg-surface-container rounded-full transition-colors"
                >
                  <span className="material-symbols-outlined text-base">close</span>
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4 bg-surface-bg">
              {messages.length === 0 && (
                <div className="flex flex-col items-center justify-center h-full gap-3 text-center">
                  <div className="w-16 h-16 rounded-full bg-surface-container-low flex items-center justify-center">
                    <span className="material-symbols-outlined text-eco-green text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
                  </div>
                  <p className="text-sm text-text-secondary max-w-xs">
                    Eko sana yardımcı olmak için burada. Fiyat pazarlığı veya yeşil teslimat hakkında soru sor!
                  </p>
                </div>
              )}
              {messages.map((msg) => (
                <MessageBubble key={msg.id} msg={msg} onAccept={handleAccept} />
              ))}
              {isLoading && (
                <div className="flex gap-2 items-end">
                  <div className="w-7 h-7 rounded-full bg-surface-container flex-shrink-0 flex items-center justify-center border border-eco-green/30">
                    <span className="material-symbols-outlined text-eco-green text-sm" style={{ fontVariationSettings: "'FILL' 1" }}>eco</span>
                  </div>
                  <div className="bg-surface-card border border-outline-variant rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-outline rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-outline rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-outline rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-t border-outline-variant bg-surface-card">
              {/* Quick suggestions */}
              {messages.length <= 1 && (
                <div className="flex gap-2 mb-2 overflow-x-auto pb-1">
                  {['İndirim var mı?', 'Yeşil teslimat nedir?', 'Bu fiyat müzakere edilebilir mi?'].map((s) => (
                    <button
                      key={s}
                      onClick={() => setInput(s)}
                      className="flex-shrink-0 text-xs bg-surface-container-low border border-outline-variant text-on-surface-variant px-3 py-1.5 rounded-full hover:border-primary hover:text-primary transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}
              <div className="flex items-center gap-2 bg-surface-bg border border-outline-variant rounded-full px-4 py-2 focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Eko'ya mesaj yaz..."
                  className="flex-1 bg-transparent border-none text-sm focus:ring-0 focus:outline-none text-text-primary placeholder-text-secondary"
                />
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="p-1 text-primary disabled:text-outline transition-colors"
                >
                  <span className="material-symbols-outlined text-lg" style={{ fontVariationSettings: "'FILL' 1" }}>send</span>
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}

// Mock responses for when backend isn't ready
function getMockReply(msg: string, total: number): Omit<ChatMessage, 'id' | 'timestamp'> {
  const lower = msg.toLowerCase()

  if (lower.includes('indirim') || lower.includes('ucuz') || lower.includes('fiyat') || lower.includes('pahalı') || lower.includes('müzakere') || lower.includes('tl')) {
    return {
      role: 'assistant',
      text: `Anlıyorum! Sepetiniz şu an ${new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY', minimumFractionDigits: 0 }).format(total)} tutarında. Sizin için en iyi teklifimi hazırladım:`,
      offer: {
        original_price: total,
        offered_price: Math.round(total * 0.88),
        discount_amount: Math.round(total * 0.12),
        gifts: ['Kulaklık Kılıfı'],
        free_shipping: true,
        is_final: false,
      },
    }
  }

  if (lower.includes('yeşil') || lower.includes('karbon') || lower.includes('teslimat') || lower.includes('çevre')) {
    return {
      role: 'assistant',
      text: 'Harika tercih! Siparişini 3 gün içinde konsolide teslimatla gönderebiliriz. Hem sana indirim hem de çevreye katkı:',
      carbon: {
        discount_amount: 49,
        co2_saved_kg: 2.3,
        tree_equivalent: '2.3 kg = bir ağacın 3 günlük temizlediği hava',
        express_date: new Date(Date.now() + 86400000).toISOString(),
        consolidated_date: new Date(Date.now() + 3 * 86400000).toISOString(),
      },
    }
  }

  if (lower.includes('merhaba') || lower.includes('selam') || lower.includes('hi')) {
    return {
      role: 'assistant',
      text: 'Merhaba! Ben Eko, akıllı alışveriş asistanınım. 🌱 Size fiyat pazarlığında yardımcı olabilirim ya da çevre dostu teslimat seçeneklerini sunabilirim. Ne yapmamı istersiniz?',
    }
  }

  return {
    role: 'assistant',
    text: 'Anladım! Size nasıl yardımcı olabileceğimi söyler misiniz? Fiyat pazarlığı veya yeşil teslimat konularında destek verebilirim.',
  }
}

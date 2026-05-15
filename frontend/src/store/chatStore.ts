import { create } from 'zustand'
import type { AgentLog, OfferDetails, CarbonData } from '@/api/chat'

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text: string
  offer?: OfferDetails
  carbon?: CarbonData
  timestamp: Date
}

interface ChatState {
  messages: ChatMessage[]
  logs: AgentLog[]
  isOpen: boolean
  isLoading: boolean
  addMessage: (msg: Omit<ChatMessage, 'id' | 'timestamp'>) => void
  addLogs: (logs: AgentLog[]) => void
  setLoading: (v: boolean) => void
  toggleChat: () => void
  openChat: () => void
  reset: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  logs: [],
  isOpen: false,
  isLoading: false,
  addMessage: (msg) =>
    set((s) => ({
      messages: [
        ...s.messages,
        { ...msg, id: crypto.randomUUID(), timestamp: new Date() },
      ],
    })),
  addLogs: (newLogs) =>
    set((s) => ({ logs: [...s.logs, ...newLogs] })),
  setLoading: (v) => set({ isLoading: v }),
  toggleChat: () => set((s) => ({ isOpen: !s.isOpen })),
  openChat: () => set({ isOpen: true }),
  reset: () => set({ messages: [], logs: [], isLoading: false }),
}))

import { create } from 'zustand'
import type { Persona } from '@/api/products'
import { MOCK_PERSONAS } from '@/data/mockData'

interface SessionState {
  sessionId: string | null
  persona: Persona
  setPersona: (persona: Persona) => void
  setSession: (sessionId: string) => void
}

export const useSessionStore = create<SessionState>((set) => ({
  sessionId: null,
  persona: MOCK_PERSONAS[0], // Default: Ayşe (eco-conscious)
  setPersona: (persona) => set({ persona, sessionId: null }),
  setSession: (sessionId) => set({ sessionId }),
}))

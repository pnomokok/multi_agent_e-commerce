import { useState, useRef, useEffect } from 'react'
import { useSessionStore } from '@/store/sessionStore'
import { MOCK_PERSONAS, PERSONA_META } from '@/data/mockData'

export default function PersonaSelector() {
  const { persona, setPersona } = useSessionStore()
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const meta = PERSONA_META[persona.id]

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-outline-variant bg-surface-card hover:bg-surface-container-low transition-colors text-sm"
      >
        <span className={`material-symbols-outlined text-base ${meta.color}`}
          style={{ fontVariationSettings: "'FILL' 1" }}>
          {meta.icon}
        </span>
        <span className="font-medium text-text-primary hidden sm:inline">{persona.name}</span>
        <span className="text-xs text-text-secondary hidden sm:inline">({meta.label})</span>
        <span className="material-symbols-outlined text-sm text-text-secondary">
          {open ? 'expand_less' : 'expand_more'}
        </span>
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-72 bg-surface-card border border-outline-variant rounded-xl shadow-xl z-50 overflow-hidden">
          <div className="px-4 py-2 bg-surface-container-low border-b border-outline-variant">
            <p className="text-xs font-medium text-text-secondary uppercase tracking-wide">Demo Persona Seç</p>
          </div>
          {MOCK_PERSONAS.map((p) => {
            const m = PERSONA_META[p.id]
            const isActive = p.id === persona.id
            return (
              <button
                key={p.id}
                onClick={() => { setPersona(p); setOpen(false) }}
                className={`w-full flex items-start gap-3 px-4 py-3 hover:bg-surface-container-low transition-colors text-left ${isActive ? 'bg-surface-container' : ''}`}
              >
                <span
                  className={`material-symbols-outlined text-xl mt-0.5 ${m.color}`}
                  style={{ fontVariationSettings: "'FILL' 1" }}
                >
                  {m.icon}
                </span>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-text-primary text-sm">{p.name}</span>
                    <span className={`text-xs px-1.5 py-0.5 rounded-full font-medium ${
                      isActive ? 'bg-primary text-on-primary' : 'bg-surface-container text-text-secondary'
                    }`}>
                      {m.label}
                    </span>
                  </div>
                  <p className="text-xs text-text-secondary mt-0.5">{m.description}</p>
                </div>
              </button>
            )
          })}
        </div>
      )}
    </div>
  )
}

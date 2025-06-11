import { create } from 'zustand'
import { devtools, persist } from 'zustand/middleware'

export interface BlackSwanEvent {
  id: string
  timestamp: Date
  source: string
  severity: 'low' | 'medium' | 'high' | 'critical'
  confidence: number
  title: string
  description: string
  riskFactors: string[]
  recommendedActions: string[]
  affectedAssets: string[]
  sentiment: number
  isRead: boolean
}

interface EventState {
  events: BlackSwanEvent[]
  selectedEvent: BlackSwanEvent | null
  filter: {
    severity: string[]
    source: string[]
    dateRange: { from: Date | null; to: Date | null }
  }
  isLoading: boolean
  error: string | null
}

interface EventActions {
  addEvent: (event: BlackSwanEvent) => void
  addEvents: (events: BlackSwanEvent[]) => void
  selectEvent: (eventId: string) => void
  markAsRead: (eventId: string) => void
  updateFilter: (filter: Partial<EventState['filter']>) => void
  clearEvents: () => void
  setLoading: (isLoading: boolean) => void
  setError: (error: string | null) => void
}

export const useEventStore = create<EventState & EventActions>()(
  devtools(
    persist(
      (set) => ({
        // State
        events: [],
        selectedEvent: null,
        filter: {
          severity: [],
          source: [],
          dateRange: { from: null, to: null }
        },
        isLoading: false,
        error: null,

        // Actions
        addEvent: (event) =>
          set((state) => ({
            events: [event, ...state.events].slice(0, 1000) // Keep last 1000 events
          })),

        addEvents: (events) =>
          set((state) => ({
            events: [...events, ...state.events].slice(0, 1000)
          })),

        selectEvent: (eventId) =>
          set((state) => ({
            selectedEvent: state.events.find((e) => e.id === eventId) || null
          })),

        markAsRead: (eventId) =>
          set((state) => ({
            events: state.events.map((e) =>
              e.id === eventId ? { ...e, isRead: true } : e
            )
          })),

        updateFilter: (filter) =>
          set((state) => ({
            filter: { ...state.filter, ...filter }
          })),

        clearEvents: () =>
          set(() => ({
            events: [],
            selectedEvent: null
          })),

        setLoading: (isLoading) => set(() => ({ isLoading })),
        setError: (error) => set(() => ({ error }))
      }),
      {
        name: 'blackswan-events',
        partialize: (state) => ({ events: state.events }) // Only persist events
      }
    )
  )
)
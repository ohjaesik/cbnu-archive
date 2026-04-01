import { create } from 'zustand'
import type { ChatMessage } from '@/types/chat'

interface ChatState {
  sessionId: string | null
  messages: ChatMessage[]
  isLoading: boolean
  setSessionId: (id: string) => void
  addMessage: (message: ChatMessage) => void
  setLoading: (loading: boolean) => void
  resetSession: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  sessionId: null,
  messages: [],
  isLoading: false,
  setSessionId: (sessionId) => set({ sessionId }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setLoading: (isLoading) => set({ isLoading }),
  resetSession: () => set({ sessionId: null, messages: [], isLoading: false }),
}))

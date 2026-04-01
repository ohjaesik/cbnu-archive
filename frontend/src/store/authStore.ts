import { create } from 'zustand'
import type { UserRole } from '@/types/user'

interface AuthState {
  accessToken: string | null
  userId: number | null
  role: UserRole
  setAuth: (token: string, userId: number, role: UserRole) => void
  setAccessToken: (token: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: null,
  userId: null,
  role: 'GUEST',
  setAuth: (accessToken, userId, role) => set({ accessToken, userId, role }),
  setAccessToken: (accessToken) => set({ accessToken }),
  logout: () => set({ accessToken: null, userId: null, role: 'GUEST' }),
}))

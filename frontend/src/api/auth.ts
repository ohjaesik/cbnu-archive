import { api } from './axiosInstance'
import type { LoginRequest, LoginResponse } from '@/types/user'

export const login = (data: LoginRequest) =>
  api.post<LoginResponse>('/api/auth/login', data).then((r) => r.data)

export const logout = () => api.post('/api/auth/logout')

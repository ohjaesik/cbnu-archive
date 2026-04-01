import { api } from './axiosInstance'
import type { ChatRequest, ChatResponse } from '@/types/chat'

export const sendMessage = (data: ChatRequest) =>
  api.post<ChatResponse>('/api/chat', data).then((r) => r.data)

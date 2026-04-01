import { api } from './axiosInstance'
import type { NaturalSearchResult } from '@/types/chat'
import type { PagedResponse, ProjectSummary } from '@/types/project'

interface KeywordSearchParams {
  q: string
  sort?: string
  page?: number
  size?: number
}

export const searchKeyword = (params: KeywordSearchParams) =>
  api.get<PagedResponse<ProjectSummary>>('/api/search', { params }).then((r) => r.data)

export const searchNatural = (query: string, sessionId?: string) =>
  api
    .post<NaturalSearchResult>('/api/search/natural', { query, sessionId })
    .then((r) => r.data)

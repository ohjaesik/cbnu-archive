import { api } from './axiosInstance'
import type {
  PagedResponse,
  ProjectCreateRequest,
  ProjectDetail,
  ProjectListParams,
  ProjectSummary,
  RecommendationResult,
} from '@/types/project'

export const getProjects = (params: ProjectListParams) =>
  api.get<PagedResponse<ProjectSummary>>('/api/projects', { params }).then((r) => r.data)

export const getProjectDetail = (id: number) =>
  api.get<ProjectDetail>(`/api/projects/${id}`).then((r) => r.data)

export const createProject = (data: ProjectCreateRequest) =>
  api.post<{ projectId: number; status: string }>('/api/projects', data).then((r) => r.data)

export const updateProject = (id: number, data: Partial<ProjectCreateRequest>) =>
  api.patch(`/api/projects/${id}`, data)

export const deleteProject = (id: number) => api.delete(`/api/projects/${id}`)

export const getMyProjects = () =>
  api.get<ProjectSummary[]>('/api/projects/my').then((r) => r.data)

export const getRecommendations = (projectId: number) =>
  api.get<RecommendationResult>(`/api/projects/${projectId}/recommendations`).then((r) => r.data)

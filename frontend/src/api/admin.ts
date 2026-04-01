import { api } from './axiosInstance'
import type { PagedResponse, ProjectSummary, Visibility } from '@/types/project'

interface AuditLog {
  id: number
  action: string
  targetId: number
  actorId: number
  timestamp: string
}

interface AdminStats {
  totalProjects: number
  pendingProjects: number
  approvedThisMonth: number
  downloadsThisMonth: number
  topTags: { tag: string; count: number }[]
}

export const getPendingProjects = (params?: { page?: number; size?: number }) =>
  api
    .get<PagedResponse<ProjectSummary>>('/api/admin/projects/pending', { params })
    .then((r) => r.data)

export const approveProject = (id: number, visibility: Visibility) =>
  api.patch(`/api/admin/projects/${id}/approve`, { visibility })

export const rejectProject = (id: number, reason: string) =>
  api.patch(`/api/admin/projects/${id}/reject`, { reason })

export const requestRevision = (id: number, fields: string[]) =>
  api.patch(`/api/admin/projects/${id}/request-revision`, { fields })

export const getStats = () => api.get<AdminStats>('/api/admin/stats').then((r) => r.data)

export const getAuditLogs = (params?: { page?: number; size?: number }) =>
  api.get<PagedResponse<AuditLog>>('/api/admin/audit-logs', { params }).then((r) => r.data)

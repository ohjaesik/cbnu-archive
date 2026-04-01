export type ProjectStatus =
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'REJECTED'
  | 'REVISION_REQUESTED'
  | 'PRIVATE'
  | 'DELETED'

export type Visibility = 'PUBLIC' | 'CAMPUS_ONLY' | 'RESTRICTED'

export type SortOption = 'latest' | 'oldest' | 'views' | 'downloads'

import type { ProjectFile } from './file'

export interface ProjectMember {
  name: string
  studentId: string
  role: string
}

export interface ProjectSummary {
  id: number
  title: string
  summary: string
  year: number
  semester: 1 | 2
  subjectName: string
  teamName: string
  techStacks: string[]
  tags: string[]
  status: ProjectStatus
  viewCount: number
  downloadCount: number
  createdAt: string
}

export interface ProjectDetail extends ProjectSummary {
  description: string
  members: ProjectMember[]
  visibility: Visibility
  files: ProjectFile[]
}

export interface ProjectCreateRequest {
  title: string
  summary: string
  description: string
  year: number
  semester: 1 | 2
  subjectName: string
  teamName?: string
  members: ProjectMember[]
  techStacks: string[]
  tags: string[]
  fileIds: number[]
}

export interface PagedResponse<T> {
  total: number
  page: number
  size: number
  items: T[]
}

export interface ProjectListParams {
  keyword?: string
  years?: number[]
  semester?: 1 | 2
  subjects?: string[]
  techStacks?: string[]
  domains?: string[]
  isTeam?: boolean
  sort?: SortOption
  page?: number
  size?: number
}

export interface RecommendationItem {
  id: number
  title: string
  matchReason: string
}

export interface RecommendationResult {
  recommendations: RecommendationItem[]
}

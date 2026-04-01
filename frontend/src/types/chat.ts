import type { ProjectSummary } from './project'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  projects?: ProjectSummary[]
  suggestedFollowUps?: string[]
}

export interface ChatRequest {
  message: string
  sessionId: string | null
}

export interface ChatResponse {
  sessionId: string
  reply: string
  projects: ProjectSummary[]
  suggestedFollowUps: string[]
}

export interface NaturalSearchResult {
  interpretedConditions: Record<string, unknown>
  answer: string
  projects: (ProjectSummary & { matchReason: string })[]
}

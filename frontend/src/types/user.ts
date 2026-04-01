export type UserRole = 'GUEST' | 'STUDENT' | 'ADMIN'

export interface User {
  userId: number
  identifier: string
  role: UserRole
}

export interface LoginRequest {
  identifier: string
  password: string
}

export interface LoginResponse {
  accessToken: string
  userId: number
  role: UserRole
}

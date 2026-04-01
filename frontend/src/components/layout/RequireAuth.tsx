import { Outlet, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import type { UserRole } from '@/types/user'

interface RequireAuthProps {
  role: UserRole
}

export function RequireAuth({ role }: RequireAuthProps) {
  const currentRole = useAuthStore((s) => s.role)

  const roleLevel: Record<UserRole, number> = { GUEST: 0, STUDENT: 1, ADMIN: 2 }

  if (roleLevel[currentRole] < roleLevel[role]) {
    const redirect = window.location.pathname
    return <Navigate to={`/login?redirect=${encodeURIComponent(redirect)}`} replace />
  }

  return <Outlet />
}

import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { logout } from '@/api/auth'

export function GNB() {
  const { role } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    useAuthStore.getState().logout()
    navigate('/login')
  }

  return (
    <header className="sticky top-0 z-50 border-b border-gray-200 bg-white">
      <div className="mx-auto flex h-14 max-w-7xl items-center justify-between px-4">
        <Link to="/" className="text-lg font-bold text-primary-600">
          AI Archive
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          <Link to="/projects" className="text-gray-600 hover:text-gray-900">
            프로젝트
          </Link>
          <Link to="/chat" className="text-gray-600 hover:text-gray-900">
            AI 탐색
          </Link>
          {role === 'STUDENT' || role === 'ADMIN' ? (
            <>
              <Link to="/my" className="text-gray-600 hover:text-gray-900">
                내 프로젝트
              </Link>
              {role === 'ADMIN' && (
                <Link to="/admin/pending" className="text-gray-600 hover:text-gray-900">
                  관리
                </Link>
              )}
              <button
                onClick={handleLogout}
                className="text-gray-600 hover:text-gray-900"
              >
                로그아웃
              </button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-md bg-primary-600 px-3 py-1.5 text-white hover:bg-primary-700"
            >
              로그인
            </Link>
          )}
        </nav>
      </div>
    </header>
  )
}

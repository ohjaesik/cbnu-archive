import { Outlet } from 'react-router-dom'
import { GNB } from './GNB'

export function PageWrapper() {
  return (
    <div className="min-h-screen bg-gray-50">
      <GNB />
      <main className="mx-auto max-w-7xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}

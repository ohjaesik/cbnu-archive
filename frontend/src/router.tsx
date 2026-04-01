import { createBrowserRouter } from 'react-router-dom'
import { PageWrapper } from '@/components/layout/PageWrapper'
import { RequireAuth } from '@/components/layout/RequireAuth'
import Home from '@/pages/Home'
import Login from '@/pages/Login'
import ProjectList from '@/pages/ProjectList'
import ProjectDetail from '@/pages/ProjectDetail'
import ProjectUpload from '@/pages/ProjectUpload'
import ProjectEdit from '@/pages/ProjectEdit'
import MyProjects from '@/pages/MyProjects'
import Chat from '@/pages/Chat'
import AdminPendingList from '@/pages/admin/AdminPendingList'
import AdminReview from '@/pages/admin/AdminReview'
import AdminStats from '@/pages/admin/AdminStats'
import AdminMetadata from '@/pages/admin/AdminMetadata'

const router = createBrowserRouter([
  {
    path: '/',
    element: <PageWrapper />,
    children: [
      { index: true, element: <Home /> },
      { path: 'login', element: <Login /> },
      { path: 'projects', element: <ProjectList /> },
      { path: 'projects/:id', element: <ProjectDetail /> },

      // STUDENT 이상 접근 가능
      {
        element: <RequireAuth role="STUDENT" />,
        children: [
          { path: 'projects/new', element: <ProjectUpload /> },
          { path: 'projects/:id/edit', element: <ProjectEdit /> },
          { path: 'my-projects', element: <MyProjects /> },
          { path: 'chat', element: <Chat /> },
        ],
      },

      // ADMIN 전용
      {
        path: 'admin',
        element: <RequireAuth role="ADMIN" />,
        children: [
          { index: true, element: <AdminPendingList /> },
          { path: 'review/:id', element: <AdminReview /> },
          { path: 'stats', element: <AdminStats /> },
          { path: 'metadata', element: <AdminMetadata /> },
        ],
      },
    ],
  },
])

export default router

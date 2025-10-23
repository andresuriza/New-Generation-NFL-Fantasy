import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import Layout from './layout'
import Home from '../pages/home'
import Register from '../pages/register'
import Login from '../pages/login'
import PlayerProfile from '../pages/playerProfile'
import NotFound from '../pages/notFound' // si ya la creaste
import RequireAuth from './requireAuth'
import PlayerProfileEdit from '../pages/playerProfileEdit'
import LeagueCreate from '../pages/leagueCreate'
import LeagueAdminStatus from '../pages/leagueAdminStatus'
import LeagueConfigEdit from '../pages/leagueConfigEdit'


const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: '/', element: <Home /> },
      { path: '/register', element: <Register /> },
      { path: '/login', element: <Login /> },
      { path: '/player/profile', element: (
    <RequireAuth>
      <PlayerProfile />
    </RequireAuth>
) },
      { path: '/players', element: <div className="container" style={{ paddingTop: 24 }}>Próximamente: Explorador de jugadores</div> },
      { path: '*', element: <NotFound /> },
      { path: '/player/profile/edit', element: (
  <RequireAuth>
    <PlayerProfileEdit />
  </RequireAuth>
)},{ path: '/league/create', element: (
  <RequireAuth>
    <LeagueCreate />
  </RequireAuth>
)},{ path: '/league/:id/admin/status', element: (
  <RequireAuth>
    <LeagueAdminStatus />
  </RequireAuth>
)},{ path: '/league/:id/admin/config', element: (
  <RequireAuth>
    <LeagueConfigEdit />
  </RequireAuth>
)},
    ],
  },
])

export default function AppRoutes() {
  return <RouterProvider router={router} />
}

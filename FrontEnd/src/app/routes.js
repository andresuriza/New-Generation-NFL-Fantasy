import { createBrowserRouter, RouterProvider } from "react-router-dom";
import Layout from "./layout";
import Home from "../pages/home";
import Register from "../pages/usuario/register";
import Login from "../pages/shared/login";
import UserProfile from "../pages/usuario/userProfile";
import NotFound from "../pages/notFound"; // si ya la creaste
import RequireAuth from "./requireAuth";
import PlayerProfileEdit from "../pages/administrator/playerProfileEdit";
import LeagueCreate from "../pages/usuario/leagueCreate";
import LeagueAdminStatus from "../pages/usuario/leagueAdminStatus";
import LeagueConfigEdit from "../pages/usuario/leagueConfigEdit";
import UnlockConfirm from "../pages/shared/unlockConfirm";
import TeamPage from "../pages/usuario/TeamPage";
import CreateTeamPage from "../pages/administrator/CreateTeamPage";
import EditarEquipo from "../pages/administrator/EditarEquipo";
import SeasonCreate from "../pages/administrator/seasonCreate";
import LeagueJoin from "../pages/usuario/leagueJoin";
import CreatePlayerPage from "../pages/administrator/CreatePlayerForm";

const router = createBrowserRouter([
  {
    element: <Layout />,
    children: [
      { path: "/", element: <Home /> },
      { path: "/register", element: <Register /> },
      { path: "/login", element: <Login /> },
      { path: "/season/create", element: <SeasonCreate /> },
      { path: "/league/join", element: <LeagueJoin /> },
      {
        path: "/player/profile",
        element: (
          <RequireAuth>
            <UserProfile />
          </RequireAuth>
        ),
      },
      {
        path: "/players",
        element: (
          <div className="container" style={{ paddingTop: 24 }}>
            Próximamente: Explorador de jugadores
          </div>
        ),
      },
      { path: "/account/unlock/confirm", element: <UnlockConfirm /> },
      { path: "*", element: <NotFound /> },
      {
        path: "/player/profile/edit",
        element: (
          <RequireAuth>
            <PlayerProfileEdit />
          </RequireAuth>
        ),
      },
      {
        path: "/league/create",
        element: (
          <RequireAuth>
            <LeagueCreate />
          </RequireAuth>
        ),
      },
      {
        path: "/league/:id/admin/status",
        element: (
          <RequireAuth>
            <LeagueAdminStatus />
          </RequireAuth>
        ),
      },
      {
        path: "/league/:id/admin/config",
        element: (
          <RequireAuth>
            <LeagueConfigEdit />
          </RequireAuth>
        ),
      },

      {
        path: "/equipo/:id",
        element: <TeamPage />,
      },
      {
        path: "/equipo/:id/edit",
        element: <EditarEquipo />,
      },
      {
        path: "/crear-equipo",
        element: <CreateTeamPage />,
      },
      {
  path: "/create-player",
  element: (
    <RequireAuth>
      <CreatePlayerPage />
    </RequireAuth>
  ),
},

    ],
  },
]);

export default function AppRoutes() {
  return <RouterProvider router={router} />;
}

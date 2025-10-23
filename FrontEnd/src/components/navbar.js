import { NavLink } from "react-router-dom";
import { useAuth } from "../context/authContext";
import LogoutButton from "./logoutButton";

const linkClass = ({ isActive }) => `button ${isActive ? "" : "button--ghost"}`;

export default function Navbar() {
  const { isAuthenticated } = useAuth();

  return (
    <nav className="navbar">
      <div className="navbar__inner container">
        <div className="brand">
          <div className="brand__logo" />
          <div>
            <div className="brand__title">NFL Fantasy Team</div>
            <span className="badge">2025 • Season</span>
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          <NavLink className={linkClass} to="/">
            Home
          </NavLink>
          <NavLink className={linkClass} to="/players">
            Jugadores
          </NavLink>
          {!isAuthenticated ? (
            <>
              <NavLink className={linkClass} to="/register">
                Registrarse
              </NavLink>
              <NavLink className={linkClass} to="/login">
                Login
              </NavLink>
            </>
          ) : (
            <>
              <NavLink className={linkClass} to="/season/create">
                Temporada
              </NavLink>
              <NavLink className={linkClass} to="/player/profile">
                Perfil
              </NavLink>
              <LogoutButton className="button button--ghost">
                Cerrar sesión
              </LogoutButton>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}

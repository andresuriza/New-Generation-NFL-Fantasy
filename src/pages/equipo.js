import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContext"; // ajusta la ruta si tu archivo se llama AuthContext
import LogoutButton from "../components/logoutButton";
import { getProfile, getHistory, DEFAULTS } from "../utils/profileData";

export default function Equipo() {
  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <h1>Equipo</h1>
    </div>
  );
}

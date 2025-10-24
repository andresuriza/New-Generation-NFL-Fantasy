import { useMemo, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/authContext"; 
import { getProfile, getHistory, DEFAULTS } from "../../utils/profileData";
import { list as apiListEquipos } from "../../utils/communicationModule/resources/equipos";
import { list as apiListUsuarios } from "../../utils/communicationModule/resources/usuarios";
import { list as apiListLigas } from "../../utils/communicationModule/resources/ligas";

const DEFAULT_AVATAR = DEFAULTS.DEFAULT_AVATAR;

// ----- MOCKS VISUALES (sin backend) para ligas/equipos -----
function getMockCommissionerLeagues(email) {
  if ((email || "").toLowerCase() === "demo@nfl.com") {
    return [
      {
        id: "lg_123",
        name: "Liga TEC",
        season: 2024,
        teams: 10,
        scoring: "PPR",
      },
      {
        id: "lg_987",
        name: "Dynasty CR",
        season: 2024,
        teams: 12,
        scoring: "Half-PPR",
      },
    ];
  }
  return [];
}

// ----- Componentes UI auxiliares -----
function Field({ label, children }) {
  return (
    <div style={{ display: "grid", gap: 4 }}>
      <div style={{ fontSize: 12, color: "var(--muted)" }}>{label}</div>
      <div style={{ fontWeight: 600 }}>{children || "—"}</div>
    </div>
  );
}

function EmptyState({ title, subtitle, action }) {
  return (
    <div className="card" style={{ textAlign: "center", padding: 24 }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      <p style={{ color: "var(--muted)" }}>{subtitle}</p>
      {action}
    </div>
  );
}

export default function PlayerProfile() {
  const { session, isAuthenticated } = useAuth();
  const [teams, setTeams] = useState([]);
  const navigate = useNavigate();

  // Perfil y datos persistidos en localStorage (visual)
  const profile = useMemo(
    () => (session ? getProfile(session.email) : null),
    [session]
  );
  const history = useMemo(
    () => (session ? getHistory(session.email) : []),
    [session]
  );

  // Mocks de ligas/equipos (solo lectura)
  const commishLeagues = useMemo(
    () => (session ? getMockCommissionerLeagues(session.email) : []),
    [session]
  );

  useEffect(() => {
    let active = true;
    async function fetchTeams() {
      try {
        const [equiposApi, usuariosApi, ligasApi] = await Promise.all([
          apiListEquipos(),
          apiListUsuarios(),
          apiListLigas(),
        ]);
        if (!active) return;
        const usuariosMap = (Array.isArray(usuariosApi) ? usuariosApi : []).reduce((m, u) => {
          m[String(u.id)] = u.alias || u.nombre || u.correo;
          return m;
        }, {});
        const ligasMap = (Array.isArray(ligasApi) ? ligasApi : []).reduce((m, l) => {
          m[String(l.id)] = l.nombre;
          return m;
        }, {});

        const apiList = Array.isArray(equiposApi) ? equiposApi : [];
        const flat = apiList.map((team) => ({
          id: team.id,
          name: team.nombre,
          manager: usuariosMap[String(team.usuario_id)] || (team.usuario_id || "").toString().slice(0, 8),
          leagueName: ligasMap[String(team.liga_id)] || String(team.liga_id) || "Sin Liga",
        }));
        setTeams(flat);
      } catch (_) {
        setTeams([]);
      }
    }
    fetchTeams();
    return () => { active = false };
  }, [session]);

  if (!isAuthenticated || !profile) return null;

  const photo = profile.profileImage || DEFAULT_AVATAR;

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      {/* Header de perfil */}
      <div className="card" style={{ display: "grid", gap: 16 }}>
        <div
          style={{
            display: "flex",
            gap: 16,
            alignItems: "center",
            flexWrap: "wrap",
          }}
        >
          <img
            src={photo}
            alt="Foto de perfil"
            width={72}
            height={72}
            style={{
              width: 72,
              height: 72,
              borderRadius: 16,
              objectFit: "cover",
              border: "1px solid var(--border)",
            }}
            onError={(e) => {
              e.currentTarget.src = DEFAULT_AVATAR;
            }}
          />
          <div style={{ flex: 1, minWidth: 220 }}>
            <h2 style={{ margin: 0 }}>{profile.name}</h2>
            <div style={{ color: "var(--muted)", fontSize: 14 }}>
              {profile.email}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            <button
              className="button"
              onClick={() => navigate("/player/profile/edit")}
            >
              Editar perfil
            </button>
          </div>
        </div>

        {/* Datos del perfil */}
        <div
          className="grid"
          style={{ gridTemplateColumns: "repeat(4, minmax(0,1fr))" }}
        >
          <Field label="ID">
            {(session?.user && session.user.id) || profile.id}
          </Field>
          <Field label="Alias">
            {(session?.user && session.user.alias) || profile.alias}
          </Field>
          <Field label="Idioma">
            {(profile.language || "en").toUpperCase()}
          </Field>
          <Field label="Rol">{profile.role}</Field>
          <Field label="Estado">{profile.status}</Field>
          <Field label="Creado">
            {new Date(profile.createdAt).toLocaleString()}
          </Field>
          <Field label="Correo">{profile.email}</Field>
          <Field label="Nombre">{profile.name}</Field>
        </div>
      </div>

      {/* Ligas como comisionado */}
      <section style={{ marginTop: 24 }}>
        <h3 style={{ margin: "0 0 12px 0" }}>Ligas donde soy comisionado</h3>
        {commishLeagues.length === 0 ? (
          <EmptyState
            title="Aún no eres comisionado en ninguna liga"
            subtitle="Crea una liga o solicita el rol de comisionado a un administrador."
            action={<button className="button">Crear liga</button>}
          />
        ) : (
          <div className="grid grid-3">
            {commishLeagues.map((lg) => (
              <div key={lg.id} className="card">
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "baseline",
                  }}
                >
                  <h4 style={{ margin: 0 }}>{lg.name}</h4>
                  <span className="badge">{lg.season}</span>
                </div>
                <div style={{ marginTop: 8, color: "var(--muted)" }}>
                  {lg.teams} equipos • {lg.scoring}
                </div>
                <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                  <button
                    className="button"
                    onClick={() => navigate(`/league/${lg.id}`)}
                  >
                    Ver liga
                  </button>

                  <button
                    className="button button--ghost"
                    onClick={() => navigate(`/league/${lg.id}/admin/status`)}
                  >
                    Administrar estado
                  </button>

                  <button
                    className="button button--ghost"
                    onClick={() => navigate(`/league/${lg.id}/admin/config`)}
                  >
                    Configurar liga
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Mis equipos por liga */}
      <section style={{ marginTop: 24 }}>
        <h3 style={{ margin: "0 0 12px 0" }}>Mis equipos</h3>
        <div style={{ marginBottom: 22 }}>
          <button className="button" onClick={() => navigate("/crear-equipo")}>
            Crear equipo
          </button>
        </div>
        {teams.length === 0 ? (
          <EmptyState
            title="No tienes equipos aún"
            subtitle="Crea tu primer equipo utilizando el botón de arriba."
          />
        ) : (
          <div className="grid grid-3">
            {teams.map((tm) => (
              <div key={tm.id} className="card">
                <div style={{ marginBottom: 6, color: "var(--muted)" }}>
                  Liga: <strong>{tm.leagueName}</strong>
                </div>
                <h4 style={{ margin: 0 }}>{tm.name}</h4>
                <div style={{ marginTop: 6, color: "var(--muted)" }}>
                  Manager: <strong>{tm.manager}</strong>
                </div>
                <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                  <button
                    className="button"
                    onClick={() => navigate(`/equipo/${tm.id}`)}
                  >
                    Ver equipo
                  </button>
                  <button
                    className="button button--ghost"
                    onClick={() => navigate(`/equipo/${tm.id}/edit`)}
                  >
                    Gestionar
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Historial de cambios */}
      <section style={{ marginTop: 24 }}>
        <h3 style={{ margin: "0 0 12px 0" }}>Historial de cambios</h3>
        {history.length === 0 ? (
          <div className="card" style={{ padding: 16, color: "var(--muted)" }}>
            Aún no hay cambios registrados en tu perfil.
          </div>
        ) : (
          <div className="grid">
            {history.map((h) => (
              <div key={h.id} className="card">
                <div style={{ fontSize: 12, color: "var(--muted)" }}>
                  {new Date(h.at).toLocaleString()}
                </div>
                <ul style={{ margin: "8px 0 0", paddingLeft: 18 }}>
                  {h.changes.map((c, idx) => (
                    <li key={idx}>
                      <strong>{c.field}</strong>: “{String(c.oldValue)}” → “
                      {String(c.newValue)}”
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}

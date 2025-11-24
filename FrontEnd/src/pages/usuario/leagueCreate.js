// TODO: Revisar turnos disponibles

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  validateLeagueName,
  validateLeaguePasswordWrapper,
  validateTeamSize,
  validateCommissionerTeamName,
  LEAGUE_TEAM_SIZES,
} from "../../utils/leagueValidators";
import { CrearLiga } from "../../utils/communicationModule/resources/ligas";
import { fakeLeagueCreateVisual } from "../../utils/leagueNetwork";
import { useAuth } from "../../context/authContext";
import { GetTemporadaActual } from "../../utils/communicationModule/resources/temporadas";

const CURRENT_SEASON = 2025;

const DEFAULTS = {
  status: "Pre-Draft",
  tradeDeadlineActive: false,
  allowDecimals: true,
  maxSeasonTradesPerTeam: null, // sin límite
  maxSeasonFAAddsPerTeam: null, // sin límite
};

const PASS_PLACEHOLDER = "8–12, alfanumérica, con mayús/minús";
const WEEKS_BY_PLAYOFFS = {
  4: "Semanas 16–17",
  6: "Semanas 16–18",
};

export default function LeagueCreate() {
  const { user } = useAuth();
  const navigate = useNavigate();

  // Estado del formulario
  const [form, setForm] = useState({
    name: "",
    description: "",
    teams: 10,
    password: "",
    equipos_max: 0,
    playoffs_equipos: 0,
    puntajes_decimales: false,
    nombre_equipo_comisionado: "",
  });
  const [commishTeamName, setCommishTeamName] = useState("");
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [toast, setToast] = useState({ type: null, message: "" });

  // Cupos disponibles
  const availableSlots = useMemo(() => {
    const total = Number(form.teams) || 0;
    return Math.max(total - 1, 0);
  }, [form.teams]);

  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setToast({ type: null, message: "" });
  }

  function validateAll() {
    const e = {};
    const eName = validateLeagueName(form.name);
    if (eName) e.name = eName;
    const eSize = validateTeamSize(form.teams);
    if (eSize) e.teams = eSize;
    const ePass = validateLeaguePasswordWrapper(form.password);
    if (ePass) e.password = ePass;
    const eTeam = validateCommissionerTeamName(form.nombre_equipo_comisionado);
    if (eTeam) e.commishTeamName = eTeam;
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setToast({ type: null, message: "" });
    if (!validateAll()) return;

    //setSubmitting(true);

    // Autogenerados visuales
    const generated = {
      id: crypto.randomUUID ? crypto.randomUUID() : `lg_${Date.now()}`,
      createdAt: new Date().toISOString(),
      status: DEFAULTS.status,
      season: CURRENT_SEASON,
      tradeDeadlineActive: DEFAULTS.tradeDeadlineActive,
      maxSeasonTradesPerTeam: DEFAULTS.maxSeasonTradesPerTeam,
      maxSeasonFAAddsPerTeam: DEFAULTS.maxSeasonFAAddsPerTeam,
      allowDecimals: !!form.allowDecimals,
      playoffs: Number(form.playoffs), // 4 o 6
    };

    //console.log(form);

    try {
      const temporada = await GetTemporadaActual();

      const created = await CrearLiga({
        nombre: form.name,
        descripcion: form.description,
        contrasena: form.password,
        equipos_max: form.teams,
        playoffs_equipos: form.playoffs_equipos,
        puntajes_decimales: form.puntajes_decimales,
        nombre_equipo_comisionado: form.nombre_equipo_comisionado,
        temporada_id: temporada.id,
        comisionado_id: user?.id,
      });

      setSubmitting(false);

      // Éxito (visual): mostramos un resumen con datos devueltos por la “API”
      setToast({
        type: "ok",
        message:
          `Liga creada: ${form.name} • ID: ${generated.id} • ` +
          //`Cupos disponibles: ${res.data.remainingSlots}. ` +
          `Estado: ${generated.status} • Temporada: ${generated.season} • ` +
          `Playoffs: ${generated.playoffs} (${
            WEEKS_BY_PLAYOFFS[generated.playoffs]
          }).`,
      });

      // Redirigir a lo que indique la “API” visual
      setTimeout(() => navigate("/player/profile"), 900); // <-- cambio 2 (redirect_to)
      return;
    } catch (err) {
      setSubmitting(false);
      setToast({
        type: "err",
        message: err.message || "No se pudo crear la liga. Intenta de nuevo.",
      });
      return;
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 720, margin: "0 auto" }}>
        <h2 style={{ marginTop: 0 }}>Crear liga</h2>
        <form className="form" onSubmit={handleSubmit} noValidate>
          <div className="form__group">
            <label htmlFor="name">Nombre de la liga *</label>
            <input
              id="name"
              className={`input ${errors.name ? "input--invalid" : ""}`}
              value={form.name}
              onChange={(e) => setField("name", e.target.value)}
              maxLength={100}
              placeholder="Mi liga NFL"
            />
            {errors.name && <div className="error">{errors.name}</div>}
          </div>
          <div className="form__group">
            <label htmlFor="description">Descripción (opcional)</label>
            <textarea
              id="description"
              className="input"
              rows={3}
              value={form.description}
              onChange={(e) => setField("description", e.target.value)}
              placeholder="Reglas, notas, etc."
            />
          </div>
          <div className="form__group">
            <label htmlFor="password">Contraseña de la liga *</label>
            <input
              id="password"
              className={`input ${errors.password ? "input--invalid" : ""}`}
              type="password"
              value={form.password}
              onChange={(e) => setField("password", e.target.value)}
              maxLength={12}
              placeholder={PASS_PLACEHOLDER}
            />
            {errors.password && <div className="error">{errors.password}</div>}
          </div>
          <div className="form__group">
            <label htmlFor="teams">Cantidad de equipos maximo *</label>
            <select
              id="teams"
              className={`input ${errors.teams ? "input--invalid" : ""}`}
              value={form.teams}
              onChange={(e) => setField("teams", Number(e.target.value))}
            >
              {LEAGUE_TEAM_SIZES.map((n) => (
                <option key={n} value={n}>
                  {n}
                </option>
              ))}
            </select>
            {errors.teams && <div className="error">{errors.teams}</div>}
            <div className="help">
              Cupos disponibles luego de asignarte tu equipo:{" "}
              <strong>{availableSlots}</strong>
            </div>
          </div>
          <div className="form__group">
            <label>Formato de playoffs *</label>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              {[4, 6].map((n) => (
                <label
                  key={n}
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: 6,
                  }}
                >
                  <input
                    type="radio"
                    name="playoffs"
                    value={n}
                    checked={Number(form.playoffs_equipos) === n}
                    onChange={(e) =>
                      setField("playoffs_equipos", Number(e.target.value))
                    }
                  />
                  {n} equipos ({WEEKS_BY_PLAYOFFS[n]})
                </label>
              ))}
            </div>
          </div>
          <div
            className="form__group"
            style={{ display: "flex", alignItems: "center", gap: 8 }}
          >
            <input
              id="allowDecimals"
              type="checkbox"
              checked={!!form.puntajes_decimales}
              onChange={(e) => setField("puntajes_decimales", e.target.checked)}
            />
            <label htmlFor="allowDecimals">
              Permitir puntajes con decimales
            </label>
          </div>
          <div className="form__group">
            <label htmlFor="commishTeam">Nombre de tu equipo *</label>
            <input
              id="commishTeam"
              className={`input ${
                errors.commishTeamName ? "input--invalid" : ""
              }`}
              value={form.nombre_equipo_comisionado}
              onChange={(e) =>
                setField("nombre_equipo_comisionado", e.target.value)
              }
              maxLength={50}
              placeholder="Mi primer equipo"
            />
            {errors.commishTeamName && (
              <div className="error">{errors.commishTeamName}</div>
            )}
          </div>
          <fieldset className="card" style={{ borderColor: "var(--border)" }}>
            <legend style={{ color: "var(--muted)" }}>Se creará con</legend>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              <li>
                Estado: <strong>{DEFAULTS.status}</strong>
              </li>
              <li>
                Temporada actual: <strong>{CURRENT_SEASON}</strong>
              </li>
              <li>
                Trade deadline: <strong>inactivo</strong>
              </li>
              <li>
                Límites de temporada: <strong>sin límites</strong>
              </li>
              <li>
                Decimales: <strong>{form.allowDecimals ? "sí" : "no"}</strong>
              </li>
              <li>
                Comisionado principal: <strong>tú</strong>
              </li>
              <li>
                Tu equipo: <strong>{commishTeamName || "—"}</strong>
              </li>
            </ul>
          </fieldset>
          <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
            <button className="button button--accent" disabled={submitting}>
              {submitting ? "Creando…" : "Crear liga"}
            </button>
            <button
              type="button"
              className="button button--ghost"
              onClick={() => navigate(-1)}
              disabled={submitting}
            >
              Cancelar
            </button>
          </div>
          {toast.message && (
            <div
              className={`toast ${
                toast.type === "ok" ? "toast--ok" : "toast--err"
              }`}
              style={{ marginTop: 12 }}
            >
              {toast.message}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}

// src/pages/usuario/leagueJoin.js
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  validateAlias,
  validateName as validateTeamName,
} from "../../utils/validators";
import {
  GetLigas,
  JoinLiga,
} from "../../utils/communicationModule/resources/ligas";
import { GetTemporadaId } from "../../utils/communicationModule/resources/temporadas";
import { useAuth } from "../../context/authContext";

export default function LeagueJoin() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [s, setS] = useState("");
  const [status, setStatus] = useState("");
  const [results, setResults] = useState([]);
  const [selected, setSelected] = useState(null);
  const [name, setName] = useState("");
  const [alias, setAlias] = useState("");
  const [teamName, setTeamName] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [toast, setToast] = useState({ type: null, message: "" });
  const [ligas, setLigas] = useState([]);

  function searchLeaguesLocal({ q = "", s = "", status } = {}) {
    //console.log(status);
    const all = ligas;
    const qnorm = q.trim().toLowerCase();
    const sNorm = s.trim().toLowerCase();

    return all.filter((lg) => {
      const byQ = !qnorm || (lg.nombre || "").toLowerCase().includes(qnorm);
      const bySeason =
        !sNorm || (lg.temporada_name || "").toLowerCase().includes(sNorm);
      const byStatus =
        !status ||
        (lg.estado || "").toLowerCase() === String(status).toLowerCase();
      return byQ && bySeason && byStatus;
    });
  }

  useEffect(() => {
    document.title = "Buscar liga";
  }, []);

  useEffect(() => {
    async function GetLigasAPI() {
      try {
        const ligas_api_original = await GetLigas();
        const ligas_api = await Promise.all(
          ligas_api_original.map(async (e) => {
            try {
              const temporadaName = await GetTemporadaId(e.temporada_id);
              return {
                ...e,
                temporada_name: await temporadaName.nombre,
              };
            } catch (error) {
              console.error("Error obteniendo temporada");
              return { ...e, temporadaName: "Desconocido" };
            }
          })
        );
        setLigas(ligas_api);
      } catch (error) {
        console.error("Error fecthing ligas");
        setLigas([]);
      }
    }

    GetLigasAPI();
  }, []);

  function doSearch() {
    const list = searchLeaguesLocal({
      q,
      s,
      status: status || undefined,
    });
    setResults(list);
  }

  const seasonsInData = useMemo(() => {
    const uniq = new Set(results.map((r) => r.temporada_id).filter(Boolean));
    return Array.from(uniq).sort();
  }, [results]);

  function validateJoin() {
    const e = {};
    const eAlias = validateAlias(alias);
    if (eAlias) e.alias = eAlias;
    const eTeam = validateTeamName(teamName);
    if (eTeam)
      e.teamName =
        "Nombre de equipo: " + eTeam.replace("El nombre", "obligatorio y ≤ 50");
    if (!password || !password.trim())
      e.password = "Ingresa la contraseña de la liga.";
    setErrors(e);
    return Object.keys(e).length === 0;
  }

  async function handleJoin() {
    setToast({ type: null, message: "" });
    if (!selected) return;
    if (!validateJoin()) return;

    setLoading(true);
    try {
      const res = await JoinLiga({
        liga_id: selected.id,
        usuario_id: user.id,
        contrasena: password,
        alias: alias.trim(),
      });

      setLoading(false);
      setToast({
        type: "ok",
        message: `¡Te uniste a ${selected.nombre}!`,
      });
      setTimeout(() => navigate("/player/profile"), 900);
    } catch (err) {
      setLoading(false);
      setToast({
        type: "err",
        message: err?.message || "No fue posible unirse. Verifica los datos.",
      });
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ marginTop: 12 }}>
        <h3 style={{ marginTop: 0 }}>Unirse a liga</h3>
        <div
          className="grid"
          style={{ gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}
        >
          <div className="form__group">
            <label>Nombre liga*</label>
            <input
              className={`input ${errors.alias ? "input--invalid" : ""}`}
              value={name}
              onChange={(e) => setName(e.target.value)}
              maxLength={50}
            />
            {errors.alias && <div className="error">{errors.alias}</div>}
          </div>
          <div className="form__group">
            <label>Alias (opcional)</label>
            <input
              className={`input ${errors.alias ? "input--invalid" : ""}`}
              value={alias}
              onChange={(e) => setAlias(e.target.value)}
              maxLength={50}
            />
            {errors.alias && <div className="error">{errors.alias}</div>}
          </div>
          <div className="form__group">
            <label>Nombre de equipo *</label>
            <input
              className={`input ${errors.teamName ? "input--invalid" : ""}`}
              value={teamName}
              onChange={(e) => setTeamName(e.target.value)}
              maxLength={50}
            />
            {errors.teamName && <div className="error">{errors.teamName}</div>}
          </div>
          <div className="form__group">
            <label>Contraseña de la liga *</label>
            <input
              className={`input ${errors.password ? "input--invalid" : ""}`}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              maxLength={12}
            />
            {errors.password && <div className="error">{errors.password}</div>}
          </div>
        </div>

        <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
          <button
            className="button button--accent"
            onClick={handleJoin}
            disabled={loading}
          >
            {loading ? "Procesando…" : "Unirme"}
          </button>
          <button
            className="button button--ghost"
            onClick={() => setSelected(null)}
            disabled={loading}
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
      </div>
    </div>
  );
}

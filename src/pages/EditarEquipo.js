import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiGetEquipo, apiUpdateEquipo, apiGetEquipoMedia, apiUploadEquipoImage, apiListLigas } from "../utils/api";
import { useAuth } from "../context/authContext";

export default function EditarEquipo() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth() || {};

  const [teamName, setTeamName] = useState("");
  const [managerName, setManagerName] = useState("");
  const [leagueName, setLeagueName] = useState("");
  const [initialLigaId, setInitialLigaId] = useState("");
  const [ligas, setLigas] = useState([]);
  const [image, setImage] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [error, setError] = useState("");
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Load existing team and ligas
  useEffect(() => {
    let isMounted = true;
    async function load() {
      setLoading(true);
      setError("");
      try {
        // fetch ligas in parallel
        const ligasPromise = apiListLigas().catch(() => []);
        const equipo = await apiGetEquipo(id);
        if (!equipo) throw new Error("Equipo no encontrado");
        // Backend shape: { id, liga_id, usuario_id, nombre, thumbnail?, creado_en, actualizado_en }
        if (!isMounted) return;
  setTeamName(equipo.nombre || "");
        // We don't have manager/league names in this endpoint; keep local placeholders
        setManagerName(user?.alias || user?.nombre || "");
        // set league id for selection; we'll show names in a dropdown
  setLeagueName(equipo.liga_id || "");
  setInitialLigaId(equipo.liga_id || "");

        // resolve ligas and set state
        const ligasRes = await ligasPromise;
        if (Array.isArray(ligasRes)) setLigas(ligasRes);

        // Try to get media thumbnail
        try {
          const media = await apiGetEquipoMedia(id);
          if (isMounted && media?.url) setThumbnail(media.url);
        } catch (_) {
          // ignore if no media
        }

        // Load existing local logs for UX continuity
        const storedLogs = JSON.parse(localStorage.getItem("team_change_log") || "[]");
        const teamLogs = storedLogs
          .filter((l) => l.teamId === id)
          .sort((a, b) => new Date(b.when) - new Date(a.when));
        if (isMounted) setLogs(teamLogs);
      } catch (e) {
        if (!isMounted) return;
        setError(e?.message || "No se pudo cargar el equipo");
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    load();
    return () => { isMounted = false };
  }, [id, user]);

  const handleImageChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file
    if (!["image/jpeg", "image/png", "image/webp"].includes(file.type)) {
      setError("Formato invalido, utilizar JPEG/PNG/WEBP.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Imagen muy grande (max 5MB).");
      return;
    }

    setImage(file);

    try {
      // Upload to backend and use returned URL
      const media = await apiUploadEquipoImage(id, file);
      if (media?.url) {
        setThumbnail(media.url);
        // Persist thumbnail into equipo as well (if backend supports it)
        try {
          await apiUpdateEquipo(id, { thumbnail: media.url });
        } catch (err) {
          // non-fatal, media already uploaded and preview updated
          console.warn('No se pudo actualizar thumbnail del equipo:', err?.message || err);
        }
      }
    } catch (err) {
      setError(err?.message || "No se pudo subir la imagen");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validations
    if (teamName.length < 1 || teamName.length > 100) {
      setError("El nombre del equipo debe estar entre 1 y 100 caracteres.");
      return;
    }
    // Manager/league display only for now (backend EquipoUpdate solo permite nombre)

    try {
      const payload = { nombre: teamName };
      if (initialLigaId && leagueName && leagueName !== initialLigaId) {
        payload.liga_id = leagueName;
      }
      const updated = await apiUpdateEquipo(id, payload);
      // If an image was selected, it was already uploaded in handleImageChange

      // Log the change (local UX)
      const prevLogs = JSON.parse(localStorage.getItem("team_change_log") || "[]");
      const newLog = {
        teamId: id,
        who: managerName || user?.alias || user?.nombre || "usuario",
        what: "Se actualizó información del equipo",
        why: "Editado mediante form",
        when: new Date().toISOString(),
      };
      const allLogs = [newLog, ...prevLogs];
      localStorage.setItem("team_change_log", JSON.stringify(allLogs));
      setLogs((cur) => [newLog, ...cur]);

      alert("Equipo actualizado con éxito!");
      navigate("/player/profile");
    } catch (err) {
      setError(err?.message || "No se pudo actualizar el equipo");
    }
  };

  return (
    <div className="container create-team-page">
      <h2 className="section-title">Actualizar equipo</h2>
      {loading && <div className="toast">Cargando...</div>}
      <form className="card form" onSubmit={handleSubmit}>
        <div className="form__group">
          <label>Nombre de equipo</label>
          <input
            type="text"
            className="input"
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            placeholder="Ingresar nombre de equipo..."
          />
        </div>

        <div className="form__group">
          <label>Manager</label>
          <input
            type="text"
            className="input"
            value={managerName}
            onChange={(e) => setManagerName(e.target.value)}
            placeholder="Ingresar nombre de manager..."
          />
        </div>

        <div className="form__group">
          <label>Liga</label>
          <select
            className="input"
            value={leagueName}
            onChange={(e) => setLeagueName(e.target.value)}
            title="Selecciona la liga del equipo"
          >
            {ligas.length === 0 && (
              <option value="">Cargando ligas…</option>
            )}
            {ligas.map((l) => (
              <option key={l.id} value={l.id}>
                {l.nombre}
              </option>
            ))}
          </select>
        </div>

        <div className="form__group">
          <label>Imagen de equipo (JPEG/PNG, max 5MB)</label>
          <input type="file" accept="image/*" onChange={handleImageChange} />
        </div>

        {thumbnail && (
          <div className="thumbnail-preview">
            <p>Thumbnail generado:</p>
            <img src={thumbnail} alt="Thumbnail preview" />
          </div>
        )}

        {error && <div className="toast toast--err">{error}</div>}

        <button type="submit" className="button button--accent">
          Editar equipo
        </button>
      </form>

      <div className="card changelog">
        <h3>Log de cambios</h3>
        {logs.length === 0 ? (
          <p className="muted">Sin acciones registradas.</p>
        ) : (
          <ul>
            {logs.map((log, idx) => (
              <li key={idx}>
                <strong>{log.who}</strong> — {log.what} <br />
                <span className="why">{log.why}</span>
                <div className="timestamp">{log.when}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

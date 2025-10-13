import { useEffect, useMemo, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { apiRegisterEquipo, apiListLigas, apiUploadEquipoImage, apiUpdateEquipo } from "../utils/api";
import { useAuth } from "../context/authContext";

export default function CreateTeamPage() {
  const { user, isAuthenticated } = useAuth() || {};
  const [teamName, setTeamName] = useState("");
  // Manager is always the logged-in user (enforced)
  const managerName = useMemo(() => user?.alias || user?.nombre || user?.correo || "", [user]);
  const [ligaId, setLigaId] = useState("");
  const [ligas, setLigas] = useState([]);
  const [image, setImage] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [error, setError] = useState("");
  const [log, setLog] = useState([]);

  const teamId = uuidv4();

  // Usar para borrar equipos
  //localStorage.clear();

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate format
    const validTypes = ["image/jpeg", "image/png"];
    if (!validTypes.includes(file.type)) {
      setError("Formato invalido, utilizar JPEG o PNG.");
      setImage(null);
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError("Imagen muy grande (max 5MB).");
      setImage(null);
      return;
    }

    // Validate dimensions
    const img = new Image();
    img.onload = () => {
      if (
        img.width < 300 ||
        img.height < 300 ||
        img.width > 1024 ||
        img.height > 1024
      ) {
        setError(
          "Las dimensiones de la imagen deben estar entre 300x300 y 1024x1024 px."
        );
        setImage(null);
      } else {
        setError("");
        setImage(file);

        // Generate thumbnail automatically
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d");
        const scale = 100 / Math.max(img.width, img.height);
        canvas.width = img.width * scale;
        canvas.height = img.height * scale;
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        const thumbData = canvas.toDataURL("image/jpeg", 0.8);
        setThumbnail(thumbData);
      }
    };
    img.src = URL.createObjectURL(file);
  };

  // Load available ligas
  useEffect(() => {
    let alive = true
    async function load() {
      try {
        const data = await apiListLigas()
        if (alive) setLigas(Array.isArray(data) ? data : [])
      } catch {
        if (alive) setLigas([])
      }
    }
    load()
    return () => { alive = false }
  }, [])

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    // Validations
    if (!isAuthenticated || !user?.id) {
      setError("Debes iniciar sesión para crear un equipo.");
      return;
    }
    if (teamName.length < 1 || teamName.length > 100) {
      setError("El nombre del equipo debe estar entre 1 y 100 caracteres.");
      return;
    }
    if (!ligaId) {
      setError("Debes seleccionar una liga.");
      return;
    }
    if (!image) {
      setError("Una imagen valida debe ser subida.");
      return;
    }

    try {
      // Create equipo on backend
      const created = await apiRegisterEquipo({
        liga_id: ligaId,
        usuario_id: user.id,
        nombre: teamName,
        thumbnail: null,
      })

      // Upload image and persist thumbnail url
      try {
        const media = await apiUploadEquipoImage(created.id, image)
        if (media?.url) {
          await apiUpdateEquipo(created.id, { thumbnail: media.url })
          setThumbnail(media.url)
        }
      } catch (_err) {
        // non-fatal
      }

      // Local UX log (optional)
      const prevLogs = JSON.parse(localStorage.getItem("team_change_log") || "[]")
      const entry = {
        teamId: created.id,
        who: managerName,
        what: `Equipo creado: "${teamName}"`,
        why: "Registro equipo nuevo",
        when: new Date().toLocaleString(),
      }
      const allLogs = [entry, ...prevLogs]
      localStorage.setItem("team_change_log", JSON.stringify(allLogs))
      setLog(allLogs)

      alert(`Equipo "${teamName}" creado!`)
    } catch (err) {
      setError(err?.message || "No se pudo crear el equipo.")
    }
  };

  return (
    <div className="container create-team-page">
      <h2 className="section-title">Crear equipo nuevo</h2>

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
          <input type="text" className="input" value={managerName} readOnly />
          <small className="help">El manager es el usuario autenticado.</small>
        </div>

        <div className="form__group">
          <label>Liga</label>
          <select
            className="input"
            value={ligaId}
            onChange={(e) => setLigaId(e.target.value)}
          >
            <option value="">Selecciona una liga…</option>
            {ligas.map((l) => (
              <option key={l.id} value={l.id}>{l.nombre}</option>
            ))}
          </select>
        </div>

        <div className="form__group">
          <label>Imagen de equipo (JPEG/PNG, max 5MB)</label>
          <input type="file" accept="image/*" onChange={handleImageUpload} />
        </div>

        {thumbnail && (
          <div className="thumbnail-preview">
            <p>Thumbnail generado:</p>
            <img src={thumbnail} alt="Thumbnail preview" />
          </div>
        )}

        {error && <div className="toast toast--err">{error}</div>}

        <button type="submit" className="button button--accent">
          Crear equipo
        </button>
      </form>

      <div className="card changelog">
        <h3>Log de cambios</h3>
        {log.length === 0 ? (
          <p className="muted">Sin acciones registradas.</p>
        ) : (
          <ul>
            {log.map((entry, idx) => (
              <li key={idx}>
                <strong>{entry.who}</strong> — {entry.what} <br />
                <span className="why">{entry.why}</span>
                <div className="timestamp">{entry.when}</div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

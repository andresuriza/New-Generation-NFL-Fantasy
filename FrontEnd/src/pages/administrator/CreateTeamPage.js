import { useEffect, useMemo, useState } from "react";
import {
  postNFLTeam,
  update as apiUpdateEquipo,
} from "../../utils/communicationModule/resources/equipos";
import { GetLigas as apiListLigas } from "../../utils/communicationModule/resources/ligas";
import { uploadEquipoImage as apiUploadEquipoImage } from "../../utils/communicationModule/resources/media";
import { useAuth } from "../../context/authContext";

export default function CreateTeamPage() {
  const { user, isAuthenticated } = useAuth() || {};
  const [teamName, setTeamName] = useState("");
  const [cityName, setCityName] = useState("");
  const managerName = useMemo(
    () => user?.alias || user?.nombre || user?.correo || "",
    [user]
  );
  const [ligaId, setLigaId] = useState("");
  const [ligas, setLigas] = useState([]);
  const [image, setImage] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [error, setError] = useState("");
  const [log, setLog] = useState([]);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const validTypes = ["image/jpeg", "image/png"];
    if (!validTypes.includes(file.type)) {
      setError("Formato invalido, utilizar JPEG o PNG.");
      setImage(null);
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError("Imagen muy grande (max 5MB).");
      setImage(null);
      return;
    }

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

  useEffect(() => {
    let alive = true;
    async function load() {
      try {
        const data = await apiListLigas();
        if (alive) setLigas(Array.isArray(data) ? data : []);
      } catch {
        if (alive) setLigas([]);
      }
    }
    load();
    return () => {
      alive = false;
    };
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!isAuthenticated || !user?.id) {
      setError("Debes iniciar sesión para crear un equipo.");
      return;
    }
    if (teamName.length < 1 || teamName.length > 100) {
      setError("El nombre del equipo debe estar entre 1 y 100 caracteres.");
      return;
    }
    if (!image) {
      setError("Una imagen valida debe ser subida.");
      return;
    }

    try {
      // Create equipo on backend
      const created = await postNFLTeam({
        nombre: teamName,
        ciudad: cityName,
        thumbnail: thumbnail,
      });

      // Upload image and persist thumbnail url
      try {
        const media = await apiUploadEquipoImage(created.id, image);
        if (media?.url) {
          await apiUpdateEquipo(created.id, { thumbnail: media.url });
          setThumbnail(media.url);
        }
      } catch (_err) {
        // non-fatal
      }

      // Local UX log (optional)
      const prevLogs = JSON.parse(
        localStorage.getItem("team_change_log") || "[]"
      );
      const entry = {
        teamId: created.id,
        who: managerName,
        what: `Equipo creado: "${teamName}"`,
        why: "Registro equipo nuevo",
        when: new Date().toLocaleString(),
      };
      const allLogs = [entry, ...prevLogs];
      localStorage.setItem("team_change_log", JSON.stringify(allLogs));
      setLog(allLogs);

      alert(`Equipo "${teamName}" creado!`);
    } catch (err) {
      setError(err?.message || "No se pudo crear el equipo.");
    }
  };

  return (
    <div className="container create-team-page">
      <h2 className="section-title">Crear equipo NFL</h2>

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
          <label>Ciudad</label>
          <input
            type="text"
            className="input"
            value={cityName}
            onChange={(e) => setCityName(e.target.value)}
            placeholder="Ingresar ciudad..."
          />
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

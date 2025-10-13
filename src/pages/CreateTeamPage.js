import { useState } from "react";
import { v4 as uuidv4 } from "uuid";

export default function CreateTeamPage() {
  const [teamName, setTeamName] = useState("");
  const [managerName, setManagerName] = useState("");
  const [leagueName, setLeagueName] = useState("");
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

  const teams = JSON.parse(localStorage.getItem("fantasy_teams") || "[]");
  const logs = JSON.parse(localStorage.getItem("team_change_log") || "[]");

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    // Check for duplicates inside the same league (case-insensitive)
    const nameTaken = teams.some(
      (t) =>
        t.league.trim().toLowerCase() === leagueName.trim().toLowerCase() &&
        t.name.trim().toLowerCase() === teamName.trim().toLowerCase()
    );

    // Validations
    if (teamName.length < 1 || teamName.length > 100) {
      setError("El nombre del equipo debe estar entre 1 y 100 caracteres.");
      return;
    }

    if (nameTaken) {
      setError(`El nombre "${teamName}" ya existe en esta liga.`);
      return;
    }

    if (!managerName.trim()) {
      setError("El nombre del manager es requerido.");
      return;
    }
    if (!leagueName.trim()) {
      setError("El nombre de la liga es requerido.");
      return;
    }
    if (!image) {
      setError("Una imagen valida debe ser subida.");
      return;
    }

    // Create team object
    const newTeam = {
      id: teamId,
      name: teamName,
      manager: managerName,
      league: leagueName,
      image: thumbnail,
      state: "Activo",
      players: [],
      createdAt: new Date().toISOString(),
    };

    teams.push(newTeam);
    localStorage.setItem("fantasy_teams", JSON.stringify(teams));

    // Log change
    const entry = {
      teamId: teamId,
      who: managerName,
      what: `Equipo creado: "${teamName}"`,
      why: "Registro equipo nuevo",
      when: new Date().toLocaleString(),
    };
    setLog([...log, entry]);

    logs.push(entry);
    localStorage.setItem("team_change_log", JSON.stringify(logs));

    alert(`Equipo "${teamName}" creado!`);
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
          <input
            type="text"
            className="input"
            value={leagueName}
            onChange={(e) => setLeagueName(e.target.value)}
            placeholder="Ingresar nombre de liga.."
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

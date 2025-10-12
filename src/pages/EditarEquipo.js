import { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";

export default function EditarEquipo() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [teamName, setTeamName] = useState("");
  const [managerName, setManagerName] = useState("");
  const [leagueName, setLeagueName] = useState("");
  const [image, setImage] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [error, setError] = useState("");
  const [logs, setLogs] = useState([]);

  // Load existing team
  useEffect(() => {
    const stored = JSON.parse(localStorage.getItem("fantasy_teams") || "[]");
    const found = stored.find((t) => t.id === id);

    if (!found) {
      setError("Equipo no encontrado.");
      return;
    }

    setTeamName(found.name);
    setManagerName(found.manager);
    setLeagueName(found.league);
    setThumbnail(found.image);

    // Load existing logs
    const storedLogs = JSON.parse(
      localStorage.getItem("team_change_log") || "[]"
    );
    const teamLogs = storedLogs
      .filter((l) => l.teamId === id)
      .sort((a, b) => new Date(b.when) - new Date(a.when)); // newest first

    console.log(storedLogs);

    setLogs(teamLogs);
  }, [id]);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setError("Formato invalido, utilizar JPEG o PNG.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Imagen muy grande (max 5MB).");
      return;
    }

    const reader = new FileReader();
    reader.onload = (ev) => setThumbnail(ev.target.result);
    reader.readAsDataURL(file);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    const teams = JSON.parse(localStorage.getItem("fantasy_teams") || "[]");
    // Validate duplicate name (excluding current team)
    // Check for duplicates inside the same league (case-insensitive)
    const duplicate = teams.some(
      (t) =>
        t.id !== id &&
        t.league.trim().toLowerCase() === leagueName.trim().toLowerCase() &&
        t.name.trim().toLowerCase() === teamName.trim().toLowerCase()
    );
    if (duplicate) {
      setError(`El nombre "${teamName}" ya existe en esta liga.`);
      return;
    }

    // Validations
    if (teamName.length < 1 || teamName.length > 100) {
      setError("El nombre del equipo debe estar entre 1 y 100 caracteres.");
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

    // Update the team
    const updated = teams.map((t) =>
      t.id === id
        ? {
            ...t,
            name: teamName,
            manager: managerName,
            league: leagueName,
            image: thumbnail,
            updatedAt: new Date().toISOString(),
          }
        : t
    );

    localStorage.setItem("fantasy_teams", JSON.stringify(updated));

    // Log the change
    const logs = JSON.parse(localStorage.getItem("team_change_log") || "[]");
    const newLog = {
      teamId: id,
      who: managerName,
      what: "Se actualizó información del equipo",
      why: "Editado mediante form",
      when: new Date().toISOString(),
    };
    const allLogs = [...logs, newLog];
    localStorage.setItem("team_change_log", JSON.stringify(allLogs));
    setLogs([newLog, ...logs]);

    alert("Equipo actualizado con exito!");
    navigate("/player/profile");
  };

  return (
    <div className="container create-team-page">
      <h2 className="section-title">Actualizar equipo</h2>
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

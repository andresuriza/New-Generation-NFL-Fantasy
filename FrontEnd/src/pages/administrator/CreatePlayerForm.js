import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/global.css";
import { list } from "../../utils/communicationModule/resources/equipos.js";
import { postPlayer, postPlayers } from "../../utils/communicationModule/resources/players.js";

export default function CreateNflPlayerForm() {
  // Estado del formulario
  const [form, setForm] = useState({
    nombre: "",
    posicion: "",
    equipo_id: "",
    imagen_url: "",
    thumbnail_url: "",
    activo: true,
  });

  // Lista de equipos
  const [teams, setTeams] = useState([]);

  // Notificaciones
  const [toast, setToast] = useState({ type: null, message: "" });

  // Estado general
  const [status, setStatus] = useState("");

  // Navegación
  const navigate = useNavigate();

  // Archivo JSON
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");
  const [jsonData, setJsonData] = useState(null);

  // Maneja el archivo JSON cargado
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        setJsonData(data);
        setStatus("JSON cargado correctamente");
      } catch (err) {
        setStatus("Archivo JSON inválido");
      }
    };
    reader.readAsText(file);
  };

  // Sube los datos del JSON
  const handleUpload = async () => {
    if (!jsonData) {
      setStatus("Debe seleccionar un archivo JSON válido");
      return;
    }

    try {
      await postPlayers({ jugadores: jsonData, filename: fileName });
      alert("Jugadores creados con éxito");
    } catch (err) {
      setError(err?.message || "Error al subir archivo");
    }
  };

  // Actualiza los campos del formulario
  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setToast({ type: null, message: "" });
  }

  // Carga los equipos
  useEffect(() => {
    async function GetTeams() {
      try {
        const [teams] = await Promise.all([list()]);
        setTeams(teams);
      } catch (_) {
        setTeams([]);
      }
    }

    GetTeams();
  }, []);

  // Posiciones disponibles
  const examplePositions = ["QB", "RB", "WR", "TE", "K", "DEF"];

  // Maneja submit del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      await postPlayer({
        nombre: form.nombre,
        posicion: form.posicion,
        equipo_id: form.equipo_id,
        imagen_url: form.imagen_url,
        thumbnail_url: form.imagen_url,
        activo: form.activo,
      });

      alert(`Jugador "${form.nombre}" creado`);
    } catch (err) {
      setError(err?.message || "No se pudo crear el jugador");
    }
  };

  return (
    <div className="nfl-player-form-wrapper">
      <div className="card nfl-player-form">
        <div className="card-header">
          <h2 className="nfl-player-form__title">Creación manual de jugador NFL</h2>
          <p className="nfl-player-form__subtitle">
            Como administrador puedes crear jugadores NFL manualmente para gestionar sus datos.
          </p>
        </div>

        <form className="card-body nfl-player-form__body" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="player-name" className="form-label">
              Nombre del jugador <span className="required">*</span>
            </label>
            <input
              id="player-name"
              type="text"
              required
              className="form-input"
              placeholder="Ej. Patrick Mahomes"
              value={form.nombre}
              onChange={(e) => setField("nombre", e.target.value)}
            />
          </div>

          <div className="form-field">
            <label htmlFor="player-position" className="form-label">
              Posición <span className="required">*</span>
            </label>
            <select
              id="player-position"
              required
              className="form-select"
              onChange={(e) => setField("posicion", e.target.value)}
              value={form.posicion}
            >
              <option value="" disabled>Selecciona una posición</option>
              {examplePositions.map((pos) => (
                <option key={pos} value={pos}>{pos}</option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="player-team" className="form-label">
              Equipo NFL <span className="required">*</span>
            </label>
            <select
              id="player-team"
              required
              className="form-select"
              onChange={(e) => setField("equipo_id", e.target.value)}
              value={form.equipo_id}
            >
              <option value="" disabled>Selecciona un equipo</option>
              {teams.map((team) => (
                <option key={team.id} value={team.id}>{team.nombre}</option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label htmlFor="player-image" className="form-label">
              URL de imagen <span className="required">*</span>
            </label>
            <input
              id="player-img"
              type="url"
              required
              className="form-input"
              value={form.imagen_url}
              onChange={(e) => setField("imagen_url", e.target.value)}
            />
          </div>

          {form.imagen_url && (
            <div className="form-field nfl-player-form__thumbnail">
              <span className="form-label">Vista previa</span>
              <div className="nfl-player-form__thumbnail-box">
                <img src={form.imagen_url} alt="Vista previa del jugador" />
              </div>
            </div>
          )}

          <div className="form-field form-field--inline">
            <label className="form-checkbox">
              <input
                type="checkbox"
                checked={form.activo}
                onChange={(e) => setField("activo", e.target.checked)}
              />
              <span>Jugador activo</span>
            </label>
          </div>

          {error && <div className="toast toast--err">{error}</div>}

          <div className="form-actions">
            <button type="submit" className="button">Guardar jugador</button>
            <button type="button" className="button button--ghost" onClick={() => navigate(-1)}>
              Cancelar
            </button>
          </div>
        </form>

        <div className="form-field">
          <p>O bien, subir archivo JSON con jugadores:</p>
          <input type="file" accept=".json" onChange={handleFileChange} />
          <button className="button" onClick={handleUpload}>Subir</button>
          {status && <p>{status}</p>}
        </div>
      </div>
    </div>
  );
}

// src/components/CreateNflPlayerForm.js
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/global.css";
import { list } from "../../utils/communicationModule/resources/equipos.js";
import {
  postPlayer,
  postPlayers,
} from "../../utils/communicationModule/resources/players.js";

function CreateNflPlayerForm() {
  const [form, setForm] = useState({
    nombre: "",
    posicion: "",
    equipo_id: "",
    imagen_url: "",
    thumbnail_url: "",
    activo: true,
  });
  const [teams, setTeams] = useState([]);
  const [toast, setToast] = useState({ type: null, message: "" });
  const [status, setStatus] = useState("");

  const navigate = useNavigate();

  // Solo usamos estado para la vista previa del thumbnail
  const [imageUrl, setImageUrl] = useState("");
  const [error, setError] = useState("");
  const [fileName, setFileName] = useState("");
  const [jsonData, setJsonData] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target.result);
        setJsonData(data);
        setStatus("JSON loaded successfully!");
      } catch (err) {
        console.error("Invalid JSON:", err);
        setStatus("Invalid JSON file");
      }
    };
    reader.readAsText(file);
  };

  const handleUpload = async () => {
    if (!jsonData) {
      setStatus("Please select a valid JSON file first.");
      return;
    }

    try {
      const response = await postPlayers({
        jugadores: jsonData,
        filename: fileName,
      });
      alert("Jugadores creados con éxito!");
    } catch (err) {
      setError(err?.message || "Error al subir archivo");
    }
  };

  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setToast({ type: null, message: "" });
  }

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

  // Datos de ejemplo (luego los puedes traer del backend o props)
  const examplePositions = ["QB", "RB", "WR", "TE", "K", "DEF"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      const created = await postPlayer({
        nombre: form.nombre,
        posicion: form.posicion,
        equipo_id: form.equipo_id,
        imagen_url: form.imagen_url,
        thumbnail_url: form.imagen_url,
        activo: form.activo,
      });

      alert(`Jugador "${form.nombre}" creado!`);
    } catch (err) {
      setError(err?.message || "No se pudo crear el jugador.");
    }
  };

  return (
    <div className="nfl-player-form-wrapper">
      <div className="card nfl-player-form">
        {/* Header */}
        <div className="card-header">
          <h2 className="nfl-player-form__title">
            Creación manual de jugador NFL
          </h2>
          <p className="nfl-player-form__subtitle">
            Como administrador puedes crear jugadores NFL manualmente para
            gestionar sus datos en la plataforma.
          </p>
        </div>

        {/* Body */}
        <form
          className="card-body nfl-player-form__body"
          onSubmit={handleSubmit}
        >
          {/* Nombre */}
          <div className="form-field">
            <label htmlFor="player-name" className="form-label">
              Nombre del jugador <span className="required">*</span>
            </label>
            <input
              id="player-name"
              name="name"
              type="text"
              required
              className="form-input"
              placeholder="Ej. Patrick Mahomes"
              value={form.nombre}
              onChange={(e) => setField("nombre", e.target.value)}
            />
            <small className="form-help">
              Usa el nombre oficial del jugador para evitar duplicados.
            </small>
          </div>

          {/* Posición */}
          <div className="form-field">
            <label htmlFor="player-position" className="form-label">
              Posición <span className="required">*</span>
            </label>
            <select
              id="player-position"
              name="position"
              required
              className="form-select"
              onChange={(e) => setField("posicion", e.target.value)}
              value={form.posicion}
            >
              <option value="" disabled>
                Selecciona una posición
              </option>
              {examplePositions.map((pos) => (
                <option key={pos} value={pos}>
                  {pos}
                </option>
              ))}
            </select>
          </div>

          {/* Equipo NFL */}
          <div className="form-field">
            <label htmlFor="player-team" className="form-label">
              Equipo NFL <span className="required">*</span>
            </label>
            <select
              id="player-team"
              name="team"
              required
              className="form-select"
              onChange={(e) => setField("equipo_id", e.target.value)}
              value={form.equipo_id}
            >
              <option value="" disabled>
                Selecciona un equipo
              </option>
              {/* Cambiar aqui */}
              {teams.map((team) => (
                <option key={team.id} value={team.id}>
                  {team.nombre}
                </option>
              ))}
            </select>
            <small className="form-help">
              Solo se muestran equipos existentes en la liga.
            </small>
          </div>

          {/* Imagen */}
          <div className="form-field">
            <label htmlFor="player-image" className="form-label">
              URL de imagen <span className="required">*</span>
            </label>
            <input
              id="player-img"
              name="image"
              type="url"
              required
              className="form-input"
              value={form.imagen_url}
              onChange={(e) => setField("imagen_url", e.target.value)}
            />
          </div>

          {/* Thumbnail generado (vista previa) */}
          {form.imagen_url && (
            <div className="form-field nfl-player-form__thumbnail">
              <span className="form-label">Thumbnail generado</span>
              <div className="nfl-player-form__thumbnail-box">
                <img src={form.imagen_url} alt="Vista previa del jugador" />
              </div>
            </div>
          )}

          {/* Estado activo */}
          <div className="form-field form-field--inline">
            <label className="form-checkbox">
              <input
                type="checkbox"
                name="isActive"
                checked={form.activo}
                onChange={(e) => setField("activo", e.target.checked)}
              />
              <span>Jugador activo</span>
            </label>
            <small className="form-help">
              Los jugadores nuevos se crean activos por defecto.
            </small>
          </div>

          {/* Notas / criterios visuales */}
          <div className="nfl-player-form__info-box">
            <p className="nfl-player-form__info-title">Notas</p>
            <ul className="nfl-player-form__info-list">
              <li>Todos los campos marcados con * son obligatorios.</li>
              <li>Antes de guardar se validarán los datos requeridos.</li>
              <li>
                Si el nombre del jugador ya existe para el mismo equipo NFL se
                mostrará un mensaje y no se creará el registro.
              </li>
            </ul>
          </div>
          {error && <div className="toast toast--err">{error}</div>}

          {/* Botones */}
          <div className="form-actions">
            <button type="submit" className="button">
              Guardar jugador
            </button>
            <button
              type="button"
              className="button button--ghost"
              onClick={() => navigate(-1)}
            >
              Cancelar
            </button>
          </div>
        </form>
        <div className="form-field">
          <p>O bien, subir archivo JSON con jugadores: </p>
          <input type="file" accept=".json" onChange={handleFileChange} />
          <button className="button" onClick={handleUpload}>
            Subir
          </button>
          {status && <p>{status}</p>}
        </div>
      </div>
    </div>
  );
}

export default CreateNflPlayerForm;

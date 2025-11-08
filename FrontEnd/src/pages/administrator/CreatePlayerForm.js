// src/components/CreateNflPlayerForm.js
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../../styles/global.css";

function CreateNflPlayerForm() {
  const navigate = useNavigate();

  // Solo usamos estado para la vista previa del thumbnail
  const [imageUrl, setImageUrl] = useState("");

  // Datos de ejemplo (luego los puedes traer del backend o props)
  const examplePositions = ["QB", "RB", "WR", "TE", "K", "DEF"];
  const exampleTeams = [
    "Arizona Cardinals",
    "Atlanta Falcons",
    "Baltimore Ravens",
    "Buffalo Bills",
    "Carolina Panthers",
    "Chicago Bears",
  ];

  const handleSubmit = (e) => {
    e.preventDefault();
    // Meramente visual por ahora
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
        <form className="card-body nfl-player-form__body" onSubmit={handleSubmit}>
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
              defaultValue=""
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
              defaultValue=""
            >
              <option value="" disabled>
                Selecciona un equipo
              </option>
              {exampleTeams.map((team) => (
                <option key={team} value={team}>
                  {team}
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
              id="player-image"
              name="image"
              type="url"
              required
              className="form-input"
              placeholder="https://ejemplo.com/jugador.jpg"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
            />
            <small className="form-help">
              La imagen se usará para el perfil del jugador y el thumbnail.
            </small>
          </div>

          {/* Thumbnail generado (vista previa) */}
          {imageUrl && (
            <div className="form-field nfl-player-form__thumbnail">
              <span className="form-label">Thumbnail generado</span>
              <div className="nfl-player-form__thumbnail-box">
                <img src={imageUrl} alt="Vista previa del jugador" />
              </div>
            </div>
          )}

          {/* Estado activo */}
          <div className="form-field form-field--inline">
            <label className="form-checkbox">
              <input
                type="checkbox"
                name="isActive"
                defaultChecked={true}
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
      </div>
    </div>
  );
}

export default CreateNflPlayerForm;

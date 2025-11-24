// src/pages/administrator/AddPlayerNews.js
import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/authContext";
import "../../styles/global.css";
import { postPlayerNews } from "../../utils/communicationModule/resources/players.js";

function AddPlayerNews() {
  const { id } = useParams(); // Assuming player ID comes from URL params
  const { session } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    texto: "",
    es_lesion: false,
    resumen: "",
    designacion: "",
  });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Check if user is admin
  const isAdmin = session?.user?.rol === "administrador";
  if (!isAdmin) {
    navigate("/");
    return null;
  }

  // Injury designation options with descriptions
  const injuryDesignations = [
    { value: "O", label: "Fuera (O)", description: "no jugarán" },
    { value: "D", label: "Dudoso (D)", description: "muy poco probable que jueguen (~25%)" },
    { value: "Q", label: "Cuestionable (Q)", description: "probabilidad ~50%, suele definirse el día del partido" },
    { value: "P", label: "Probable (P)", description: "casi seguro que juega (usado en reportes de práctica)" },
    { value: "FP", label: "Participación Plena (FP)", description: "casi seguro que juega (usado en reportes de práctica)" },
    { value: "IR", label: "Reserva de Lesionados (IR)", description: "fuera por periodo extendido según reglas de la liga/NFL" },
    { value: "PUP", label: "Incapaz Físicamente de Jugar (PUP)", description: "no habilitado para jugar hasta cumplir requisitos médicos/reglamentarios" },
    { value: "SUS", label: "Suspendido (SUS)", description: "no elegible por sanción" },
  ];

  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setError("");
    setSuccess("");
  }

  const validateForm = () => {
    if (form.texto.length < 10 || form.texto.length > 300) {
      setError("El texto debe tener entre 10 y 300 caracteres.");
      return false;
    }

    if (form.es_lesion) {
      if (!form.resumen.trim()) {
        setError("El resumen es requerido para noticias de lesión.");
        return false;
      }
      if (form.resumen.length > 30) {
        setError("El resumen no puede exceder 30 caracteres.");
        return false;
      }
      if (!form.designacion) {
        setError("La designación es requerida para noticias de lesión.");
        return false;
      }
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const newsData = {
        jugador_id: id,
        texto: form.texto,
        es_lesion: form.es_lesion,
        resumen: form.es_lesion ? form.resumen : null,
        designacion: form.es_lesion ? form.designacion : null,
      };

      await postPlayerNews(newsData);

      setSuccess("Noticia agregada exitosamente al jugador.");
      setForm({
        texto: "",
        es_lesion: false,
        resumen: "",
        designacion: "",
      });
    } catch (err) {
      setError(err?.message || "Error al agregar la noticia. Verifique que el jugador existe y está activo.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="nfl-player-form-wrapper">
      <div className="card nfl-player-form">
        {/* Header */}
        <div className="card-header">
          <h2 className="nfl-player-form__title">
            Agregar Noticia a Jugador
          </h2>
          <p className="nfl-player-form__subtitle">
            Como administrador puedes agregar noticias sobre jugadores para mantener informados a los usuarios sobre novedades y lesiones.
          </p>
        </div>

        {/* Body */}
        <form
          className="card-body nfl-player-form__body"
          onSubmit={handleSubmit}
        >
          {/* Texto de la noticia */}
          <div className="form-field">
            <label htmlFor="news-text" className="form-label">
              Texto de la noticia <span className="required">*</span>
            </label>
            <textarea
              id="news-text"
              name="texto"
              required
              className="form-input"
              placeholder="Escribe la noticia sobre el jugador..."
              value={form.texto}
              onChange={(e) => setField("texto", e.target.value)}
              rows={4}
              maxLength={300}
            />
            <small className="form-help">
              {form.texto.length}/300 caracteres. Debe tener entre 10 y 300 caracteres.
            </small>
          </div>

          {/* ¿Es noticia de lesión? */}
          <div className="form-field form-field--inline">
            <label className="form-checkbox">
              <input
                type="checkbox"
                name="es_lesion"
                checked={form.es_lesion}
                onChange={(e) => setField("es_lesion", e.target.checked)}
              />
              <span>Esta es una noticia de lesión</span>
            </label>
          </div>

          {/* Resumen (solo si es lesión) */}
          {form.es_lesion && (
            <div className="form-field">
              <label htmlFor="news-summary" className="form-label">
                Resumen <span className="required">*</span>
              </label>
              <input
                id="news-summary"
                name="resumen"
                type="text"
                required={form.es_lesion}
                className="form-input"
                placeholder="Resumen breve de la lesión..."
                value={form.resumen}
                onChange={(e) => setField("resumen", e.target.value)}
                maxLength={30}
              />
              <small className="form-help">
                {form.resumen.length}/30 caracteres. Máximo 30 caracteres.
              </small>
            </div>
          )}

          {/* Designación (solo si es lesión) */}
          {form.es_lesion && (
            <div className="form-field">
              <label htmlFor="injury-designation" className="form-label">
                Designación de lesión <span className="required">*</span>
              </label>
              <select
                id="injury-designation"
                name="designacion"
                required={form.es_lesion}
                className="form-select"
                value={form.designacion}
                onChange={(e) => setField("designacion", e.target.value)}
              >
                <option value="" disabled>
                  Selecciona una designación
                </option>
                {injuryDesignations.map((designation) => (
                  <option key={designation.value} value={designation.value}>
                    {designation.label} - {designation.description}
                  </option>
                ))}
              </select>
              <small className="form-help">
                Selecciona la designación que mejor describe el estado del jugador.
              </small>
            </div>
          )}

          {/* Notas / criterios visuales */}
          <div className="nfl-player-form__info-box">
            <p className="nfl-player-form__info-title">Notas importantes</p>
            <ul className="nfl-player-form__info-list">
              <li>La fecha y hora de creación se generan automáticamente al guardar.</li>
              <li>Se registra auditoría con el autor, fecha/hora y cambios realizados.</li>
              <li>Si es noticia de lesión, el resumen y designación son obligatorios.</li>
              <li>El texto debe tener entre 10 y 300 caracteres.</li>
              <li>Si el jugador no existe o está inactivo, la operación será rechazada.</li>
            </ul>
          </div>

          {/* Mensajes de error y éxito */}
          {error && <div className="toast toast--err">{error}</div>}
          {success && <div className="toast toast--success">{success}</div>}

          {/* Botones */}
          <div className="form-actions">
            <button
              type="submit"
              className="button"
              disabled={isSubmitting}
            >
              {isSubmitting ? "Guardando..." : "Agregar Noticia"}
            </button>
            <button
              type="button"
              className="button button--ghost"
              onClick={() => navigate(-1)}
              disabled={isSubmitting}
            >
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddPlayerNews;
import React, { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useAuth } from "../../context/authContext";
import "../../styles/global.css";
import { postPlayerNews } from "../../utils/communicationModule/resources/players.js";

// Obtener ID del jugador desde los parámetros de la URL
function AddPlayerNews() {
  // ID del jugador
  const { id } = useParams();
  // Sesión del usuario
  const { session } = useAuth();
  // Navegación
  const navigate = useNavigate(); 

  // Estado del formulario
  const [form, setForm] = useState({
    texto: "",
    es_lesion: false,
    resumen: "",
    designacion: "",
  });

  // Estado para manejo de errores y éxito
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Verificar si el usuario es administrador
  const isAdmin = session?.user?.rol === "administrador";
  if (!isAdmin) {
    navigate("/");
    return null;
  }

  // Opciones de designaciones de lesión
  const injuryDesignations = [
    { value: "O", label: "Fuera (O)", description: "no jugarán" },
    { value: "D", label: "Dudoso (D)", description: "muy poco probable (~25%)" },
    { value: "Q", label: "Cuestionable (Q)", description: "probabilidad ~50%" },
    { value: "P", label: "Probable (P)", description: "casi seguro que juega" },
    { value: "FP", label: "Participación Plena (FP)", description: "usado en práctica" },
    { value: "IR", label: "Reserva Lesionados (IR)", description: "fuera largo plazo" },
    { value: "PUP", label: "PUP", description: "no habilitado para jugar" },
    { value: "SUS", label: "Suspendido", description: "sanción" },
  ];

  // Actualizar campo del formulario
  function setField(name, value) {
    setForm((f) => ({ ...f, [name]: value }));
    setError("");
    setSuccess("");
  }

  // Validar datos del formulario antes de enviar
  const validateForm = () => {
    if (form.texto.length < 10 || form.texto.length > 300) {
      setError("El texto debe tener entre 10 y 300 caracteres.");
      return false;
    }

    if (form.es_lesion) {
      if (!form.resumen.trim()) {
        setError("El resumen es obligatorio para noticias de lesión.");
        return false;
      }
      if (form.resumen.length > 30) {
        setError("El resumen no puede exceder 30 caracteres.");
        return false;
      }
      if (!form.designacion) {
        setError("La designación es requerida.");
        return false;
      }
    }
    return true;
  };

  // Manejar el envío del formulario
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!validateForm()) return;

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

      setSuccess("Noticia agregada exitosamente.");
      setForm({ texto: "", es_lesion: false, resumen: "", designacion: "" });
    } catch (err) {
      setError(err?.message || "Error al agregar noticia.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="nfl-player-form-wrapper">
      <div className="card nfl-player-form">
        <div className="card-header">
          <h2 className="nfl-player-form__title">Agregar Noticia a Jugador</h2>
          <p className="nfl-player-form__subtitle">
            Los administradores pueden agregar noticias relevantes o sobre lesiones de jugadores.
          </p>
        </div>

        <form className="card-body nfl-player-form__body" onSubmit={handleSubmit}>
          <div className="form-field">
            <label htmlFor="news-text" className="form-label">Texto de la noticia *</label>
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
            <small className="form-help">{form.texto.length}/300 caracteres</small>
          </div>

          <div className="form-field form-field--inline">
            <label className="form-checkbox">
              <input
                type="checkbox"
                name="es_lesion"
                checked={form.es_lesion}
                onChange={(e) => setField("es_lesion", e.target.checked)}
              />
              <span>Noticia de lesión</span>
            </label>
          </div>

          {form.es_lesion && (
            <div className="form-field">
              <label htmlFor="news-summary" className="form-label">Resumen *</label>
              <input
                id="news-summary"
                name="resumen"
                type="text"
                required
                className="form-input"
                placeholder="Resumen breve..."
                value={form.resumen}
                onChange={(e) => setField("resumen", e.target.value)}
                maxLength={30}
              />
              <small className="form-help">{form.resumen.length}/30 caracteres</small>
            </div>
          )}

          {form.es_lesion && (
            <div className="form-field">
              <label htmlFor="injury-designation" className="form-label">Designación *</label>
              <select
                id="injury-designation"
                name="designacion"
                required
                className="form-select"
                value={form.designacion}
                onChange={(e) => setField("designacion", e.target.value)}
              >
                <option value="" disabled>Selecciona una designación</option>
                {injuryDesignations.map((d) => (
                  <option key={d.value} value={d.value}>{d.label} - {d.description}</option>
                ))}
              </select>
            </div>
          )}

          <div className="nfl-player-form__info-box">
            <p className="nfl-player-form__info-title">Notas importantes</p>
            <ul className="nfl-player-form__info-list">
              <li>La creación registra fecha, hora y autor automáticamente.</li>
              <li>Si es noticia de lesión, el resumen y designación son obligatorios.</li>
              <li>El texto debe tener entre 10 y 300 caracteres.</li>
              <li>Si el jugador no existe o está inactivo, se rechazará la operación.</li>
            </ul>
          </div>

          {error && <div className="toast toast--err">{error}</div>}
          {success && <div className="toast toast--success">{success}</div>}

          <div className="form-actions">
            <button type="submit" className="button" disabled={isSubmitting}>
              {isSubmitting ? "Guardando..." : "Agregar Noticia"}
            </button>
            <button type="button" className="button button--ghost" onClick={() => navigate(-1)} disabled={isSubmitting}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default AddPlayerNews;
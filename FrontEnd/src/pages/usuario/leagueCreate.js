import { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authContext' // ajusta la ruta si tu archivo es authContext
import {
  validateLeagueName,
  validateLeaguePasswordWrapper,
  validateTeamSize,
  validateCommissionerTeamName,
  LEAGUE_TEAM_SIZES
} from '../../utils/leagueValidators'
import { fakeCreateLeagueRequest } from '../../utils/network'

const CURRENT_SEASON = 2025 // temporada “actual” (solo informativa, control admin)
const DEFAULTS = {
  status: 'Pre-Draft',
  tradeDeadlineActive: false,
  allowDecimals: true,
  maxSeasonTradesPerTeam: null, // sin límite
  maxSeasonFAAddsPerTeam: null, // sin límite
}

const PASS_PLACEHOLDER = '8–12, alfanumérica, con mayús/minús'
const WEEKS_BY_PLAYOFFS = {
  4: 'Semanas 16–17',
  6: 'Semanas 16–18',
}

export default function LeagueCreate() {
  const { isAuthenticated } = useAuth()
  const navigate = useNavigate()

  // Estado del formulario
  const [form, setForm] = useState({
    name: '',
    description: '',
    teams: 10,
    password: '',
    playoffs: 4, // 4 o 6
    allowDecimals: DEFAULTS.allowDecimals,
  })
  const [commishTeamName, setCommishTeamName] = useState('')
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const [toast, setToast] = useState({ type: null, message: '' })

  // Cupos disponibles
  const availableSlots = useMemo(() => {
    const total = Number(form.teams) || 0
    return Math.max(total - 1, 0)
  }, [form.teams])

  function setField(name, value) {
    setForm(f => ({ ...f, [name]: value }))
    setToast({ type: null, message: '' })
  }

  function validateAll() {
    const e = {}
    const eName = validateLeagueName(form.name); if (eName) e.name = eName
    const eSize = validateTeamSize(form.teams); if (eSize) e.teams = eSize
    const ePass = validateLeaguePasswordWrapper(form.password); if (ePass) e.password = ePass
    const eTeam = validateCommissionerTeamName(commishTeamName); if (eTeam) e.commishTeamName = eTeam
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setToast({ type: null, message: '' })
    if (!validateAll()) return

    setSubmitting(true)

    // Autogenerados visuales
    const generated = {
      id: crypto.randomUUID ? crypto.randomUUID() : `lg_${Date.now()}`,
      createdAt: new Date().toISOString(),
      status: DEFAULTS.status,
      season: CURRENT_SEASON,
      tradeDeadlineActive: DEFAULTS.tradeDeadlineActive,
      maxSeasonTradesPerTeam: DEFAULTS.maxSeasonTradesPerTeam,
      maxSeasonFAAddsPerTeam: DEFAULTS.maxSeasonFAAddsPerTeam,
      allowDecimals: !!form.allowDecimals,
      playoffs: Number(form.playoffs), // 4 o 6
    }

    // “Crear” en servidor (simulado). Si falla, no se crea parcialmente.
    try {
      await fakeCreateLeagueRequest({
        ...generated,
        name: form.name.trim(),
        description: form.description.trim(),
        teams: Number(form.teams),
        commishTeamName: commishTeamName.trim(),
        // password NUNCA debería enviarse en claro; aquí es visual.
      })
    } catch (err) {
      setSubmitting(false)
      setToast({ type: 'err', message: err.message || 'No se pudo crear la liga. Intenta de nuevo.' })
      return
    }

    setSubmitting(false)
    // Éxito (visual): mostramos un resumen y redirigimos a algún lugar (home o “detalle visual”)
    setToast({
      type: 'ok',
      message:
        `Liga creada: ${form.name} • ID: ${generated.id} • Cupos disponibles: ${availableSlots}. ` +
        `Estado: ${generated.status} • Temporada: ${generated.season} • Playoffs: ${generated.playoffs} (${WEEKS_BY_PLAYOFFS[generated.playoffs]}).`
    })

    // Redirigir tras un pequeño delay para que se vea el mensaje
    setTimeout(() => navigate('/'), 900)
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 720, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Crear liga</h2>
        <p style={{ color: 'var(--muted)' }}>
          Todo es visual (sin backend). El nombre debe ser único en el sistema — esto se validará cuando haya servidor.
        </p>

        <form className="form" onSubmit={handleSubmit} noValidate>
          {/* Nombre */}
          <div className="form__group">
            <label htmlFor="name">Nombre de la liga *</label>
            <input
              id="name"
              className={`input ${errors.name ? 'input--invalid' : ''}`}
              value={form.name}
              onChange={(e) => setField('name', e.target.value)}
              maxLength={100}
              placeholder="Mi liga NFL"
            />
            {errors.name && <div className="error">{errors.name}</div>}
          </div>

          {/* Descripción opcional */}
          <div className="form__group">
            <label htmlFor="description">Descripción (opcional)</label>
            <textarea
              id="description"
              className="input"
              rows={3}
              value={form.description}
              onChange={(e) => setField('description', e.target.value)}
              placeholder="Reglas, notas, etc."
            />
          </div>

          {/* Cantidad de equipos */}
          <div className="form__group">
            <label htmlFor="teams">Cantidad de equipos *</label>
            <select
              id="teams"
              className={`input ${errors.teams ? 'input--invalid' : ''}`}
              value={form.teams}
              onChange={(e) => setField('teams', Number(e.target.value))}
            >
              {LEAGUE_TEAM_SIZES.map(n => <option key={n} value={n}>{n}</option>)}
            </select>
            {errors.teams && <div className="error">{errors.teams}</div>}
            <div className="help">Cupos disponibles luego de asignarte tu equipo: <strong>{availableSlots}</strong></div>
          </div>

          {/* Contraseña de liga */}
          <div className="form__group">
            <label htmlFor="password">Contraseña de la liga *</label>
            <input
              id="password"
              className={`input ${errors.password ? 'input--invalid' : ''}`}
              type="password"
              value={form.password}
              onChange={(e) => setField('password', e.target.value)}
              maxLength={12}
              placeholder={PASS_PLACEHOLDER}
            />
            {errors.password && <div className="error">{errors.password}</div>}
          </div>

          {/* Playoffs */}
          <div className="form__group">
            <label>Formato de playoffs *</label>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {[4,6].map(n => (
                <label key={n} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="radio"
                    name="playoffs"
                    value={n}
                    checked={Number(form.playoffs) === n}
                    onChange={(e) => setField('playoffs', Number(e.target.value))}
                  />
                  {n} equipos ({WEEKS_BY_PLAYOFFS[n]})
                </label>
              ))}
            </div>
          </div>

          {/* Decimales */}
          <div className="form__group" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              id="allowDecimals"
              type="checkbox"
              checked={!!form.allowDecimals}
              onChange={(e) => setField('allowDecimals', e.target.checked)}
            />
            <label htmlFor="allowDecimals">Permitir puntajes con decimales (por defecto activo)</label>
          </div>

          {/* Equipo del comisionado */}
          <div className="form__group">
            <label htmlFor="commishTeam">Nombre de tu equipo *</label>
            <input
              id="commishTeam"
              className={`input ${errors.commishTeamName ? 'input--invalid' : ''}`}
              value={commishTeamName}
              onChange={(e) => setCommishTeamName(e.target.value)}
              maxLength={50}
              placeholder="Mi primer equipo"
            />
            {errors.commishTeamName && <div className="error">{errors.commishTeamName}</div>}
          </div>

          {/* Resumen (solo lectura) */}
          <fieldset className="card" style={{ borderColor: 'var(--border)' }}>
            <legend style={{ color: 'var(--muted)' }}>Se creará con</legend>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              <li>Estado: <strong>{DEFAULTS.status}</strong></li>
              <li>Temporada actual: <strong>{CURRENT_SEASON}</strong></li>
              <li>Trade deadline: <strong>inactivo</strong></li>
              <li>Límites de temporada: <strong>sin límites</strong></li>
              <li>Decimales: <strong>{form.allowDecimals ? 'sí' : 'no'}</strong></li>
              <li>Comisionado principal: <strong>tú</strong></li>
              <li>Tu equipo: <strong>{commishTeamName || '—'}</strong></li>
            </ul>
          </fieldset>

          {/* Acciones */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button className="button button--accent" disabled={submitting}>
              {submitting ? 'Creando…' : 'Crear liga'}
            </button>
            <button type="button" className="button button--ghost" onClick={() => navigate(-1)} disabled={submitting}>
              Cancelar
            </button>
          </div>

          {/* Mensajes */}
          {toast.message && (
            <div className={`toast ${toast.type === 'ok' ? 'toast--ok' : 'toast--err'}`} style={{ marginTop: 12 }}>
              {toast.message}
            </div>
          )}
        </form>
      </div>
    </div>
  )
}

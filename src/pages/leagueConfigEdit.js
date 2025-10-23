import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/authContext' // ajusta si tu archivo es authContext
import { getLeague, saveLeague, addAudit, isCommissioner } from '../utils/leagueStore'
import {
  GAME_SCHEMES, SCORING,
  validateLeagueName,
  validatePreDraftEditable,
  validateTeamSizeWithRegistered,
  validateGameScheme,
  validateScoringSystem,
  validatePlayoffsTeams,
  validateDecimalsFlag,
  validateTradeDeadline,
  validatePositiveLimitOrNull
} from '../utils/leagueEditValidators'
import { LEAGUE_TEAM_SIZES } from '../utils/leagueValidators'
import { fakeUpdateLeagueConfigRequest } from '../utils/network'

const WEEKS_BY_PLAYOFFS = { 4: 'Semanas 16–17', 6: 'Semanas 16–18' }

export default function LeagueConfigEdit() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { session } = useAuth()

  const [league, setLeague] = useState(() => getLeague(id))
  const isCommish = isCommissioner(session?.email, league)
  const isPreDraft = league.status === 'Pre-Draft'

  // Form state (clon editable)
  const [form, setForm] = useState({
    name: league.name,
    teams: league.teams,
    gameScheme: league.gameScheme,
    scoringSystem: league.scoringSystem,
    playoffsTeams: league.playoffsTeams,
    allowDecimals: !!league.allowDecimals,
    tradeDeadlineActive: !!league.tradeDeadlineActive,
    tradeDeadlineAt: league.tradeDeadlineAt || '',
    maxSeasonTradesPerTeam: league.maxSeasonTradesPerTeam ?? '',
    maxSeasonFAAddsPerTeam: league.maxSeasonFAAddsPerTeam ?? '',
  })

  const [errors, setErrors] = useState({})
  const [toast, setToast] = useState({ type: null, message: '' })
  const [saving, setSaving] = useState(false)

  const availableAfter = useMemo(() => Math.max(Number(form.teams) - Number(league.registeredTeams), 0), [form.teams, league.registeredTeams])

  function setField(k, v) {
    setForm(f => ({ ...f, [k]: v }))
    setToast({ type: null, message: '' })
  }

  function validateAll() {
    const e = {}

    // Nombre (siempre editable)
    const eName = validateLeagueName(form.name); if (eName) e.name = eName

    // Resto: solo Pre-Draft
    const pre = validatePreDraftEditable(league.status)
    const restrictedTouched =
      form.teams !== league.teams ||
      form.gameScheme !== league.gameScheme ||
      form.scoringSystem !== league.scoringSystem ||
      form.playoffsTeams !== league.playoffsTeams ||
      form.allowDecimals !== league.allowDecimals ||
      form.tradeDeadlineActive !== league.tradeDeadlineActive ||
      form.tradeDeadlineAt !== (league.tradeDeadlineAt || '') ||
      String(form.maxSeasonTradesPerTeam) !== String(league.maxSeasonTradesPerTeam ?? '') ||
      String(form.maxSeasonFAAddsPerTeam) !== String(league.maxSeasonFAAddsPerTeam ?? '')

    if (restrictedTouched && pre) e.global = pre

    // Si es Pre-Draft, validar campos restringidos
    if (!pre) {
      const eTeams = validateTeamSizeWithRegistered(form.teams, league.registeredTeams); if (eTeams) e.teams = eTeams
      const eScheme = validateGameScheme(form.gameScheme); if (eScheme) e.gameScheme = eScheme
      const eScore = validateScoringSystem(form.scoringSystem); if (eScore) e.scoringSystem = eScore
      const ePO = validatePlayoffsTeams(form.playoffsTeams); if (ePO) e.playoffsTeams = ePO
      const eDec = validateDecimalsFlag(form.allowDecimals); if (eDec) e.allowDecimals = eDec
      const eDL = validateTradeDeadline(form.tradeDeadlineActive, form.tradeDeadlineAt, league.season); if (eDL) e.tradeDeadlineAt = eDL
      const eLimitTrades = validatePositiveLimitOrNull(form.maxSeasonTradesPerTeam); if (eLimitTrades) e.maxSeasonTradesPerTeam = eLimitTrades
      const eLimitFA = validatePositiveLimitOrNull(form.maxSeasonFAAddsPerTeam); if (eLimitFA) e.maxSeasonFAAddsPerTeam = eLimitFA
    }

    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleSave(e) {
    e.preventDefault()
    if (!isCommish) {
      setToast({ type: 'err', message: 'No tienes permisos para editar esta liga.' })
      return
    }
    if (!validateAll()) return

    setSaving(true)
    try {
      // “Llamada” a servidor (visual). Si falla, no hay cambios parciales.
      await fakeUpdateLeagueConfigRequest({ id: league.id, form })
    } catch (err) {
      setSaving(false)
      setToast({ type: 'err', message: err.message || 'Fallo de red o validación. No se guardaron cambios.' })
      return
    }

    // Aplicar cambios y auditar
    const next = { ...league }
    const changes = []

    // Siempre editable
    if (next.name !== form.name) {
      changes.push({ field: 'name', oldValue: next.name, newValue: form.name })
      next.name = form.name.trim()
    }

    // Pre-Draft: resto
    if (isPreDraft) {
      if (next.teams !== form.teams) {
        changes.push({ field: 'teams', oldValue: next.teams, newValue: form.teams })
        next.teams = Number(form.teams)
      }
      if (next.gameScheme !== form.gameScheme) {
        changes.push({ field: 'gameScheme', oldValue: next.gameScheme, newValue: form.gameScheme })
        next.gameScheme = form.gameScheme
      }
      if (next.scoringSystem !== form.scoringSystem) {
        changes.push({ field: 'scoringSystem', oldValue: next.scoringSystem, newValue: form.scoringSystem })
        next.scoringSystem = form.scoringSystem
      }
      if (next.playoffsTeams !== form.playoffsTeams) {
        changes.push({ field: 'playoffsTeams', oldValue: next.playoffsTeams, newValue: form.playoffsTeams })
        next.playoffsTeams = Number(form.playoffsTeams)
      }
      if (Boolean(next.allowDecimals) !== Boolean(form.allowDecimals)) {
        changes.push({ field: 'allowDecimals', oldValue: Boolean(next.allowDecimals), newValue: Boolean(form.allowDecimals) })
        next.allowDecimals = !!form.allowDecimals
      }
      if (Boolean(next.tradeDeadlineActive) !== Boolean(form.tradeDeadlineActive) ||
          (next.tradeDeadlineAt || '') !== (form.tradeDeadlineAt || '')) {
        changes.push({
          field: 'tradeDeadline',
          oldValue: next.tradeDeadlineActive ? (next.tradeDeadlineAt || '[sin fecha]') : 'inactivo',
          newValue: form.tradeDeadlineActive ? (form.tradeDeadlineAt || '[sin fecha]') : 'inactivo'
        })
        next.tradeDeadlineActive = !!form.tradeDeadlineActive
        next.tradeDeadlineAt = form.tradeDeadlineActive ? form.tradeDeadlineAt : null
      }
      const conv = (v) => (v === '' || v === null || v === undefined ? null : Number(v))
      if (String(next.maxSeasonTradesPerTeam ?? '') !== String(form.maxSeasonTradesPerTeam)) {
        changes.push({ field: 'maxSeasonTradesPerTeam', oldValue: next.maxSeasonTradesPerTeam ?? 'sin límite', newValue: conv(form.maxSeasonTradesPerTeam) ?? 'sin límite' })
        next.maxSeasonTradesPerTeam = conv(form.maxSeasonTradesPerTeam)
      }
      if (String(next.maxSeasonFAAddsPerTeam ?? '') !== String(form.maxSeasonFAAddsPerTeam)) {
        changes.push({ field: 'maxSeasonFAAddsPerTeam', oldValue: next.maxSeasonFAAddsPerTeam ?? 'sin límite', newValue: conv(form.maxSeasonFAAddsPerTeam) ?? 'sin límite' })
        next.maxSeasonFAAddsPerTeam = conv(form.maxSeasonFAAddsPerTeam)
      }
    }

    saveLeague(next)
    addAudit(next.id, {
      action: 'config_update',
      by: session?.email,
      notes: 'Edición de configuración de liga.',
      fields: changes
    })
    setLeague(next)
    setSaving(false)
    setToast({ type: 'ok', message: 'Configuración guardada.' })

    // Regresa a detalle/admin si quieres
    setTimeout(() => navigate(-1), 700)
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 800, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Configurar liga</h2>
        <p style={{ color: 'var(--muted)' }}>
          {league.name} • ID: <code>{league.id}</code> • Temporada: <strong>{league.season}</strong> • Estado: <strong>{league.status}</strong>
        </p>

        {!isCommish && (
          <div className="toast toast--err" style={{ marginBottom: 12 }}>
            Solo el comisionado puede editar la configuración.
          </div>
        )}
        {errors.global && (
          <div className="toast toast--err" style={{ marginBottom: 12 }}>
            {errors.global}
          </div>
        )}

        <form className="form" onSubmit={handleSave} noValidate>
          {/* Siempre editable: nombre */}
          <div className="form__group">
            <label htmlFor="name">Nombre de la liga *</label>
            <input
              id="name"
              className={`input ${errors.name ? 'input--invalid' : ''}`}
              value={form.name}
              onChange={(e) => setField('name', e.target.value)}
              maxLength={100}
            />
            {errors.name && <div className="error">{errors.name}</div>}
          </div>

          {/* Solo Pre-Draft: capacidad de equipos */}
          <div className="form__group">
            <label htmlFor="teams">Cantidad de equipos (Pre-Draft)</label>
            <select
              id="teams"
              className={`input ${errors.teams ? 'input--invalid' : ''}`}
              value={form.teams}
              onChange={(e) => setField('teams', Number(e.target.value))}
              disabled={!isPreDraft}
            >
              {LEAGUE_TEAM_SIZES.map(n => <option key={n} value={n}>{n}</option>)}
            </select>
            {errors.teams && <div className="error">{errors.teams}</div>}
            <div className="help">Registrados: {league.registeredTeams} • Cupos resultantes: <strong>{availableAfter}</strong></div>
          </div>

          {/* Solo Pre-Draft: esquema, puntaje, playoffs, decimales */}
          <div className="form__group">
            <label>Esquema de juego (Pre-Draft)</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {GAME_SCHEMES.map(s => (
                <label key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="radio"
                    name="gameScheme"
                    value={s}
                    checked={form.gameScheme === s}
                    disabled={!isPreDraft}
                    onChange={(e) => setField('gameScheme', e.target.value)}
                  />
                  {s}
                </label>
              ))}
            </div>
            {errors.gameScheme && <div className="error">{errors.gameScheme}</div>}
          </div>

          <div className="form__group">
            <label>Sistema de puntaje (Pre-Draft)</label>
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {SCORING.map(s => (
                <label key={s} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="radio"
                    name="scoring"
                    value={s}
                    checked={form.scoringSystem === s}
                    disabled={!isPreDraft}
                    onChange={(e) => setField('scoringSystem', e.target.value)}
                  />
                  {s}
                </label>
              ))}
            </div>
            {errors.scoringSystem && <div className="error">{errors.scoringSystem}</div>}
          </div>

          <div className="form__group">
            <label>Playoffs (Pre-Draft)</label>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              {[4,6].map(n => (
                <label key={n} style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                  <input
                    type="radio"
                    name="playoffs"
                    value={n}
                    checked={Number(form.playoffsTeams) === n}
                    disabled={!isPreDraft}
                    onChange={(e) => setField('playoffsTeams', Number(e.target.value))}
                  />
                  {n} equipos ({WEEKS_BY_PLAYOFFS[n]})
                </label>
              ))}
            </div>
            {errors.playoffsTeams && <div className="error">{errors.playoffsTeams}</div>}
          </div>

          <div className="form__group" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              id="allowDecimals"
              type="checkbox"
              checked={!!form.allowDecimals}
              disabled={!isPreDraft}
              onChange={(e) => setField('allowDecimals', e.target.checked)}
            />
            <label htmlFor="allowDecimals">Permitir puntajes con decimales (Pre-Draft)</label>
          </div>
          {errors.allowDecimals && <div className="error">{errors.allowDecimals}</div>}
          <div className="help">Si se desactivan, &lt; 0.50 redondea hacia abajo y ≥ 0.50 hacia arriba.</div>

          {/* Trade deadline */}
          <div className="form__group">
            <label>Fecha límite de intercambios (Pre-Draft)</label>
            <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
              <input
                id="tdActive"
                type="checkbox"
                checked={!!form.tradeDeadlineActive}
                disabled={!isPreDraft}
                onChange={(e) => setField('tradeDeadlineActive', e.target.checked)}
              />
              <label htmlFor="tdActive">Activar</label>
              <input
                type="date"
                className={`input ${errors.tradeDeadlineAt ? 'input--invalid' : ''}`}
                value={form.tradeDeadlineAt || ''}
                disabled={!isPreDraft || !form.tradeDeadlineActive}
                onChange={(e) => setField('tradeDeadlineAt', e.target.value)}
              />
            </div>
            {errors.tradeDeadlineAt && <div className="error">{errors.tradeDeadlineAt}</div>}
            <div className="help">Debe estar dentro de la temporada {league.season}–{league.season + 1}.</div>
          </div>

          {/* Límites por temporada (por equipo) */}
          <div className="form__group">
            <label>Límites por temporada (Pre-Draft)</label>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(2, minmax(0,1fr))' }}>
              <div>
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>Máx. cambios por equipo</div>
                <input
                  className={`input ${errors.maxSeasonTradesPerTeam ? 'input--invalid' : ''}`}
                  type="number"
                  min={1} max={100}
                  placeholder="vacío = sin límite"
                  value={form.maxSeasonTradesPerTeam}
                  disabled={!isPreDraft}
                  onChange={(e) => setField('maxSeasonTradesPerTeam', e.target.value)}
                />
                {errors.maxSeasonTradesPerTeam && <div className="error">{errors.maxSeasonTradesPerTeam}</div>}
              </div>
              <div>
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>Máx. contrataciones FA por equipo</div>
                <input
                  className={`input ${errors.maxSeasonFAAddsPerTeam ? 'input--invalid' : ''}`}
                  type="number"
                  min={1} max={100}
                  placeholder="vacío = sin límite"
                  value={form.maxSeasonFAAddsPerTeam}
                  disabled={!isPreDraft}
                  onChange={(e) => setField('maxSeasonFAAddsPerTeam', e.target.value)}
                />
                {errors.maxSeasonFAAddsPerTeam && <div className="error">{errors.maxSeasonFAAddsPerTeam}</div>}
              </div>
            </div>
          </div>

          {/* Acciones */}
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button className="button button--accent" disabled={saving || !isCommish}>
              {saving ? 'Guardando…' : 'Guardar'}
            </button>
            <button type="button" className="button button--ghost" onClick={() => navigate(-1)} disabled={saving}>
              Cancelar
            </button>
          </div>

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

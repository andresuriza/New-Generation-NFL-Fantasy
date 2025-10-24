// src/pages/usuario/leagueJoin.js
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { searchLeaguesLocal, fakeJoinLeagueVisual } from '../../utils/leagueJoinNetwork'
import { validateAlias, validateName as validateTeamName } from '../../utils/validators'

export default function LeagueJoin() {
  const navigate = useNavigate()
  const [q, setQ] = useState('')
  const [season, setSeason] = useState('')
  const [status, setStatus] = useState('') // 'Pre-Draft' | 'Active' | 'Inactive'
  const [results, setResults] = useState([])
  const [selected, setSelected] = useState(null)
  const [alias, setAlias] = useState('')
  const [teamName, setTeamName] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ type: null, message: '' })

  useEffect(() => { document.title = 'Buscar liga' }, [])

  function doSearch() {
    const list = searchLeaguesLocal({ q, season: season || undefined, status: status || undefined })
    setResults(list)
  }

  useEffect(() => { doSearch() }, []) // primera carga

  const seasonsInData = useMemo(() => {
    const uniq = new Set(results.map(r => r.season).filter(Boolean))
    return Array.from(uniq).sort()
  }, [results])

  function validateJoin() {
    const e = {}
    const eAlias = validateAlias(alias); if (eAlias) e.alias = eAlias
    const eTeam = validateTeamName(teamName); if (eTeam) e.teamName = 'Nombre de equipo: ' + eTeam.replace('El nombre', 'obligatorio y ≤ 50')
    if (!password || !password.trim()) e.password = 'Ingresa la contraseña de la liga.'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  async function handleJoin() {
    setToast({ type: null, message: '' })
    if (!selected) return
    if (!validateJoin()) return

    setLoading(true)
    try {
      const res = await fakeJoinLeagueVisual({
        leagueId: selected.id,
        alias: alias.trim(),
        teamName: teamName.trim(),
        password: password, // el backend real validará
      })
      setLoading(false)
      setToast({
        type: 'ok',
        message: `¡Te uniste a ${selected.name}! Cupos restantes: ${res.data.remainingSlots}.`
      })
      setTimeout(() => navigate(res.data.redirect_to), 900)
    } catch (err) {
      setLoading(false)
      // mensaje genérico (no revelar detalles)
      setToast({ type: 'err', message: err?.message || 'No fue posible unirse. Verifica los datos.' })
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 900, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Buscar liga y unirse</h2>
        <p className="help">Visual / mock. El backend validará alias único, nombre de equipo y contraseña real.</p>

        {/* Filtros */}
        <div className="grid" style={{ gridTemplateColumns: '2fr 1fr 1fr auto', gap: 8 }}>
          <input className="input" placeholder="Buscar por nombre…" value={q} onChange={e => setQ(e.target.value)} />
          <input className="input" placeholder="Temporada (ej. 2025)" value={season} onChange={e => setSeason(e.target.value)} />
          <select className="input" value={status} onChange={e => setStatus(e.target.value)}>
            <option value="">Estado (todos)</option>
            <option>Pre-Draft</option>
            <option>Active</option>
            <option>Inactive</option>
          </select>
          <button className="button" onClick={doSearch}>Buscar</button>
        </div>

        {/* Resultados */}
        <div className="card" style={{ marginTop: 12 }}>
          <h3 style={{ marginTop: 0 }}>Resultados ({results.length})</h3>
          {results.length === 0 && <div className="help">No hay ligas que coincidan con los filtros.</div>}
          {results.map(lg => {
            const capacity = Number(lg.teams || lg.teamsMax || 0)
            const regs = Number(lg.registeredTeams || (lg.members?.length || 0))
            const remaining = capacity ? Math.max(capacity - regs, 0) : 0
            return (
              <div key={lg.id} className={`card ${selected?.id === lg.id ? 'card--selected' : ''}`} style={{ marginBottom: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8 }}>
                  <div>
                    <div style={{ fontWeight: 600 }}>{lg.name}</div>
                    <div className="help">
                      Temporada: {lg.season || '—'} • Estado: {lg.status || '—'} • Cupos restantes: {remaining}
                    </div>
                    {lg.description && <div className="help">{lg.description}</div>}
                  </div>
                  <div>
                    <button className="button" onClick={() => setSelected(lg)} disabled={remaining <= 0}>
                      {remaining <= 0 ? 'Sin cupos' : (selected?.id === lg.id ? 'Seleccionada' : 'Unirme')}
                    </button>
                  </div>
                </div>
              </div>
            )
          })}
        </div>

        {/* Formulario de unión */}
        {selected && (
          <div className="card" style={{ marginTop: 12 }}>
            <h3 style={{ marginTop: 0 }}>Unirse a: {selected.name}</h3>
            <div className="grid" style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
              <div className="form__group">
                <label>Alias (opcional)</label>
                <input className={`input ${errors.alias ? 'input--invalid' : ''}`} value={alias} onChange={e => setAlias(e.target.value)} maxLength={50} />
                {errors.alias && <div className="error">{errors.alias}</div>}
              </div>
              <div className="form__group">
                <label>Nombre de equipo *</label>
                <input className={`input ${errors.teamName ? 'input--invalid' : ''}`} value={teamName} onChange={e => setTeamName(e.target.value)} maxLength={50} />
                {errors.teamName && <div className="error">{errors.teamName}</div>}
              </div>
              <div className="form__group">
                <label>Contraseña de la liga *</label>
                <input className={`input ${errors.password ? 'input--invalid' : ''}`} type="password" value={password} onChange={e => setPassword(e.target.value)} maxLength={12} />
                {errors.password && <div className="error">{errors.password}</div>}
              </div>
            </div>

            <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
              <button className="button button--accent" onClick={handleJoin} disabled={loading}>
                {loading ? 'Procesando…' : 'Unirme'}
              </button>
              <button className="button button--ghost" onClick={() => setSelected(null)} disabled={loading}>Cancelar</button>
            </div>

            {toast.message && (
              <div className={`toast ${toast.type === 'ok' ? 'toast--ok' : 'toast--err'}`} style={{ marginTop: 12 }}>
                {toast.message}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

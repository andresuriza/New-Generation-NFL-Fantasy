import { useMemo, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useAuth } from '../context/authContext' // ajusta si tu archivo es authContext
import { getLeague, saveLeague, addAudit, isCommissioner } from '../utils/leagueStore'
import { fakeToggleLeagueStateRequest } from '../utils/network'

export default function LeagueAdminStatus() {
  const { id } = useParams()
  const navigate = useNavigate()
  const { session, isAuthenticated } = useAuth()

  const [league, setLeague] = useState(() => getLeague(id))
  const [loading, setLoading] = useState(false)
  const [toast, setToast] = useState({ type: null, message: '' })
  const [confirmOpen, setConfirmOpen] = useState(false) // modal de confirmación para desactivar

  const canToggle = useMemo(() => isAuthenticated && isCommissioner(session?.email, league), [isAuthenticated, session, league])
  const isInactive = league.status === 'Inactive'
  const isPreDraft = league.status === 'Pre-Draft'
  const isActiveSeason = league.status === 'Active'

  function onError(msg) {
    setToast({ type: 'err', message: msg })
  }

  async function doToggle(to) {
    if (!canToggle) {
      onError('No tienes permisos para cambiar el estado de la liga.')
      return
    }
    // Reglas:
    // - Solo activar si está Inactive
    if (to === 'Active' && league.status !== 'Inactive') {
      onError('Solo puedes activar una liga que está inactiva.')
      return
    }
    // - Desactivar se permite desde cualquier estado
    setLoading(true)
    setToast({ type: null, message: '' })

    try {
      await fakeToggleLeagueStateRequest({ leagueId: league.id, to })
    } catch (e) {
      setLoading(false)
      onError(e.message || 'No se pudo cambiar el estado. Intenta de nuevo.')
      return
    }

    // Aplicar cambios visuales
    const next = { ...league }
    if (to === 'Inactive') {
      next.status = 'Inactive'
      // Si se desactiva antes del draft → eliminar draft pendiente
      if (isPreDraft && next.draft?.pending) {
        next.draft = { pending: false, sessionId: null }
      }
      addAudit(league.id, {
        action: 'deactivate',
        by: session?.email,
        notes: isPreDraft ? 'Desactivada en Pre-Draft: sesión de draft eliminada.' : 'Desactivada durante temporada: no sumará puntos mientras esté inactiva.'
      })
      saveLeague(next)
      setLeague(next)
      setToast({ type: 'ok', message: 'Liga desactivada. No sumará puntos mientras esté inactiva.' })
      setConfirmOpen(false)
      setLoading(false)
      return
    }

    if (to === 'Active') {
      next.status = (isPreDraft ? 'Pre-Draft' : 'Active') // ojo: si estaba Inactive pero originalmente era Pre-Draft… NO recreamos draft. Mantén estado coherente:
      // Si estaba inactiva y originalmente era Pre-Draft, definimos que al reactivar queda Pre-Draft sin draft:
      if (league.status === 'Inactive' && league.draft?.sessionId == null && league.draft?.pending === false && isPreDraft) {
        next.status = 'Pre-Draft' // sin recrear draft
      } else {
        next.status = 'Active'
      }
      addAudit(league.id, {
        action: 'activate',
        by: session?.email,
        notes: isPreDraft
          ? 'Reactivada antes del draft. La sesión de draft no se recrea automáticamente.'
          : 'Reactivada durante temporada. No se recalculan puntos de semanas inactivas.'
      })
      saveLeague(next)
      setLeague(next)
      setToast({
        type: 'ok',
        message: isPreDraft
          ? 'Liga activada. Sigue en Pre-Draft sin recrear sesión de draft.'
          : 'Liga activada. No se recalculan puntos de semanas anteriores.'
      })
      setLoading(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 800, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Estado de la liga</h2>
        <p style={{ color: 'var(--muted)' }}>
          <strong>{league.name}</strong> • ID: <code>{league.id}</code> • Temporada: <strong>{league.season}</strong>
        </p>

        {/* Estado actual */}
        <div className="grid" style={{ gridTemplateColumns: 'repeat(3, minmax(0,1fr))', marginTop: 8 }}>
          <Info label="Estado">{league.status}</Info>
          <Info label="Semana actual">{league.currentWeek}</Info>
          <Info label="Comisionado">{league.commissionerEmail}</Info>
        </div>

        {/* Mensajes de comportamiento */}
        {league.status === 'Inactive' && (
          <div className="toast toast--err" style={{ marginTop: 12 }}>
            La liga está inactiva: no se suman puntos en la semana en curso ni siguientes hasta que se active.
          </div>
        )}
        {league.status === 'Active' && (
          <div className="toast toast--ok" style={{ marginTop: 12 }}>
            La liga está activa y sumando puntos normalmente.
          </div>
        )}
        {isPreDraft && (
          <div className="toast" style={{ marginTop: 12 }}>
            Estado Pre-Draft. {league.draft?.pending ? 'Hay una sesión de draft pendiente.' : 'No hay sesión de draft activa (no se recreará automáticamente).'}
          </div>
        )}

        {/* Acciones */}
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginTop: 16 }}>
          <button
            className="button button--ghost"
            disabled={!canToggle || loading || league.status === 'Inactive'}
            onClick={() => doToggle('Inactive')}
            onMouseDown={(e) => { // abrir confirmación antes de desactivar
              e.preventDefault(); // evitamos disparo inmediato
              if (!canToggle || loading || league.status === 'Inactive') return;
              setConfirmOpen(true);
            }}
          >
            Desactivar liga
          </button>

          <button
            className="button button--accent"
            disabled={!canToggle || loading || league.status !== 'Inactive'}
            onClick={() => doToggle('Active')}
          >
            Activar liga
          </button>

          <button className="button" onClick={() => navigate(-1)} disabled={loading}>Volver</button>
        </div>

        {!canToggle && (
          <div className="toast toast--err" style={{ marginTop: 12 }}>
            No tienes permisos para activar o desactivar esta liga (solo el comisionado).
          </div>
        )}

        {toast.message && (
          <div className={`toast ${toast.type === 'ok' ? 'toast--ok' : 'toast--err'}`} style={{ marginTop: 12 }}>
            {toast.message}
          </div>
        )}
      </div>

      {/* Modal de confirmación para desactivar */}
      {confirmOpen && (
        <ConfirmModal
          title="Confirmar desactivación"
          loading={loading}
          onCancel={() => setConfirmOpen(false)}
          onConfirm={async () => {
            setConfirmOpen(false)
            await doToggle('Inactive')
          }}
          isPreDraft={isPreDraft}
        />
      )}

      {/* Historial */}
      <section style={{ marginTop: 24 }}>
        <h3 style={{ margin: '0 0 12px 0' }}>Historial de estado</h3>
        {(!league.audit || league.audit.length === 0) ? (
          <div className="card" style={{ padding: 16, color: 'var(--muted)' }}>
            Aún no hay cambios de estado registrados.
          </div>
        ) : (
          <div className="grid">
            {league.audit.map((a) => (
              <div key={a.id} className="card">
                <div style={{ fontSize: 12, color: 'var(--muted)' }}>
                  {new Date(a.at).toLocaleString()} • {a.by}
                </div>
                <div style={{ marginTop: 6, fontWeight: 600 }}>
                  {a.action === 'deactivate' ? 'Desactivación' : 'Activación'}
                </div>
                {a.notes && <div style={{ color: 'var(--muted)', marginTop: 6 }}>{a.notes}</div>}
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

function Info({ label, children }) {
  return (
    <div className="card" style={{ padding: 12 }}>
      <div style={{ fontSize: 12, color: 'var(--muted)' }}>{label}</div>
      <div style={{ fontWeight: 700 }}>{children}</div>
    </div>
  )
}

function ConfirmModal({ title, onCancel, onConfirm, isPreDraft, loading }) {
  return (
    <div
      style={{
        position: 'fixed', inset: 0, background: 'rgba(0,0,0,.45)',
        display: 'grid', placeItems: 'center', zIndex: 1000
      }}
      role="dialog" aria-modal="true"
    >
      <div className="card" style={{ width: 480 }}>
        <h3 style={{ marginTop: 0 }}>{title}</h3>
        <p style={{ color: 'var(--muted)' }}>
          {isPreDraft
            ? 'Estás por desactivar la liga en estado Pre-Draft. La sesión de draft pendiente será eliminada. ¿Continuar?'
            : 'Estás por desactivar la liga. Mientras permanezca inactiva, no se sumarán puntos.'}
        </p>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="button button--ghost" onClick={onCancel} disabled={loading}>Cancelar</button>
          <button className="button button--accent" onClick={onConfirm} disabled={loading}>
            {loading ? 'Procesando…' : 'Confirmar'}
          </button>
        </div>
      </div>
    </div>
  )
}

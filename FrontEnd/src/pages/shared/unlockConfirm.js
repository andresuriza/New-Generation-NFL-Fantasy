import { useEffect, useMemo, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

export default function UnlockConfirm() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('pending')
  const [message, setMessage] = useState('Validando token…')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const [changed, setChanged] = useState(false)
  const [email, setEmail] = useState('')
  const [resent, setResent] = useState(false)

  const token = useMemo(() => searchParams.get('token') || '', [searchParams])

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('Token de desbloqueo faltante o inválido.')
      return
    }

    async function confirm() {
      try {
        const base = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
        const basePath = process.env.REACT_APP_API_BASE_PATH || '/api'
        const res = await fetch(`${base}${basePath}/usuarios/unlock/confirm?token=${encodeURIComponent(token)}`)
        const data = await res.json().catch(() => ({}))
        if (!res.ok) {
          throw new Error(data?.detail || data?.message || 'No se pudo desbloquear la cuenta')
        }
        setStatus('ok')
        setMessage(data?.message || 'Tu cuenta ha sido desbloqueada. Ahora puedes definir una nueva contraseña.')
      } catch (err) {
        setStatus('error')
        setMessage(err?.message || 'Enlace inválido o expirado. Puedes solicitar uno nuevo abajo.')
      }
    }

    confirm()
  }, [token])

  async function handleSetPassword(e) {
    e.preventDefault()
    if (submitting) return
    // Client-side basic policy check (8-12, alfanumérica, minúscula y mayúscula)
    const policy = /^[A-Za-z0-9]{8,12}$/
    if (!policy.test(newPassword) || !/[a-z]/.test(newPassword) || !/[A-Z]/.test(newPassword)) {
      setMessage('Contraseña inválida. Debe ser alfanumérica de 8–12 caracteres, con al menos una minúscula y una mayúscula.')
      return
    }
    if (newPassword !== confirmPassword) {
      setMessage('Las contraseñas no coinciden.')
      return
    }
    try {
      setSubmitting(true)
      const base = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
      const basePath = process.env.REACT_APP_API_BASE_PATH || '/api'
      const res = await fetch(`${base}${basePath}/usuarios/unlock/set-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token, new_password: newPassword }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data?.detail || data?.message || 'No se pudo actualizar la contraseña')
      }
      setChanged(true)
      setMessage(data?.message || 'Contraseña actualizada correctamente. Ya puedes iniciar sesión.')
    } catch (err) {
      setMessage(err?.message || 'No se pudo actualizar la contraseña')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleResend(e) {
    e.preventDefault()
    if (!email) {
      setMessage('Ingresa tu correo para recibir un nuevo enlace.')
      return
    }
    try {
      setSubmitting(true)
      const base = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
      const basePath = process.env.REACT_APP_API_BASE_PATH || '/api'
      const res = await fetch(`${base}${basePath}/usuarios/unlock/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo: email }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data?.detail || data?.message || 'No se pudo enviar el enlace')
      }
      setResent(true)
      setMessage('Si la cuenta existe y está bloqueada, enviaremos instrucciones a tu correo.')
    } catch (err) {
      setMessage(err?.message || 'No se pudo enviar el enlace')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 560, margin: '0 auto', textAlign: 'center' }}>
        <h2 style={{ marginTop: 0 }}>Desbloqueo de cuenta</h2>
        <p className={status === 'ok' ? 'toast toast--ok' : status === 'error' ? 'toast toast--err' : 'help'}>
          {message}
        </p>
        {status === 'ok' && !changed && (
          <form onSubmit={handleSetPassword} style={{ marginTop: 16, textAlign: 'left' }}>
            <div style={{ marginBottom: 12 }}>
              <label className="label" htmlFor="pwd">Nueva contraseña</label>
              <input
                id="pwd"
                type="password"
                className="input"
                value={newPassword}
                onChange={e => setNewPassword(e.target.value)}
                placeholder="8–12, alfanumérica, Aa"
                required
                minLength={8}
                maxLength={12}
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label className="label" htmlFor="pwd2">Confirmar contraseña</label>
              <input
                id="pwd2"
                type="password"
                className="input"
                value={confirmPassword}
                onChange={e => setConfirmPassword(e.target.value)}
                required
                minLength={8}
                maxLength={12}
              />
            </div>
            <button className="button button--accent" type="submit" disabled={submitting}>
              {submitting ? 'Guardando…' : 'Guardar nueva contraseña'}
            </button>
          </form>
        )}
        {status === 'error' && (
          <form onSubmit={handleResend} style={{ marginTop: 16, textAlign: 'left' }}>
            <div style={{ marginBottom: 12 }}>
              <label className="label" htmlFor="email">Correo electrónico</label>
              <input
                id="email"
                type="email"
                className="input"
                value={email}
                onChange={e => setEmail(e.target.value)}
                required
              />
            </div>
            <button className="button button--accent" type="submit" disabled={submitting}>
              {submitting ? 'Enviando…' : 'Solicitar nuevo enlace'}
            </button>
            {resent && <p className="help" style={{ marginTop: 8 }}>Revisa tu correo para el nuevo enlace.</p>}
          </form>
        )}
        <div style={{ marginTop: 16 }}>
          {status === 'ok' && changed ? (
            <button className="button button--accent" onClick={() => navigate('/login')}>Ir a iniciar sesión</button>
          ) : status !== 'ok' ? (
            <button className="button" onClick={() => navigate('/')}>Volver al inicio</button>
          ) : null}
        </div>
      </div>
    </div>
  )
}

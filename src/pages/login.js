import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authContext'
import { LOGIN_REDIRECT } from '../app/config'

export default function Login() {
  const { loginAsync } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [caps, setCaps] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [info, setInfo] = useState('')
  const [requesting, setRequesting] = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setInfo('')
    setLoading(true)

    try {
      const result = await loginAsync({ correo: email.trim(), contrasena: password })
      setLoading(false)
      if (!result.ok) {
        const status = result.status
        // Backend messages already localized; surface them
        setError(result.message || (status === 423 ? 'Cuenta bloqueada o inactiva.' : 'Credenciales inválidas.'))
        return
      }
  let redirect = result.data?.redirect_to || LOGIN_REDIRECT
  // Normalize known legacy path
  if (redirect === '/profile') redirect = '/player/profile'
  navigate(redirect)
    } catch (e) {
      setLoading(false)
      setError('No se pudo conectar con el servidor.')
    }
  }

  async function handleRequestUnlock() {
    setError('')
    setInfo('')
    const correo = email.trim()
    if (!correo) {
      setError('Ingresa tu correo para solicitar el desbloqueo.')
      return
    }
    try {
      setRequesting(true)
      const base = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000'
      const basePath = process.env.REACT_APP_API_BASE_PATH || '/api'
      const res = await fetch(`${base}${basePath}/usuarios/unlock/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo }),
      })
      const data = await res.json().catch(() => ({}))
      if (!res.ok) {
        throw new Error(data?.detail || data?.message || 'No se pudo procesar la solicitud')
      }
      setInfo(data?.message || 'Si la cuenta existe y está bloqueada, enviaremos un enlace a tu correo.')
    } catch (err) {
      setError(err?.message || 'No se pudo procesar la solicitud')
    } finally {
      setRequesting(false)
    }
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 480, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Iniciar sesión</h2>
        <p style={{ color: 'var(--muted)' }}>Introduce tu correo y contraseña para acceder.</p>

        <form className="form" onSubmit={handleSubmit} noValidate>
          <div className="form__group">
            <label htmlFor="email">Correo</label>
            <input
              id="email"
              className="input"
              name="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="tucorreo@ejemplo.com"
              maxLength={50}
              inputMode="email"
            />
          </div>

          <div className="form__group">
            <label htmlFor="password">Contraseña</label>
            <input
              id="password"
              className="input"
              type="password"
              name="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyUp={(e) => setCaps(e.getModifierState && e.getModifierState('CapsLock'))}
              placeholder="••••••••"
              maxLength={12}
            />
            {caps && <div className="help">Bloq Mayús activado</div>}
          </div>

          <button className="button button--accent" disabled={loading}>
            {loading ? 'Verificando…' : 'Entrar'}
          </button>

          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            <button type="button" className="button" onClick={handleRequestUnlock} disabled={requesting}>
              {requesting ? 'Enviando…' : 'Solicitar desbloqueo'}
            </button>
          </div>

          {error && <div className="toast toast--err" style={{ marginTop: 12 }}>{error}</div>}
          {info && <div className="toast toast--ok" style={{ marginTop: 12 }}>{info}</div>}

          <div className="help" style={{ marginTop: 8 }}>
            ¿No tienes cuenta? Regístrate.
          </div>
        </form>
      </div>
    </div>
  )
}

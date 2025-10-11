import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authContext'
import { getAuthMeta, setAuthMeta, resetAuthMeta } from '../utils/session'

// Credenciales DEMO — cambia aquí si quieres
const DEMO_EMAIL = 'demo@nfl.com'
const DEMO_PASSWORD = 'DemoPass1'

function isValidCredentials(email, password) {
  return email.toLowerCase() === DEMO_EMAIL && password === DEMO_PASSWORD
}

export default function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [caps, setCaps] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const meta = getAuthMeta(email)

    if (meta.locked) {
      setLoading(false)
      setError('Tu cuenta está bloqueada. Contacta al administrador.')
      return
    }

    // Validación visual (genérica)
    const ok = isValidCredentials(email.trim(), password)
    if (!ok) {
      const failed = (meta.failedCount || 0) + 1
      const locked = failed >= 5
      setAuthMeta(email, { failedCount: failed, locked })
      setLoading(false)
      setError('Usuario o contraseña inválidos.') // genérico
      return
    }

    // éxito: reset intentos, crea sesión y redirige
    resetAuthMeta(email)
    login({ email })
    setLoading(false)
    navigate('/player/profile') // redirección al perfil del jugador
  }

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 480, margin: '0 auto' }}>
        <h2 style={{ marginTop: 0 }}>Iniciar sesión</h2>
        <p style={{ color: 'var(--muted)' }}>
          Demo visual (sin backend). Se bloquea la cuenta tras 5 intentos fallidos.
        </p>

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

          {error && <div className="toast toast--err" style={{ marginTop: 12 }}>{error}</div>}

          <div className="help" style={{ marginTop: 8 }}>
            Tip demo: <code>{DEMO_EMAIL}</code> / <code>{DEMO_PASSWORD}</code>
          </div>
        </form>
      </div>
    </div>
  )
}

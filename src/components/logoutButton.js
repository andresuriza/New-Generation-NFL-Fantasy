import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authContext'
import { LOGOUT_REDIRECT } from '../app/config'

export default function LogoutButton({ className = 'button', children = 'Cerrar sesión' }) {
  const { logoutAsync } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleClick() {
    setError('')
    setLoading(true)
    try {
      const res = await logoutAsync()
  // 1) Desmonta vistas protegidas
  navigate(LOGOUT_REDIRECT, { replace: true })
      setLoading(false)
      if (!res?.ok) {
        setError(res?.message || 'La sesión podría no haberse cerrado correctamente. Intenta de nuevo.')
      }
    } catch (e) {
      setLoading(false)
      setError('No se pudo cerrar la sesión. Intenta de nuevo.')
    }
  }

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', gap: 8 }}>
      <button className={className} onClick={handleClick} disabled={loading}>
        {loading ? 'Cerrando…' : children}
      </button>
      {error && <div className="toast toast--err">{error}</div>}
    </div>
  )
}

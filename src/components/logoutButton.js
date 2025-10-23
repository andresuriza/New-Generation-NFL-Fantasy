import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authContext'
import { fakeLogoutRequest } from '../utils/network'

export default function LogoutButton({ className = 'button', children = 'Cerrar sesión' }) {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleClick() {
    setError('')
    setLoading(true)
    try {
      await fakeLogoutRequest()
    } catch {
      setLoading(false)
      setError('La sesión podría no haberse cerrado correctamente. Intenta de nuevo.')
      return
    }

    // 1) Desmonta vistas protegidas
    navigate('/', { replace: true })
    // 2) Limpia la sesión en el siguiente tick
    setTimeout(() => logout(), 0)
    setLoading(false)
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

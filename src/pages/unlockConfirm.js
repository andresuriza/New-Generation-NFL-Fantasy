import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'

export default function UnlockConfirm() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState('pending')
  const [message, setMessage] = useState('Validando token…')

  useEffect(() => {
    const token = searchParams.get('token')
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
        setMessage(data?.message || 'Tu cuenta ha sido desbloqueada. Ya puedes iniciar sesión.')
      } catch (err) {
        setStatus('error')
        setMessage(err?.message || 'No se pudo desbloquear la cuenta')
      }
    }

    confirm()
  }, [searchParams])

  return (
    <div className="container" style={{ paddingTop: 24, paddingBottom: 48 }}>
      <div className="card" style={{ maxWidth: 560, margin: '0 auto', textAlign: 'center' }}>
        <h2 style={{ marginTop: 0 }}>Desbloqueo de cuenta</h2>
        <p className={status === 'ok' ? 'toast toast--ok' : status === 'error' ? 'toast toast--err' : 'help'}>
          {message}
        </p>
        <div style={{ marginTop: 16 }}>
          {status === 'ok' ? (
            <button className="button button--accent" onClick={() => navigate('/login')}>Ir a iniciar sesión</button>
          ) : (
            <button className="button" onClick={() => navigate('/')}>Volver al inicio</button>
          )}
        </div>
      </div>
    </div>
  )
}

import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { getSession, createSession, clearSession, updateActivity, isExpired } from '../utils/session'
import { apiLogin } from '../utils/api'

const AuthCtx = createContext(null)

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const s = getSession()
    return s && !isExpired(s) ? s : null
  })

  useEffect(() => {
    function onStorage(e) {
      if (e && e.key && e.key !== 'nfl_session') return
      const s = getSession()
      if (!s || isExpired(s)) { setSession(null); return }
      setSession(s)
    }
    window.addEventListener('storage', onStorage)
    const id = setInterval(() => {
      const s = getSession()
      if (s && isExpired(s)) {
        clearSession()
        setSession(null)
      }
    }, 60 * 1000)
    return () => { window.removeEventListener('storage', onStorage); clearInterval(id) }
  }, [])

  useEffect(() => {
    if (!session) return
    const bump = () => updateActivity()
    window.addEventListener('click', bump)
    window.addEventListener('keydown', bump)
    window.addEventListener('mousemove', bump)
    return () => {
      window.removeEventListener('click', bump)
      window.removeEventListener('keydown', bump)
      window.removeEventListener('mousemove', bump)
    }
  }, [session])

  async function loginAsync({ correo, contrasena }) {
    try {
      const res = await apiLogin({ correo, contrasena })
      // Backend returns: { access_token, refresh_token, token_type, usuario, expires_in, redirect_to }
      const { access_token, refresh_token, usuario } = res
      const s = createSession({
        email: usuario?.correo,
        userId: usuario?.id,
        accessToken: access_token,
        refreshToken: refresh_token,
        user: usuario,
      })
      setSession(s)
      return { ok: true, data: res }
    } catch (err) {
      const status = err?.status
      const message = err?.message || 'No se pudo iniciar sesión'
      return { ok: false, status, message }
    }
  }

  async function logoutAsync() {
    // For now we only clear local session; backend session invalidation can be added later
    clearSession()
    setSession(null)
    return { ok: true }
  }

  const value = useMemo(() => ({
    session,
    // old demo login remains available but prefer loginAsync
    login: ({ email }) => { const s = createSession({ email }); setSession(s) },
    loginAsync,
    logout: () => { clearSession(); setSession(null) },
    logoutAsync,
    isAuthenticated: !!session,
    user: session?.user || null,
    accessToken: session?.accessToken || null,
  }), [session])

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}

export function useAuth() {
  return useContext(AuthCtx)
}

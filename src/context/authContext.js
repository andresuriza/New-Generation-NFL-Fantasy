import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { getSession, createSession, clearSession, updateActivity, isExpired } from '../utils/session'
import { fakeLogoutRequest } from '../utils/network'

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

  async function logoutAsync() {
    // 1) intenta “cerrar sesión” en servidor
    try {
      await fakeLogoutRequest()
    } catch (err) {
      // NO limpiamos sesión: informará el botón/llamador
      return { ok: false, message: 'Fallo de red. Intenta de nuevo.' }
    }
    // 2) éxito: limpiar sesión local (todas las pestañas)
    clearSession()
    setSession(null)
    return { ok: true }
  }

  const value = useMemo(() => ({
    session,
    login: ({ email }) => { const s = createSession({ email }); setSession(s) },
    logout: () => { clearSession(); setSession(null) },   // sin red (por si lo quieres usar)
    logoutAsync,                                          // ⬅️ con red simulada
    isAuthenticated: !!session
  }), [session])

  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>
}

export function useAuth() {
  return useContext(AuthCtx)
}

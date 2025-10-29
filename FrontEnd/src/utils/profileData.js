const DEFAULT_AVATAR = 'https://avatars.githubusercontent.com/u/9919?s=200&v=4'
const PROFILE_KEY = (email) => `profile_${email.toLowerCase()}`
const HISTORY_KEY = (email) => `profile_history_${email.toLowerCase()}`

// Perfil base “mock” si no hay nada guardado
function defaultProfile(email) {
  const base = email?.split('@')[0] || 'user'
  return {
    id: 'usr_' + (email?.replace(/[^a-z0-9]/gi, '').slice(0, 10) || 'demo'),
    name: base.charAt(0).toUpperCase() + base.slice(1),
    email,
    alias: 'Coach ' + base,
    language: 'en',
    profileImage: null,
    createdAt: new Date('2024-08-20T14:35:00Z').toISOString(),
    role: 'manager',
    status: 'active',
  }
}

export function getProfile(email) {
  if (!email) return null
  try {
    const saved = JSON.parse(localStorage.getItem(PROFILE_KEY(email)))
    return saved || defaultProfile(email)
  } catch {
    return defaultProfile(email)
  }
}

export function saveProfile(email, partial) {
  const current = getProfile(email)
  const merged = { ...current, ...partial }
  localStorage.setItem(PROFILE_KEY(email), JSON.stringify(merged))
  return merged
}

export function getHistory(email) {
  if (!email) return []
  try {
    return JSON.parse(localStorage.getItem(HISTORY_KEY(email))) || []
  } catch {
    return []
  }
}

export function addHistory(email, changes) {
  // changes: [{ field, oldValue, newValue }]
  const hist = getHistory(email)
  hist.unshift({
    id: `chg_${Date.now()}`,
    at: new Date().toISOString(),
    changes
  })
  localStorage.setItem(HISTORY_KEY(email), JSON.stringify(hist))
  return hist
}

export const DEFAULTS = { DEFAULT_AVATAR }

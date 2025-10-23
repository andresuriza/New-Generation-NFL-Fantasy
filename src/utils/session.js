// ====== Configuración ======
export const INACTIVITY_MS = 12 * 60 * 60 * 1000; // 12 horas
const SESSION_KEY = 'nfl_session';
const AUTH_META_KEY = 'nfl_auth_meta'; // por email: { failedCount, locked }

// ====== Helpers de storage ======
function read(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback } catch { return fallback }
}
function write(key, value) {
  localStorage.setItem(key, JSON.stringify(value));
}

// ====== Auth meta (intentos / lock) ======
export function getAuthMeta(email) {
  const meta = read(AUTH_META_KEY, {});
  return meta[email?.toLowerCase?.()] || { failedCount: 0, locked: false };
}

export function setAuthMeta(email, partial) {
  const key = email?.toLowerCase?.();
  const meta = read(AUTH_META_KEY, {});
  meta[key] = { ...(meta[key] || { failedCount: 0, locked: false }), ...partial };
  write(AUTH_META_KEY, meta);
}

export function resetAuthMeta(email) {
  const key = email?.toLowerCase?.();
  const meta = read(AUTH_META_KEY, {});
  if (meta[key]) {
    meta[key] = { failedCount: 0, locked: false };
    write(AUTH_META_KEY, meta);
  }
}

// ====== Sesión ======
export function getSession() {
  return read(SESSION_KEY, null); // { email, userId, createdAt, lastActivity }
}

export function createSession({ email, userId = 'demo-user' }) {
  const now = Date.now();
  const session = { email, userId, createdAt: now, lastActivity: now };
  write(SESSION_KEY, session);
  // dispara evento manual para otras pestañas
  window.dispatchEvent(new StorageEvent('storage', { key: SESSION_KEY }));
  return session;
}

export function updateActivity() {
  const s = getSession();
  if (!s) return;
  s.lastActivity = Date.now();
  write(SESSION_KEY, s);
  window.dispatchEvent(new StorageEvent('storage', { key: SESSION_KEY }));
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY);
  window.dispatchEvent(new StorageEvent('storage', { key: SESSION_KEY }));
}

export function isExpired(sess) {
  if (!sess) return true;
  return Date.now() - (sess.lastActivity || sess.createdAt) > INACTIVITY_MS;
}

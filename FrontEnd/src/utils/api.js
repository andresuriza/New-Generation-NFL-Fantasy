// Minimal API client for backend integration
// Uses REACT_APP_API_BASE_URL or defaults to http://localhost:8000
// All endpoints are under /api on the backend

import { getSession } from './session';

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
const BASE_API_PATH = process.env.REACT_APP_API_BASE_PATH || '/api';

async function request(path, options = {}) {
  const { method = 'GET', body, headers } = options;
  const session = getSession();
  const token = session?.accessToken;

  const isFormData = typeof FormData !== 'undefined' && body instanceof FormData;

  const finalHeaders = {
    ...(headers || {}),
    // Only set JSON content-type when not sending FormData
    ...(!isFormData ? { 'Content-Type': 'application/json' } : {}),
  };
  if (token) finalHeaders['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${BASE_API_PATH}${path}`, {
    method,
    headers: finalHeaders,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    credentials: 'omit',
  });

  let data = null;
  const ct = res.headers.get('Content-Type') || '';
  if (ct.includes('application/json')) {
    try { data = await res.json(); } catch { data = null; }
  } else {
    try { data = await res.text(); } catch { data = null; }
  }

  if (!res.ok) {
    const message = (data && (data.detail || data.message)) || res.statusText;
    const err = new Error(message || 'Request failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export async function apiLogin({ correo, contrasena }) {
  return request('/usuarios/login', {
    method: 'POST',
    body: { correo, contrasena },
  });
}

export async function apiRegisterUser({ nombre, alias, correo, contrasena, confirmar_contrasena, rol = 'manager' }) {
  return request('/usuarios/', {
    method: 'POST',
    body: { nombre, alias, correo, contrasena, confirmar_contrasena, rol },
  });
}

export async function apiRegisterEquipo({ liga_id, usuario_id, nombre, thumbnail }) {
  return request('/equipos/', {
    method: 'POST',
    body: { liga_id, usuario_id, nombre, thumbnail },
  });
}

export { BASE_URL };

export async function apiGetEquipo(equipoId) {
  return request(`/equipos/${equipoId}`);
}

export async function apiUpdateEquipo(equipoId, payload) {
  return request(`/equipos/${equipoId}`, {
    method: 'PUT',
    body: payload,
  });
}

export async function apiListEquipos() {
  return request(`/equipos/`);
}

export async function apiListUsuarios() {
  return request(`/usuarios/`);
}

export async function apiGetUsuario(usuarioId) {
  return request(`/usuarios/${usuarioId}`);
}

export async function apiUpdateUsuario(usuarioId, payload) {
  return request(`/usuarios/${usuarioId}`, {
    method: 'PUT',
    body: payload,
  });
}

export async function apiListLigas() {
  return request(`/ligas/`);
}

export async function apiGetLiga(ligaId) {
  return request(`/ligas/${ligaId}`);
}

export async function apiGetEquipoMedia(equipoId) {
  return request(`/media/${equipoId}`);
}

export async function apiUploadEquipoImage(equipoId, file) {
  const session = getSession();
  const token = session?.accessToken;
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}${BASE_API_PATH}/media/upload/${equipoId}`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : undefined,
    body: form,
    credentials: 'omit',
  });

  const ct = res.headers.get('Content-Type') || '';
  let data = null;
  if (ct.includes('application/json')) {
    try { data = await res.json(); } catch { /* noop */ }
  } else {
    try { data = await res.text(); } catch { /* noop */ }
  }

  if (!res.ok) {
    const message = (data && (data.detail || data.message)) || res.statusText;
    const err = new Error(message || 'Upload failed');
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

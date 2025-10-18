import http, { request } from '../httpClient';

// Equipos endpoints
export const register = ({ liga_id, usuario_id, nombre, thumbnail }) =>
  request('/equipos/', { method: 'POST', body: { liga_id, usuario_id, nombre, thumbnail } });

export const list = () => http.get('/equipos/');

export const getById = (equipoId) => http.get(`/equipos/${equipoId}`);

export const update = (equipoId, payload) => http.put(`/equipos/${equipoId}`, payload);

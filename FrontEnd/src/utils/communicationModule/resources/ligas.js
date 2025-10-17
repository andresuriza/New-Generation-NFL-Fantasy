import http from '../httpClient';

// Ligas endpoints
export const list = () => http.get('/ligas/');

export const getById = (ligaId) => http.get(`/ligas/${ligaId}`);

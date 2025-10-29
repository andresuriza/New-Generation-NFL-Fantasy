import http, { request } from "../httpClient";

// POST Equipo
export const register = ({ nombre, liga_id, usuario_id, thumbnail }) =>
  request("/equipos/", {
    method: "POST",
    body: { nombre, liga_id, usuario_id, thumbnail },
  });

// GET Equipo
export const list = () => http.get("/equipos/");

export const getById = (equipoId) => http.get(`/equipos/${equipoId}`);

// UPDATE Equipo
export const update = (equipoId, payload) =>
  http.put(`/equipos/${equipoId}`, payload);

// TODO: Revisar orden

import http, { request } from "../httpClient";

// POST Equipo
export const register = ({ liga_id, usuario_id, nombre, thumbnail }) =>
  // Importa orden?
  request("/equipos/", {
    method: "POST",
    body: { liga_id, usuario_id, nombre, thumbnail },
  });

// GET Equipo
export const list = () => http.get("/equipos/");

export const getById = (equipoId) => http.get(`/equipos/${equipoId}`);

// UPDATE Equipo
export const update = (equipoId, payload) =>
  http.put(`/equipos/${equipoId}`, payload);

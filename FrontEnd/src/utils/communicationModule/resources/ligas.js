import http, { request } from "../httpClient";

// Ligas endpoints
export const GetLigas = () => http.get("/ligas/");

export const getById = (ligaId) => http.get(`/ligas/${ligaId}`);

export const CrearLiga = ({
  nombre,
  descripcion,
  contrasena,
  equipos_max,
  temporada_id,
  comisionado_id,
}) =>
  request("/ligas/", {
    method: "POST",
    body: {
      nombre,
      descripcion,
      contrasena,
      equipos_max,
      temporada_id,
      comisionado_id,
    },
  });

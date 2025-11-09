import http, { request } from "../httpClient";

// Ligas endpoints
export const GetLigas = () => http.get("/ligas/");

export const SearchLeague = ({ nombre, skip, limit }) => {
  const params = new URLSearchParams({
    nombre,
    skip,
    limit,
  });

  return request(`ligas/buscar?${params.toString()}`, {
    method: "GET",
  });
};
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

export const JoinLeague = ({
  liga_id,
  usuario_id,
  contrasena,
  alias,
  nombre_equipo,
}) =>
  request(`/ligas/${liga_id}/unirse`, {
    method: "POST",
    body: {
      usuario_id,
      contrasena,
      alias,
      nombre_equipo,
    },
  });

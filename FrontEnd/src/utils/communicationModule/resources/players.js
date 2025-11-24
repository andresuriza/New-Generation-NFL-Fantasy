import { request } from "../httpClient";

export const postPlayer = ({
  nombre,
  posicion,
  equipo_id,
  imagen_url,
  thumbnail_url,
  activo,
}) =>
  request("/jugadores/", {
    method: "POST",
    body: {
      nombre,
      posicion,
      equipo_id,
      imagen_url,
      thumbnail_url,
      activo,
    },
  });

export const postPlayers = (data) =>
  request("/jugadores/bulk", {
    method: "POST",
    body: data,
  });

export const postPlayerNews = ({
  jugador_id,
  texto,
  es_lesion,
  resumen,
  designacion,
}) =>
  request(`/jugadores/${jugador_id}/noticias`, {
    method: "POST",
    body: {
      texto,
      es_lesion,
      resumen,
      designacion,
    },
  });

export const getPlayers = ({
  skip = 0,
  limit = 100,
  posicion,
  equipo_id,
  activo,
  nombre,
} = {}) => {
  const params = new URLSearchParams();
  if (skip !== undefined) params.append('skip', skip);
  if (limit !== undefined) params.append('limit', limit);
  if (posicion) params.append('posicion', posicion);
  if (equipo_id) params.append('equipo_id', equipo_id);
  if (activo !== undefined) params.append('activo', activo);
  if (nombre) params.append('nombre', nombre);

  const queryString = params.toString();
  const url = queryString ? `/jugadores/buscar?${queryString}` : '/jugadores/';

  return request(url);
};

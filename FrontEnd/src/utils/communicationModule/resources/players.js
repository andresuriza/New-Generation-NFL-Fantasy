import { request } from "../httpClient";

export const postPlayer = (
  nombre,
  posicion,
  equipo_id,
  imagen_url,
  thumbnail_url,
  activo
) => {
  return request("/jugadores/", {
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
};

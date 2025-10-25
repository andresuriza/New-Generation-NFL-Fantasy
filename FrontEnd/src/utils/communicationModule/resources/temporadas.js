import http, { request } from "../httpClient";

// Ligas endpoints
export const GetTemporada = () => http.get("/temporadas/");

export const getById = (ligaId) => http.get(`/temporadas/${ligaId}`);

// Aqui colocaria un POST... SI TUVIERA UNO
export const CrearTemporada = ({
  nombre,
  semanas,
  fecha_inicio,
  fecha_fin,
  es_actual,
}) =>
  request("/temporadas/", {
    method: "POST",
    body: {
      nombre,
      semanas,
      fecha_inicio,
      fecha_fin,
      es_actual,
    },
  });

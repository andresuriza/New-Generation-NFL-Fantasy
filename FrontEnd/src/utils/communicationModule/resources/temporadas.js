import http, { request } from "../httpClient";

// Ligas endpoints
export const GetTemporada = () => http.get("/temporadas/");

export const GetTemporadaActual = () => http.get("/temporadas/actual");

export const GetTemporadaId = (id) => http.get(`/temporadas/${id}`);

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

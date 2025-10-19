import http, { request } from "../httpClient";

// Ligas endpoints
export const list = () => http.get("/ligas/");

export const getById = (ligaId) => http.get(`/ligas/${ligaId}`);

// Aqui colocaria un POST... SI TUVIERA UNO
export const CrearLiga = ({ nombre }) =>
  request("/ligas/", {
    method: "POST",
    body: { nombre },
  });

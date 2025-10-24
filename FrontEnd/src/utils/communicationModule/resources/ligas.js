import http, { request } from "../httpClient";

// Ligas endpoints
export const GetLigas = () => http.get("/ligas/");

export const getById = (ligaId) => http.get(`/ligas/${ligaId}`);

// Aqui colocaria un POST... SI TUVIERA UNO
export const CrearLiga = ({
  nombre,
  descripcion,
  contrasena,
  equipos_max,
  temporada_id,
  comisionado_id,
  cupo_equipos,
  playoffs_equipos,
  puntajes_decimales,
  trade_deadline_activa,
  limite_cambios_temp,
  limite_agentes_temp,
  formato_posiciones,
  puntos_config,
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
      cupo_equipos,
      playoffs_equipos,
      puntajes_decimales,
      trade_deadline_activa,
      limite_cambios_temp,
      limite_agentes_temp,
      formato_posiciones,
      puntos_config,
    },
  });

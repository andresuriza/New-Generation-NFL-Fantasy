import http, { request } from "../httpClient";

// Usuarios endpoints
export const login = ({ correo, contrasena }) =>
  request("/usuarios/login", { method: "POST", body: { correo, contrasena } });

export const register = ({
  nombre,
  alias,
  correo,
  idioma,
  imagen_perfil_url,
  contrasena,
  confirmar_contrasena,
  rol,
}) =>
  request("/usuarios/", {
    method: "POST",
    body: {
      nombre,
      alias,
      correo,
      idioma,
      imagen_perfil_url,
      contrasena,
      confirmar_contrasena,
      rol,
    },
  });

export const list = () => http.get("/usuarios/");

export const getById = (usuarioId) => http.get(`/usuarios/${usuarioId}`);

export const update = (usuarioId, payload) =>
  http.put(`/usuarios/${usuarioId}`, payload);

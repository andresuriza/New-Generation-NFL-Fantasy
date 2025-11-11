// Reusable HTTP client for backend integration
// - Injects Authorization header from session
// - Handles JSON and FormData bodies automatically
// - Normalizes error objects with status and data

import { getSession } from "../session";

export const BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";
export const BASE_API_PATH = process.env.REACT_APP_API_BASE_PATH || "/api";

function buildUrl(path) {
  const base = `${BASE_URL}${BASE_API_PATH}`.replace(/\/$/, "");
  const p = String(path || "").startsWith("/") ? path : `/${path || ""}`;
  return `${base}${p}`;
}

async function handleResponse(res) {
  const ct = res.headers.get("Content-Type") || "";
  let data = null;
  if (ct.includes("application/json")) {
    try {
      data = await res.json();
    } catch {
      data = null;
    }
  } else {
    try {
      data = await res.text();
    } catch {
      data = null;
    }
  }

  if (!res.ok) {
    let rawMsg =
      data?.detail ||
      data?.message ||
      data?.error ||
      res.statusText ||
      "Solicitud fallida";

    if (typeof rawMsg !== "string") {
      rawMsg = JSON.stringify(rawMsg);
    }

    const err = new Error(rawMsg);
    err.status = res.status;
    err.data = data;
    throw err;
  }

  return data;
}

export async function request(path, options = {}) {
  const { method = "GET", body, headers } = options;
  const session = getSession();
  const token = session?.accessToken;

  const isFormData =
    typeof FormData !== "undefined" && body instanceof FormData;

  const finalHeaders = {
    ...(headers || {}),
    ...(!isFormData ? { "Content-Type": "application/json" } : {}),
  };
  if (token) finalHeaders["Authorization"] = `Bearer ${token}`;

  const res = await fetch(buildUrl(path), {
    method,
    headers: finalHeaders,
    body: body ? (isFormData ? body : JSON.stringify(body)) : undefined,
    credentials: "omit",
  });

  return handleResponse(res);
}

export const http = {
  get: (path, options = {}) => request(path, { ...options, method: "GET" }),
  post: (path, body, options = {}) =>
    request(path, { ...options, method: "POST", body }),
  put: (path, body, options = {}) =>
    request(path, { ...options, method: "PUT", body }),
  patch: (path, body, options = {}) =>
    request(path, { ...options, method: "PATCH", body }),
  delete: (path, options = {}) =>
    request(path, { ...options, method: "DELETE" }),
};

export default http;

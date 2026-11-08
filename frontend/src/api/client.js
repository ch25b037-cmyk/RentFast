import { ApiError } from "./errors";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";
let accessToken = null;

export function setAccessToken(token) { accessToken = token; }
export function clearAccessToken() { accessToken = null; }

async function request(path, options = {}, retry = true) {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  if (accessToken) headers.set("Authorization", `Bearer ${accessToken}`);
  const response = await fetch(`${baseUrl}${path}`, { ...options, headers, credentials: "include" });
  if (response.status === 401 && retry && path !== "/auth/refresh") {
    const refreshed = await request("/auth/refresh", { method: "POST" }, false);
    if (refreshed.access_token) {
      setAccessToken(refreshed.access_token);
      return request(path, options, false);
    }
  }
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    const error = payload.error ?? {};
    throw new ApiError(error.code ?? "INTERNAL_ERROR", error.message ?? "Request failed", error.details, response.status);
  }
  if (response.status === 204) return null;
  return response.json();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body: JSON.stringify(body) }),
  patch: (path, body) => request(path, { method: "PATCH", body: JSON.stringify(body) }),
  delete: (path) => request(path, { method: "DELETE" }),
};

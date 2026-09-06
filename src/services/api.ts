/**
 * Voice of a Girl — typed API client.
 *
 * Axios instance pre-configured with the JWT from localStorage. All requests
 * go through `/api` (proxied to Django by Vite and by the production server).
 */
import axios from "axios";
import type { AxiosError } from "axios";

export const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

http.interceptors.request.use((config) => {
  const token = localStorage.getItem("voice_access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

http.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("voice_access_token");
      localStorage.removeItem("voice_refresh_token");
      localStorage.removeItem("voice_user");
    }
    return Promise.reject(err);
  }
);

export function apiError(err: unknown): string {
  if (err && typeof err === "object" && "response" in err) {
    const e = err as AxiosError<{ detail?: string; [k: string]: unknown }>;
    if (e.response?.data?.detail) return String(e.response.data.detail);
    const d = e.response?.data;
    if (d && typeof d === "object") {
      return Object.values(d)
        .map((v) => (Array.isArray(v) ? v.join(", ") : String(v)))
        .join("; ");
    }
  }
  return "Something went wrong. Please try again.";
}

export async function apiGet<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  const res = await http.get<T>(url, { params });
  return res.data;
}

export async function apiPost<T>(url: string, body?: unknown): Promise<T> {
  const res = await http.post<T>(url, body);
  return res.data;
}

export async function apiPatch<T>(url: string, body?: unknown): Promise<T> {
  const res = await http.patch<T>(url, body);
  return res.data;
}

export async function apiDelete(url: string): Promise<void> {
  await http.delete(url);
}

export interface LoginPayload {
  access: string;
  refresh: string;
  user: import("./types").User;
}

export function persistAuth(payload: LoginPayload) {
  localStorage.setItem("voice_access_token", payload.access);
  localStorage.setItem("voice_refresh_token", payload.refresh);
  localStorage.setItem("voice_user", JSON.stringify(payload.user));
}

export function clearAuth() {
  localStorage.removeItem("voice_access_token");
  localStorage.removeItem("voice_refresh_token");
  localStorage.removeItem("voice_user");
}

export function loadUser(): import("./types").User | null {
  const raw = localStorage.getItem("voice_user");
  if (!raw) return null;
  try {
    return JSON.parse(raw) as import("./types").User;
  } catch {
    return null;
  }
}

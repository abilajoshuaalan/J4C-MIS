/**
 * Axios instance with JWT auth: attaches the access token to every
 * request, and on a 401 transparently refreshes via the refresh token
 * and retries the original request once. If refresh also fails, the user
 * is logged out (handled by auth/AuthContext's response interceptor hook).
 */
import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export const apiClient = axios.create({ baseURL: API_BASE });

let refreshPromise = null;
let onAuthFailure = () => {};

export function setOnAuthFailure(fn) {
  onAuthFailure = fn;
}

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");
      if (!refreshToken) {
        onAuthFailure();
        return Promise.reject(error);
      }
      try {
        if (!refreshPromise) {
          refreshPromise = axios
            .post(`${API_BASE}/token/refresh/`, { refresh: refreshToken })
            .then((res) => {
              localStorage.setItem("access_token", res.data.access);
              return res.data.access;
            })
            .finally(() => {
              refreshPromise = null;
            });
        }
        const newAccess = await refreshPromise;
        originalRequest.headers.Authorization = `Bearer ${newAccess}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        onAuthFailure();
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

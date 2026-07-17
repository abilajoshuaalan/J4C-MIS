/**
 * Auth state: login (obtains JWT pair), logout, and the current user's
 * profile (role + region), fetched from /api/me/ (FR-03: role-aware,
 * region-aware dashboard). Roles are exactly the three from v4 — see
 * cases/models.py UserProfile.Role on the backend.
 */
import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { apiClient, setOnAuthFailure } from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMe = useCallback(async () => {
    try {
      const res = await apiClient.get("/me/");
      setUser(res.data.user);
      setProfile(res.data.profile);
    } catch {
      setUser(null);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    setOnAuthFailure(() => {
      setUser(null);
      setProfile(null);
    });
    if (localStorage.getItem("access_token")) {
      fetchMe();
    } else {
      setLoading(false);
    }
  }, [fetchMe]);

  const login = useCallback(
    async (username, password, rememberDevice) => {
      setError(null);
      try {
        const res = await apiClient.post("/token/", { username, password });
        localStorage.setItem("access_token", res.data.access);
        localStorage.setItem("refresh_token", res.data.refresh);
        if (rememberDevice) {
          localStorage.setItem("remember_device", "1");
        }
        await fetchMe();
        return true;
      } catch (err) {
        // FR-04: reject invalid credentials with a clear message.
        setError(
          err.response?.status === 401
            ? "Invalid email or password."
            : "Sign-in failed. Check your connection and try again."
        );
        return false;
      }
    },
    [fetchMe]
  );

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    setProfile(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, profile, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

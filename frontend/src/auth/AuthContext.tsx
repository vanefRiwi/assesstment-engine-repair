import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { authApi } from "../api/auth-api";
import { setAccessToken, setUnauthorizedHandler } from "../api/http";
import type { User } from "../api/types";
import { tokenExpiresAt } from "./token";

// sessionStorage keeps the token for this tab only; it is cleared when the browser tab closes.
const STORAGE_KEY = "engine-repair.token";

interface AuthState {
  user: User | null;
  loading: boolean;
  sessionExpired: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: (expired?: boolean) => void;
}

const AuthContext = createContext<AuthState | null>(null);

function readStoredToken(): string | null {
  const token = sessionStorage.getItem(STORAGE_KEY);
  const expiresAt = token ? tokenExpiresAt(token) : null;
  return token && expiresAt && expiresAt > Date.now() ? token : null;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(readStoredToken);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(Boolean(token));
  const [sessionExpired, setSessionExpired] = useState(false);

  const logout = useCallback((expired = false) => {
    sessionStorage.removeItem(STORAGE_KEY);
    setAccessToken(null);
    setToken(null);
    setUser(null);
    setSessionExpired(expired);
  }, []);

  useEffect(() => setUnauthorizedHandler(() => logout(true)), [logout]);

  // Load the profile for the current token and schedule the logout at expiry.
  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }
    setAccessToken(token);
    setLoading(true);
    authApi
      .me()
      .then(setUser)
      .catch(() => logout(true))
      .finally(() => setLoading(false));

    const expiresAt = tokenExpiresAt(token) ?? Date.now();
    const timer = window.setTimeout(() => logout(true), Math.max(expiresAt - Date.now(), 0));
    return () => window.clearTimeout(timer);
  }, [token, logout]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await authApi.login(email, password);
    sessionStorage.setItem(STORAGE_KEY, response.access_token);
    setSessionExpired(false);
    setToken(response.access_token);
  }, []);

  const value = useMemo(
    () => ({ user, loading, sessionExpired, login, logout }),
    [user, loading, sessionExpired, login, logout],
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used inside AuthProvider");
  return context;
}

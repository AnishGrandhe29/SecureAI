"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

// ─── Types ──────────────────────────────────────────────────────────

export interface Filters {
  year?: number | null;
  genre?: string | null;
  city?: string | null;
  month?: string | null;
}

export interface AuthState {
  token: string | null;
  role: string | null;
  username: string | null;
}

interface AppContextType {
  filters: Filters;
  setFilters: React.Dispatch<React.SetStateAction<Filters>>;
  auth: AuthState;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  apiUrl: string;
  apiFetch: (path: string, options?: RequestInit) => Promise<Response>;
}

const AppContext = createContext<AppContextType | null>(null);

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}

// ─── Provider ───────────────────────────────────────────────────────

export function AppProvider({ children }: { children: React.ReactNode }) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const [filters, setFilters] = useState<Filters>({});
  const [auth, setAuth] = useState<AuthState>({
    token: null,
    role: null,
    username: null,
  });

  const login = useCallback(async (username: string, password: string) => {
    try {
      const res = await fetch(`${apiUrl}/api/auth/token`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) return false;
      const data = await res.json();
      setAuth({ token: data.access_token, role: data.role, username });
      return true;
    } catch {
      return false;
    }
  }, [apiUrl]);

  const logout = useCallback(() => {
    setAuth({ token: null, role: null, username: null });
  }, []);

  const apiFetch = useCallback(async (path: string, options: RequestInit = {}) => {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string> || {}),
    };
    if (auth.token) {
      headers["Authorization"] = `Bearer ${auth.token}`;
    }
    return fetch(`${apiUrl}${path}`, { ...options, headers });
  }, [apiUrl, auth.token]);

  return (
    <AppContext.Provider value={{ filters, setFilters, auth, login, logout, apiUrl, apiFetch }}>
      {children}
    </AppContext.Provider>
  );
}

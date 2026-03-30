import React, { createContext, useContext, useEffect, useState } from "react";
import { saveToken, getToken, saveUser, getUser, clearAuth } from "@/lib/auth";
import * as api from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<{ ok: boolean; error?: string }>;
  register: (email: string, password: string, username: string, displayName?: string) => Promise<{ ok: boolean; error?: string }>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState>({
  user: null,
  token: null,
  loading: true,
  isAuthenticated: false,
  login: async () => ({ ok: false }),
  register: async () => ({ ok: false }),
  logout: async () => {},
  refreshUser: async () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const storedToken = await getToken();
      if (storedToken) {
        setToken(storedToken);
        try {
          const me = await api.getMe();
          if (me?.id) {
            setUser(me);
            await saveUser(me);
          } else {
            await clearAuth();
          }
        } catch {
          await clearAuth();
        }
      }
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    try {
      const data = await api.login(email, password);
      if (data.access_token) {
        await saveToken(data.access_token);
        setToken(data.access_token);
        const me = await api.getMe();
        if (me?.id) {
          setUser(me);
          await saveUser(me);
        }
        return { ok: true };
      }
      return { ok: false, error: data.detail || "Login failed" };
    } catch (e: any) {
      return { ok: false, error: e.message || "Network error" };
    }
  }

  async function register(email: string, password: string, username: string, displayName?: string) {
    try {
      const data = await api.register(email, password, username, displayName);
      if (data.access_token) {
        await saveToken(data.access_token);
        setToken(data.access_token);
        const me = await api.getMe();
        if (me?.id) {
          setUser(me);
          await saveUser(me);
        }
        return { ok: true };
      }
      return { ok: false, error: data.detail || "Registration failed" };
    } catch (e: any) {
      return { ok: false, error: e.message || "Network error" };
    }
  }

  async function logout() {
    await clearAuth();
    setUser(null);
    setToken(null);
  }

  async function refreshUser() {
    try {
      const me = await api.getMe();
      if (me?.id) {
        setUser(me);
        await saveUser(me);
      }
    } catch {}
  }

  return (
    <AuthContext.Provider
      value={{ user, token, loading, isAuthenticated: !!user, login, register, logout, refreshUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}

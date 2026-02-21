"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

function setCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Strict`;
}
function deleteCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^| )${name}=([^;]+)`));
  return match ? match[2] : null;
}

interface User {
  id: string;
  username: string;
  display_name: string;
  avatar_url: string;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string, user?: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  login: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);

  // Restaurar sesión al iniciar
  useEffect(() => {
    const savedToken = getCookie("auth_token") || localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken) {
      setToken(savedToken);
      setCookie("auth_token", savedToken, 7);
    }
    if (savedUser) {
      try { setUser(JSON.parse(savedUser)); } catch {}
    }
  }, []);

  function login(t: string, u?: User) {
    setToken(t);
    setCookie("auth_token", t, 7);
    localStorage.setItem("token", t);
    if (u) {
      setUser(u);
      localStorage.setItem("user", JSON.stringify(u));
    }
  }

  function logout() {
    setToken(null);
    setUser(null);
    deleteCookie("auth_token");
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() { return useContext(AuthContext); }

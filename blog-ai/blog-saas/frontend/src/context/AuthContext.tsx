"use client";
import { createContext, useContext, useState, useEffect, ReactNode } from "react";

function setCookie(name: string, value: string, days = 7) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${value}; expires=${expires}; path=/; SameSite=Strict; Secure`;
}
function deleteCookie(name: string) {
  document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
}

interface User {
  id: string | number;
  username: string;
  display_name: string;
  avatar_url: string;
  is_superuser?: boolean;
}

interface AuthContextType {
  token: string | null;
  user: User | null;
  login: (token: string, user?: User) => void;
  logout: () => void;
  isLoaded: boolean;
}

const AuthContext = createContext<AuthContextType>({
  token: null,
  user: null,
  login: () => {},
  logout: () => {},
  isLoaded: false,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Inicializar desde localStorage al cargar
  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    const savedUser = localStorage.getItem("user");
    if (savedToken) {
      setToken(savedToken);
      setCookie("auth_token", savedToken, 7);
    }
    if (savedUser) {
      try {
        const u = JSON.parse(savedUser);
        setUser(u);
        // Refrescar is_superuser desde /auth/me
        fetch("/api/proxy/api/v1/auth/me", {
          headers: { "Authorization": `Bearer ${savedToken}` }
        }).then(r => r.ok ? r.json() : null).then(me => {
          if (me) {
            const updated = { ...u, is_superuser: me.is_superuser || false };
            setUser(updated);
            localStorage.setItem("user", JSON.stringify(updated));
          }
        }).catch(() => {});
      } catch {}
    }
    setIsLoaded(true);
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
    <AuthContext.Provider value={{ token, user, login, logout, isLoaded }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() { return useContext(AuthContext); }

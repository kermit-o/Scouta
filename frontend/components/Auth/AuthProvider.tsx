// ui/components/Auth/AuthProvider.tsx

'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import axios from 'axios';

// --- Tipos ---
interface User {
  id: number;
  email: string;
  credits_balance: number; // CLAVE para la monetización
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  fetchUserCredits: () => Promise<void>;
}

// Inicialización del Contexto
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// URL Base de su Backend FastAPI (usando la variable de entorno)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const TOKEN_KEY = 'forge_saas_token';

// --- Auth Provider Componente ---
export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const isAuthenticated = !!user;

  // 1. Configuración de Axios para incluir el Token
  const setupAxiosInterceptors = useCallback((token: string | null) => {
    // Esto asegura que cada solicitud a la API incluya el token JWT
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, []);

  // 2. Cargar Sesión al Inicio
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (token) {
      setupAxiosInterceptors(token);
      // Intentar obtener el perfil del usuario para validar el token
      verifyToken(token).finally(() => setLoading(false));
    } else {
      setLoading(false);
    }
  }, [setupAxiosInterceptors]);

  // Función de verificación de Token (Interactúa con su ruta de FastAPI)
  const verifyToken = async (token: string) => {
    try {
      // Necesita una ruta en FastAPI para obtener el usuario actual (ej. /users/me)
      const response = await axios.get(`${API_URL}/users/me`); 
      setUser(response.data);
    } catch (error) {
      console.error('Token verification failed', error);
      localStorage.removeItem(TOKEN_KEY);
      setupAxiosInterceptors(null);
      setUser(null);
    }
  };
  
  // 3. Lógica de LOGIN
  const login = async (email: string, password: string) => {
    setLoading(true);
    try {
      // Usa su ruta de login de FastAPI para obtener el token
      const response = await axios.post(`${API_URL}/auth/login`, { username: email, password });
      
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem(TOKEN_KEY, access_token);
      setupAxiosInterceptors(access_token);
      setUser(userData);
      
      // La respuesta de su backend debe incluir el objeto del usuario (incluyendo 'credits_balance')
      // Si FastAPI solo devuelve el token, se necesita una llamada a /users/me después del login.
      
    } catch (error: any) {
      console.error('Login error', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Error en el login.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Lógica de LOGOUT
  const logout = () => {
    localStorage.removeItem(TOKEN_KEY);
    setupAxiosInterceptors(null);
    setUser(null);
  };
  
  // 5. Fetch de Créditos (CLAVE para la UI)
  const fetchUserCredits = async () => {
      // Esto se llamará para actualizar el balance de créditos en el Navbar.
      try {
          const response = await axios.get(`${API_URL}/users/credits`);
          setUser(prevUser => (prevUser ? { ...prevUser, credits_balance: response.data.credits } : null));
      } catch(error) {
          console.error("Error fetching credits");
      }
  };


  return (
    <AuthContext.Provider value={{ user, isAuthenticated, loading, login, logout, fetchUserCredits }}>
      {children}
    </AuthContext.Provider>
  );
};

// Hook personalizado para usar la autenticación
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
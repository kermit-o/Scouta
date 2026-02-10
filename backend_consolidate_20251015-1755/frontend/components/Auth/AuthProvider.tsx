'use client'
import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Verificar si hay usuario en localStorage
    const savedUser = localStorage.getItem('forge_user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<void> => {
    setLoading(true);
    try {
      // Simular llamada a API
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const userData: User = {
        id: 'user-' + Date.now(),
        email: email,
        name: email.split('@')[0]
      };
      
      setUser(userData);
      localStorage.setItem('forge_user', JSON.stringify(userData));
      
      console.log('✅ Login exitoso, redirigiendo...');
      // Redirigir usando el router de Next.js
      // router.push('/dashboard'); // desactivado para permitir rutas como /forge/lego-builder
    } catch (error) {
      console.error('❌ Error en login:', error);
      throw new Error('Credenciales inválidas');
    } finally {
      setLoading(false);
    }
  };

  const signup = async (email: string, password: string, name: string): Promise<void> => {
    setLoading(true);
    try {
      // Simular registro
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const userData: User = {
        id: 'user-' + Date.now(),
        email: email,
        name: name
      };
      
      setUser(userData);
      localStorage.setItem('forge_user', JSON.stringify(userData));
      
      console.log('✅ Registro exitoso, redirigiendo...');
      // router.push('/dashboard'); // desactivado para permitir rutas como /forge/lego-builder
    } catch (error) {
      console.error('❌ Error en registro:', error);
      throw new Error('Error en el registro');
    } finally {
      setLoading(false);
    }
  };

  const logout = (): void => {
    setUser(null);
    localStorage.removeItem('forge_user');
    console.log('✅ Logout exitoso');
    router.push('/login');
  };

  const value: AuthContextType = {
    user,
    login,
    signup,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

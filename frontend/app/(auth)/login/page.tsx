// ui/app/(auth)/login/page.tsx

'use client';

import React, { useState, FormEvent, useEffect } from 'react';
import { useAuth } from '../../../components/Auth/AuthProvider';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Usamos el hook de autenticación
  const { login, isAuthenticated, loading } = useAuth();
  const router = useRouter();

  // Redirigir si ya está autenticado
  useEffect(() => {
    if (isAuthenticated && !loading) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, loading, router]);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      // Llamada a la función 'login' del AuthProvider, que interactúa con FastAPI
      await login(email, password);
      
      // La redirección exitosa se maneja en el useEffect, pero forzamos el push por seguridad
      router.push('/dashboard'); 
      
    } catch (err: any) {
      // Manejo de errores de su backend (e.g., credenciales inválidas)
      setError(err.message || 'Error al iniciar sesión. Verifique sus credenciales.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Si el usuario ya está autenticado o estamos cargando, mostramos un estado simple
  if (loading || isAuthenticated) {
    return <div className="flex justify-center items-center h-screen text-xl">Cargando...</div>;
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-xl w-full max-w-md">
        <h2 className="text-3xl font-bold mb-6 text-center text-gray-800">Acceder a Scouta Forge</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="email">
              Correo Electrónico
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="password">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm p-2 bg-red-100 border border-red-200 rounded-lg">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSubmitting}
            className={`w-full py-3 px-4 rounded-lg text-white font-semibold transition duration-300 ${
              isSubmitting
                ? 'bg-gray-400 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isSubmitting ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </button>
        </form>
        
        <p className="mt-6 text-center text-sm text-gray-600">
          ¿No tienes una cuenta?{' '}
          <a href="/signup" className="text-blue-600 hover:text-blue-800 font-medium">
            Regístrate aquí
          </a>
        </p>
      </div>
    </div>
  );
}
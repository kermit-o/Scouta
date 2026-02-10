'use client'
import React, { useEffect } from 'react';
import { useAuth } from '../components/Auth/AuthProvider';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function HomePage() {
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    // Si el usuario está autenticado, redirigir al dashboard
    if (user) {
      router.push('/dashboard');
    }
  }, [user, router]);

  // Si está autenticado, mostrar loading mientras redirige
  if (user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Redirigiendo al dashboard...</p>
        </div>
      </div>
    );
  }

  // Página principal para usuarios no autenticados
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-900 mb-6">
            �� Forge SaaS
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Genera proyectos completos con inteligencia artificial. 
            Desde aplicaciones web hasta APIs y apps móviles.
          </p>
          
          <div className="flex gap-4 justify-center mb-12">
            <Link 
              href="/signup" 
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
            >
              Comenzar Gratis
            </Link>
            <Link 
              href="/login" 
              className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Iniciar Sesión
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl mb-4">⚡</div>
            <h3 className="text-xl font-semibold mb-2">Rápido</h3>
            <p className="text-gray-600">
              Genera proyectos completos en minutos, no en días.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl mb-4">🤖</div>
            <h3 className="text-xl font-semibold mb-2">Inteligente</h3>
            <p className="text-gray-600">
              IA que entiende tus necesidades y genera código optimizado.
            </p>
          </div>
          
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
            <div className="text-2xl mb-4">🎯</div>
            <h3 className="text-xl font-semibold mb-2">Preciso</h3>
            <p className="text-gray-600">
              Proyectos listos para producción con mejores prácticas.
            </p>
          </div>
        </div>

        {/* Project Types */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h2 className="text-3xl font-bold text-center mb-8">
            Tipos de Proyectos
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 bg-blue-50 rounded-lg">
              <div className="text-lg">🌐</div>
              <div className="font-medium">Web Apps</div>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <div className="text-lg">📱</div>
              <div className="font-medium">Mobile</div>
            </div>
            <div className="p-4 bg-purple-50 rounded-lg">
              <div className="text-lg">🔗</div>
              <div className="font-medium">APIs</div>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <div className="text-lg">💻</div>
              <div className="font-medium">Desktop</div>
            </div>
          </div>
        </div>

        {/* Status */}
        <div className="text-center mt-12 p-6 bg-green-50 rounded-xl border border-green-200">
          <div className="text-green-600 font-semibold">
            ✅ Sistema funcionando - Backend conectado en puerto 8001
          </div>
          <div className="text-sm text-green-500 mt-2">
            Frontend: http://localhost:3000 | Backend: http://localhost:8001
          </div>
        </div>
      </div>
    </div>
  );
}

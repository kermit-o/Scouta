'use client'
import React from 'react';
import { useAuth } from '../../components/Auth/AuthProvider';
import Link from 'next/link';

export default function DashboardPage() {
  const { user, logout } = useAuth();

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">No autenticado</h1>
          <Link href="/login" className="text-blue-600 hover:text-blue-800">
            Ir al login
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-sm">F</span>
              </div>
              <h1 className="text-xl font-bold text-gray-900">Forge SaaS</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Hola, {user.name}</span>
              <button
                onClick={logout}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
              >
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🎉 ¡Bienvenido a tu Dashboard!
          </h1>
          <p className="text-xl text-gray-600">
            Estás autenticado como: <strong>{user.email}</strong>
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1 */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4">
              <span className="text-2xl">🚀</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Crear Proyecto</h3>
            <p className="text-gray-600 mb-4">Genera un nuevo proyecto con IA</p>
            <Link 
              href="/create" 
              className="inline-block bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Comenzar
            </Link>
          </div>

          {/* Card 2 */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4">
              <span className="text-2xl">📊</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Mis Proyectos</h3>
            <p className="text-gray-600 mb-4">Revisa tus proyectos generados</p>
            <button className="bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors">
              Ver Proyectos
            </button>
          </div>

          {/* Card 3 */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4">
              <span className="text-2xl">⚙️</span>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Configuración</h3>
            <p className="text-gray-600 mb-4">Administra tu cuenta</p>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
              Configurar
            </button>
          </div>
        </div>

        {/* User Info */}
        <div className="mt-8 bg-white rounded-2xl shadow-lg border border-gray-200 p-6 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Información de tu Cuenta</h2>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">ID:</span>
              <span className="font-mono text-sm">{user.id}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Nombre:</span>
              <span className="font-medium">{user.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="font-medium">{user.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Estado:</span>
              <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                Activo
              </span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

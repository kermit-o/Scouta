'use client'
import React, { useState, useEffect } from 'react';
import { useAuth } from '../../../components/Auth/AuthProvider';
import { useRouter } from 'next/navigation';

const API_BASE_URL = 'http://localhost:8001';

export default function CreateProject() {
  const [formData, setFormData] = useState({
    project_name: '',
    requirements: ''
  });
  const [loading, setLoading] = useState(false);
  const [createdProject, setCreatedProject] = useState<any>(null);
  const [error, setError] = useState('');
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking');
  
  const { user } = useAuth();
  const router = useRouter();

  // Verificar estado del backend
  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (response.ok) {
          setBackendStatus('online');
        } else {
          setBackendStatus('offline');
        }
      } catch (err) {
        setBackendStatus('offline');
      }
    };

    checkBackend();
  }, []);

  // Redirigir si no está autenticado
  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) return;
    
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: user.id,
          project_name: formData.project_name,
          requirements: formData.requirements
        })
      });

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const project = await response.json();
      setCreatedProject(project);
      console.log('✅ Proyecto creado:', project);
      
    } catch (error) {
      console.error('❌ Error creando proyecto:', error);
      setError(`No se pudo crear el proyecto: ${error instanceof Error ? error.message : 'Error desconocido'}`);
    } finally {
      setLoading(false);
    }
  };

  // Mostrar loading si no está autenticado
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <p className="text-gray-600">Redirigiendo al login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-100 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🚀 Crear Nuevo Proyecto
          </h1>
          <p className="text-lg text-gray-600">
            Describe tu idea y genera el código automáticamente con IA
          </p>
        </div>

        {/* Estado del Backend */}
        <div className={`mb-6 p-4 rounded-xl text-center ${
          backendStatus === 'online' ? 'bg-green-100 text-green-800 border border-green-300' :
          backendStatus === 'offline' ? 'bg-red-100 text-red-800 border border-red-300' :
          'bg-yellow-100 text-yellow-800 border border-yellow-300'
        }`}>
          {backendStatus === 'online' && '✅ Backend conectado y funcionando'}
          {backendStatus === 'offline' && '❌ Backend no disponible - No se pueden crear proyectos'}
          {backendStatus === 'checking' && '🔍 Verificando conexión con el backend...'}
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Formulario */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Detalles del Proyecto
            </h2>
            
            {error && (
              <div className="mb-6 bg-red-100 border border-red-300 text-red-800 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Nombre del Proyecto
                </label>
                <input
                  type="text"
                  value={formData.project_name}
                  onChange={(e) => setFormData({...formData, project_name: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  placeholder="Mi App Increíble"
                  required
                  disabled={backendStatus !== 'online'}
                />
              </div>
              
              <div className="mb-6">
                <label className="block text-gray-700 font-medium mb-2">
                  Descripción y Requerimientos
                </label>
                <textarea
                  value={formData.requirements}
                  onChange={(e) => setFormData({...formData, requirements: e.target.value})}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200"
                  rows={6}
                  placeholder="Describe en detalle lo que quieres construir..."
                  required
                  disabled={backendStatus !== 'online'}
                />
              </div>
              
              <button
                type="submit"
                disabled={loading || backendStatus !== 'online'}
                className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Creando Proyecto...
                  </span>
                ) : (
                  '🎯 Crear Proyecto'
                )}
              </button>
            </form>
          </div>

          {/* Resultados */}
          <div className="space-y-6">
            {/* Proyecto Creado */}
            {createdProject && (
              <div className="bg-green-50 rounded-2xl border border-green-200 p-6">
                <div className="flex items-center mb-4">
                  <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mr-3">
                    <span className="text-white text-sm">✓</span>
                  </div>
                  <h3 className="text-lg font-semibold text-green-800">
                    ¡Proyecto Creado Exitosamente!
                  </h3>
                </div>
                <div className="space-y-2">
                  <p><strong>ID:</strong> {createdProject.id}</p>
                  <p><strong>Nombre:</strong> {createdProject.project_name}</p>
                  <p><strong>Estado:</strong> 
                    <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      {createdProject.status}
                    </span>
                  </p>
                  <p className="text-sm text-green-600 mt-4">
                    ✅ El proyecto ha sido creado en el backend. 
                    Puedes continuar con la planificación y generación de código.
                  </p>
                </div>
              </div>
            )}

            {/* Información de Debug */}
            <div className="bg-blue-50 rounded-2xl border border-blue-200 p-6">
              <h3 className="text-lg font-semibold text-blue-800 mb-3">
                Información de Debug
              </h3>
              <div className="space-y-2 text-sm">
                <p><strong>Backend URL:</strong> {API_BASE_URL}</p>
                <p><strong>Estado:</strong> {backendStatus}</p>
                <p><strong>Usuario:</strong> {user?.email}</p>
                <p><strong>User ID:</strong> {user?.id}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

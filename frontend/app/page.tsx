// ui/app/page.tsx

'use client'
import React, { useState, useEffect } from 'react';
import { useAuth } from '../components/Auth/AuthProvider'; // Asegúrate que esta ruta es correcta
import { getProjects, ProjectResponse, ProjectRequirements, createProject } from '../lib/api/project';
import ProjectCreationForm from '../components/Project/ProjectCreationForm'; // Lo crearemos en la Tarea 3
import ProjectList from '../components/Project/ProjectList'; // Lo crearemos en la Tarea 4

export default function HomePage() {
  const { user, token, logout } = useAuth();
  const [projects, setProjects] = useState<ProjectResponse[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 1. Hook para cargar la lista de proyectos
  useEffect(() => {
    if (token) {
      fetchProjects();
    } else if (!user) {
      // Si no hay token ni usuario, el AuthProvider debería redirigir al login
      console.warn("Usuario no autenticado. Esperando token...");
      setIsLoading(false);
    }
  }, [token, user]);

  const fetchProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getProjects(token as string);
      setProjects(data);
    } catch (err) {
      console.error("Error al cargar proyectos:", err);
      setError("No se pudieron cargar los proyectos. ¿Está el backend activo?");
      setProjects([]);
    } finally {
      setIsLoading(false);
    }
  };

  // 2. Handler para crear un nuevo proyecto
  const handleCreateProject = async (data: ProjectRequirements) => {
    if (!token) {
        alert("Error: Debes iniciar sesión para crear un proyecto.");
        return;
    }
    try {
        const newProject = await createProject(data, token);
        // Añadir el nuevo proyecto (en estado 'QUEUED') a la lista
        setProjects(prev => [newProject, ...prev]);
        alert(`Proyecto "${newProject.name}" creado. El proceso de IA ha comenzado.`);
    } catch (err) {
        console.error("Error en la creación del proyecto:", err);
        alert("Fallo al crear el proyecto. Revisa la consola y el backend.");
    }
  };

  if (!user || isLoading) {
    return <main className="p-8 text-center">Cargando...</main>;
  }

  return (
    <main className="min-h-screen bg-gray-50 p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-extrabold text-indigo-700">Froge SaaS Dashboard 🚀</h1>
        <button 
          onClick={logout} 
          className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded transition duration-200"
        >
          Cerrar Sesión ({user.email})
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Columna de Creación de Proyecto (1/3) */}
        <div className="lg:col-span-1">
          <ProjectCreationForm onSubmit={handleCreateProject} /> 
        </div>

        {/* Columna de Listado de Proyectos (2/3) */}
        <div className="lg:col-span-2">
          <h2 className="text-2xl font-semibold text-gray-800 mb-4">Proyectos Generados</h2>
          {error && <p className="text-red-500 mb-4 border border-red-300 p-3 rounded">{error}</p>}
          
          <ProjectList projects={projects} onRefresh={fetchProjects} />
        </div>
      </div>
    </main>
  );
}
// ui/components/Project/ProjectList.tsx

'use client'
import React from 'react';
//import { ProjectResponse } from '../../lib/api/project';
import { RefreshCcw } from 'lucide-react'; // Asumiendo que usas iconos, ej: lucide-react

interface ProjectListProps {
  projects: ProjectResponse[];
  onRefresh: () => void;
}

// Función auxiliar para renderizar el estado del Job con colores
const getStatusBadge = (status: ProjectResponse['status']) => {
  let color = 'bg-gray-200 text-gray-800';
  let text = 'Pendiente';

  switch (status) {
    case 'QUEUED':
      color = 'bg-yellow-100 text-yellow-800 animate-pulse';
      text = 'En Cola (Intake)';
      break;
    case 'RUNNING':
      color = 'bg-blue-100 text-blue-800 animate-pulse';
      text = 'En Proceso (Agentes)';
      break;
    case 'DONE':
      color = 'bg-green-100 text-green-800';
      text = 'Completado ✅';
      break;
    case 'FAILED':
      color = 'bg-red-100 text-red-800';
      text = 'Fallido ❌';
      break;
  }

  return (
    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${color}`}>
      {text}
    </span>
  );
};

export default function ProjectList({ projects, onRefresh }: ProjectListProps) {
  if (projects.length === 0) {
    return (
      <div className="text-center p-10 bg-white rounded-xl shadow-lg">
        <p className="text-gray-500">Aún no has generado ningún proyecto. ¡Empieza en el formulario de la izquierda!</p>
        <button onClick={onRefresh} className="mt-4 text-sm text-indigo-600 hover:text-indigo-800 flex items-center mx-auto">
          <RefreshCcw size={16} className="mr-1" /> Reintentar Carga
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold text-gray-800">Tus Proyectos ({projects.length})</h3>
        <button onClick={onRefresh} className="text-sm text-indigo-600 hover:text-indigo-800 flex items-center">
          <RefreshCcw size={16} className="mr-1" /> Actualizar Estado
        </button>
      </div>
      
      <div className="space-y-4">
        {projects.map((project) => (
          <div key={project.id} className="p-4 border border-gray-200 rounded-lg flex justify-between items-center hover:bg-gray-50 transition duration-150">
            <div>
              <p className="text-lg font-bold text-gray-900">{project.name}</p>
              <p className="text-sm text-gray-500 truncate max-w-lg">{project.requirements.substring(0, 80)}...</p>
              <p className="text-xs text-gray-400 mt-1">Creado: {new Date(project.created_at).toLocaleString()}</p>
            </div>
            <div className="flex flex-col items-end space-y-2">
              {getStatusBadge(project.status)}
              {project.status === 'DONE' && (
                <a href={`/projects/${project.id}/download`} className="text-sm text-green-600 hover:text-green-800 font-medium">
                  Descargar Código
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
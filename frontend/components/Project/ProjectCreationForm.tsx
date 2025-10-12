// ui/components/Project/ProjectCreationForm.tsx

'use client'
import React, { useState } from 'react';
import { ProjectRequirements } from '../../lib/api/project';

interface ProjectCreationFormProps {
  onSubmit: (data: ProjectRequirements) => Promise<void>;
}

export default function ProjectCreationForm({ onSubmit }: ProjectCreationFormProps) {
  const [name, setName] = useState('');
  const [requirements, setRequirements] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || !requirements.trim()) {
      alert("Por favor, introduce un nombre y la idea/requisitos.");
      return;
    }

    setIsSubmitting(true);
    await onSubmit({ name, requirements });
    setIsSubmitting(false);

    // Limpiar el formulario después de la creación
    setName('');
    setRequirements('');
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-indigo-200">
      <h2 className="text-2xl font-bold text-indigo-600 mb-4">Nueva Idea de Proyecto</h2>
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">Nombre del Proyecto</label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            disabled={isSubmitting}
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500"
            placeholder="Ej: Plataforma de Gestión de Citas"
            required
          />
        </div>
        <div className="mb-6">
          <label htmlFor="requirements" className="block text-sm font-medium text-gray-700 mb-1">Requisitos Detallados (La idea que la IA generará)</label>
          <textarea
            id="requirements"
            rows={6}
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            disabled={isSubmitting}
            className="w-full border border-gray-300 rounded-lg p-3 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
            placeholder="Necesito un backend en FastAPI con modelos para Usuarios y Productos. El frontend debe ser en Next.js con una página de listado de productos y un formulario de creación."
            required
          />
        </div>
        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full py-3 px-4 rounded-lg text-white font-semibold transition duration-300 ${isSubmitting ? 'bg-indigo-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700'}`}
        >
          {isSubmitting ? 'Iniciando Forja de Código...' : 'Generar Proyecto con IA'}
        </button>
      </form>
    </div>
  );
}
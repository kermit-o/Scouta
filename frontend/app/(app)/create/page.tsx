// ui/app/(app)/create/page.tsx

'use client';

import React, { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/components/Auth/AuthProvider'; // Necesario para el saldo

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const COST_OF_RUN = 10; // Mostrar al usuario el costo

export default function CreateProjectPage() {
    const [requirements, setRequirements] = useState('');
    const [projectName, setProjectName] = useState('');
    const [error, setError] = useState<string | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const { user, fetchUserCredits } = useAuth(); // Usamos user para mostrar saldo
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsSubmitting(true);

        if (!user || user.credits_balance < COST_OF_RUN) {
            setError(`Necesitas ${COST_OF_RUN} créditos para generar. Recarga tu cuenta.`);
            setIsSubmitting(false);
            return;
        }

        try {
            // 1. Crear el proyecto (POST /api/projects)
            const creationResponse = await axios.post(`${API_URL}/api/projects/`, {
                name: projectName || "Nuevo Proyecto Generado",
                requirements: requirements,
            });

            const projectId = creationResponse.data.id;

            // 2. Iniciar la generación (POST /api/projects/{id}/run)
            await axios.post(`${API_URL}/api/projects/${projectId}/run`);

            // 3. Actualizar el saldo de créditos en la UI
            fetchUserCredits();

            alert('¡Generación iniciada! Revisa el progreso en tu dashboard.');
            router.push(`/project/${projectId}`); // Redirigir a la vista del proyecto

        } catch (err: any) {
            const detail = err.response?.data?.detail || 'Error desconocido al iniciar la generación.';
            setError(detail);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto py-10">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-2">Nuevo Proyecto de IA</h1>
            <p className="text-xl text-gray-600 mb-8">Describe tu aplicación en lenguaje natural para que Forge la construya.</p>
            
            {/* Display de Créditos y Costo */}
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6 rounded-lg">
                <p className="text-sm text-yellow-800 font-medium">
                    Costo de Generación: **{COST_OF_RUN} créditos**. Tu saldo actual: **{user?.credits_balance ?? 0}**.
                    <Link href="/billing" className="ml-3 text-blue-600 hover:underline">
                        Recargar
                    </Link>
                </p>
            </div>
            
            <form onSubmit={handleSubmit} className="space-y-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="name">
                        Nombre del Proyecto (Opcional)
                    </label>
                    <input
                        id="name"
                        type="text"
                        value={projectName}
                        onChange={(e) => setProjectName(e.target.value)}
                        placeholder="Mi App de Gestión de Inventario"
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                        disabled={isSubmitting}
                    />
                </div>
                
                {/* El Editor de Prompts (Core de la UX) */}
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="requirements">
                        Requisitos de la Aplicación (Mínimo 50 caracteres)
                    </label>
                    <textarea
                        id="requirements"
                        value={requirements}
                        onChange={(e) => setRequirements(e.target.value)}
                        rows={10}
                        required
                        placeholder="Necesito una aplicación web full-stack con React y FastAPI. Debe tener un sistema de autenticación de usuarios y una base de datos para almacenar productos. La página principal debe mostrar una tabla de productos con filtros y capacidad de editar/eliminar."
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 resize-none"
                        disabled={isSubmitting}
                    />
                </div>

                {error && (
                    <div className="text-red-600 text-sm p-3 bg-red-100 border border-red-200 rounded-lg">
                        {error}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={isSubmitting || requirements.length < 50 || user!.credits_balance < COST_OF_RUN}
                    className={`w-full py-3 px-4 rounded-lg text-white font-semibold transition duration-300 ${
                        isSubmitting || requirements.length < 50 || user!.credits_balance < COST_OF_RUN
                            ? 'bg-gray-400 cursor-not-allowed'
                            : 'bg-blue-600 hover:bg-blue-700'
                    }`}
                >
                    {isSubmitting ? 'Iniciando pipeline de Agentes...' : `Generar Aplicación (Consume ${COST_OF_RUN} Créditos)`}
                </button>
            </form>
        </div>
    );
}
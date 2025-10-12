// ui/app/(app)/dashboard/page.tsx

'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ProjectListItem {
    id: string;
    name: string;
    status: string;
    created_at: string;
    type: string;
    entities: number; 
}

export default function DashboardPage() {
    const [projects, setProjects] = useState<ProjectListItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchProjects = async () => {
            setLoading(true);
            try {
                // Axios ya tiene el token gracias al interceptor en AuthProvider
                const response = await axios.get(`${API_URL}/api/projects`);
                setProjects(response.data.projects);
                setError(null);
            } catch (err: any) {
                console.error("Error al cargar proyectos:", err);
                // Si falla, probablemente el token expiró.
                setError("No se pudieron cargar los proyectos. Intente reconectar.");
            } finally {
                setLoading(false);
            }
        };

        fetchProjects();
    }, []);

    if (loading) return <p className="text-center mt-8">Cargando tus proyectos generados...</p>;
    if (error) return <p className="text-center mt-8 text-red-600">{error}</p>;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold text-gray-900">Tus Proyectos ({projects.length})</h1>
                <Link href="/create" className="bg-green-600 text-white py-2 px-4 rounded-lg shadow-md hover:bg-green-700 transition duration-150 font-medium">
                    + Nuevo Proyecto
                </Link>
            </div>

            {projects.length === 0 ? (
                <div className="text-center p-12 bg-white rounded-lg shadow-inner">
                    <p className="text-xl text-gray-600 mb-4">Aún no tienes proyectos. ¡Comienza a codificar con IA!</p>
                    <Link href="/create" className="text-blue-600 hover:text-blue-800 font-medium">
                        Generar mi primera aplicación
                    </Link>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {projects.map((project) => (
                        <Link key={project.id} href={`/project/${project.id}`} className="block bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition duration-300 transform hover:-translate-y-1">
                            <h2 className="text-xl font-semibold text-gray-800 truncate mb-2">{project.name}</h2>
                            <p className="text-sm text-gray-500 mb-3">{project.type} &middot; {project.entities} Entidades</p>
                            <div className={`inline-block px-3 py-1 text-xs font-semibold rounded-full ${project.status === 'generated' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                {project.status.toUpperCase()}
                            </div>
                        </Link>
                    ))}
                </div>
            )}
        </div>
    );
}
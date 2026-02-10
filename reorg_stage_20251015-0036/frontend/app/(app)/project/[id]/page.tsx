// ui/app/(app)/project/[id]/page.tsx

'use client';

import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useParams } from 'next/navigation';
import Link from 'next/link';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Tipos simplificados para la respuesta de la API
interface ProjectData {
    id: string;
    name: string;
    status: string;
    requirements: string;
    specification: any; 
    generated_code: { [path: string]: string } | null; // { 'src/main.py': 'def hello(): ...' }
    logs: string[] | null;
}

const POLLING_INTERVAL_MS = 3000; // Consultar el estado cada 3 segundos

export default function ProjectViewPage() {
    const params = useParams();
    const projectId = params.id as string;
    
    const [project, setProject] = useState<ProjectData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Estado para el editor de código (mostrar el archivo seleccionado)
    const [selectedFile, setSelectedFile] = useState<string | null>(null);

    // Función principal de fetching (con lógica de polling)
    const fetchProjectStatus = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/projects/${projectId}`);
            const data: ProjectData = response.data;
            setProject(data);
            setError(null);

            // Si el proyecto ya tiene código generado, seleccionar el primer archivo
            if (data.generated_code && !selectedFile) {
                const firstFilePath = Object.keys(data.generated_code)[0];
                setSelectedFile(firstFilePath);
            }

            return data.status;

        } catch (err: any) {
            console.error("Error fetching project:", err);
            setError(err.response?.data?.detail || 'No se pudo obtener el proyecto. Acceso denegado o ID inválido.');
            return 'error';
        } finally {
            setLoading(false);
        }
    }, [projectId, selectedFile]);


    // Lógica de POLLING
    useEffect(() => {
        let interval: NodeJS.Timeout | null = null;

        const startPolling = async () => {
            const status = await fetchProjectStatus();
            
            // Si el estado no es 'generated', configurar el intervalo de polling
            if (status !== 'generated' && status !== 'error' && interval === null) {
                interval = setInterval(async () => {
                    const currentStatus = await fetchProjectStatus();
                    // Detener el polling si termina o hay error
                    if (currentStatus === 'generated' || currentStatus === 'error') {
                        if (interval) clearInterval(interval);
                    }
                }, POLLING_INTERVAL_MS);
            }
        };

        startPolling();

        // Limpieza: Asegurar que el intervalo se detenga al desmontar el componente
        return () => {
            if (interval) clearInterval(interval);
        };
    }, [fetchProjectStatus]);
    
    const projectStatus = project?.status.toLowerCase() || 'loading';
    const isGenerated = projectStatus === 'generated';
    const codeFiles = project?.generated_code ? Object.keys(project.generated_code) : [];

    // --- Contenido del Archivo Seleccionado ---
    const CodeContent = () => {
        if (!selectedFile || !project?.generated_code) return null;
        const code = project.generated_code[selectedFile];
        
        return (
            <div className="bg-gray-800 p-4 rounded-b-lg overflow-x-auto text-sm">
                <pre>
                    <code className="text-green-300">
                        {code}
                    </code>
                </pre>
            </div>
        );
    };

    if (loading) return <p className="text-center mt-16 text-xl">🚀 Conectando con el pipeline de agentes...</p>;
    if (error) return <p className="text-center mt-16 text-red-600 font-medium">{error}</p>;
    if (!project) return null; // Si el proyecto es null y no hay error, no renderizar nada.


    return (
        <div className="max-w-7xl mx-auto py-10">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                    <p className="text-lg text-gray-500 mt-1">ID: {project.id}</p>
                </div>
                <div className={`px-4 py-2 rounded-full text-white font-semibold shadow-md ${
                    isGenerated ? 'bg-green-500' : 
                    projectStatus === 'running' ? 'bg-blue-500 animate-pulse' :
                    'bg-yellow-500'
                }`}>
                    Estado: {projectStatus.toUpperCase()}
                </div>
            </div>

            {/* Visualizador de Progreso */}
            {!isGenerated && (
                <div className="bg-white p-6 rounded-xl shadow-lg mb-8">
                    <h2 className="text-2xl font-semibold mb-4">Progreso de la Generación de Código</h2>
                    <p className="text-gray-700 mb-4">
                        <span className="font-bold">Requisitos:</span> {project.requirements.substring(0, 150)}...
                    </p>
                    {/* Placeholder para la visualización del log en tiempo real */}
                    <div className="bg-gray-900 text-white p-4 rounded-lg h-48 overflow-y-scroll text-xs font-mono">
                        {project.logs && project.logs.length > 0 ? (
                            project.logs.map((log, index) => <p key={index} className="mb-1">{log}</p>)
                        ) : (
                            <p className="text-yellow-400">Esperando el primer reporte del Agente Principal...</p>
                        )}
                    </div>
                </div>
            )}

            {/* Visualizador de Código Generado */}
            {isGenerated && (
                <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                    <h2 className="text-2xl font-semibold p-4 border-b">Código Generado</h2>
                    
                    {/* Pestañas de Archivos */}
                    <div className="flex border-b bg-gray-100 overflow-x-auto">
                        {codeFiles.map(filePath => (
                            <button
                                key={filePath}
                                onClick={() => setSelectedFile(filePath)}
                                className={`px-4 py-2 text-sm font-medium border-r transition duration-150 ${
                                    selectedFile === filePath
                                        ? 'bg-gray-800 text-white'
                                        : 'text-gray-700 hover:bg-gray-200'
                                }`}
                            >
                                {filePath}
                            </button>
                        ))}
                    </div>

                    {/* Contenido del Archivo */}
                    <CodeContent />
                    
                    {/* Botón de Acción Final */}
                    <div className="p-4 bg-gray-50 flex justify-end">
                        <a 
                            href={`${API_URL}/api/projects/${projectId}/artifact`} // Apunta al endpoint de descarga
                            download 
                            className="bg-blue-600 text-white py-2 px-6 rounded-lg font-semibold hover:bg-blue-700 transition duration-150"
                        >
                            Descargar Proyecto (.zip)
                        </a>
                    </div>
                </div>
            )}
        </div>
    );
}
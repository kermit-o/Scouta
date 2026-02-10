import React, { useState, useCallback, useEffect } from 'react';
import axios from 'axios';
import { Loader2, Zap, Hourglass, CheckCircle, XCircle, ChevronRight } from 'lucide-react';

// URL base de la API
const API_BASE_URL = 'http://localhost:8000/api';
const POLLING_INTERVAL = 3000; // 3 segundos

// Tipos de datos para el estado
type ProjectStatus = 'idle' | 'analyzing' | 'processing' | 'completed' | 'failed';
type AgentStatus = 'running' | 'completed' | 'failed';

interface AgentRun {
  agent: string;
  status: AgentStatus;
  started_at: string | null;
  ended_at: string | null;
  duration: number | null;
}

interface ProjectState {
  id: string;
  name: string;
  status: ProjectStatus;
  requirements: string;
  error: string | null;
  agentRuns: AgentRun[]; // Nuevo campo para el estado del pipeline
}

// Secuencia de agentes para la visualización (debe coincidir con supervisor_agent.py)
const AGENT_SEQUENCE = [
  { id: 'intake', name: '1. Análisis de Requisitos' },
  { id: 'spec', name: '2. Creación de Especificación' },
  { id: 'planning', name: '3. Diseño Arquitectónico' },
  { id: 'builder', name: '4. Generación de Código' },
  { id: 'documenter', name: '5. Documentación y README' },
  { id: 'tester', name: '6. Pruebas Funcionales' },
];

/**
 * Componente principal para ingresar requisitos y monitorear la generación del proyecto.
 */
const PromptEditor: React.FC = () => {
  const [requirements, setRequirements] = useState('');
  const [projectName, setProjectName] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [project, setProject] = useState<ProjectState | null>(null);

  /**
   * Obtiene el estado más reciente del proyecto y actualiza el estado local.
   */
  const fetchProjectStatus = useCallback(async (projectId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/status`);
      const { status: currentStatus, pipeline_details: agentRuns } = response.data;

      setProject(prev => {
        if (!prev) return null;
        
        return {
          ...prev,
          status: currentStatus === 'completed' || agentRuns.some((a: AgentRun) => a.status === 'failed') 
            ? currentStatus : 'processing', // Forzamos 'processing' si no ha terminado
          agentRuns: agentRuns,
          error: currentStatus === 'failed' ? 'El pipeline falló en una etapa. Revisa los logs del agente.' : null,
        };
      });
      
      // Devolver el estado actual para determinar si detener el polling
      return currentStatus;
      
    } catch (error) {
      console.error('Error al consultar estado:', error);
      setProject(prev => prev ? { ...prev, status: 'failed', error: 'Fallo la conexión o el servidor.' } : null);
      return 'failed';
    }
  }, []);


  /**
   * Efecto para iniciar el Polling
   */
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;

    if (project && project.status === 'processing' && project.id !== 'N/A') {
      intervalId = setInterval(async () => {
        const finalStatus = await fetchProjectStatus(project.id);
        
        // Detener el polling si el proyecto ha terminado o fallado
        if (finalStatus === 'completed' || finalStatus === 'failed') {
          if (intervalId) clearInterval(intervalId);
        }
      }, POLLING_INTERVAL);
    }

    // Limpieza: Detener el polling al desmontar o si el estado cambia
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [project, fetchProjectStatus]);


  /**
   * Maneja el envío del formulario para iniciar la generación.
   */
  const handleGenerateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!requirements.trim()) return;

    setIsLoading(true);
    setProject(null);

    try {
      const payload = {
        requirements: requirements,
        project_name: projectName || undefined,
      };

      const response = await axios.post(`${API_BASE_URL}/generate`, payload);
      
      const { project_id, status: initialStatus, specification } = response.data;
      
      const newProject: ProjectState = {
        id: project_id,
        name: projectName || specification?.name || 'Proyecto Generado',
        status: initialStatus,
        requirements: requirements,
        error: null,
        agentRuns: [], // Inicialmente vacío
      };
      setProject(newProject);
      
    } catch (error) {
      let errorMessage = 'Error desconocido al iniciar la generación.';
      if (axios.isAxiosError(error) && error.response) {
        errorMessage = `Error ${error.response.status}: ${error.response.data.detail || error.response.data.error || error.message}`;
      } else if (error instanceof Error) {
        errorMessage = error.message;
      }
      
      setProject({
        id: 'N/A',
        name: projectName || 'Error',
        status: 'failed',
        requirements: requirements,
        error: errorMessage,
        agentRuns: [],
      });

    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Helper para obtener estilos del estado general del proyecto.
   */
  const getProjectStatusDisplay = useCallback((status: ProjectStatus) => {
    switch (status) {
      case 'processing':
      case 'analyzing':
        return { icon: <Loader2 className="w-5 h-5 animate-spin mr-2 text-blue-500" />, color: 'border-blue-500 bg-blue-50', text: 'En Proceso' };
      case 'completed':
        return { icon: <CheckCircle className="w-5 h-5 text-green-500 mr-2" />, color: 'border-green-500 bg-green-50', text: 'Completado' };
      case 'failed':
        return { icon: <XCircle className="w-5 h-5 text-red-500 mr-2" />, color: 'border-red-500 bg-red-50', text: 'Fallido' };
      default:
        return { icon: <Hourglass className="w-5 h-5 text-gray-500 mr-2" />, color: 'border-gray-500 bg-gray-50', text: 'Analizado' };
    }
  }, []);

  /**
   * Helper para obtener estilos de un agente específico en el pipeline.
   */
  const getAgentStepDisplay = useCallback((agentId: string, currentRuns: AgentRun[]) => {
    const run = currentRuns.find(r => r.agent === agentId);
    
    if (run) {
      if (run.status === 'completed') {
        return { color: 'text-green-600 bg-green-100', icon: <CheckCircle className="w-5 h-5" /> };
      }
      if (run.status === 'failed') {
        return { color: 'text-red-600 bg-red-100', icon: <XCircle className="w-5 h-5" /> };
      }
      if (run.status === 'running') {
        return { color: 'text-blue-600 bg-blue-100', icon: <Loader2 className="w-5 h-5 animate-spin" /> };
      }
    }
    
    // Si no ha empezado o es el siguiente
    const isNext = !currentRuns.some(r => r.agent === agentId) && currentRuns.some(r => r.status === 'running');
    if (isNext) {
         return { color: 'text-yellow-600 bg-yellow-100', icon: <Hourglass className="w-5 h-5" /> };
    }

    return { color: 'text-gray-500 bg-gray-100', icon: <ChevronRight className="w-5 h-5" /> };
  }, []);


  return (
    <div className="flex flex-col h-full bg-gray-50 p-6 rounded-xl shadow-2xl font-sans">
      {/* Encabezado del Editor */}
      <div className="mb-6 border-b pb-4">
        <h2 className="text-3xl font-extrabold text-gray-900 flex items-center">
          <Zap className="w-7 h-7 mr-2 text-indigo-600" />
          Forge AI - Editor de Requisitos
        </h2>
        <p className="text-gray-600 mt-1">Describe la aplicación que deseas generar. El pipeline de Agentes se iniciará automáticamente.</p>
      </div>

      {/* Formulario de Requisitos */}
      <form onSubmit={handleGenerateProject} className="flex flex-col space-y-4 flex-grow">
        {/* Campo de Nombre del Proyecto */}
        <input
            type="text"
            placeholder="Nombre opcional del proyecto (ej: TaskMaster 3000)"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 transition duration-150"
            disabled={isLoading}
        />

        {/* Área de Texto de Requisitos */}
        <textarea
          value={requirements}
          onChange={(e) => setRequirements(e.target.value)}
          placeholder="Escribe aquí tus requisitos detallados..."
          className="flex-grow w-full p-4 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500 resize-none text-gray-800 transition duration-150"
          rows={10}
          disabled={isLoading}
        />

        {/* Botón de Generación */}
        <button
          type="submit"
          className={`w-full py-3 px-4 rounded-xl text-white font-semibold flex items-center justify-center transition duration-300 ${
            isLoading || !requirements.trim()
              ? 'bg-indigo-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 shadow-lg shadow-indigo-200'
          }`}
          disabled={isLoading || !requirements.trim()}
        >
          {isLoading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin mr-2" />
              Iniciando Pipeline...
            </>
          ) : (
            <>
              <Zap className="w-5 h-5 mr-2" />
              Generar Proyecto Completo
            </>
          )}
        </button>
      </form>

      {/* Bloque de Estado del Proyecto Generado y Pipeline Tracker */}
      {project && (
        <div className={`mt-6 p-4 rounded-xl border-l-4 shadow-md ${getProjectStatusDisplay(project.status).color}`}>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xl font-bold text-gray-900">{project.name}</h3>
            <div className={`flex items-center px-3 py-1 text-sm font-medium rounded-full ${getProjectStatusDisplay(project.status).color.replace('border-', 'bg-').replace('50', '200')}`}>
              {getProjectStatusDisplay(project.status).icon}
              {getProjectStatusDisplay(project.status).text}
            </div>
          </div>
          
          <p className="text-sm text-gray-600 mt-2">
            <strong>ID de Proyecto:</strong> <span className="font-mono bg-gray-200 px-1 rounded text-xs">{project.id}</span>
          </p>
          
          {/* Visualización del Pipeline Tracker */}
          {project.status !== 'idle' && (
            <div className="mt-4 pt-4 border-t border-gray-200">
              <h4 className="text-lg font-semibold mb-3 text-gray-700">Progreso del Pipeline (Agentes)</h4>
              <div className="space-y-3">
                {AGENT_SEQUENCE.map((agent, index) => {
                  const display = getAgentStepDisplay(agent.id, project.agentRuns);
                  const run = project.agentRuns.find(r => r.agent === agent.id);
                  const duration = run && run.started_at && run.ended_at 
                    ? ` (${(new Date(run.ended_at).getTime() - new Date(run.started_at).getTime()) / 1000}s)` 
                    : '';

                  return (
                    <div key={agent.id} className="flex items-center text-sm">
                      <div className={`p-2 rounded-full mr-3 ${display.color}`}>
                        {display.icon}
                      </div>
                      <span className={`font-medium ${display.color.includes('text-gray') ? 'text-gray-600' : 'text-gray-800'}`}>
                        {agent.name}
                      </span>
                      <span className="ml-auto text-xs text-gray-500">
                        {run ? `${run.status}${duration}` : 'Pendiente'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Mensaje de Error */}
          {project.error && (
            <div className="p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg mt-4 text-sm">
              <strong>Error Crítico:</strong> {project.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PromptEditor;

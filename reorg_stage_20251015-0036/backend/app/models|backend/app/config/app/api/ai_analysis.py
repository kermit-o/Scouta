# cat > core/app/routers/ai_analysis.py

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any

# 1. Importaciones del cliente DeepSeek y configuración
from agents.deepseek_client import DeepSeekClient 
from app.config.ai_config import ai_config
# Importación del agente de intake existente (necesario para el endpoint /analyze-requirements)
from app.agents.intake_agent import IntakeAgent 
# Importación del SUPERVISOR (CLAVE: basado en el archivo que me mostraste)
from app.agents.supervisor_agent import ProjectSupervisor 

router = APIRouter(tags=["AI Analysis"])
deepseek_client = DeepSeekClient() 
intake_agent = IntakeAgent() # Instanciación para /analyze-requirements
supervisor = ProjectSupervisor() # Instanciación del supervisor para la orquestación

class IdeaInput(BaseModel):
    """Esquema para la idea de proyecto enviada desde el frontend."""
    idea: str
    
class RequirementsInput(BaseModel):
    """Esquema para el análisis de requisitos tradicional."""
    requirements: str
    project_id: str = "temp-project" # Valor por defecto

    
# -------------------------------------------------------------
# 1. ENDPOINT PRINCIPAL MODIFICADO: ANALYZE -> ORCHESTRATE
# -------------------------------------------------------------
@router.post("/analyze-idea", response_model=Dict[str, Any])
async def analyze_project_idea(input: IdeaInput):
    """
    Endpoint principal: recibe una idea, la analiza con DeepSeek, 
    y luego crea el proyecto e inicia el proceso de generación.
    """
    
    # Pre-chequeo rápido para evitar llamadas a la API sin clave
    if not ai_config.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Servicio AI (DeepSeek) no configurado. Revise DEEPSEEK_API_KEY."
        )

    try:
        # 1. Llamada a DeepSeek para Análisis Estructurado (ASYNC)
        print(f"Iniciando análisis de idea con DeepSeek: {input.idea[:50]}...")
        analysis_result = await deepseek_client.analyze_idea(input.idea) 
        
        # 2. CREAR PROYECTO e INICIAR TAREA (Llama al nuevo método del Supervisor)
        print("Creando proyecto y cargando plan de DeepSeek...")
        
        # EL CAMBIO CLAVE: Llama al Supervisor para guardar el plan y crear el proyecto
        project_id = supervisor.create_and_start_project(
            raw_idea=input.idea,
            analysis_plan=analysis_result
        ) 
        
        # 3. Respuesta al cliente
        return {
            "status": "Generation Started",
            "project_id": str(project_id), # Aseguramos que sea string para el JSON
            "message": "Análisis completado y proyecto creado en la DB. Proceso de generación en cola/iniciado."
        }
        
    except ValueError as e:
        # Esto captura errores de validación/parsing de JSON desde DeepSeek
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, 
                            detail=f"Error de formato JSON de la IA: {e}")
        
    except Exception as e:
        # Esto captura errores de red, API o fallos en el supervisor
        print(f"Error fatal con DeepSeek o Supervisor: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Fallo inesperado al comunicarse o iniciar la orquestación: {e.__class__.__name__}")


# -------------------------------------------------------------
# 2. ENDPOINT MIGRADO: ANÁLISIS DE REQUISITOS EXISTENTE (SIN CAMBIOS)
# -------------------------------------------------------------
@router.post("/analyze-requirements")
async def analyze_requirements_fastapi(input: RequirementsInput):
    """Analiza requisitos con el agente de Intake tradicional."""
    try:
        if not input.requirements:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Se requieren requisitos.")
        
        print(f"Iniciando análisis de requisitos tradicional para el proyecto {input.project_id}...")
        # Asumo que intake_agent.run es awaitable
        result = await intake_agent.run(input.project_id, input.requirements) 
        
        return result
        
    except Exception as e:
        print(f"Error en el análisis de requisitos: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Error interno al analizar requisitos: {e.__class__.__name__}")


# -------------------------------------------------------------
# 3. ENDPOINT MIGRADO: PRUEBA DE INTEGRACIÓN (SIN CAMBIOS)
# -------------------------------------------------------------
@router.get("/test", response_model=Dict[str, Any])
async def test_ai_fastapi():
    """Prueba de integración IA llamando al agente de Intake."""
    try:
        test_requirements = "Sistema de blog simple con usuarios y posts"
        # Asumo que intake_agent.run es awaitable
        test_result = await intake_agent.run("test-project", test_requirements) 
        
        return {
            "message": "✅ Forge SaaS AI - Integración activa",
            "test_result": test_result
        }
    except Exception as e:
        print(f"Error en la prueba de IA: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Fallo en la prueba de integración de AI: {e.__class__.__name__}")


# -------------------------------------------------------------
# 4. ENDPOINT MIGRADO: HEALTH CHECK (SIN CAMBIOS)
# -------------------------------------------------------------
@router.get("/health", response_model=Dict[str, Any])
def ai_health():
    """Health check de la integración IA"""
    return {
        "status": "healthy",
        "service": "forge-ai-integration",
        "features": ["deepseek-api", "requirements-analysis", "tech-stack-recommendation"]
    }
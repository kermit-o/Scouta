# cat > backend/app/agents/specification_agent.py

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from backend.app.core.app.agents.agent_base import AgentBase
import json # Necesario para manejar el JSON de DeepSeek

# Los esquemas BaseModel permanecen intactos
class RoomModel(BaseModel):
    name: str = Field(..., description="Name of the room")
    capacity: int = Field(..., description="Capacity of the room")

class APIEndpoint(BaseModel):
    method: str = Field(..., description="HTTP method")
    path: str = Field(..., description="API path")
    description: str = Field(..., description="Endpoint description")

class FullProjectSpecification(BaseModel):
    project_name: str = Field(..., description="Name of the project")
    description: str = Field(..., description="Project description")
    entities: List[Dict[str, Any]] = Field(..., description="List of entities")
    api_endpoints: List[APIEndpoint] = Field(..., description="List of API endpoints")
    database_schema: Dict[str, Any] = Field(..., description="Database schema")
    # Agregamos los campos que queremos para el output final de este agente


class SpecificationAgent(AgentBase):
    """Agent for creating detailed technical specifications"""
    
    def __init__(self):
        super().__init__("Specification Agent")
    
    def run(self, project_id: str, current_requirements: dict) -> dict:
        """Create detailed technical specifications from requirements analysis"""
        self.log_activity(f"Creating specifications for project {project_id}")
        
        # El input ahora viene del IntakeAgent, con la clave 'specification'
        # que puede ser un JSON (DeepSeek) o una string (Intake tradicional)
        analysis_input = current_requirements.get('specification')
        
        # Inicializar datos clave que podemos obtener del plan previo
        initial_plan = {}
        
        # 1. DETECCIÓN DEL PLAN ESTRUCTURADO (DEEPSEEK)
        if isinstance(analysis_input, dict):
            # Es un plan de DeepSeek/IntakeAgent. Extraemos lo que necesitamos.
            self.log_activity("Plan estructurado detectado. Iniciando enriquecimiento.")
            
            initial_plan = analysis_input
            
            # Formateamos el plan como string para el prompt (JSON legible)
            analysis_text = json.dumps(initial_plan, indent=2)
            
            prompt_goal = "ENRIQUECE y COMPLETA esta especificación inicial."
            
        elif analysis_input:
            # Es un análisis de texto sin formato (Intake tradicional).
            self.log_activity("Análisis de texto simple detectado. Generando especificación completa.")
            analysis_text = str(analysis_input)
            prompt_goal = "CREA una especificación técnica DETALLADA basada en este análisis."
        else:
            # Fallback
            analysis_text = current_requirements.get('raw_requirements', 'No analysis available')
            self.log_activity("No se encontró análisis. Usando requisitos brutos.")
            prompt_goal = "CREA una especificación técnica DETALLADA basada en estos requisitos brutos."


        # 2. CONSTRUCCIÓN DEL PROMPT DE ENRIQUECIMIENTO/CREACIÓN
        
        prompt = f"""
        TAREA: {prompt_goal}

        ANALISIS/PLAN DE ENTRADA:
        ---
        {analysis_text}
        ---

        INSTRUCCIONES:
        Transforma la información de ENTRADA en una especificación técnica completa y lista para ser construida.
        Debes completar y detallar las siguientes secciones, siendo específico en los detalles técnicos:
        1. Base de Datos: Esquema de Tablas (con campos y tipos).
        2. API: Estructura completa de Endpoints (método, path, y descripción breve).
        3. Arquitectura y Stack Tecnológico Propuesto (si no está ya en el plan de entrada, proponlo).
        4. Requisitos de Autenticación/Autorización detallados.
        5. Estructura de Archivos recomendada (ej. /src/controllers, /src/models).
        """
        
        try:
            # 3. Llamada al LLM para generar o enriquecer la especificación
            specifications_raw = self.generate_ai_response(prompt, "You are a senior solutions architect and technical spec writer.")
            
            # 4. Asumo que specifications_raw es el JSON de la especificación completa
            # Si el output no es JSON, se necesitaría un paso extra para estructurarlo. 
            # Si generate_ai_response usa structured output, el output puede ser un dict.
            # specifications_dict = json.loads(specifications_raw) # Descomentar si la salida es raw string JSON
            
            # 5. Devolver la especificación enriquecida y los metadatos
            return {
                "project_id": project_id, 
                "status": "completed",
                # Specifications debe contener el resultado del LLM.
                # Si el LLM devolvió un string/JSON, lo guardamos aquí.
                "specifications": specifications_raw, 
                
                # Metadatos para el Supervisor (mejor extraerlos del specification_raw si es JSON)
                # Por ahora, usamos los valores anteriores para no romper la estructura:
                "main_entities": initial_plan.get('entities', ["users", "products"]),
                "architecture": initial_plan.get('suggested_stack', {}).get('framework', 'fullstack'),
                "database_tables": [e['name'] for e in initial_plan.get('entities', []) if isinstance(e, dict)] or ["users"],
                "api_endpoints": specifications_raw.get('api_endpoints', []) # Asumo que el LLM genera este campo si el output es JSON
            }
        except Exception as e:
            self.log_activity(f"Error en Specification Agent: {e}")
            return {
                "project_id": project_id,
                "status": "failed", 
                "error": str(e)
            }
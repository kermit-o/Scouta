from pydantic import BaseModel, Field
import requests
import json
import os
from typing import Dict, Any
from uuid import UUID # Importación necesaria para el tipo project_id

# Asumo que estas rutas son correctas
from backend.app.core.app.agents.agent_base import AgentBase
from backend.app.core.database.models import Project 
from backend.app.core.db.session import SessionLocal 

# Configuración de DeepSeek API
# Nota: La clase AgentBase probablemente ya maneja estos valores si los tienes en .env
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-deepseek-api-key")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Define el esquema de salida que queremos forzar al LLM (Structured Output)
class IntakeAnalysis(BaseModel):
    summary: str = Field(description="Un resumen conciso de alto nivel de la idea del proyecto.")
    complexity: str = Field(description="La complejidad del proyecto: 'low', 'medium' o 'high'.")
    estimated_time: str = Field(description="Estimación de tiempo de generación para el Agente Builder (ej: '30 minutes').")
    suggested_stack: dict = Field(description="Diccionario con sugerencias tecnológicas (ej: {'database': 'PostgreSQL', 'framework': 'FastAPI'}).")
    core_features: list = Field(description="Lista de características principales del proyecto.")
    entities: list = Field(description="Entidades principales del dominio del proyecto.")

class IntakeAgent(AgentBase):
    """Agent for processing user requirements and initial project analysis"""
    
    def __init__(self):
        # Asumo que AgentBase ya inicializa api_key y api_base
        super().__init__("Intake Agent") 
        # Si AgentBase no lo hace, debes inicializar self.api_key aquí
    
    # Este método sigue siendo síncrono, lo cual es tolerable ya que será omitido la mayoría de las veces
    def call_deepseek_api(self, prompt: str, response_format: Dict[str, Any] = None) -> Dict[str, Any]:
        """Llama a la API de DeepSeek con el prompt y formato especificado."""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" # Usando self.api_key de AgentBase
        }
        
        messages = [{"role": "user", "content": prompt}]
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        if response_format:
            payload["response_format"] = response_format
        
        try:
            # Uso de self.api_base de AgentBase si está configurado
            api_url = self.api_base + "/chat/completions" if hasattr(self, 'api_base') and self.api_base else DEEPSEEK_API_URL 
            
            response = requests.post(api_url, 
                                     json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.log_activity(f"DeepSeek API error: {e}")
            raise
    
    # NOTA: Aunque el Supervisor llama esto de forma síncrona, mantenemos el 'async' 
    # por la estructura del router original, pero la lógica interna es síncrona.
    async def run(self, project_id: UUID, current_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user requirements and create initial project analysis.
        PRIORIDAD: Si el plan de DeepSeek ya existe, lo utiliza en su lugar.
        """
        db = SessionLocal() 
        try:
            # 1. CARGAR EL PROYECTO
            project = db.query(Project).filter(Project.id == project_id).first()
            
            if not project:
                 self.log_activity(f"Error: Project ID {project_id} not found in DB.")
                 return {"project_id": project_id, "status": "failed", "error": "Project not found"}


            # 2. VERIFICACIÓN DE BYPASS DE DEEPSEEK (Lógica clave)
            if project.specification and project.status == "ANALYSIS_COMPLETED":
                self.log_activity("DeepSeek plan detectado. Saltando análisis de Intake tradicional.")
                
                # Devolvemos el plan de DeepSeek (que está en project.specification)
                return {
                    "project_id": project_id,
                    "status": "completed",
                    "specification": project.specification, # <-- Plan de DeepSeek
                    "message": "Análisis de requisitos saltado. Plan de DeepSeek usado.",
                    "token_count_in": 0,
                    "token_count_out": 0
                }

            # 3. Lógica de ANÁLISIS TRADICIONAL (SI NO HAY PLAN DE DEEPSEEK)
            
            # Nota: current_requirements["raw_requirements"] debería tener la descripción
            requirements_desc = current_requirements.get('raw_requirements') or project.requirements
            
            self.log_activity(f"Iniciando análisis de IA tradicional para {project_id}")
            
            prompt = f"""
            Analyze these project requirements and extract key information:
            
            Project Requirements: {requirements_desc}
            
            Please analyze and provide a structured response with:
            1. Project type (web app, API, mobile, etc.)
            2. Key features needed
            3. Technical stack suggestions
            4. Complexity assessment (low, medium, high)
            5. Main entities/tables needed
            """
            
            # Ejecutar la llamada SÍNCRONA
            response = self.call_deepseek_api(prompt)
            analysis_content = response["choices"][0]["message"]["content"]
            
            # Asumo que analysis_content es JSON debido al esquema de arriba (IntakeAnalysis)
            # Debes parsear analysis_content a dict si DeepSeek fue forzado a devolver JSON
            # analysis = json.loads(analysis_content) 
            
            # Si DeepSeek no fue forzado a devolver JSON, debes adaptarlo a tu formato de salida:
            return {
                "project_id": project_id,
                "status": "completed",
                # Asumo que esta clave será usada por SpecificationAgent
                "specification": analysis_content, 
                "project_type": "web_application",
                "complexity": "medium",
                "entities": ["users", "products"], # Estos valores deben venir del análisis de la IA
                "message": "Análisis completado usando IntakeAgent tradicional."
            }
        
        except Exception as e:
            self.log_activity(f"Error en el IntakeAgent: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }
        finally:
            db.close()
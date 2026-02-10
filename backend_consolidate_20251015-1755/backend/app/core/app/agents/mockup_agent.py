import json
from typing import Dict, Any
from backend.app.core.app.agents.agent_base import AgentBase
from pydantic import BaseModel, Field

# --- Pydantic Schema para el Reporte de Mockup ---
class MockupReport(BaseModel):
    """Contiene el código HTML generado para el prototipo."""
    status: str = Field(..., description="Estado del proceso de generación del mockup: 'success' o 'failed'.")
    summary: str = Field(..., description="Resumen de alto nivel del mockup generado.")
    html_content: str = Field(..., description="El código HTML completo y único que representa el frontend del mockup.")

# --- CLASE PRINCIPAL DEL AGENTE ---

class MockupAgent(AgentBase):
    """
    Agente especializado en generar un prototipo (mockup) interactivo del frontend 
    del proyecto basado en las especificaciones.
    El resultado es un único archivo HTML con estilos Tailwind CSS y JS de esqueleto.
    """
    
    def __init__(self):
        super().__init__("Mockup Agent")

    def _generate_mockup_html(self, specifications: str, db_schema_str: str) -> MockupReport:
        """
        Utiliza el LLM para generar el código HTML del prototipo.
        """
        
        prompt = f"""
        TAREA: Eres un diseñador de interfaz de usuario y desarrollador frontend experto. 
        Tu trabajo es generar un prototipo de interfaz de usuario completamente funcional y estético 
        basado en las especificaciones proporcionadas.

        --- ESPECIFICACIÓN DEL PROYECTO ---
        {specifications}

        --- ESQUEMA DE BASE DE DATOS (Para referencia de campos) ---
        {db_schema_str}

        REQUISITOS DEL MOCKUP:
        1. **Archivo Único:** Genera un único archivo HTML. Todo el CSS (usando Tailwind) y JavaScript deben estar INCRUSTADOS.
        2. **Estética:** Utiliza Tailwind CSS (cargando la CDN en el <head>) para asegurar un diseño moderno, limpio, con esquinas redondeadas y excelente UX. Hazlo visualmente atractivo.
        3. **Responsividad:** El diseño debe ser totalmente responsive (móvil y escritorio).
        4. **Funcionalidad Esqueleto:** El JavaScript debe simular la navegación entre las vistas CRUD principales (ej: Lista de Productos, Formulario de Creación). No se requiere la lógica de backend real; solo simula las interacciones de la interfaz de usuario.
        5. **Output Estricto:** Devuelve el resultado siguiendo estrictamente el esquema JSON de Pydantic 'MockupReport'.
        """
        
        self.log_activity("Generando prototipo de interfaz de usuario interactiva...")

        # El LLM genera el informe JSON siguiendo el esquema MockupReport
        report_json = self.generate_structured_ai_response(
            prompt, 
            "You are a master frontend engineer. Your output must strictly follow the MockupReport Pydantic schema.",
            MockupReport
        )
        
        return report_json

    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la generación del prototipo y retorna el HTML.
        """
        self.log_activity(f"Creando Mockup del Frontend para el proyecto {project_id}")

        specifications = requirements.get('specifications', 'No specifications provided')
        db_schema = requirements.get('database_schema', {'database_schema': []})
        db_schema_str = json.dumps(db_schema, indent=2)

        if not specifications:
            self.log_activity("Error: Las especificaciones del proyecto no están disponibles.")
            return {
                "project_id": project_id,
                "status": "mockup_skipped",
                "summary": "Skipped because specifications were missing."
            }
        
        try:
            # 1. Generar el HTML del Mockup
            mockup_report = self._generate_mockup_html(specifications, db_schema_str)
            
            # 2. Devolver el resultado
            return {
                "project_id": project_id,
                "status": "mockup_generated",
                "summary": mockup_report.summary,
                "mockup_html": mockup_report.html_content,
            }
        
        except Exception as e:
            self.log_activity(f"Fallo en la ejecución del Mockup Agent: {e}")
            return {
                "project_id": project_id,
                "status": "mockup_agent_error",
                "error": str(e)
            }

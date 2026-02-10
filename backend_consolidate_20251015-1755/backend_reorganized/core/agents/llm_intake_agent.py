"""
LLM Intake Agent - Consulta REAL a DeepSeek para análisis de requisitos
"""
import json
from services.robust_deepseek_client import RobustDeepSeekClient

class LLMIntakeAgent:
    def __init__(self):
        self.client = RobustDeepSeekClient()
    
    def run(self, project_id: str, user_requirements: dict) -> dict:
        """Consulta REAL al LLM para análisis de requisitos"""
        print("🧠 LLM Intake Agent - Consultando DeepSeek...")
        
        try:
            # Construir prompt para el LLM
            prompt = f"""
            Como arquitecto de software IA, analiza ESTOS requisitos y genera especificaciones técnicas detalladas:

            REQUISITOS DEL USUARIO: {user_requirements}

            GENERA un análisis técnico estructurado que incluya:
            1. Componentes específicos necesarios
            2. Stack tecnológico recomendado  
            3. Arquitectura del sistema
            4. Características técnicas detalladas
            5. Dependencias y integraciones

            Responde en formato JSON válido.
            """
            
            # Consulta REAL al LLM
            analysis = self.client.generate_code(prompt, "Análisis de Requisitos Técnicos")
            
            # Parsear respuesta del LLM
            structured_analysis = self._parse_llm_response(analysis, user_requirements)
            
            print(f"✅ Análisis LLM completado - {len(structured_analysis.get('components', []))} componentes")
            return structured_analysis
            
        except Exception as e:
            print(f"❌ Error en análisis LLM: {e}")
            return self._fallback_analysis(user_requirements)
    
    def _parse_llm_response(self, llm_response: str, original_requirements: dict) -> dict:
        """Parsea la respuesta del LLM a estructura consistente"""
        try:
            # Intentar extraer JSON de la respuesta
            if '{' in llm_response and '}' in llm_response:
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return {
                    "project_name": original_requirements.get("name", "Proyecto Generado"),
                    "project_type": parsed.get("project_type", "web_app"),
                    "components": parsed.get("components", []),
                    "tech_stack": parsed.get("tech_stack", []),
                    "architecture": parsed.get("architecture", {}),
                    "features": parsed.get("features", []),
                    "llm_analysis": llm_response,
                    "status": "analyzed_by_llm"
                }
        except:
            pass
        
        # Fallback si no se puede parsear
        return self._fallback_analysis(original_requirements)
    
    def _fallback_analysis(self, requirements: dict) -> dict:
        """Análisis de fallback cuando el LLM falla"""
        return {
            "project_name": requirements.get("name", "Proyecto"),
            "project_type": requirements.get("type", "web_app"),
            "components": [
                {"name": "Frontend Principal", "type": "frontend", "description": "Interfaz de usuario principal"},
                {"name": "API Backend", "type": "backend", "description": "Servicios y lógica de negocio"},
                {"name": "Base de Datos", "type": "database", "description": "Almacenamiento persistente"}
            ],
            "tech_stack": ["React", "Node.js", "MongoDB"],
            "features": requirements.get("features", ["feature1"]),
            "status": "fallback_analysis"
        }

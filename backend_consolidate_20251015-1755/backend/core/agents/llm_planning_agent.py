"""
LLM Planning Agent - Consulta REAL a DeepSeek para planificación
"""
import json
from services.robust_deepseek_client import RobustDeepSeekClient

class LLMPlanningAgent:
    def __init__(self):
        self.client = RobustDeepSeekClient()
        print("[LLMPlanningAgent] Initialized - CONSULTA REAL A DEEPSEEK")
    
    def run(self, project_spec: dict) -> dict:
        """Consulta REAL al LLM para crear plan de desarrollo"""
        print("📊 LLM Planning Agent - Consultando DeepSeek para planificación...")
        
        try:
            # Construir prompt para planificación
            prompt = f"""
            Como planificador de desarrollo IA, crea un plan de desarrollo DETALLADO basado en:

            ESPECIFICACIONES: {json.dumps(project_spec, indent=2)}

            GENERA un plan de desarrollo que incluya:
            1. Fases de desarrollo específicas
            2. Arquitectura de carpetas y archivos
            3. Dependencias a instalar
            4. Secuencia de implementación
            5. Entregables por fase

            Responde en formato JSON válido.
            """
            
            # Consulta REAL al LLM
            plan_response = self.client.generate_code(prompt, "Planificación de Desarrollo")
            
            # Parsear y estructurar el plan
            development_plan = self._parse_plan_response(plan_response, project_spec)
            
            print(f"✅ Planificación LLM completada - {len(development_plan.get('phases', []))} fases")
            return development_plan
            
        except Exception as e:
            print(f"❌ Error en planificación LLM: {e}")
            return self._fallback_plan(project_spec)
    
    def _parse_plan_response(self, llm_response: str, project_spec: dict) -> dict:
        """Parsea la respuesta de planificación del LLM"""
        try:
            if '{' in llm_response and '}' in llm_response:
                json_start = llm_response.find('{')
                json_end = llm_response.rfind('}') + 1
                json_str = llm_response[json_start:json_end]
                parsed = json.loads(json_str)
                
                return {
                    "project_name": project_spec.get("project_name", "Proyecto"),
                    "phases": parsed.get("phases", []),
                    "architecture": parsed.get("architecture", {}),
                    "dependencies": parsed.get("dependencies", []),
                    "file_structure": parsed.get("file_structure", []),
                    "implementation_sequence": parsed.get("implementation_sequence", []),
                    "llm_plan": llm_response,
                    "status": "planned_by_llm"
                }
        except:
            pass
        
        return self._fallback_plan(project_spec)
    
    def _fallback_plan(self, project_spec: dict) -> dict:
        """Plan de fallback"""
        return {
            "project_name": project_spec.get("project_name", "Proyecto"),
            "phases": [
                {
                    "name": "Fase 1: Setup Inicial",
                    "description": "Configuración inicial del proyecto",
                    "tasks": ["Crear estructura de carpetas", "Configurar package.json"]
                }
            ],
            "file_structure": [
                "src/",
                "package.json",
                "README.md"
            ],
            "status": "fallback_plan"
        }

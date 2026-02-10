"""
Real DeepSeek API Client - Conecta REALMENTE a la API de DeepSeek
"""
import os
import httpx
import json
from typing import Dict, List, Optional, Any
import asyncio

class RealDeepSeekClient:
    """Cliente REAL para DeepSeek AI API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY no encontrada en variables de entorno")
            
        self.base_url = "https://api.deepseek.com/v1"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        self.client = httpx.AsyncClient(timeout=60.0, headers=self.headers)

    async def generate_code(self, prompt: str, context: str = "") -> str:
        """Genera código REAL consultando a la API de DeepSeek"""
        try:
            print(f"🤖 CONSULTANDO DEEPSEEK API...")
            
            messages = [
                {
                    "role": "system", 
                    "content": "Eres un experto desarrollador full-stack. Genera código limpio, funcional y bien documentado."
                },
                {
                    "role": "user",
                    "content": f"{context}\n\n{prompt}"
                }
            ]
            
            payload = {
                "model": "deepseek-coder",
                "messages": messages,
                "max_tokens": 4000,
                "temperature": 0.7,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                code = result['choices'][0]['message']['content']
                print(f"✅ DeepSeek respondió ({len(code)} caracteres)")
                return code
            else:
                error_msg = f"API Error {response.status_code}: {response.text}"
                print(f"❌ {error_msg}")
                return f"// Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Error en conexión: {str(e)}"
            print(f"❌ {error_msg}")
            return f"// Error: {error_msg}"

    async def analyze_requirements(self, user_input: str, project_context: Dict = None) -> Dict[str, Any]:
        """Analiza requisitos REALMENTE con DeepSeek"""
        prompt = f"""
        Como arquitecto de software IA, analiza ESTE requisito y genera especificaciones técnicas detalladas:

        REQUISITO: "{user_input}"
        
        CONTEXTO: {project_context or 'Nuevo proyecto'}
        
        GENERA un análisis estructurado con:
        1. Componentes técnicos específicos necesarios
        2. Stack tecnológico recomendado
        3. Arquitectura sugerida
        4. Preguntas de clarificación
        5. Especificaciones técnicas detalladas
        
        Responde en formato JSON estructurado.
        """
        
        analysis = await self.generate_code(prompt, "Analista de Requisitos Técnicos")
        return self._parse_analysis_response(analysis)

    async def design_component(self, component_spec: Dict, project_context: Dict) -> Dict[str, Any]:
        """Diseña un componente específico consultando a DeepSeek"""
        prompt = f"""
        Diseña este componente técnicamente:

        COMPONENTE: {component_spec.get('name', 'Componente')}
        DESCRIPCIÓN: {component_spec.get('description', 'Sin descripción')}
        CONTEXTO: {project_context}
        
        Genera un diseño técnico detallado que incluya:
        - Estructura del componente
        - Props/inputs necesarios
        - Estado interno
        - Funcionalidades específicas
        - Integraciones necesarias
        """
        
        design = await self.generate_code(prompt, "Diseñador de Componentes")
        return {"design": design, "component": component_spec.get('name')}

    async def generate_component_code(self, component_design: Dict, tech_stack: List[str]) -> Dict[str, str]:
        """Genera código REAL para un componente consultando a DeepSeek"""
        prompt = f"""
        Genera código IMPLEMENTADO COMPLETO basado en este diseño:

        DISEÑO: {component_design.get('design', '')}
        TECNOLOGÍAS: {tech_stack}
        
        REQUISITOS:
        - Código 100% funcional, NO placeholder
        - Incluir todos los imports necesarios
        - Manejo de estado y efectos
        - Estilos profesionales
        - Manejo de errores
        - Documentación clara
        
        Solo genera el código listo para usar.
        """
        
        code = await self.generate_code(prompt, "Generador de Código")
        return {
            "main_code": code,
            "file_path": self._determine_file_path(component_design.get('component', 'unknown')),
            "tech_stack": tech_stack
        }

    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """Parsea la respuesta de análisis del LLM"""
        try:
            # Intentar parsear como JSON
            if '{' in analysis_text and '}' in analysis_text:
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                json_str = analysis_text[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback a estructura básica
        return {
            "components": [
                {"name": "Componente Principal", "description": analysis_text[:200] + "..."},
                {"name": "API Backend", "description": "Endpoints y lógica de negocio"},
                {"name": "Base de Datos", "description": "Esquema y modelos de datos"}
            ],
            "tech_stack": ["React", "Node.js", "MongoDB"],
            "clarification_questions": [
                "¿Qué funcionalidades específicas necesitas?",
                "¿Prefieres algún stack tecnológico en particular?"
            ],
            "analysis": analysis_text
        }

    def _determine_file_path(self, component_name: str) -> str:
        """Determina la ruta del archivo basado en el nombre del componente"""
        name_clean = component_name.lower().replace(' ', '_')
        if 'frontend' in component_name.lower() or 'react' in component_name.lower():
            return f"src/components/{name_clean}.jsx"
        elif 'backend' in component_name.lower() or 'api' in component_name.lower():
            return f"server/api/{name_clean}.js"
        elif 'page' in component_name.lower():
            return f"src/pages/{name_clean}.jsx"
        else:
            return f"src/{name_clean}.jsx"

    async def close(self):
        """Cierra el cliente"""
        await self.client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

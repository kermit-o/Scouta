import httpx
import json
from typing import Dict, Any, List
from config.ai_config import ai_config

class DeepSeekClient:
    def __init__(self):
        self.api_key = ai_config.deepseek_api_key
        self.base_url = ai_config.deepseek_base_url
        self.model = ai_config.model
        
    async def analyze_idea(self, user_idea: str) -> Dict[str, Any]:
        """
        Analiza una idea de usuario usando DeepSeek y devuelve
        recomendaciones técnicas estructuradas
        """
        prompt = self._create_analysis_prompt(user_idea)
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=ai_config.get_headers(),
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": self._get_system_prompt()
                            },
                            {
                                "role": "user", 
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 2000,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    analysis_content = result["choices"][0]["message"]["content"]
                    return self._parse_analysis_response(analysis_content)
                else:
                    print(f"❌ Error DeepSeek API: {response.status_code} - {response.text}")
                    return self._get_fallback_analysis(user_idea)
                    
        except Exception as e:
            print(f"❌ Error con DeepSeek: {e}")
            return self._get_fallback_analysis(user_idea)
    
    def _get_system_prompt(self) -> str:
        """Prompt del sistema para el análisis técnico"""
        return """Eres un arquitecto de software senior con 15+ años de experiencia.
        Tu tarea es analizar ideas de proyectos y generar recomendaciones técnicas específicas.

        Responde SIEMPRE en formato JSON válido con esta estructura:
        {
            "project_type": "tipo_de_proyecto",
            "architecture": "descripción de arquitectura",
            "recommended_stack": ["tech1", "tech2", ...],
            "features": ["feature1", "feature2", ...],
            "complexity": "Baja|Media|Alta",
            "estimated_weeks": número,
            "technical_considerations": ["consideración1", ...],
            "deployment_recommendation": "plataforma_recomendada"
        }

        Tipos de proyecto disponibles:
        - react_web_app: Aplicación web con React
        - nextjs_app: Aplicación con Next.js (SSR/SSG)
        - fastapi_service: API REST con FastAPI
        - react_native_mobile: App móvil con React Native
        - chrome_extension: Extensión de Chrome
        - ai_agent: Agente de IA
        - blockchain_dapp: Aplicación descentralizada

        Sé específico y práctico en tus recomendaciones."""
    
    def _create_analysis_prompt(self, user_idea: str) -> str:
        """Crear prompt para análisis de idea"""
        return f"""
        Analiza esta idea de proyecto y proporciona recomendaciones técnicas específicas:

        IDEA DEL USUARIO: "{user_idea}"

        Considera:
        1. ¿Qué tipo de proyecto sería más adecuado?
        2. ¿Qué stack tecnológico recomiendas?
        3. ¿Qué características debería incluir?
        4. ¿Cuál es la complejidad estimada?
        5. ¿Cuánto tiempo de desarrollo estimas?
        6. ¿Consideraciones técnicas importantes?
        7. ¿Plataforma de deployment recomendada?

        Responde con el JSON especificado.
        """
    
    def _parse_analysis_response(self, content: str) -> Dict[str, Any]:
        """Parsear la respuesta de DeepSeek"""
        try:
            # Limpiar y extraer JSON
            clean_content = content.strip()
            if "```json" in clean_content:
                json_str = clean_content.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_content:
                json_str = clean_content.split("```")[1].split("```")[0].strip()
            else:
                json_str = clean_content
            
            analysis = json.loads(json_str)
            
            # Validar estructura mínima
            required_fields = ["project_type", "architecture", "recommended_stack", "features"]
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Campo requerido faltante: {field}")
            
            print("✅ Análisis DeepSeek parseado correctamente")
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"⚠️  Error parseando respuesta DeepSeek: {e}")
            print(f"📄 Contenido: {content[:200]}...")
            return self._get_fallback_analysis("idea de usuario")
    
    def _get_fallback_analysis(self, user_idea: str) -> Dict[str, Any]:
        """Análisis de fallback cuando DeepSeek no está disponible"""
        print("⚠️  Usando análisis de fallback")
        
        # Lógica básica de análisis (similar a la anterior pero mejorada)
        idea_lower = user_idea.lower()
        
        # Determinar tipo de proyecto
        if any(word in idea_lower for word in ['móvil', 'mobile', 'app', 'ios', 'android']):
            project_type = "react_native_mobile"
            architecture = "Aplicación móvil nativa con React Native"
        elif any(word in idea_lower for word in ['api', 'backend', 'servicio', 'rest', 'graphql']):
            project_type = "fastapi_service" 
            architecture = "API REST con autenticación JWT y documentación automática"
        elif any(word in idea_lower for word in ['extensión', 'extension', 'chrome', 'navegador']):
            project_type = "chrome_extension"
            architecture = "Extensión Chrome con background scripts y content scripts"
        elif any(word in idea_lower for word in ['ia', 'ai', 'inteligencia artificial', 'machine learning']):
            project_type = "ai_agent"
            architecture = "Arquitectura de agentes con LLM y herramientas"
        elif any(word in idea_lower for word in ['blockchain', 'web3', 'dapp', 'descentralizado']):
            project_type = "blockchain_dapp"
            architecture = "Smart contracts + Frontend Web3 con MetaMask"
        else:
            project_type = "nextjs_app"
            architecture = "SPA moderna con App Router y optimización SEO"
        
        # Determinar características
        features = []
        if any(word in idea_lower for word in ['usuario', 'login', 'registro', 'auth', 'autenticación']):
            features.append("auth")
        if any(word in idea_lower for word in ['pago', 'stripe', 'paypal', 'tarjeta', 'subscription']):
            features.append("payment")
        if any(word in idea_lower for word in ['admin', 'dashboard', 'panel', 'gestión']):
            features.append("admin_panel")
        if any(word in idea_lower for word in ['tiempo real', 'chat', 'notificaciones', 'websocket']):
            features.append("real_time")
        if any(word in idea_lower for word in ['ia', 'ai', 'inteligencia artificial']):
            features.append("ai_enhanced")
        
        # Stack tecnológico recomendado
        if project_type == "react_native_mobile":
            stack = ["react", "typescript", "nodejs", "firebase"]
        elif project_type == "fastapi_service":
            stack = ["python", "postgresql", "docker", "jwt"]
        elif project_type == "nextjs_app":
            stack = ["react", "typescript", "tailwind", "nodejs"]
        else:
            stack = ["react", "typescript", "tailwind"]
        
        # Calcular complejidad y tiempo
        complexity_score = len(features)
        if complexity_score <= 2:
            complexity = "Baja"
            estimated_weeks = 1
        elif complexity_score <= 4:
            complexity = "Media" 
            estimated_weeks = 2
        else:
            complexity = "Alta"
            estimated_weeks = 3
        
        return {
            "project_type": project_type,
            "architecture": architecture,
            "recommended_stack": stack,
            "features": features,
            "complexity": complexity,
            "estimated_weeks": estimated_weeks,
            "technical_considerations": [
                "Considerar escalabilidad desde el inicio",
                "Implementar logging y monitoreo",
                "Planificar estrategia de testing"
            ],
            "deployment_recommendation": "vercel" if project_type in ["react_web_app", "nextjs_app"] else "docker"
        }

# Cliente global
deepseek_client = DeepSeekClient()

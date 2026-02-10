import json
import logging
from typing import Dict, Any, List
from core.agents.agent_base import AgentBase

logger = logging.getLogger(__name__)

class UniversalAnalystAgent(AgentBase):
    """
    Universal Analyst Agent - Detecta automáticamente el tipo de proyecto
    sin asumir que es una aplicación web
    """
    
    def __init__(self):
        super().__init__("Universal Analyst Agent")
        self.supported_project_types = [
            "web_app", "mobile_app", "desktop_app", "game", 
            "browser_extension", "ai_agent", "blockchain_dapp", 
            "cli_tool", "api_service", "iot_system", "library_package"
        ]
        # Inicializar llm para compatibilidad
        self.llm = self
    
    async def get_completion(self, prompt: str) -> str:
        """Implementación simple para pruebas - simula respuesta del LLM"""
        # Simular análisis basado en palabras clave en lugar de llamar al LLM real
        return self._simulate_llm_response(prompt)
    
    def _simulate_llm_response(self, prompt: str) -> str:
        """Simular respuesta del LLM basado en el prompt"""
        # Extraer la idea del usuario del prompt
        import re
        idea_match = re.search(r'IDEA DEL USUARIO: "([^"]+)"', prompt)
        user_idea = idea_match.group(1) if idea_match else "idea desconocida"
        
        # Determinar tipo de proyecto basado en palabras clave
        project_type = self._detect_project_type_fallback(user_idea)
        business_domain = self._detect_business_domain(user_idea)
        platforms = self._detect_platforms(user_idea)
        
        # Crear respuesta JSON válida
        response_data = {
            "project_type": project_type,
            "business_domain": business_domain,
            "target_platforms": platforms,
            "main_entities": ["User", "Data", "Settings"],
            "key_features": ["basic_functionality", "user_interface"],
            "user_roles": ["user", "admin"],
            "complexity_level": 6,
            "technical_considerations": ["basic_implementation"],
            "architecture_recommendations": {
                "primary_technology": self._get_primary_tech(project_type),
                "alternative_technologies": ["alternative_tech"],
                "database_type": "document",
                "ui_framework": self._get_ui_framework(project_type),
                "deployment_requirements": ["basic_deployment"]
            },
            "detection_confidence": 85
        }
        
        # Devolver JSON válido
        return json.dumps(response_data, ensure_ascii=False)
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementación del método abstracto para compatibilidad con AgentBase
        """
        logger.info(f"Universal Analyst Agent ejecutando para proyecto {project_id}")
        
        # Obtener requisitos del usuario
        user_idea = requirements.get('raw_requirements', '') or requirements.get('user_idea', '')
        
        if not user_idea:
            return {
                "project_id": project_id,
                "status": "failed",
                "error": "No se proporcionaron requisitos del usuario"
            }
        
        # Ejecutar análisis asíncrono de forma síncrona para compatibilidad
        try:
            import asyncio
            # Crear nuevo event loop si es necesario
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            analysis_result = loop.run_until_complete(self.analyze_idea(user_idea))
            
            return {
                "project_id": project_id,
                "status": "completed",
                "analysis": analysis_result,
                "project_type": analysis_result.get('project_type'),
                "complexity_score": analysis_result.get('complexity_level'),
                "message": "Análisis universal completado exitosamente"
            }
            
        except Exception as e:
            logger.error(f"Error en análisis universal: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }
    
    async def analyze_idea(self, user_idea: str) -> Dict[str, Any]:
        """
        Analiza CUALQUIER tipo de proyecto y detecta automáticamente su categoría
        """
        logger.info(f"🔍 Universal Analyst analyzing idea: {user_idea[:100]}...")
        
        try:
            # Usar el método simulado en lugar del LLM real
            response = await self.get_completion(user_idea)
            analysis = self._parse_llm_response(response)
            
            # Validar y enriquecer el análisis
            enriched_analysis = self._validate_and_enrich_analysis(analysis, user_idea)
            
            logger.info(f"✅ Analysis completed. Project type: {enriched_analysis.get('project_type')}")
            return enriched_analysis
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            return self._get_fallback_analysis(user_idea, str(e))
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parsea la respuesta del LLM y extrae el JSON"""
        try:
            # Intentar parsear directamente como JSON
            return json.loads(response.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            logger.error(f"Response was: {response}")
            # Fallback a análisis básico
            return self._get_fallback_analysis("", f"JSON parsing failed: {e}")
    
    def _validate_and_enrich_analysis(self, analysis: Dict, user_idea: str) -> Dict:
        """Valida y enriquece el análisis con información adicional"""
        
        # Validar campos requeridos
        required_fields = ["project_type", "business_domain", "complexity_level", "key_features"]
        for field in required_fields:
            if field not in analysis:
                analysis[field] = self._get_fallback_value(field, user_idea)
        
        # Validar project_type
        if analysis["project_type"] not in self.supported_project_types:
            analysis["project_type"] = self._detect_project_type_fallback(user_idea)
        
        # Enriquecer con información derivada
        analysis["estimated_development_time"] = self._estimate_dev_time(analysis["complexity_level"])
        analysis["team_size_recommendation"] = self._recommend_team_size(analysis["complexity_level"])
        analysis["risk_factors"] = self._identify_risks(analysis)
        analysis["success_metrics"] = self._suggest_success_metrics(analysis["business_domain"])
        
        # Asegurar arrays
        array_fields = ["main_entities", "key_features", "user_roles", "technical_considerations"]
        for field in array_fields:
            if field not in analysis or not isinstance(analysis[field], list):
                analysis[field] = []
        
        return analysis
    
    def _detect_project_type_fallback(self, user_idea: str) -> str:
        """Detección de fallback basada en palabras clave"""
        idea_lower = user_idea.lower()
        
        detection_rules = [
            ("mobile_app", ["móvil", "ios", "android", "teléfono", "celular"]),
            ("game", ["juego", "videojuego", "game", "gaming", "jugador"]),
            ("desktop_app", ["escritorio", "desktop", "windows", "mac", "linux"]),
            ("browser_extension", ["extensión", "navegador", "chrome", "firefox", "browser"]),
            ("ai_agent", ["ia", "inteligencia artificial", "machine learning", "ml", "agente"]),
            ("blockchain_dapp", ["blockchain", "web3", "dapp", "smart contract", "cripto"]),
            ("cli_tool", ["comando", "terminal", "cli", "línea de comandos"]),
            ("api_service", ["api", "servicio", "backend", "microservicio"]),
            ("iot_system", ["iot", "internet de las cosas", "sensor", "dispositivo"]),
            ("library_package", ["librería", "paquete", "sdk", "framework"]),
        ]
        
        for project_type, keywords in detection_rules:
            if any(keyword in idea_lower for keyword in keywords):
                return project_type
        
        return "web_app"  # Por defecto
    
    def _detect_business_domain(self, user_idea: str) -> str:
        """Detectar dominio de negocio"""
        idea_lower = user_idea.lower()
        
        if any(word in idea_lower for word in ["juego", "game"]):
            return "gaming"
        elif any(word in idea_lower for word in ["tarea", "productividad", "gestiona"]):
            return "productivity"
        elif any(word in idea_lower for word in ["anuncio", "bloquear"]):
            return "utility"
        elif any(word in idea_lower for word in ["gasto", "finanza", "dinero"]):
            return "finance"
        elif any(word in idea_lower for word in ["extensión", "navegador"]):
            return "browser_tools"
        else:
            return "software_application"
    
    def _detect_platforms(self, user_idea: str) -> List[str]:
        """Detectar plataformas objetivo"""
        idea_lower = user_idea.lower()
        platforms = []
        
        if "ios" in idea_lower or "android" in idea_lower:
            platforms.extend(["ios", "android"])
        elif "chrome" in idea_lower or "firefox" in idea_lower or "navegador" in idea_lower:
            platforms.append("browser")
        elif "windows" in idea_lower or "mac" in idea_lower or "linux" in idea_lower:
            platforms.extend(["windows", "mac", "linux"])
        else:
            platforms.append("web")
            
        return platforms
    
    def _get_primary_tech(self, project_type: str) -> str:
        """Obtener tecnología principal"""
        tech_map = {
            "mobile_app": "react_native",
            "game": "godot_engine", 
            "browser_extension": "javascript",
            "cli_tool": "python",
            "desktop_app": "electron",
            "blockchain_dapp": "solidity",
            "ai_agent": "python",
            "web_app": "react"
        }
        return tech_map.get(project_type, "react")
    
    def _get_ui_framework(self, project_type: str) -> str:
        """Obtener framework UI"""
        ui_map = {
            "mobile_app": "native_mobile",
            "game": "game_engine", 
            "browser_extension": "browser_popup",
            "cli_tool": "command_line",
            "desktop_app": "desktop_ui",
            "web_app": "web_based"
        }
        return ui_map.get(project_type, "web_based")
    
    def _estimate_dev_time(self, complexity: int) -> str:
        """Estimar tiempo de desarrollo basado en complejidad"""
        time_estimates = {
            1: "1 semana",
            2: "1-2 semanas", 
            3: "2-3 semanas",
            4: "3-4 semanas",
            5: "1-2 meses",
            6: "2-3 meses",
            7: "3-4 meses", 
            8: "4-6 meses",
            9: "6-9 meses",
            10: "9+ meses"
        }
        return time_estimates.get(complexity, "1-2 meses")
    
    def _recommend_team_size(self, complexity: int) -> Dict[str, Any]:
        """Recomendar tamaño de equipo basado en complejidad"""
        if complexity <= 3:
            return {"developers": 1, "designers": 0, "qa": 0}
        elif complexity <= 6:
            return {"developers": 1, "designers": 1, "qa": 0.5}
        elif complexity <= 8:
            return {"developers": 2, "designers": 1, "qa": 1}
        else:
            return {"developers": 3, "designers": 1, "qa": 1, "devops": 1}
    
    def _identify_risks(self, analysis: Dict) -> List[str]:
        """Identificar riesgos basados en el análisis"""
        risks = []
        
        # Riesgos por complejidad
        if analysis["complexity_level"] > 7:
            risks.append("alta_complejidad_tecnica")
        
        # Riesgos por tipo de proyecto
        project_type = analysis["project_type"]
        if project_type == "game":
            risks.extend(["desarrollo_graficos", "optimizacion_rendimiento"])
        elif project_type == "mobile_app":
            risks.extend(["store_approval", "fragmentation_dispositivos"])
        elif project_type == "blockchain_dapp":
            risks.extend(["seguridad_smart_contracts", "gas_costs"])
        elif project_type == "ai_agent":
            risks.extend(["calidad_datos", "entrenamiento_modelos"])
        
        # Riesgos por plataformas múltiples
        if len(analysis.get("target_platforms", [])) > 2:
            risks.append("desarrollo_multiples_plataformas")
            
        return risks
    
    def _suggest_success_metrics(self, business_domain: str) -> List[str]:
        """Sugerir métricas de éxito basadas en el dominio"""
        metrics_map = {
            "ecommerce": ["conversion_rate", "average_order_value", "customer_acquisition_cost"],
            "social": ["daily_active_users", "engagement_rate", "retention_rate"],
            "productivity": ["tasks_completed", "time_saved", "user_adoption"],
            "gaming": ["daily_players", "session_length", "retention_7d"],
            "finance": ["transactions_processed", "security_incidents", "uptime"],
            "education": ["completion_rate", "learning_outcomes", "user_satisfaction"],
            "utility": ["user_satisfaction", "performance_improvement", "adoption_rate"]
        }
        return metrics_map.get(business_domain, ["user_adoption", "performance", "reliability"])
    
    def _get_fallback_value(self, field: str, user_idea: str) -> Any:
        """Valores de fallback para campos requeridos"""
        fallbacks = {
            "project_type": self._detect_project_type_fallback(user_idea),
            "business_domain": "software_application", 
            "complexity_level": 5,
            "key_features": ["basic_crud", "user_interface"]
        }
        return fallbacks.get(field, "")
    
    def _get_fallback_analysis(self, user_idea: str, error: str) -> Dict[str, Any]:
        """Análisis de fallback completo cuando el LLM falla"""
        project_type = self._detect_project_type_fallback(user_idea)
        
        return {
            "project_type": project_type,
            "business_domain": "software_application",
            "target_platforms": ["web"],
            "main_entities": ["User", "Data"],
            "key_features": ["basic_functionality", "user_interface"],
            "user_roles": ["user"],
            "complexity_level": 5,
            "technical_considerations": ["basic_implementation"],
            "architecture_recommendations": {
                "primary_technology": "react",
                "alternative_technologies": ["vue", "angular"],
                "database_type": "document",
                "ui_framework": "web_based",
                "deployment_requirements": ["web_hosting"]
            },
            "detection_confidence": 50,
            "estimated_development_time": "1-2 meses",
            "team_size_recommendation": {"developers": 1, "designers": 0, "qa": 0},
            "risk_factors": ["basic_development_risks"],
            "success_metrics": ["user_adoption", "basic_functionality"],
            "error": error,
            "fallback_used": True
        }

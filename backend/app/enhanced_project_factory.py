import os
import json
from typing import Dict, Any, List
from core.project_factory import ProjectRequirements, ProjectType
from generators.simple_engine import SimpleTemplateEngine
from agents.orchestrator.ai_orchestrator import AIOrchestrator
import uuid

class EnhancedProjectFactory:
    def __init__(self, openai_api_key: str = None):
        self.template_engine = SimpleTemplateEngine()
        self.ai_orchestrator = AIOrchestrator(api_key=openai_api_key) if openai_api_key else None
        self.project_plans = {}
        print("🚀 EnhancedProjectFactory inicializado")
    
    def create_project(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Crea un proyecto completo integrando IA + generadores"""
        
        print(f"🚀 Iniciando creación de proyecto: {requirements.name}")
        print(f"📋 Tipo: {requirements.project_type.value}")
        print(f"🎯 Características: {requirements.features}")
        
        try:
            # 1. PLANIFICACIÓN CON IA (si está disponible)
            project_plan = self._generate_ai_plan(requirements)
            self.project_plans[requirements.name] = project_plan
            
            # 2. GENERACIÓN BASADA EN TIPO
            print(f"🔧 Buscando generador para: {requirements.project_type.value}")
            generation_result = self._generate_by_type(requirements, project_plan)
            
            # 3. ENRIQUECER RESULTADO
            final_result = self._enrich_result(generation_result, requirements, project_plan)
            
            print(f"🎉 PROYECTO CREADO EXITOSAMENTE: {requirements.name}")
            return final_result
            
        except Exception as e:
            print(f"❌ Error creando proyecto: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "project_name": requirements.name,
                "project_id": str(uuid.uuid4())[:8]
            }
    
    def _generate_ai_plan(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Genera un plan detallado usando IA o fallback"""
        
        # Si no hay API key de OpenAI, usar plan por defecto
        if not self.ai_orchestrator or not hasattr(self.ai_orchestrator, 'client'):
            print("⚠️  IA no disponible, usando plan optimizado por defecto")
            return self._create_enhanced_default_plan(requirements)
        
        try:
            prompt = self._create_planning_prompt(requirements)
            
            response = self.ai_orchestrator.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un arquitecto de software experto que genera planes de proyecto en JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            plan_content = response.choices[0].message.content
            print("📋 Plan de IA generado exitosamente")
            return self._parse_ai_plan(plan_content, requirements)
            
        except Exception as e:
            print(f"⚠️  Error con IA, usando plan por defecto: {e}")
            return self._create_enhanced_default_plan(requirements)
    
    def _create_planning_prompt(self, requirements: ProjectRequirements) -> str:
        """Crea el prompt para la planificación con IA"""
        
        return f"""
        Como arquitecto de software, genera un plan JSON para este proyecto:

        NOMBRE: {requirements.name}
        DESCRIPCIÓN: {requirements.description}
        TIPO: {requirements.project_type.value}
        CARACTERÍSTICAS: {requirements.features}
        TECNOLOGÍAS: {requirements.technologies}
        AUTH: {requirements.auth_required}
        PAGOS: {requirements.payment_integration}

        Responde SOLO con JSON en este formato:
        {{
            "architecture": "tipo de arquitectura",
            "tech_stack": ["tecnologia1", "tecnologia2"],
            "file_structure": ["ruta1/", "ruta2/archivo.ext"],
            "dependencies": {{
                "react": "^18.0.0",
                "vite": "^4.0.0"
            }},
            "features": ["feature1", "feature2"],
            "deployment": "plataforma"
        }}
        """
    
    def _parse_ai_plan(self, plan_content: str, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Parsea la respuesta de IA a un plan estructurado"""
        try:
            # Limpiar y extraer JSON
            clean_content = plan_content.strip()
            if "```json" in clean_content:
                json_str = clean_content.split("```json")[1].split("```")[0].strip()
            elif "```" in clean_content:
                json_str = clean_content.split("```")[1].split("```")[0].strip()
            else:
                json_str = clean_content
            
            # Remover posibles markdown o texto extraño
            json_str = json_str.replace('```', '').strip()
            
            plan_data = json.loads(json_str)
            print("✅ Plan de IA parseado correctamente")
            return plan_data
            
        except json.JSONDecodeError as e:
            print(f"⚠️  Error parseando JSON de IA: {e}")
            print(f"📄 Contenido recibido: {plan_content[:200]}...")
            return self._create_enhanced_default_plan(requirements)
        except Exception as e:
            print(f"⚠️  Error inesperado parseando plan: {e}")
            return self._create_enhanced_default_plan(requirements)
    
    def _create_enhanced_default_plan(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Crea un plan por defecto mejorado"""
        
        base_tech_stack = ["react", "vite", "javascript"]
        if "typescript" in requirements.technologies:
            base_tech_stack.append("typescript")
        if "tailwind" in requirements.technologies:
            base_tech_stack.append("tailwindcss")
        
        plan = {
            "architecture": "Modern SPA (Single Page Application)",
            "tech_stack": base_tech_stack,
            "file_structure": [
                "src/components/",
                "src/pages/",
                "src/styles/",
                "src/hooks/",
                "public/",
                "package.json",
                "vite.config.js",
                "index.html"
            ],
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "vite": "^4.4.0"
            },
            "features": requirements.features + ["responsive", "modern_ui"],
            "deployment": requirements.deployment_target
        }
        
        # Añadir dependencias basadas en características
        if requirements.auth_required:
            plan["dependencies"]["auth_provider"] = "to_be_implemented"
        if requirements.payment_integration:
            plan["dependencies"]["payment_processor"] = "stripe_or_similar"
        
        return plan
    
    def _generate_by_type(self, requirements: ProjectRequirements, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Genera el proyecto basado en el tipo"""
        
        print(f"🔧 Generando proyecto tipo: {requirements.project_type.value}")
        
        # PRIMERO intentar con generadores especializados
        specialized_result = self._generate_with_specialized(requirements, plan)
        if specialized_result:
            print("🎯 ¡Generador especializado usado exitosamente!")
            return specialized_result
        
        # SI FALLA, usar React básico
        print(f"⚠️  Usando generador React básico para: {requirements.project_type.value}")
        return self._generate_react_project(requirements, plan)
    
    def _generate_with_specialized(self, requirements: ProjectRequirements, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Usar generadores especializados si están disponibles"""
        try:
            print(f"🎯 Intentando usar generador especializado para: {requirements.project_type.value}")
            
            # Importar dinámicamente para evitar errores de importación
            import importlib
            specialized_module = importlib.import_module('generators.specialized')
            SpecializedGenerator = getattr(specialized_module, 'SpecializedGenerator')
            
            generator = SpecializedGenerator()
            result = generator.generate_project(
                project_type=requirements.project_type.value,
                project_name=requirements.name,
                description=requirements.description,
                features=requirements.features,
                technologies=requirements.technologies
            )
            
            if result.get("success"):
                # Enriquecer el resultado con el plan de IA
                result["ai_plan"] = plan
                result["requirements"] = requirements.dict()
                result["enhanced"] = True
                result["specialized_generator"] = True
                
                print(f"✅ Proyecto generado con generador especializado: {requirements.project_type.value}")
                return result
            else:
                print(f"⚠️  Generador especializado falló: {result.get('error')}")
            
        except ImportError as e:
            print(f"⚠️  No se pudo importar generadores especializados: {e}")
        except Exception as e:
            print(f"⚠️  Error con generador especializado: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _generate_react_project(self, requirements: ProjectRequirements, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un proyecto React usando el template engine existente"""
        
        try:
            # Usar el SimpleTemplateEngine que ya funciona
            result = self.template_engine.generate_react_project(
                project_name=requirements.name,
                description=requirements.description,
                output_dir="generated_projects",
                validate=True
            )
            
            return result
            
        except Exception as e:
            print(f"❌ Error en generación React: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_name": requirements.name
            }
    
    def _enrich_result(self, generation_result: Dict[str, Any], requirements: ProjectRequirements, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Enriquece el resultado con metadatos y optimizaciones"""
        
        if not generation_result.get("success", False):
            return generation_result
        
        # Crear resultado enriquecido
        enriched = generation_result.copy()
        
        # Añadir metadatos del proyecto
        enriched.update({
            "project_id": str(uuid.uuid4())[:8],
            "project_type": requirements.project_type.value,
            "requirements": requirements.dict(),
            "ai_plan": plan,
            "features_implemented": self._get_implemented_features(requirements),
            "next_steps": self._generate_next_steps(requirements),
            "generated_at": str(os.path.getmtime(enriched["project_path"]) if enriched.get("project_path") else "unknown")
        })
        
        # Añadir características específicas
        if requirements.auth_required:
            enriched["features_implemented"].append("auth_system_planned")
        if requirements.payment_integration:
            enriched["features_implemented"].append("payment_integration_planned")
        
        print(f"✅ Proyecto enriquecido con {len(enriched['features_implemented'])} características")
        return enriched
    
    def _get_implemented_features(self, requirements: ProjectRequirements) -> List[str]:
        """Obtiene lista de características implementadas"""
        base_features = ["react_app", "vite_build", "modern_ui", "responsive_design"]
        
        if requirements.auth_required:
            base_features.append("auth_ready")
        if requirements.payment_integration:
            base_features.append("payment_ready")
        if "real_time" in requirements.features:
            base_features.append("realtime_ready")
        if "admin_panel" in requirements.features:
            base_features.append("admin_ready")
            
        return base_features
    
    def _generate_next_steps(self, requirements: ProjectRequirements) -> List[str]:
        """Genera pasos siguientes para el usuario"""
        steps = [
            f"cd {requirements.name}",
            "npm install",
            "npm run dev"
        ]
        
        if requirements.auth_required:
            steps.append("# Implementar sistema de autenticación")
        if requirements.payment_integration:
            steps.append("# Integrar Stripe o similar para pagos")
        
        steps.extend([
            "# Personalizar componentes en src/",
            "# Añadir rutas en src/pages/",
            "# Deploy con: npm run build"
        ])
        
        return steps

# Función de conveniencia para uso rápido
def create_project_from_idea(name: str, description: str, project_type: str = "react_web_app") -> Dict[str, Any]:
    """Crea un proyecto rápidamente desde una idea"""
    
    factory = EnhancedProjectFactory()
    
    requirements = ProjectRequirements(
        name=name,
        description=description,
        project_type=ProjectType(project_type),
        features=["modern_ui", "responsive"],
        technologies=["react", "javascript"]
    )
    
    return factory.create_project(requirements)

if __name__ == "__main__":
    # Prueba rápida del sistema
    print("�� Probando EnhancedProjectFactory...")
    
    factory = EnhancedProjectFactory()
    
    test_req = ProjectRequirements(
        name="Test Proyecto Mejorado",
        description="Proyecto de prueba del sistema mejorado",
        project_type=ProjectType.REACT_WEB_APP,
        features=["demo", "test"],
        technologies=["react"]
    )
    
    result = factory.create_project(test_req)
    print(f"🎯 Resultado: {result.get('success')}")
    if result.get('success'):
        print(f"📍 Ruta: {result.get('project_path')}")
    else:
        print(f"❌ Error: {result.get('error')}")

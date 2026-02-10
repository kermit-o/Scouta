"""
Real Supervisor Fixed - Usa las interfaces REALES de los agentes
"""
import asyncio
import os
import json
import uuid
from typing import Dict, Any
from datetime import datetime

class RealSupervisorFixed:
    """Supervisor que usa las interfaces REALES de los agentes existentes"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_real_agents()
    
    def _initialize_real_agents(self):
        """Inicializa los agentes REALES con sus interfaces reales"""
        try:
            from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
            from core.agents.planning_agent import PlanningAgent
            from core.agents.builder_agent import BuilderAgent
            
            self.agents['intake'] = EnhancedIntakeAgent()
            self.agents['planning'] = PlanningAgent()
            self.agents['builder'] = BuilderAgent()
            
            print("✅ Supervisor: Agentes REALES cargados")
            print("🔍 Interfaces reales:")
            print("   - EnhancedIntakeAgent.run(project_id, requirements)")
            print("   - PlanningAgent.run(project_spec)") 
            print("   - BuilderAgent.run(project_id, requirements)")
            
        except Exception as e:
            print(f"❌ Error cargando agentes reales: {e}")
    
    async def generate_blog_project(self) -> Dict[str, Any]:
        """Genera un proyecto de blog usando las interfaces REALES"""
        
        if not self.agents:
            return {"error": "No hay agentes disponibles"}
        
        print("🚀 SUPERVISOR REAL: Generando proyecto de blog...")
        
        try:
            # Generar ID único para el proyecto
            project_id = str(uuid.uuid4())
            
            # 1. ANÁLISIS - EnhancedIntakeAgent.run(project_id, requirements)
            print("🔍 Fase 1: Análisis con EnhancedIntakeAgent...")
            intake_requirements = {
                "name": "Blog Personal",
                "description": "Blog con autenticación, posts en markdown y dashboard admin",
                "type": "web_app", 
                "features": ["login", "markdown_editor", "dashboard", "responsive"],
                "stack": ["react", "node", "sqlite"]
            }
            
            analysis = await self.agents['intake'].run(project_id, intake_requirements)
            print(f"   ✅ Análisis completado")
            
            # 2. PLANIFICACIÓN - PlanningAgent.run(project_spec)
            print("📊 Fase 2: Planificación con PlanningAgent...")
            plan = await self.agents['planning'].run(analysis)
            print(f"   ✅ Planificación completada")
            
            # 3. CONSTRUCCIÓN - BuilderAgent.run(project_id, requirements)  
            print("🏗️ Fase 3: Construcción con BuilderAgent...")
            build_result = await self.agents['builder'].run(project_id, plan)
            print(f"   ✅ Construcción completada")
            
            # 4. VERIFICACIÓN
            verification = self._verify_real_project(build_result)
            
            return {
                "status": "success",
                "project_id": project_id,
                "analysis": analysis,
                "plan": plan,
                "build_result": build_result,
                "verification": verification,
                "agents_used": list(self.agents.keys())
            }
            
        except Exception as e:
            print(f"❌ Error en generación: {e}")
            import traceback
            traceback.print_exc()
            return {"status": "error", "error": str(e)}
    
    def _verify_real_project(self, build_result: Any) -> Dict[str, Any]:
        """Verificación REAL del proyecto generado"""
        verification = {
            "has_result": build_result is not None,
            "result_type": type(build_result).__name__,
            "is_dict": isinstance(build_result, dict),
            "has_project_path": False,
            "files_count": 0,
            "has_error": False
        }
        
        if isinstance(build_result, dict):
            verification.update({
                "has_project_path": "project_path" in build_result,
                "keys": list(build_result.keys()),
                "has_error": "error" in build_result or build_result.get("status") == "error"
            })
            
            if "project_path" in build_result:
                project_path = build_result["project_path"]
                if os.path.exists(project_path):
                    try:
                        files = []
                        for root, dirs, filenames in os.walk(project_path):
                            files.extend(filenames)
                        verification["files_count"] = len(files)
                    except Exception as e:
                        verification["files_error"] = str(e)
        
        return verification

    async def generate_minimal_project(self) -> Dict[str, Any]:
        """Genera un proyecto mínimo para testing"""
        print("🎯 Generando proyecto mínimo de prueba...")
        
        project_id = str(uuid.uuid4())
        
        try:
            # Análisis mínimo
            intake_requirements = {
                "name": "Test Project",
                "description": "Proyecto de prueba mínimo",
                "type": "web_app",
                "features": ["basic_setup"],
                "stack": ["html", "css", "js"]
            }
            
            analysis = await self.agents['intake'].run(project_id, intake_requirements)
            plan = await self.agents['planning'].run(analysis)
            build_result = await self.agents['builder'].run(project_id, plan)
            
            return {
                "status": "success",
                "project_id": project_id,
                "build_result": build_result
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

"""
Sync Supervisor - Usa las interfaces REALES y SINCRÓNICAS de los agentes
"""
import os
import json
import uuid
from typing import Dict, Any

class SyncSupervisor:
    """Supervisor que usa las interfaces SINCRÓNICAS reales de los agentes"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_sync_agents()
    
    def _initialize_sync_agents(self):
        """Inicializa los agentes con sus interfaces SINCRÓNICAS reales"""
        try:
            from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
            from core.agents.planning_agent import PlanningAgent
            from core.agents.builder_agent import BuilderAgent
            
            self.agents['intake'] = EnhancedIntakeAgent()
            self.agents['planning'] = PlanningAgent()
            self.agents['builder'] = BuilderAgent()
            
            print("✅ Supervisor Sincrónico: Agentes cargados")
            print("🔍 Interfaces sincrónicas detectadas")
            
        except Exception as e:
            print(f"❌ Error cargando agentes: {e}")
    
    def generate_blog_project(self) -> Dict[str, Any]:
        """Genera proyecto de blog usando interfaces SINCRÓNICAS"""
        
        if not self.agents:
            return {"error": "No hay agentes disponibles"}
        
        print("🚀 SUPERVISOR SINCRÓNICO: Generando proyecto...")
        
        try:
            project_id = str(uuid.uuid4())
            
            # 1. ANÁLISIS - EnhancedIntakeAgent.run(project_id, requirements) - SINCRÓNICO
            print("🔍 Fase 1: Análisis (sincrónico)...")
            intake_requirements = {
                "name": "Blog Personal",
                "description": "Blog con autenticación, posts en markdown y dashboard admin",
                "type": "web_app", 
                "features": ["login", "markdown_editor", "dashboard", "responsive"],
                "stack": ["react", "node", "sqlite"],
                "must_be_complete": True
            }
            
            analysis = self.agents['intake'].run(project_id, intake_requirements)
            print(f"   ✅ Análisis completado: {analysis.get('project_name', 'Unknown')}")
            
            # 2. PLANIFICACIÓN - PlanningAgent.run(project_spec) - SINCRÓNICO
            print("📊 Fase 2: Planificación (sincrónico)...")
            plan = self.agents['planning'].run(analysis)
            print(f"   ✅ Planificación completada")
            
            # 3. CONSTRUCCIÓN - BuilderAgent.run(project_id, requirements) - SINCRÓNICO
            print("🏗️ Fase 3: Construcción (sincrónico)...")
            build_result = self.agents['builder'].run(project_id, plan)
            print(f"   ✅ Construcción completada")
            
            # 4. VERIFICACIÓN
            verification = self._verify_project(build_result)
            
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
    
    def _verify_project(self, build_result: Any) -> Dict[str, Any]:
        """Verificación del proyecto generado"""
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
                        
                        # Verificar tipos de archivos
                        code_files = [f for f in files if f.endswith(('.js', '.jsx', '.py', '.ts', '.tsx', '.html', '.css'))]
                        verification["code_files"] = len(code_files)
                        
                    except Exception as e:
                        verification["files_error"] = str(e)
        
        return verification

    def generate_minimal_test(self) -> Dict[str, Any]:
        """Genera un proyecto mínimo de prueba"""
        print("🎯 Generando prueba mínima...")
        
        project_id = str(uuid.uuid4())
        
        try:
            # Requisitos mínimos
            intake_requirements = {
                "name": "Test Project",
                "description": "Proyecto de prueba mínimo",
                "type": "web_app",
                "features": ["basic_setup"],
                "stack": ["html", "css", "js"]
            }
            
            analysis = self.agents['intake'].run(project_id, intake_requirements)
            plan = self.agents['planning'].run(analysis)
            build_result = self.agents['builder'].run(project_id, plan)
            
            return {
                "status": "success",
                "project_id": project_id,
                "build_result": build_result
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}

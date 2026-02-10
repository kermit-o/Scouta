"""
Sync Supervisor Fixed - Con BuilderAgent corregido
"""
import os
import json
import uuid
from typing import Dict, Any

class SyncSupervisorFixed:
    """Supervisor con BuilderAgent corregido"""
    
    def __init__(self):
        self.agents = {}
        self._initialize_fixed_agents()
    
    def _initialize_fixed_agents(self):
        """Inicializa agentes con BuilderAgent corregido"""
        try:
            from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
            from core.agents.planning_agent import PlanningAgent
            from core.agents.fixed_builder_agent import FixedBuilderAgent
            
            self.agents['intake'] = EnhancedIntakeAgent()
            self.agents['planning'] = PlanningAgent()
            self.agents['builder'] = FixedBuilderAgent()
            
            print("✅ Supervisor Fixed: Agentes cargados (Builder corregido)")
            
        except Exception as e:
            print(f"❌ Error cargando agentes: {e}")
    
    def generate_blog_project(self) -> Dict[str, Any]:
        """Genera proyecto de blog con Builder corregido"""
        
        if not self.agents:
            return {"error": "No hay agentes disponibles"}
        
        print("🚀 SUPERVISOR FIXED: Generando proyecto REAL...")
        
        try:
            project_id = str(uuid.uuid4())
            
            # 1. ANÁLISIS
            print("🔍 Fase 1: Análisis...")
            intake_requirements = {
                "name": "Blog Personal",
                "description": "Blog con autenticación, posts en markdown y dashboard admin",
                "type": "web_app", 
                "features": ["login", "markdown_editor", "dashboard", "responsive"],
                "stack": ["react", "node", "sqlite"],
                "must_be_complete": True
            }
            
            analysis = self.agents['intake'].run(project_id, intake_requirements)
            print(f"   ✅ Análisis completado")
            
            # 2. PLANIFICACIÓN
            print("📊 Fase 2: Planificación...")
            plan = self.agents['planning'].run(analysis)
            print(f"   ✅ Planificación completada")
            
            # 3. CONSTRUCCIÓN con Builder FIXED
            print("🏗️ Fase 3: Construcción (con Builder corregido)...")
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
        """Verificación mejorada del proyecto"""
        verification = {
            "has_result": build_result is not None,
            "result_type": type(build_result).__name__,
            "is_dict": isinstance(build_result, dict),
            "has_project_path": False,
            "files_count": 0,
            "has_error": False,
            "success": False
        }
        
        if isinstance(build_result, dict):
            verification.update({
                "has_project_path": "project_path" in build_result,
                "keys": list(build_result.keys()),
                "has_error": "error" in build_result or build_result.get("status") == "error",
                "total_files": build_result.get("total_files", 0)
            })
            
            if "project_path" in build_result:
                project_path = build_result["project_path"]
                if os.path.exists(project_path):
                    try:
                        files = []
                        for root, dirs, filenames in os.walk(project_path):
                            for f in filenames:
                                files.append(os.path.join(root, f))
                        verification["files_count"] = len(files)
                        
                        # Verificar archivos de código
                        code_files = [f for f in files if f.endswith(('.js', '.jsx', '.py', '.ts', '.tsx', '.html', '.css', '.json'))]
                        verification["code_files"] = len(code_files)
                        
                        # Éxito si tiene al menos 3 archivos de código
                        verification["success"] = verification["code_files"] >= 3
                        
                    except Exception as e:
                        verification["files_error"] = str(e)
        
        return verification

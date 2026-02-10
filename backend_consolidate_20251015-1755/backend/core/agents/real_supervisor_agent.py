"""
Real Supervisor Agent - Coordina agentes EXISTENTES para generar proyectos COMPLETOS
"""
import asyncio
import os
import json
from typing import Dict, Any, List
from datetime import datetime

class RealSupervisorAgent:
    """Supervisor REAL que usa tus agentes existentes"""
    
    def __init__(self):
        self.agents_initialized = False
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Importa y inicializa los agentes REALES que tienes"""
        try:
            from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
            from core.agents.planning_agent import PlanningAgent
            from core.agents.builder_agent import BuilderAgent
            
            self.intake_agent = EnhancedIntakeAgent()
            self.planning_agent = PlanningAgent()
            self.builder_agent = BuilderAgent()
            
            self.agents_initialized = True
            print("✅ Supervisor: Agentes reales cargados")
            
        except Exception as e:
            print(f"❌ Supervisor: Error cargando agentes - {e}")
            self.agents_initialized = False
    
    async def generate_complete_project(self, user_requirements: str) -> Dict[str, Any]:
        """Genera un proyecto COMPLETO coordinando agentes reales"""
        
        if not self.agents_initialized:
            return {"error": "Agentes no inicializados"}
        
        print("🚀 SUPERVISOR REAL: Iniciando generación de proyecto...")
        
        try:
            # 1. ANÁLISIS con EnhancedIntakeAgent
            print("🔍 Fase 1: Análisis de requisitos...")
            analysis = await self.intake_agent.run(user_requirements)
            
            # 2. PLANIFICACIÓN con PlanningAgent  
            print("📊 Fase 2: Planificación...")
            plan = await self.planning_agent.run(analysis)
            
            # 3. CONSTRUCCIÓN con BuilderAgent
            print("��️ Fase 3: Construcción...")
            project_result = await self.builder_agent.run(plan)
            
            # 4. VERIFICACIÓN
            print("✅ Fase 4: Verificación...")
            verification = self._verify_project(project_result)
            
            return {
                "status": "success",
                "analysis": analysis,
                "plan": plan,
                "project": project_result,
                "verification": verification,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error en generación: {e}")
            return {"status": "error", "error": str(e)}
    
    def _verify_project(self, project_result: Dict[str, Any]) -> Dict[str, Any]:
        """Verifica que el proyecto generado sea válido"""
        verification = {
            "has_structure": False,
            "has_code": False,
            "files_count": 0,
            "is_complete": False
        }
        
        try:
            if "project_path" in project_result:
                project_path = project_result["project_path"]
                if os.path.exists(project_path):
                    # Contar archivos
                    files = []
                    for root, dirs, filenames in os.walk(project_path):
                        files.extend([os.path.join(root, f) for f in filenames])
                    
                    verification["files_count"] = len(files)
                    verification["has_structure"] = len(files) > 0
                    
                    # Verificar archivos de código
                    code_files = [f for f in files if f.endswith(('.js', '.jsx', '.py', '.ts', '.tsx'))]
                    verification["has_code"] = len(code_files) > 0
                    
                    # Verificar completitud básica
                    verification["is_complete"] = (
                        verification["has_structure"] and 
                        verification["has_code"] and 
                        verification["files_count"] >= 5
                    )
            
        except Exception as e:
            print(f"⚠️ Error en verificación: {e}")
        
        return verification
    
    async def generate_minimal_viable_project(self, requirements: str) -> Dict[str, Any]:
        """Genera un proyecto MÍNIMO pero FUNCIONAL"""
        print("🎯 Generando MVP real...")
        
        # Requisitos específicos para forzar generación completa
        mvp_requirements = {
            "type": "web_app",
            "name": "Blog Personal MVP",
            "description": requirements,
            "features": ["autenticación", "posts markdown", "dashboard admin"],
            "stack": ["react", "node", "sqlite"],
            "must_be_complete": True  # Forzar generación completa
        }
        
        return await self.generate_complete_project(json.dumps(mvp_requirements))

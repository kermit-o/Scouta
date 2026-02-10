"""
Real Intelligent Builder Agent - Usa el cliente ROBUSTO de DeepSeek para CADA componente
"""
import os
import asyncio
from typing import Dict, Any, List
from services.robust_deepseek_client import RobustDeepSeekClient

class RealIntelligentBuilderAgent:
    def __init__(self):
        self.client = RobustDeepSeekClient()
        self.generated_components = []
    
    async def build_component(self, component_spec: Dict, project_context: Dict) -> Dict[str, Any]:
        """Construye un componente consultando al LLM REAL para CADA parte"""
        
        print(f"🏗️ CONSULTANDO AL LLM REAL PARA: {component_spec.get('name', 'Componente')}")
        
        try:
            # 1. Consulta REAL para diseño
            design_result = await self.client.design_component(component_spec, project_context)
            
            # 2. Consulta REAL para código
            tech_stack = project_context.get('tech_stack', ['React', 'Node.js'])
            code_result = await self.client.generate_component_code(design_result, tech_stack)
            
            component_result = {
                "component": component_spec.get("name"),
                "detailed_design": design_result,
                "generated_code": code_result,
                "file_path": code_result.get("file_path"),
                "status": "built_with_real_llm",
                "code_length": len(code_result.get("main_code", ""))
            }
            
            self.generated_components.append(component_result)
            return component_result
            
        except Exception as e:
            print(f"❌ Error construyendo componente: {e}")
            return {
                "component": component_spec.get("name"),
                "error": str(e),
                "status": "error"
            }
    
    async def build_complete_project(self, requirements_analysis: Dict, project_context: Dict) -> Dict[str, Any]:
        """Construye un proyecto completo consultando al LLM REAL para cada componente"""
        
        print("🚀 CONSTRUYENDO PROYECTO COMPLETO CON LLM REAL...")
        
        components_to_build = requirements_analysis.get('specific_requirements', [])
        built_components = []
        
        for component_spec in components_to_build[:5]:  # Limitar a 5 componentes para prueba
            print(f"\n🔨 [{len(built_components) + 1}/{len(components_to_build[:5])}] Construyendo: {component_spec.get('name')}")
            
            built_component = await self.build_component(component_spec, project_context)
            built_components.append(built_component)
            
            if built_component.get('status') == 'built_with_real_llm':
                print(f"   ✅ Código generado: {built_component.get('file_path')}")
                print(f"   📝 {built_component.get('code_length', 0)} caracteres de código real")
        
        return {
            "project_name": requirements_analysis.get('user_input', 'Proyecto'),
            "total_components": len(built_components),
            "successful_components": len([c for c in built_components if c.get('status') == 'built_with_real_llm']),
            "built_components": built_components,
            "status": "project_built_with_real_llm"
        }

import importlib.util
import sys
import os
from typing import Any, Optional

class AgentLoader:
    """Cargador flexible de agentes que se adapta a los nombres de clase"""
    
    @staticmethod
    def load_enhanced_intake_agent():
        """Carga el agente de intake de manera flexible"""
        try:
            # Intentar importar desde el archivo standalone
            spec = importlib.util.spec_from_file_location(
                "enhanced_intake", 
                "enhanced_intake_standalone_final.py"
            )
            enhanced_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(enhanced_module)
            
            # Buscar cualquier clase que parezca ser el agente
            for attr_name in dir(enhanced_module):
                attr = getattr(enhanced_module, attr_name)
                if (isinstance(attr, type) and 
                    'intake' in attr_name.lower() and 
                    'agent' in attr_name.lower()):
                    print(f"✅ Encontrado EnhancedIntakeAgent: {attr_name}")
                    return attr()
            
            # Si no encontramos por nombre, buscar por herencia o métodos
            for attr_name in dir(enhanced_module):
                attr = getattr(enhanced_module, attr_name)
                if isinstance(attr, type):
                    # Verificar si tiene métodos de agente
                    if hasattr(attr, 'analyze_complexity') or hasattr(attr, 'analyze_requirements'):
                        print(f"✅ Encontrado agente por métodos: {attr_name}")
                        return attr()
            
            raise ImportError("No se pudo encontrar una clase de agente válida")
            
        except Exception as e:
            print(f"❌ Error cargando EnhancedIntakeAgent: {e}")
            return None
    
    @staticmethod
    def load_dual_pipeline_supervisor():
        """Carga el supervisor de pipeline de manera flexible"""
        try:
            # Intentar importar desde el archivo standalone
            spec = importlib.util.spec_from_file_location(
                "dual_pipeline", 
                "dual_pipeline_standalone_system.py"
            )
            pipeline_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(pipeline_module)
            
            # Buscar cualquier clase que parezca ser el supervisor
            for attr_name in dir(pipeline_module):
                attr = getattr(pipeline_module, attr_name)
                if (isinstance(attr, type) and 
                    any(keyword in attr_name.lower() for keyword in ['supervisor', 'pipeline', 'manager'])):
                    print(f"✅ Encontrado DualPipeline: {attr_name}")
                    return attr()
            
            # Buscar por métodos
            for attr_name in dir(pipeline_module):
                attr = getattr(pipeline_module, attr_name)
                if isinstance(attr, type):
                    if hasattr(attr, 'analyze_and_route') or hasattr(attr, 'route_project'):
                        print(f"✅ Encontrado pipeline por métodos: {attr_name}")
                        return attr()
            
            raise ImportError("No se pudo encontrar una clase de pipeline válida")
            
        except Exception as e:
            print(f"❌ Error cargando DualPipeline: {e}")
            return None

# Prueba rápida del cargador
if __name__ == "__main__":
    print("🧪 Probando AgentLoader...")
    
    intake_agent = AgentLoader.load_enhanced_intake_agent()
    if intake_agent:
        print("✅ EnhancedIntakeAgent cargado exitosamente")
        # Probar un método
        if hasattr(intake_agent, 'analyze_complexity'):
            result = intake_agent.analyze_complexity("Test project")
            print(f"   Análisis: {result}")
    else:
        print("❌ No se pudo cargar EnhancedIntakeAgent")
    
    pipeline_supervisor = AgentLoader.load_dual_pipeline_supervisor()
    if pipeline_supervisor:
        print("✅ DualPipelineSupervisor cargado exitosamente")
    else:
        print("❌ No se pudo cargar DualPipelineSupervisor")

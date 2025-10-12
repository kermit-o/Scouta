#!/usr/bin/env python3
"""
Test para verificar que EnhancedProjectFactory use generadores especializados
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_factory_direct():
    """Test directo del EnhancedProjectFactory"""
    print("🧪 TEST: EnhancedProjectFactory Directo")
    
    try:
        from core.enhanced_project_factory import EnhancedProjectFactory
        from core.project_factory import ProjectRequirements, ProjectType
        
        print("✅ EnhancedProjectFactory importado correctamente")
        
        # Crear factory
        factory = EnhancedProjectFactory()
        print("✅ Factory creado")
        
        # Crear requirements para Next.js
        requirements = ProjectRequirements(
            name="Test Factory NextJS",
            description="Proyecto de prueba del factory",
            project_type=ProjectType.NEXTJS_APP,
            features=["auth", "admin_panel"],
            technologies=["react", "typescript", "tailwind"]
        )
        
        print("✅ Requirements creados")
        print(f"   Tipo: {requirements.project_type.value}")
        print(f"   Características: {requirements.features}")
        
        # Generar proyecto
        result = factory.create_project(requirements)
        
        print("📊 RESULTADO:")
        print(f"   Success: {result.get('success')}")
        print(f"   Enhanced: {result.get('enhanced', False)}")
        print(f"   Specialized: {result.get('specialized_generator', False)}")
        
        if result.get('success'):
            project_path = result.get('project_path')
            if project_path and os.path.exists(project_path):
                print(f"📁 Archivos en {project_path}:")
                for item in os.listdir(project_path):
                    item_path = os.path.join(project_path, item)
                    if os.path.isfile(item_path):
                        print(f"   📄 {item}")
                    else:
                        print(f"   📁 {item}/")
            
            # Verificar si es Next.js
            nextjs_files = ["next.config.js", "app/", "tsconfig.json"]
            nextjs_found = 0
            for file in nextjs_files:
                if os.path.exists(os.path.join(project_path, file)):
                    nextjs_found += 1
            
            if nextjs_found >= 2:
                print("🎯 GENERADOR NEXT.JS ESPECIALIZADO CONFIRMADO!")
            else:
                print("⚠️  Posiblemente se usó generador básico")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_factory_direct()

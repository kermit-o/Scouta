#!/usr/bin/env python3
"""
Script de prueba para el EnhancedProjectFactory
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.enhanced_project_factory import EnhancedProjectFactory
from core.project_factory import ProjectRequirements, ProjectType

def test_basic_react():
    """Prueba la generación básica de React"""
    print("🧪 TEST 1: Proyecto React Básico")
    
    factory = EnhancedProjectFactory()
    
    requirements = ProjectRequirements(
        name="Test React Básico",
        description="Una aplicación React de prueba generada por el sistema mejorado",
        project_type=ProjectType.REACT_WEB_APP,
        features=["modern_ui", "responsive"],
        technologies=["react", "javascript"]
    )
    
    result = factory.create_project(requirements)
    
    print(f"✅ Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"📍 Path: {result.get('project_path')}")
        print(f"🎨 Features: {result.get('features_implemented', [])}")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result.get('success', False)

def test_saas_project():
    """Prueba un proyecto SaaS más complejo"""
    print("\n🧪 TEST 2: Proyecto SaaS Complejo")
    
    factory = EnhancedProjectFactory()
    
    requirements = ProjectRequirements(
        name="Mi Startup SaaS",
        description="Una aplicación SaaS moderna con autenticación y sistema de pagos",
        project_type=ProjectType.REACT_WEB_APP,
        features=["auth", "payment", "admin_panel", "real_time"],
        technologies=["react", "typescript", "tailwind"],
        auth_required=True,
        payment_integration=True,
        deployment_target="vercel"
    )
    
    result = factory.create_project(requirements)
    
    print(f"✅ Success: {result.get('success', False)}")
    if result.get('success'):
        print(f"📍 Path: {result.get('project_path')}")
        print(f"🎨 Features: {result.get('features_implemented', [])}")
        print(f"📋 Next Steps: {result.get('next_steps', [])[:3]}...")
    else:
        print(f"❌ Error: {result.get('error')}")
    
    return result.get('success', False)

def test_project_listing():
    """Prueba listar proyectos generados"""
    print("\n🧪 TEST 3: Listado de Proyectos")
    
    import os
    projects_dir = "generated_projects"
    if os.path.exists(projects_dir):
        projects = os.listdir(projects_dir)
        print(f"📁 Proyectos encontrados: {len(projects)}")
        for project in projects:
            project_path = os.path.join(projects_dir, project)
            if os.path.isdir(project_path):
                has_package = os.path.exists(os.path.join(project_path, "package.json"))
                print(f"  - {project} {'📦' if has_package else '📁'}")
    else:
        print("❌ No hay proyectos generados")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL SISTEMA MEJORADO")
    print("=" * 50)
    
    success_count = 0
    total_tests = 2
    
    # Ejecutar pruebas
    if test_basic_react():
        success_count += 1
    
    if test_saas_project():
        success_count += 1
    
    test_project_listing()
    
    # Resumen
    print("\n" + "=" * 50)
    print(f"📊 RESULTADOS: {success_count}/{total_tests} pruebas exitosas")
    
    if success_count == total_tests:
        print("🎉 ¡Todas las pruebas pasaron! El sistema está funcionando.")
        print("\n🚀 PARA USAR EL SISTEMA:")
        print("1. Ejecuta: python main.py")
        print("2. Abre: http://localhost:8000")
        print("3. O usa la API en: http://localhost:8000/api/projects/create")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")

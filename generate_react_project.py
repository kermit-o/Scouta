#!/usr/bin/env python3
import os
import sys

# Añadir el directorio actual al path para importar nuestros módulos
sys.path.append('.')

try:
    from generators.template_engine import TemplateEngine
    
    print("🚀 GENERANDO PROYECTO REACT REAL")
    print("================================")
    
    # Crear Template Engine
    engine = TemplateEngine()
    
    # Datos para un proyecto React completo
    project_data = {
        "name": "Mi Primera App React",
        "description": "Una aplicación React moderna generada por Forge SaaS",
        "type": "react_web_app", 
        "features": ["auth", "crud", "responsive", "state_management"],
        "technologies": ["react", "javascript", "vite", "tailwind"]
    }
    
    # Generar el proyecto
    result = engine.generate_project(project_data, "generated_projects")
    
    print(f"\\n✅ PROYECTO GENERADO EXITOSAMENTE!")
    print(f"📍 Ubicación: {result['project_path']}")
    print(f"📊 Total archivos: {result['total_files']}")
    
    # Mostrar los comandos para ejecutar el proyecto
    project_dir = result['project_path']
    print(f"\\n🎯 PARA EJECUTAR EL PROYECTO:")
    print(f"   cd {project_dir}")
    print(f"   npm install")
    print(f"   npm run dev")
    
    # Verificar que los archivos críticos existen
    print(f"\\n📋 ARCHIVOS CRÍTICOS GENERADOS:")
    critical_files = [
        "package.json",
        "src/App.jsx", 
        "src/main.jsx",
        "index.html",
        "vite.config.js"
    ]
    
    for file in critical_files:
        file_path = os.path.join(project_dir, file)
        if os.path.exists(file_path):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - No encontrado")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

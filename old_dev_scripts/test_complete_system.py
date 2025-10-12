#!/usr/bin/env python3
import os
import sys
import shutil

# Añadir el directorio actual al path
sys.path.append('.')

def test_complete_system():
    print("🧪 FORGE SAAS - TEST COMPLETO DEL SISTEMA")
    print("==========================================")
    
    # Limpiar proyectos de prueba anteriores
    test_dirs = [
        "generated_projects/Test Project 1",
        "generated_projects/Test Project 2", 
        "test_output"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
            print(f"🧹 Limpiado: {test_dir}")
    
    try:
        # 1. Test del Template Engine
        print("\\n1. 🔧 TESTEANDO TEMPLATE ENGINE...")
        from generators.simple_engine import SimpleTemplateEngine
        
        engine = SimpleTemplateEngine()
        print("✅ Template Engine importado correctamente")
        
        # 2. Generar proyecto de prueba
        print("\\n2. 🚀 GENERANDO PROYECTO DE PRUEBA...")
        result = engine.generate_react_project(
            "Test Project 1",
            "Proyecto de prueba para validación del sistema",
            validate=True
        )
        
        if not result["success"]:
            print("❌ FALLÓ la generación del proyecto")
            return False
        
        # 3. Verificar validación
        print("\\n3. 📊 VERIFICANDO RESULTADOS DE VALIDACIÓN...")
        validation = result.get("validation", {})
        
        if validation and validation.get("success"):
            print("🎉 ¡PROYECTO GENERADO Y VALIDADO CORRECTAMENTE!")
            
            # 4. Test manual adicional
            print("\\n4. 🔍 VERIFICACIÓN MANUAL ADICIONAL...")
            project_path = result["project_path"]
            
            # Verificar archivos críticos
            critical_files = [
                "package.json",
                "src/App.jsx",
                "src/main.jsx", 
                "index.html",
                "vite.config.js"
            ]
            
            all_files_exist = True
            for file in critical_files:
                file_path = os.path.join(project_path, file)
                if os.path.exists(file_path):
                    print(f"   ✅ {file} - EXISTE")
                    # Verificar que no esté vacío
                    if os.path.getsize(file_path) > 0:
                        print(f"      📏 Tamaño: {os.path.getsize(file_path)} bytes")
                    else:
                        print(f"      ⚠️  Archivo vacío")
                        all_files_exist = False
                else:
                    print(f"   ❌ {file} - NO EXISTE")
                    all_files_exist = False
            
            if all_files_exist:
                print("\\n🎯 TODOS LOS ARCHIVOS CRÍTICOS ESTÁN PRESENTES")
                
                # Mostrar estructura
                print("\\n📁 ESTRUCTURA GENERADA:")
                for root, dirs, files in os.walk(project_path):
                    level = root.replace(project_path, '').count(os.sep)
                    indent = ' ' * 2 * level
                    print(f'{indent}{os.path.basename(root)}/')
                    subindent = ' ' * 2 * (level + 1)
                    for file in files:
                        print(f'{subindent}{file}')
                    # Solo mostrar primer nivel
                    if level > 0:
                        break
                
                return True
            else:
                print("\\n❌ FALTAN ARCHIVOS CRÍTICOS")
                return False
                
        else:
            print("❌ LA VALIDACIÓN FALLÓ o no se pudo ejecutar")
            if validation:
                print("Errores encontrados:")
                for error in validation.get("errors", []):
                    print(f"   • {error}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR EN EL TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_complete_system()
    
    print("\\n" + "="*50)
    if success:
        print("🎉 ¡SISTEMA VALIDADO CORRECTAMENTE!")
        print("🚀 Forge SaaS está listo para generar proyectos React funcionales")
    else:
        print("💥 EL SISTEMA TIENE PROBLEMAS QUE RESOLVER")
        print("🔧 Revisa los errores y corrige el Template Engine")
    
    sys.exit(0 if success else 1)

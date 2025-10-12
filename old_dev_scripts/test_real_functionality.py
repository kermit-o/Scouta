#!/usr/bin/env python3
import os
import sys
import shutil
import time

def test_real_functionality():
    """Test que realmente ejecuta el proyecto generado"""
    print("🎯 FORGE SAAS - TEST DE FUNCIONALIDAD REAL")
    print("===========================================")
    
    # Limpiar proyecto anterior
    test_project = "generated_projects/Real Functionality Test"
    if os.path.exists(test_project):
        shutil.rmtree(test_project)
    
    try:
        # 1. Generar proyecto
        print("\\n1. 🚀 GENERANDO PROYECTO...")
        from generators.simple_engine import SimpleTemplateEngine
        
        engine = SimpleTemplateEngine()
        result = engine.generate_react_project(
            "Real Functionality Test",
            "Proyecto para test de funcionalidad real",
            validate=False  # No validar para evitar problemas con Node.js
        )
        
        if not result["success"]:
            print("❌ FALLÓ la generación del proyecto")
            return False
        
        project_path = result["project_path"]
        print(f"✅ Proyecto generado: {project_path}")
        
        # 2. Verificar archivos manualmente
        print("\\n2. 🔍 VERIFICACIÓN MANUAL DE ARCHIVOS...")
        
        required_files = {
            "package.json": "Debe contener scripts y dependencias",
            "src/App.jsx": "Componente principal de React", 
            "src/main.jsx": "Punto de entrada de la aplicación",
            "index.html": "HTML base",
            "vite.config.js": "Configuración de Vite"
        }
        
        all_files_ok = True
        for file, description in required_files.items():
            file_path = os.path.join(project_path, file)
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   ✅ {file}: {size} bytes - {description}")
                
                # Verificar contenido básico
                if size == 0:
                    print(f"      ⚠️  Archivo vacío")
                    all_files_ok = False
            else:
                print(f"   ❌ {file}: NO EXISTE - {description}")
                all_files_ok = False
        
        if not all_files_ok:
            print("❌ Faltan archivos críticos")
            return False
        
        # 3. Probar instalación de dependencias
        print("\\n3. 📦 INSTALANDO DEPENDENCIAS...")
        try:
            import subprocess
            install_result = subprocess.run(
                ['npm', 'install'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if install_result.returncode == 0:
                print("✅ Dependencias instaladas correctamente")
            else:
                print(f"❌ Error instalando dependencias: {install_result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout instalando dependencias")
            return False
        except Exception as e:
            print(f"❌ Error durante instalación: {str(e)}")
            return False
        
        # 4. Probar build
        print("\\n4. 🔨 PROBANDO BUILD...")
        try:
            build_result = subprocess.run(
                ['npm', 'run', 'build'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if build_result.returncode == 0:
                print("✅ Build exitoso")
                
                # Verificar que se creó el directorio dist
                dist_path = os.path.join(project_path, "dist")
                if os.path.exists(dist_path):
                    print("✅ Directorio dist creado")
                    
                    # Contar archivos en dist
                    dist_files = []
                    for root, dirs, files in os.walk(dist_path):
                        for file in files:
                            dist_files.append(os.path.join(root, file))
                    
                    print(f"✅ {len(dist_files)} archivos generados en dist/")
                    return True
                else:
                    print("❌ Directorio dist no creado")
                    return False
            else:
                print(f"❌ Build falló: {build_result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ Timeout en build")
            return False
        except Exception as e:
            print(f"❌ Error durante build: {str(e)}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR EN EL TEST: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_real_functionality()
    
    print("\\n" + "="*50)
    if success:
        print("🎉 ¡TEST DE FUNCIONALIDAD EXITOSO!")
        print("🚀 Forge SaaS genera proyectos React COMPLETAMENTE FUNCIONALES")
        print("📦 Los proyectos pueden instalar dependencias y compilar correctamente")
    else:
        print("💥 EL TEST DE FUNCIONALIDAD FALLÓ")
        print("🔧 Revisa los errores específicos")
    
    sys.exit(0 if success else 1)

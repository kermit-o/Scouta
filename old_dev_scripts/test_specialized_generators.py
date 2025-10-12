#!/usr/bin/env python3
"""
Test para los generadores especializados
"""

import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nextjs_generator():
    """Test del generador Next.js"""
    print("🧪 TEST: Generador Next.js")
    
    try:
        from generators.specialized.nextjs_generator import NextJSGenerator
        
        generator = NextJSGenerator()
        result = generator.generate(
            project_name="Test NextJS App",
            description="Una aplicación Next.js de prueba con características avanzadas",
            features=["auth", "payment", "admin_panel"],
            technologies=["react", "typescript", "tailwind"]
        )
        
        if result.get("success"):
            print("✅ NextJS Generator: FUNCIONA")
            print(f"   Ruta: {result.get('project_path')}")
            
            # Verificar archivos generados
            project_path = result.get('project_path')
            expected_files = [
                "package.json",
                "next.config.js", 
                "app/layout.tsx",
                "app/page.tsx"
            ]
            
            for file in expected_files:
                file_path = os.path.join(project_path, file)
                if os.path.exists(file_path):
                    print(f"   ✅ {file}: EXISTE")
                else:
                    print(f"   ❌ {file}: NO EXISTE")
            
            return True
        else:
            print(f"❌ NextJS Generator: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ NextJS Generator Error: {e}")
        return False

def test_fastapi_generator():
    """Test del generador FastAPI"""
    print("\n🧪 TEST: Generador FastAPI")
    
    try:
        from generators.specialized.fastapi_generator import FastAPIGenerator
        
        generator = FastAPIGenerator()
        result = generator.generate(
            project_name="Test FastAPI Service",
            description="Un servicio FastAPI de prueba con autenticación",
            features=["auth", "payment"],
            technologies=["python", "postgresql"]
        )
        
        if result.get("success"):
            print("✅ FastAPI Generator: FUNCIONA")
            print(f"   Ruta: {result.get('project_path')}")
            
            # Verificar archivos generados
            project_path = result.get('project_path')
            expected_files = [
                "requirements.txt",
                "app/main.py",
                "app/api/__init__.py",
                "Dockerfile"
            ]
            
            for file in expected_files:
                file_path = os.path.join(project_path, file)
                if os.path.exists(file_path):
                    print(f"   ✅ {file}: EXISTE")
                else:
                    print(f"   ❌ {file}: NO EXISTE")
            
            return True
        else:
            print(f"❌ FastAPI Generator: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ FastAPI Generator Error: {e}")
        return False

def main():
    """Ejecutar tests de generadores"""
    print("🚀 TESTEANDO GENERADORES ESPECIALIZADOS")
    print("=" * 50)
    
    # Limpiar proyectos de prueba anteriores
    test_dirs = [
        "generated_projects/Test NextJS App",
        "generated_projects/Test FastAPI Service"
    ]
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    tests = [test_nextjs_generator, test_fastapi_generator]
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} falló: {e}")
            results.append(False)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESULTADOS GENERADORES ESPECIALIZADOS:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {i}. {test.__name__}: {status}")
    
    print(f"\n🎯 {passed}/{total} generadores funcionando")
    
    if passed == total:
        print("🎉 ¡TODOS LOS GENERADORES ESPECIALIZADOS FUNCIONAN!")
        print("\n🚀 Ahora tu Forge SaaS puede generar:")
        print("   - Aplicaciones Next.js con TypeScript y Tailwind")
        print("   - Servicios FastAPI con autenticación y base de datos")
        print("   - ¡Y mucho más que lovable.dev!")
    else:
        print("⚠️  Algunos generadores necesitan ajustes")

if __name__ == "__main__":
    main()

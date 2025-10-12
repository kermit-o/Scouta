#!/usr/bin/env python3
"""
Test específico para NextJS Generator corregido
"""

import sys
import os
import shutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_nextjs_generator_fixed():
    """Test del generador Next.js corregido"""
    print("🧪 TEST: Generador Next.js (Corregido)")
    
    try:
        from generators.specialized.nextjs_generator import NextJSGenerator
        
        # Limpiar directorio de prueba
        test_dir = "generated_projects/Test NextJS Fixed"
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        generator = NextJSGenerator()
        result = generator.generate(
            project_name="Test NextJS Fixed",
            description="Una aplicación Next.js de prueba CORREGIDA",
            features=["auth", "payment"],
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
                "app/page.tsx",
                "app/globals.css"
            ]
            
            for file in expected_files:
                file_path = os.path.join(project_path, file)
                if os.path.exists(file_path):
                    size = os.path.getsize(file_path)
                    print(f"   ✅ {file}: EXISTE ({size} bytes)")
                    
                    # Mostrar primeras líneas de archivos clave
                    if file in ["package.json", "next.config.js"]:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            print(f"      Contenido: {content[:100]}...")
                else:
                    print(f"   ❌ {file}: NO EXISTE")
            
            return True
        else:
            print(f"❌ NextJS Generator: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ NextJS Generator Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_nextjs_generator_fixed()

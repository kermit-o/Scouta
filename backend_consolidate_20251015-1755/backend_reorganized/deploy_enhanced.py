#!/usr/bin/env python3
"""
SCRIPT DE DESPLIEGUE MEJORADO
Despliega la versión mejorada con verificación de dependencias
"""

import os
import sys
import subprocess
import importlib.util

def check_dependencies():
    """Verifica que todas las dependencias estén instaladas"""
    print("📦 VERIFICANDO DEPENDENCIAS...")
    
    required_packages = [
        'fastapi',
        'uvicorn', 
        'pydantic',
        'importlib'
    ]
    
    missing = []
    for package in required_packages:
        try:
            if package == 'importlib':
                # importlib es parte de la stdlib
                import importlib
            else:
                importlib.import_module(package)
            print(f"   ✅ {package}")
        except ImportError:
            missing.append(package)
            print(f"   ❌ {package}")
    
    return missing

def start_server():
    """Inicia el servidor mejorado"""
    print("\\n🚀 INICIANDO SERVIDOR MEJORADO...")
    
    try:
        # Verificar que el archivo existe
        if not os.path.exists('app/main_enhanced.py'):
            print("❌ app/main_enhanced.py no existe. Ejecuta improve_system.py primero.")
            return False
        
        # Iniciar servidor
        cmd = [
            'uvicorn', 'app.main_enhanced:app', 
            '--reload', '--host', '0.0.0.0', '--port', '8001'
        ]
        
        print(f"💻 Ejecutando: {' '.join(cmd)}")
        print("🌐 Servidor disponible en: http://localhost:8001")
        print("📚 Documentación en: http://localhost:8001/docs")
        print("\\n⏹️  Presiona Ctrl+C para detener el servidor")
        
        subprocess.run(cmd)
        return True
        
    except Exception as e:
        print(f"❌ Error iniciando servidor: {e}")
        return False

def main():
    print("🎯 DESPLIEGUE MEJORADO FORGE SaaS")
    print("=" * 50)
    
    # Verificar dependencias
    missing = check_dependencies()
    if missing:
        print(f"\\n❌ Faltan dependencias: {', '.join(missing)}")
        print("💡 Ejecuta: pip install " + " ".join(missing))
        return
    
    # Iniciar servidor
    start_server()

if __name__ == "__main__":
    main()

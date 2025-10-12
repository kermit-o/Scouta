#!/usr/bin/env python3
"""
Script de prueba seguro para Forge SaaS AI
Verifica la integración sin afectar el sistema existente
"""

import sys
import os

# Agregar backend al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'app'))

def test_ai_integration():
    print("🧪 FORGE SAAS AI - PRUEBA SEGURA")
    print("=" * 50)
    
    try:
        # 1. Verificar que el agente existe
        from agents.intake import run, run_mock
        
        print("✅ Agente intake importado correctamente")
        
        # 2. Probar con mock primero (sin API)
        print("\n🔧 Probando modo mock...")
        mock_result = run_mock("test-mock", "Sistema de prueba")
        print(f"   📊 Estado: {mock_result['status']}")
        print(f"   🎯 Complejidad: {mock_result['analysis']['complexity']}")
        
        # 3. Probar con API (si está configurada)
        print("\n🚀 Probando con DeepSeek API...")
        if os.getenv("DEEPSEEK_API_KEY"):
            try:
                api_result = run("test-api", "Sistema de gestión de tareas simple")
                print(f"   📊 Estado: {api_result['status']}")
                print(f"   📝 Resumen: {api_result['analysis']['summary']}")
                print(f"   🎯 Complejidad: {api_result['analysis']['complexity']}")
                print(f"   ⏱️  Tiempo: {api_result['analysis']['estimated_time']}")
                print("   ✅ DeepSeek API funcionando correctamente")
            except Exception as e:
                print(f"   ⚠️  API no disponible: {e}")
                print("   💡 Usando modo mock para desarrollo")
        else:
            print("   ⚠️  DEEPSEEK_API_KEY no configurada")
            print("   💡 Usando modo mock")
        
        print("\n" + "=" * 50)
        print("🎉 PRUEBA COMPLETADA - Forge SaaS AI listo")
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("💡 Ejecuta el script de actualización primero")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    test_ai_integration()

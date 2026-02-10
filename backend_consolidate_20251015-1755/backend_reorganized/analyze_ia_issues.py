#!/usr/bin/env python3
import os
import re

def analyze_ia_issues():
    print("🚨 PROBLEMAS CRÍTICOS CON LA INTEGRACIÓN DE IA")
    print("=" * 55)
    
    # Problemas en PlanningAgent
    planning_file = "./core/agents/planning_agent.py"
    if os.path.exists(planning_file):
        print("🔍 PROBLEMAS EN PLANNING AGENT:")
        with open(planning_file, 'r') as f:
            content = f.read()
            
            # Errores de código
            errors = []
            if "DPSK_API_KY" in content:
                errors.append("❌ API_KEY mal escrito: 'DPSK_API_KY' debería ser 'DPSK_API_KEY'")
            if "temperatre" in content:
                errors.append("❌ Temperature mal escrito: 'temperatre' debería ser 'temperature'")
            if "Tre" in content:
                errors.append("❌ True mal escrito: 'Tre' debería ser 'True'")
            if "alse" in content:
                errors.append("❌ False mal escrito: 'alse' debería ser 'False'")
            if "ser reqirements" in content:
                errors.append("❌ User requirements mal escrito múltiples veces")
            if "otpt" in content:
                errors.append("❌ Output mal escrito: 'otpt' debería ser 'output'")
            
            for error in errors:
                print(f"   {error}")
    
    # Verificar si el agente realmente se usa
    print(f"\n🔍 USO REAL DE AGENTES CON IA:")
    server_file = "./persistent_server_fixed.py"
    if os.path.exists(server_file):
        with open(server_file, 'r') as f:
            server_content = f.read()
            if "PlanningAgent" in server_content:
                print("   ✅ PlanningAgent referenciado en servidor")
            else:
                print("   ❌ PlanningAgent NO se usa en servidor principal")
            
            if "BuilderAgent" in server_content:
                print("   ✅ BuilderAgent referenciado en servidor")
            else:
                print("   ❌ BuilderAgent NO se usa en servidor principal")
    
    # Verificar configuración de entorno
    print(f"\n🔧 CONFIGURACIÓN DE ENTORNO:")
    env_files = [".env", ".env.local", ".env.example"]
    env_configured = False
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"   ✅ {env_file} existe")
            with open(env_file, 'r') as f:
                env_content = f.read()
                if "DPSK_API" in env_content or "OPENAI_API" in env_content:
                    print("   ✅ API keys configuradas en entorno")
                    env_configured = True
                else:
                    print("   ❌ No hay API keys configuradas")
            break
    else:
        print("   ❌ No se encontró archivo .env")
    
    # Conclusión
    print(f"\n🎯 DIAGNÓSTICO:")
    if not env_configured:
        print("   ❌ SIN API KEYS: La IA no puede funcionar sin claves configuradas")
    print("   ❌ CÓDIGO CON ERRORES: Múltiples errores de sintaxis en agentes")
    print("   ❌ AGENTES NO USADOS: Los agentes con IA no se integran en el servidor")
    print("   ⚠️  IA POTENCIAL: El código referencia IA real pero no funciona")

if __name__ == "__main__":
    analyze_ia_issues()

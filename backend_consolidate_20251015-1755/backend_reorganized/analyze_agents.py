#!/usr/bin/env python3
import os
import importlib.util
import sys

def analyze_agents():
    print("🔍 ANALIZANDO AGENTES IMPLEMENTADOS")
    print("=" * 50)
    
    # Buscar archivos de agentes
    agent_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if "agent" in file.lower() and file.endswith(".py"):
                full_path = os.path.join(root, file)
                agent_files.append(full_path)
    
    print("📁 Archivos de agentes encontrados:")
    for agent_file in agent_files:
        print(f"  📄 {agent_file}")
        
        # Intentar analizar el agente
        try:
            with open(agent_file, 'r') as f:
                content = f.read()
                
                # Buscar clases de agentes
                if "class" in content and "Agent" in content:
                    lines = content.split('\n')
                    for line in lines:
                        if "class" in line and "Agent" in line:
                            print(f"     🏗️  {line.strip()}")
                
                # Buscar métodos principales
                if "def" in content:
                    methods = [line for line in lines if "def " in line and "(" in line and "):" in line]
                    if methods:
                        print(f"     📋 Métodos: {len(methods)}")
                        for method in methods[:3]:
                            print(f"        🔧 {method.strip()}")
                
        except Exception as e:
            print(f"     ❌ Error leyendo: {e}")
    
    # Verificar imports en el servidor principal
    print(f"\n📦 AGENTES IMPORTADOS EN EL SERVIDOR:")
    server_files = ["persistent_server_fixed.py", "app/main.py", "main.py"]
    for server_file in server_files:
        if os.path.exists(server_file):
            print(f"  🔍 Examinando {server_file}:")
            with open(server_file, 'r') as f:
                content = f.read()
                if "import" in content:
                    imports = [line for line in content.split('\n') if "import" in line and "agent" in line.lower()]
                    for imp in imports[:5]:
                        print(f"     📥 {imp.strip()}")

if __name__ == "__main__":
    analyze_agents()

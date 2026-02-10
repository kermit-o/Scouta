#!/usr/bin/env python3
import os
import inspect

def analyze_real_agents():
    print("🎯 AGENTES REALES IMPLEMENTADOS - ANÁLISIS DETALLADO")
    print("=" * 60)
    
    agent_files = [
        "./core/agents/planning_agent.py",
        "./core/agents/builder_agent.py", 
        "./core/agents/intake_agent.py",
        "./core/agents/tester_agent.py",
        "./core/agents/specification_agent.py",
        "./core/agents/architecture_design_agent.py",
        "./core/agents/validation_agent.py",
        "./core/agents/security_agent.py",
        "./core/agents/documenter_agent.py",
        "./core/agents/packager_agent.py",
        "./core/agents/mockup_agent.py",
        "./core/agents/data_design_agent.py",
        "./core/agents/enhanced_intake_agent.py",
        "./core/agents/supervisor_agent.py"
    ]
    
    active_agents = []
    inactive_agents = []
    
    for agent_file in agent_files:
        if os.path.exists(agent_file):
            with open(agent_file, 'r') as f:
                content = f.read()
                
                # Verificar si el agente está implementado o es solo esqueleto
                is_implemented = "def " in content and "pass" not in content
                has_ia = "openai" in content.lower() or "llm" in content.lower() or "gpt" in content.lower()
                
                # Extraer nombre de clase
                class_name = "Unknown"
                for line in content.split('\n'):
                    if "class " in line and "Agent" in line:
                        class_name = line.split("class ")[1].split("(")[0].strip()
                        break
                
                agent_info = {
                    "file": agent_file,
                    "class": class_name,
                    "implemented": is_implemented,
                    "has_ia": has_ia,
                    "lines": len(content.split('\n'))
                }
                
                if is_implemented:
                    active_agents.append(agent_info)
                else:
                    inactive_agents.append(agent_info)
    
    print("🤖 AGENTES ACTIVOS (IMPLEMENTADOS):")
    print("-" * 40)
    for agent in active_agents:
        status = "🤖 IA" if agent["has_ia"] else "🔄 SIM"
        print(f"  {status} {agent['class']:25} [{agent['lines']:3} líneas]")
        print(f"     📁 {agent['file']}")
    
    print(f"\n❌ AGENTES INACTIVOS (ESQUELETOS):")
    print("-" * 40)
    for agent in inactive_agents:
        print(f"  🚧 {agent['class']:25} [{agent['lines']:3} líneas]")
        print(f"     📁 {agent['file']}")
    
    # Verificar qué agentes se usan realmente
    print(f"\n🔍 USO REAL EN EL SISTEMA ACTUAL:")
    print("-" * 40)
    
    # Revisar el servidor principal
    server_file = "./persistent_server_fixed.py"
    if os.path.exists(server_file):
        with open(server_file, 'r') as f:
            server_content = f.read()
            used_agents = []
            for agent in active_agents:
                if agent['class'].lower() in server_content.lower():
                    used_agents.append(agent['class'])
            
            if used_agents:
                print("  ✅ Agentes usados en servidor principal:")
                for agent in used_agents:
                    print(f"     • {agent}")
            else:
                print("  ❌ No se detectan agentes usados en servidor principal")
    
    # Estadísticas
    print(f"\n📊 ESTADÍSTICAS:")
    print(f"  • Total agentes encontrados: {len(active_agents) + len(inactive_agents)}")
    print(f"  • Agentes implementados: {len(active_agents)}")
    print(f"  • Agentes con IA real: {sum(1 for a in active_agents if a['has_ia'])}")
    print(f"  • Agentes simulados: {sum(1 for a in active_agents if not a['has_ia'])}")
    print(f"  • Esqueletos sin implementar: {len(inactive_agents)}")

if __name__ == "__main__":
    analyze_real_agents()

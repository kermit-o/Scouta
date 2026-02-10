#!/usr/bin/env python3
"""
VERIFICADOR DE AGENTES IA
Comprueba qué agentes están disponibles y funcionando
"""

import os
import importlib.util
from pathlib import Path

def check_agents():
    print("🔍 VERIFICANDO AGENTES IA DISPONIBLES")
    print("=" * 60)
    
    # Buscar todos los archivos de agentes
    agent_files = list(Path('.').rglob('*agent*.py'))
    
    print(f"📁 Encontrados {len(agent_files)} archivos de agentes:")
    
    working_agents = []
    
    for agent_file in agent_files:
        # Excluir archivos de cache y tests
        if '__pycache__' in str(agent_file) or 'test' in str(agent_file).lower():
            continue
            
        print(f"\\n📄 {agent_file}:")
        
        try:
            # Intentar cargar el módulo
            spec = importlib.util.spec_from_file_location(f"agent_check", agent_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar clases de agentes
            agent_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and 'Agent' in attr_name:
                    agent_classes.append(attr_name)
            
            if agent_classes:
                print(f"   ✅ Clases: {', '.join(agent_classes)}")
                
                # Verificar métodos de cada clase
                for class_name in agent_classes:
                    cls = getattr(module, class_name)
                    methods = [method for method in dir(cls) if not method.startswith('_')]
                    print(f"      🛠️  {class_name} métodos: {methods[:5]}...")
                    
                    working_agents.append({
                        'file': str(agent_file),
                        'class': class_name,
                        'methods': methods
                    })
            else:
                print("   ❌ No se encontraron clases Agent")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print(f"\\n🎯 RESUMEN:")
    print(f"   Total agentes funcionales: {len(working_agents)}")
    
    for agent in working_agents:
        print(f"   📦 {agent['class']} en {agent['file']}")
        print(f"      Métodos: {', '.join(agent['methods'][:3])}...")

if __name__ == "__main__":
    check_agents()

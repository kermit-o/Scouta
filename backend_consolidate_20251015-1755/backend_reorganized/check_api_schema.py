#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"

def check_api_schema():
    print("🔍 VERIFICANDO ESQUEMA DE LA API")
    print("=" * 40)
    
    # Verificar el endpoint de creación de proyecto
    print("1. Probando con datos mínimos...")
    
    # Según el error, necesita project_name y requirements
    test_data = {
        "project_name": "Test Project",
        "requirements": "Test requirements"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects", json=test_data)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ Éxito: {response.json()}")
    else:
        print(f"   ❌ Error: {response.text}")
    
    # Verificar proyectos existentes para ver el formato
    print("\n2. Examinando formato de proyectos existentes...")
    projects = requests.get(f"{BASE_URL}/api/projects").json()
    if projects and len(projects) > 0:
        sample_project = projects[0]
        print("   Campos requeridos en proyectos existentes:")
        for key in sample_project.keys():
            print(f"      - {key}: {type(sample_project[key])}")
            
        print(f"\n   Ejemplo completo del primer proyecto:")
        print(json.dumps(sample_project, indent=2))

if __name__ == "__main__":
    check_api_schema()

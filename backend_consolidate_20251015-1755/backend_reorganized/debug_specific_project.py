#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8001"
PROJECT_ID = "1e89c40b-2ae0-470a-8db9-f29d14c32be9"

def debug_project():
    print(f"🔍 DIAGNÓSTICO DEL PROYECTO {PROJECT_ID}")
    print("=" * 50)
    
    # 1. Verificar estado del proyecto
    print("1. Estado del proyecto:")
    project = requests.get(f"{BASE_URL}/api/projects/{PROJECT_ID}").json()
    print(f"   Status: {project.get('status', 'NO STATUS')}")
    print(f"   Plan generado: {'generated_plan' in project}")
    
    # 2. Probar generación y ver respuesta completa
    print(f"\n2. Probando generación:")
    response = requests.post(f"{BASE_URL}/api/projects/{PROJECT_ID}/generate")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response Headers: {dict(response.headers)}")
    print(f"   Raw Response: {response.text}")
    
    try:
        data = response.json()
        print(f"   JSON Response: {json.dumps(data, indent=2)}")
        
        if 'job_id' in data:
            print(f"   ✅ Job ID obtenido: {data['job_id']}")
        else:
            print(f"   ❌ No hay job_id en la respuesta")
            print(f"   Keys disponibles: {list(data.keys())}")
    except Exception as e:
        print(f"   ❌ Error parseando JSON: {e}")
    
    # 3. Verificar directorio del proyecto
    print(f"\n3. Verificando directorio:")
    import os
    project_dir = f"generated_projects/{PROJECT_ID}"
    if os.path.exists(project_dir):
        print(f"   ✅ Directorio existe: {project_dir}")
        files = os.listdir(project_dir)
        print(f"   Archivos: {files}")
    else:
        print(f"   ❌ Directorio no existe: {project_dir}")

if __name__ == "__main__":
    debug_project()

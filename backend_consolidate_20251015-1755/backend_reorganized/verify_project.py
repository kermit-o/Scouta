#!/usr/bin/env python3
import requests
import os
import json

BASE_URL = "http://localhost:8001"

def verify_all_projects():
    print("🔍 VERIFICANDO TODOS LOS PROYECTOS")
    print("=" * 40)
    
    # Obtener todos los proyectos de la API
    response = requests.get(f"{BASE_URL}/api/projects")
    if response.status_code == 200:
        projects = response.json()
        print(f"📋 Proyectos en API: {len(projects)}")
        
        for i, project in enumerate(projects):
            print(f"\n{i+1}. 📁 {project.get('project_name', 'Sin nombre')}")
            print(f"   🆔 ID: {project.get('id')}")
            print(f"   📊 Estado: {project.get('status')}")
            print(f"   📝 Requisitos: {project.get('requirements', '')[:80]}...")
            
            # Verificar directorio
            project_id = project.get('id')
            project_dir = f"generated_projects/{project_id}"
            if os.path.exists(project_dir):
                files = []
                for root, dirs, filenames in os.walk(project_dir):
                    for file in filenames:
                        files.append(file)
                print(f"   ✅ Directorio: {project_dir} ({len(files)} archivos)")
            else:
                print(f"   ❌ Directorio: NO EXISTE")
    
    # Verificar proyectos en filesystem que no están en API
    print(f"\n🔍 PROYECTOS EN FILESYSTEM NO EN API:")
    if os.path.exists("generated_projects"):
        fs_projects = os.listdir("generated_projects")
        api_project_ids = [p.get('id') for p in projects]
        
        for fs_project in fs_projects:
            if fs_project not in api_project_ids:
                project_dir = f"generated_projects/{fs_project}"
                if os.path.isdir(project_dir):
                    files = os.listdir(project_dir)
                    print(f"   📂 {fs_project}: {len(files)} archivos - NO EN API")

if __name__ == "__main__":
    verify_all_projects()

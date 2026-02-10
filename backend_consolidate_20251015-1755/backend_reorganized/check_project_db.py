#!/usr/bin/env python3
import json
import os

def check_project_database():
    print("🔍 VERIFICANDO BASE DE DATOS DE PROYECTOS")
    print("=" * 50)
    
    # Buscar archivos de base de datos
    db_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if "project" in file.lower() and file.endswith(".json") and "generated_projects" not in root:
                db_files.append(os.path.join(root, file))
    
    print("Archivos de base de datos encontrados:")
    for db_file in db_files:
        print(f"  📄 {db_file}")
        try:
            with open(db_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"    Proyectos en DB: {len(data)}")
                    for i, proj in enumerate(data[:3]):  # Mostrar primeros 3
                        print(f"      {i+1}. ID: {proj.get('id', 'N/A')}, Name: {proj.get('project_name', 'N/A')}")
                elif isinstance(data, dict) and 'id' in data:
                    print(f"    Proyecto único: {data.get('id')} - {data.get('project_name', 'N/A')}")
        except Exception as e:
            print(f"    ❌ Error leyendo: {e}")
    
    # Verificar proyectos en generated_projects
    print(f"\n📁 Proyectos en generated_projects/:")
    gen_projects_dir = "generated_projects"
    if os.path.exists(gen_projects_dir):
        projects = os.listdir(gen_projects_dir)
        for proj_dir in projects[:10]:  # Mostrar primeros 10
            full_path = os.path.join(gen_projects_dir, proj_dir)
            if os.path.isdir(full_path):
                files = os.listdir(full_path)
                print(f"  📂 {proj_dir}: {len(files)} archivos - {files}")

if __name__ == "__main__":
    check_project_database()

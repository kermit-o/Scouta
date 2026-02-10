#!/usr/bin/env python3
import requests
import json
import os
import uuid

BASE_URL = "http://localhost:8001"

def repair_missing_project():
    print("🔧 REPARANDO PROYECTO FALTANTE EN BD")
    print("=" * 50)
    
    # 1. Primero crear un proyecto nuevo con los mismos datos
    print("1. Creando nuevo proyecto con datos del portal de noticias...")
    
    project_data = {
        "name": "Portal de Noticias Moderno",
        "description": "Sistema de portal de noticias con: artículos, categorías, autores, sistema de comentarios, búsqueda, panel administrativo y diseño responsive",
        "features": [
            "Gestión de artículos y categorías",
            "Sistema de autores y usuarios",
            "Comentarios en artículos", 
            "Búsqueda avanzada",
            "Panel administrativo",
            "Diseño responsive moderno"
        ],
        "tech_stack": {
            "frontend": "React + TypeScript + Tailwind",
            "backend": "Node.js + Express",
            "database": "MongoDB",
            "authentication": "JWT",
            "deployment": "Docker + Vercel"
        }
    }
    
    response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
    
    if response.status_code == 200:
        new_project = response.json()
        new_project_id = new_project['project_id']
        print(f"   ✅ Nuevo proyecto creado: {new_project_id}")
        
        # 2. Planificar
        print("2. Planificando proyecto...")
        plan_response = requests.post(f"{BASE_URL}/api/projects/{new_project_id}/plan")
        
        if plan_response.status_code == 200:
            print("   ✅ Planificación completada")
            
            # 3. Generar código
            print("3. Generando código...")
            gen_response = requests.post(f"{BASE_URL}/api/projects/{new_project_id}/generate")
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                print(f"   ✅ Respuesta generación: {json.dumps(gen_data, indent=2)}")
                
                if 'job_id' in gen_data:
                    job_id = gen_data['job_id']
                    print(f"   🎯 Job ID: {job_id}")
                    monitor_generation(job_id)
                else:
                    print("   ⚠️  No hay job_id, verificando estado directamente...")
                    check_final_result(new_project_id)
                    
            else:
                print(f"   ❌ Error en generación: {gen_response.text}")
        else:
            print(f"   ❌ Error en planificación: {plan_response.text}")
    else:
        print(f"   ❌ Error creando proyecto: {response.text}")
        return None
    
    return new_project_id

def monitor_generation(job_id):
    import time
    print(f"4. Monitoreando progreso...")
    for i in range(10):
        try:
            progress = requests.get(f"{BASE_URL}/api/progress/{job_id}").json()
            progress_pct = progress.get('progress', 0)
            message = progress.get('message', '')
            
            print(f"   📊 {progress_pct}% - {message}")
            
            if progress_pct == 100:
                print("   ✅ Generación completada!")
                break
            elif progress_pct == -1 or 'error' in message.lower():
                print(f"   ❌ Error: {message}")
                break
                
        except Exception as e:
            print(f"   ⚠️  Error monitoreando: {e}")
        
        time.sleep(2)

def check_final_result(project_id):
    print("5. Verificando resultado final...")
    
    # Verificar proyecto
    project = requests.get(f"{BASE_URL}/api/projects/{project_id}").json()
    print(f"   📋 Estado: {project.get('status', 'N/A')}")
    
    # Verificar directorio
    project_dir = f"generated_projects/{project_id}"
    if os.path.exists(project_dir):
        print(f"   ✅ Directorio creado: {project_dir}")
        files = []
        for root, dirs, filenames in os.walk(project_dir):
            for file in filenames:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                files.append(rel_path)
        
        print(f"   📁 Archivos generados ({len(files)}):")
        for file in sorted(files)[:15]:  # Mostrar primeros 15
            print(f"      {file}")
        if len(files) > 15:
            print(f"      ... y {len(files) - 15} más")
    else:
        print(f"   ❌ Directorio no existe: {project_dir}")
    
    # Verificar descarga
    download_info = requests.get(f"{BASE_URL}/api/projects/{project_id}/download").json()
    print(f"   📦 Info descarga: {json.dumps(download_info, indent=4)}")

if __name__ == "__main__":
    new_id = repair_missing_project()
    if new_id:
        print(f"\n🎉 PROYECTO REPARADO EXITOSAMENTE!")
        print(f"📋 ID: {new_id}")
        print(f"📁 Directorio: generated_projects/{new_id}")
        
        # Probar el flujo completo
        print(f"\n🧪 PROBANDO FLUJO COMPLETO...")
        test_full_flow(new_id)

def test_full_flow(project_id):
    """Probar que todo funcione con el nuevo proyecto"""
    print("1. ✅ Verificar proyecto en API...")
    project = requests.get(f"{BASE_URL}/api/projects/{project_id}").json()
    print(f"   Estado: {project.get('status')}")
    
    print("2. ✅ Verificar descarga...")
    download = requests.get(f"{BASE_URL}/api/projects/{project_id}/download").json()
    print(f"   Disponible: {'download_url' in download}")
    
    print("3. ✅ Verificar archivos generados...")
    project_dir = f"generated_projects/{project_id}"
    if os.path.exists(project_dir):
        readme_path = os.path.join(project_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                content = f.read()
                print(f"   README: {len(content)} caracteres")
                print(f"   Primeras líneas:")
                for line in content.split('\n')[:5]:
                    print(f"      {line}")

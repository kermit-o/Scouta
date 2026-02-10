#!/usr/bin/env python3
import requests
import json
import time
import os

BASE_URL = "http://localhost:8001"
JOB_ID = "f09a1515-838c-41eb-a797-c310706d220e"
PROJECT_ID = "89d62a26-32dd-4f86-9c40-9a4f9770a5aa"

def monitor_generation():
    print("📊 MONITOREANDO GENERACIÓN EN TIEMPO REAL")
    print("=" * 50)
    print(f"🎯 Job ID: {JOB_ID}")
    print(f"📋 Project ID: {PROJECT_ID}")
    print()
    
    max_attempts = 20
    last_progress = 0
    
    for attempt in range(max_attempts):
        try:
            # Verificar progreso
            progress_response = requests.get(f"{BASE_URL}/api/progress/{JOB_ID}")
            
            if progress_response.status_code == 200:
                progress_data = progress_response.json()
                current_progress = progress_data.get('progress', 0)
                message = progress_data.get('message', '')
                
                # Mostrar solo si hay cambio
                if current_progress != last_progress:
                    print(f"🕒 Intento {attempt + 1}/{max_attempts}:")
                    print(f"   📈 Progreso: {current_progress}%")
                    print(f"   💬 Mensaje: {message}")
                    print(f"   ⏰ Timestamp: {progress_data.get('timestamp', 'N/A')}")
                    last_progress = current_progress
                    
                    # Verificar si hay archivos generados
                    check_generated_files(PROJECT_ID)
                    print()
                
                # Verificar si está completo
                if current_progress == 100:
                    print("🎉 ¡GENERACIÓN COMPLETADA!")
                    break
                elif current_progress == -1:
                    print("❌ Error en la generación")
                    break
                    
            else:
                print(f"⚠️  Error obteniendo progreso: {progress_response.status_code}")
                
        except Exception as e:
            print(f"⚠️  Error: {e}")
        
        time.sleep(3)  # Esperar 3 segundos entre verificaciones
    
    # Verificación final
    print("\n" + "="*50)
    print("🔍 VERIFICACIÓN FINAL")
    final_check(PROJECT_ID)

def check_generated_files(project_id):
    """Verificar si se están generando archivos"""
    project_dir = f"generated_projects/{project_id}"
    if os.path.exists(project_dir):
        files = []
        try:
            for root, dirs, filenames in os.walk(project_dir):
                for file in filenames:
                    files.append(file)
            if files:
                print(f"   📁 Archivos en directorio: {len(files)}")
                # Mostrar algunos archivos importantes
                important_files = [f for f in files if any(ext in f.lower() for ext in ['.md', 'package.json', 'app.js', 'index.html'])]
                for imp_file in important_files[:3]:
                    print(f"      📄 {imp_file}")
        except Exception as e:
            print(f"   ⚠️  Error leyendo directorio: {e}")

def final_check(project_id):
    """Verificación completa final"""
    print("\n1. ✅ Verificando proyecto en API...")
    try:
        project_response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
        if project_response.status_code == 200:
            project = project_response.json()
            print(f"   📛 Nombre: {project.get('project_name')}")
            print(f"   📊 Estado: {project.get('status')}")
            print(f"   🆔 ID: {project.get('id')}")
        else:
            print(f"   ❌ Error: {project_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n2. ✅ Verificando archivos generados...")
    project_dir = f"generated_projects/{project_id}"
    if os.path.exists(project_dir):
        all_files = []
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                all_files.append(rel_path)
        
        print(f"   📊 Total de archivos: {len(all_files)}")
        
        # Mostrar estructura
        print(f"   📂 Estructura:")
        for file in sorted(all_files)[:15]:
            print(f"      📄 {file}")
        if len(all_files) > 15:
            print(f"      ... y {len(all_files) - 15} más")
            
        # Verificar README
        readme_path = os.path.join(project_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n   📖 README ({len(content)} caracteres):")
                lines = [line for line in content.split('\n') if line.strip()][:5]
                for i, line in enumerate(lines):
                    print(f"      {i+1}. {line}")
    else:
        print(f"   ❌ Directorio no existe: {project_dir}")
    
    print("\n3. ✅ Verificando descarga...")
    try:
        download_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/download")
        if download_response.status_code == 200:
            download_info = download_response.json()
            print(f"   ✅ Descarga disponible")
            if 'download_url' in download_info:
                print(f"   🔗 URL: {download_info['download_url']}")
        else:
            print(f"   ⚠️  Descarga no disponible: {download_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error: {e}")

if __name__ == "__main__":
    monitor_generation()

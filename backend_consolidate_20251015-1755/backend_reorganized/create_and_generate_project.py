#!/usr/bin/env python3
import requests
import json
import os
import time

BASE_URL = "http://localhost:8001"

def create_and_generate():
    print("🚀 CREANDO Y GENERANDO PROYECTO COMPLETO")
    print("=" * 50)
    
    # Datos del proyecto basados en el esquema correcto
    project_data = {
        "project_name": "Portal de Noticias Moderno",
        "requirements": "Sistema de portal de noticias con: artículos, categorías, autores, sistema de comentarios, búsqueda, panel administrativo y diseño responsive. Tecnologías: React, Node.js, MongoDB, JWT",
        "user_id": "news-user"  # Opcional pero recomendado
    }
    
    print("1. 📝 Creando proyecto...")
    response = requests.post(f"{BASE_URL}/api/projects", json=project_data)
    
    if response.status_code == 201:  # 201 Created es el código correcto
        project = response.json()
        project_id = project['id']  # Nota: usa 'id' no 'project_id'
        print(f"   ✅ Proyecto creado exitosamente!")
        print(f"   📋 ID: {project_id}")
        print(f"   📛 Nombre: {project['project_name']}")
        print(f"   �� Estado inicial: {project['status']}")
        
        # 2. Planificar el proyecto
        print("\n2. 📋 Planificando proyecto...")
        plan_response = requests.post(f"{BASE_URL}/api/projects/{project_id}/plan")
        
        if plan_response.status_code == 200:
            print("   ✅ Planificación iniciada")
            
            # Esperar a que se complete la planificación
            print("   ⏳ Esperando planificación...")
            time.sleep(3)
            
            # Verificar estado después de planificación
            project_after_plan = requests.get(f"{BASE_URL}/api/projects/{project_id}").json()
            print(f"   📊 Estado después de planificación: {project_after_plan.get('status')}")
            
            if project_after_plan.get('generated_plan'):
                print("   ✅ Plan generado con éxito")
            else:
                print("   ⚠️  Plan no generado, continuando...")
            
            # 3. Generar código
            print("\n3. 🏗️ Generando código...")
            gen_response = requests.post(f"{BASE_URL}/api/projects/{project_id}/generate")
            
            if gen_response.status_code == 200:
                gen_data = gen_response.json()
                print("   ✅ Solicitud de generación aceptada")
                print(f"   📦 Respuesta: {json.dumps(gen_data, indent=2)}")
                
                # Manejar la respuesta de generación
                if 'job_id' in gen_data:
                    job_id = gen_data['job_id']
                    print(f"   🎯 Job ID obtenido: {job_id}")
                    monitor_generation(job_id, project_id)
                else:
                    print("   ⚠️  No se recibió job_id, verificando estado directamente...")
                    time.sleep(5)
                    check_final_result(project_id)
                    
            else:
                print(f"   ❌ Error en generación: {gen_response.status_code} - {gen_response.text}")
        else:
            print(f"   ❌ Error en planificación: {plan_response.status_code} - {plan_response.text}")
    else:
        print(f"   ❌ Error creando proyecto: {response.status_code} - {response.text}")
        return None
    
    return project_id

def monitor_generation(job_id, project_id):
    print(f"\n4. 📊 Monitoreando progreso del job {job_id}...")
    max_attempts = 15
    completed = False
    
    for attempt in range(max_attempts):
        try:
            progress_response = requests.get(f"{BASE_URL}/api/progress/{job_id}")
            if progress_response.status_code == 200:
                progress = progress_response.json()
                progress_pct = progress.get('progress', 0)
                message = progress.get('message', '')
                
                print(f"   📈 Intento {attempt + 1}/{max_attempts}: {progress_pct}% - {message}")
                
                if progress_pct == 100:
                    print("   ✅ ¡Generación completada!")
                    completed = True
                    break
                elif progress_pct == -1 or 'error' in message.lower():
                    print(f"   ❌ Error en generación: {message}")
                    break
                elif progress_pct > 0 and progress_pct < 100:
                    print(f"   🔄 Progresando...")
            else:
                print(f"   ⚠️  Error obteniendo progreso: {progress_response.status_code}")
                
        except Exception as e:
            print(f"   ⚠️  Error monitoreando: {e}")
        
        time.sleep(2)  # Esperar 2 segundos entre intentos
    
    if not completed:
        print(f"   ⏰ Tiempo de espera agotado después de {max_attempts} intentos")
    
    # Verificar resultado final de todas formas
    check_final_result(project_id)

def check_final_result(project_id):
    print(f"\n5. 📋 VERIFICANDO RESULTADO FINAL")
    print("=" * 40)
    
    # Verificar proyecto en API
    try:
        project_response = requests.get(f"{BASE_URL}/api/projects/{project_id}")
        if project_response.status_code == 200:
            project = project_response.json()
            print(f"   ✅ Proyecto encontrado en API")
            print(f"   📛 Nombre: {project.get('project_name')}")
            print(f"   📊 Estado: {project.get('status')}")
            print(f"   🆔 ID: {project.get('id')}")
            
            if project.get('generated_plan'):
                print(f"   📋 Plan generado: Sí")
            else:
                print(f"   📋 Plan generado: No")
                
        else:
            print(f"   ❌ Error obteniendo proyecto: {project_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Verificar directorio generado
    project_dir = f"generated_projects/{project_id}"
    print(f"\n   📁 VERIFICANDO DIRECTORIO: {project_dir}")
    
    if os.path.exists(project_dir):
        print(f"   ✅ Directorio creado exitosamente!")
        
        # Contar y listar archivos
        all_files = []
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), project_dir)
                all_files.append(rel_path)
        
        print(f"   📊 Total de archivos generados: {len(all_files)}")
        
        # Mostrar estructura importante
        print(f"   📂 Estructura del proyecto:")
        
        # Agrupar por tipo de archivo
        readme_files = [f for f in all_files if 'readme' in f.lower()]
        package_files = [f for f in all_files if 'package.json' in f.lower()]
        source_files = [f for f in all_files if any(ext in f for ext in ['.js', '.jsx', '.ts', '.tsx', '.py'])]
        config_files = [f for f in all_files if any(ext in f for ext in ['.json', '.config', 'dockerfile'])]
        
        if readme_files:
            print(f"      📖 README: {readme_files[0]}")
        if package_files:
            print(f"      📦 Package: {package_files[0]}")
        if source_files:
            print(f"      💻 Código fuente: {len(source_files)} archivos")
            for sf in sorted(source_files)[:5]:
                print(f"          {sf}")
            if len(source_files) > 5:
                print(f"          ... y {len(source_files) - 5} más")
        if config_files:
            print(f"      ⚙️  Configuración: {len(config_files)} archivos")
        
        # Mostrar archivos principales
        print(f"\n   🗂️ Archivos principales:")
        main_files = sorted(all_files)[:15]
        for file in main_files:
            print(f"      📄 {file}")
        if len(all_files) > 15:
            print(f"      ... y {len(all_files) - 15} más")
            
        # Leer README si existe
        readme_path = os.path.join(project_dir, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"\n   📖 CONTENIDO DEL README ({len(content)} caracteres):")
                lines = content.split('\n')
                for i, line in enumerate(lines[:10]):
                    if line.strip():
                        print(f"      {i+1}. {line}")
                if len(lines) > 10:
                    print(f"      ... y {len(lines) - 10} líneas más")
                    
    else:
        print(f"   ❌ Directorio no creado: {project_dir}")
        print(f"   💡 Directorios existentes en generated_projects/:")
        existing_dirs = os.listdir("generated_projects") if os.path.exists("generated_projects") else []
        for dir_name in sorted(existing_dirs)[:10]:
            print(f"      📂 {dir_name}")
    
    # Verificar descarga
    print(f"\n   📦 VERIFICANDO DESCARGA...")
    try:
        download_response = requests.get(f"{BASE_URL}/api/projects/{project_id}/download")
        if download_response.status_code == 200:
            download_info = download_response.json()
            print(f"   ✅ Información de descarga disponible")
            if 'download_url' in download_info:
                print(f"   🔗 URL de descarga: {download_info['download_url']}")
            else:
                print(f"   📋 Info: {json.dumps(download_info, indent=4)}")
        else:
            print(f"   ⚠️  Descarga no disponible: {download_response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Error verificando descarga: {e}")

if __name__ == "__main__":
    print("🎯 INICIANDO GENERACIÓN DE PORTA DE NOTICIAS MODERNO")
    print("=" * 60)
    
    project_id = create_and_generate()
    
    if project_id:
        print(f"\n🎉 ¡PROCESO COMPLETADO!")
        print(f"📋 ID del proyecto: {project_id}")
        print(f"📁 Directorio: generated_projects/{project_id}")
        print(f"🌐 URL de API: http://localhost:8001/api/projects/{project_id}")
    else:
        print(f"\n❌ No se pudo completar la generación del proyecto")

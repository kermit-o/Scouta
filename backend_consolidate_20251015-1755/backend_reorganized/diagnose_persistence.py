#!/usr/bin/env python3
import requests
import json
import os
import sqlite3

BASE_URL = "http://localhost:8001"

def diagnose_persistence():
    print("🔍 DIAGNÓSTICO DE PERSISTENCIA DE DATOS")
    print("=" * 50)
    
    # 1. Verificar estado del servidor
    print("1. 🖥️  Estado del servidor:")
    try:
        health = requests.get(f"{BASE_URL}/api/health").json()
        print(f"   ✅ Servidor activo: {health}")
    except Exception as e:
        print(f"   ❌ Servidor no responde: {e}")
        return
    
    # 2. Verificar base de datos
    print("\n2. 💾 Buscando bases de datos:")
    db_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                db_files.append(os.path.join(root, file))
    
    if db_files:
        for db_file in db_files:
            print(f"   📁 Base de datos encontrada: {db_file}")
            try:
                # Intentar leer la base de datos
                conn = sqlite3.connect(db_file)
                cursor = conn.cursor()
                
                # Obtener tablas
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                print(f"   📊 Tablas en {db_file}:")
                for table in tables:
                    table_name = table[0]
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                    count = cursor.fetchone()[0]
                    print(f"      - {table_name}: {count} registros")
                    
                conn.close()
            except Exception as e:
                print(f"   ❌ Error leyendo {db_file}: {e}")
    else:
        print("   ❌ No se encontraron bases de datos SQLite")
    
    # 3. Verificar archivos JSON de proyectos
    print("\n3. 📄 Buscando archivos JSON de proyectos:")
    json_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if "project" in file.lower() and file.endswith('.json') and "generated_projects" not in root:
                json_files.append(os.path.join(root, file))
    
    for json_file in json_files[:5]:  # Mostrar primeros 5
        print(f"   📄 {json_file}")
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    print(f"      Proyectos: {len(data)}")
                elif isinstance(data, dict):
                    print(f"      Proyecto: {data.get('id', 'N/A')}")
        except Exception as e:
            print(f"      Error leyendo: {e}")
    
    # 4. Verificar si el servidor está usando memoria temporal
    print("\n4. 🧠 Verificando configuración del servidor:")
    config_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            if "config" in file.lower() and file.endswith('.py'):
                config_files.append(os.path.join(root, file))
    
    for config_file in config_files[:3]:
        print(f"   ⚙️  {config_file}")
        try:
            with open(config_file, 'r') as f:
                content = f.read()
                if "sqlite" in content.lower():
                    print(f"      → Mención a SQLite")
                if "memory" in content.lower():
                    print(f"      → Mención a memoria")
                if "temp" in content.lower():
                    print(f"      → Mención a temporal")
        except Exception as e:
            print(f"      Error leyendo: {e}")
    
    # 5. Probar crear un proyecto rápido y ver si persiste
    print("\n5. 🧪 Test de persistencia inmediata:")
    test_project = {
        "project_name": "Test Persistencia",
        "requirements": "Proyecto para testear persistencia de datos"
    }
    
    response = requests.post(f"{BASE_URL}/api/projects", json=test_project)
    if response.status_code == 201:
        project = response.json()
        test_id = project['id']
        print(f"   ✅ Proyecto de test creado: {test_id}")
        
        # Verificar inmediatamente
        immediate_check = requests.get(f"{BASE_URL}/api/projects/{test_id}")
        if immediate_check.status_code == 200:
            print(f"   ✅ Proyecto accesible inmediatamente")
        else:
            print(f"   ❌ Proyecto NO accesible inmediatamente")
        
        # Esperar 5 segundos y verificar again
        import time
        time.sleep(5)
        delayed_check = requests.get(f"{BASE_URL}/api/projects/{test_id}")
        if delayed_check.status_code == 200:
            print(f"   ✅ Proyecto persiste después de 5 segundos")
        else:
            print(f"   ❌ Proyecto NO persiste después de 5 segundos")
    else:
        print(f"   ❌ No se pudo crear proyecto de test: {response.text}")

if __name__ == "__main__":
    diagnose_persistence()

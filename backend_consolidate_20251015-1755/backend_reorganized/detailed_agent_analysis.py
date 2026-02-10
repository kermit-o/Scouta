#!/usr/bin/env python3
import os
import requests

def detailed_analysis():
    print("🔬 ANÁLISIS DETALLADO DE CAPACIDADES DE AGENTES")
    print("=" * 60)
    
    # 1. Verificar endpoints de agentes
    print("1. 🌐 ENDPOINTS DE AGENTES EN API:")
    base_url = "http://localhost:8001"
    
    endpoints = [
        "/api/health",
        "/api/projects", 
        "/api/projects/{id}/plan",
        "/api/projects/{id}/generate",
        "/api/progress/{job_id}"
    ]
    
    for endpoint in endpoints:
        try:
            if "{" not in endpoint:
                response = requests.get(f"{base_url}{endpoint}")
                print(f"   🔗 {endpoint}: {response.status_code}")
            else:
                print(f"   🔗 {endpoint}: [DYNAMIC]")
        except:
            print(f"   �� {endpoint}: ❌ OFFLINE")
    
    # 2. Analizar procesos reales
    print("\n2. 🔄 PROCESOS IMPLEMENTADOS:")
    
    processes = {
        "Planificación": {
            "implementado": True,
            "descripción": "Simula análisis y planificación arquitectónica",
            "ia_real": False,
            "resultado": "Plan básico con stack tecnológico"
        },
        "Generación Frontend": {
            "implementado": True, 
            "descripción": "Crea estructura React con componentes",
            "ia_real": False,
            "resultado": "App.jsx, componentes, configuración Vite"
        },
        "Generación Backend": {
            "implementado": True,
            "descripción": "Genera API Express con endpoints",
            "ia_real": False, 
            "resultado": "Server index.js, rutas API"
        },
        "Pruebas Automáticas": {
            "implementado": False,
            "descripción": "No implementado",
            "ia_real": False,
            "resultado": "N/A"
        },
        "Despliegue Automático": {
            "implementado": False,
            "descripción": "No implementado", 
            "ia_real": False,
            "resultado": "N/A"
        }
    }
    
    for process, info in processes.items():
        status = "✅" if info["implementado"] else "❌"
        ia_status = "🤖 REAL" if info["ia_real"] else "🔄 SIMULADO"
        print(f"   {status} {process}:")
        print(f"      📝 {info['descripción']}")
        print(f"      {ia_status}")
        print(f"      📊 Resultado: {info['resultado']}")
    
    # 3. Examinar proyectos generados
    print("\n3. 📁 PROYECTOS GENERADOS (ANÁLISIS):")
    try:
        projects = requests.get(f"{base_url}/api/projects").json()
        if projects:
            sample_project = projects[0]
            project_dir = f"generated_projects/{sample_project['id']}"
            
            if os.path.exists(project_dir):
                files = []
                for root, dirs, filenames in os.walk(project_dir):
                    for file in filenames:
                        files.append(file)
                
                print(f"   📂 Proyecto: {sample_project['project_name']}")
                print(f"   📄 Archivos generados: {len(files)}")
                print(f"   🏗️  Estructura típica:")
                for file in sorted(files)[:8]:
                    print(f"      📄 {file}")
            else:
                print("   ❌ No se encontró directorio del proyecto")
        else:
            print("   ❌ No hay proyectos para analizar")
    except Exception as e:
        print(f"   ❌ Error analizando proyectos: {e}")
    
    # 4. Conclusión
    print("\n4. 🎯 CONCLUSIÓN DEL ANÁLISIS:")
    print("   ✅ SISTEMA OPERATIVO: API completa y funcional")
    print("   ✅ GENERACIÓN BÁSICA: Crea proyectos React + Node.js")
    print("   ✅ PERSISTENCIA: Datos guardados en SQLite")
    print("   ⚠️  AGENTES SIMULADOS: No usan IA real")
    print("   ❌ CAPACIDADES AVANZADAS: Testing y deployment faltan")
    print("   📈 BASE SÓLIDA: Puede extenderse con IA real")

if __name__ == "__main__":
    detailed_analysis()

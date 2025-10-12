#!/usr/bin/env python3
"""
Test End-to-End del flujo completo de Forge SaaS
"""

import sys
import os
import requests
import json
import time

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_backend_health():
    """Test 1: Verificar que el backend esté funcionando"""
    print("🧪 TEST 1: Health Check del Backend")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend saludable")
            return True
        else:
            print(f"❌ Backend responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se pudo conectar al backend: {e}")
        return False

def test_api_endpoints():
    """Test 2: Verificar endpoints de la API"""
    print("\n🧪 TEST 2: Endpoints de la API")
    
    endpoints = [
        "/api/projects/types",
        "/api/projects/technologies", 
        "/api/projects/list"
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {endpoint}: OK")
            else:
                print(f"❌ {endpoint}: {response.status_code}")
                all_ok = False
        except Exception as e:
            print(f"❌ {endpoint}: Error - {e}")
            all_ok = False
    
    return all_ok

def test_project_creation():
    """Test 3: Crear un proyecto real"""
    print("\n🧪 TEST 3: Creación de Proyecto")
    
    project_data = {
        "name": "Test E2E Project",
        "description": "Proyecto de prueba del flujo end-to-end",
        "project_type": "react_web_app",
        "features": ["auth", "payment"],
        "technologies": ["react", "typescript", "tailwind"],
        "auth_required": True,
        "payment_integration": True,
        "deployment_target": "vercel"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/projects/create",
            json=project_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Proyecto creado exitosamente!")
                print(f"   ID: {result.get('project_id')}")
                print(f"   Ruta: {result.get('project_path')}")
                print(f"   Características: {result.get('features_implemented', [])}")
                
                # Verificar que el proyecto se generó físicamente
                project_path = result.get('project_path')
                if project_path and os.path.exists(project_path):
                    print("✅ Archivos del proyecto generados correctamente")
                    
                    # Verificar archivos clave
                    key_files = [
                        "package.json",
                        "src/App.jsx", 
                        "src/main.jsx",
                        "vite.config.js"
                    ]
                    
                    for file in key_files:
                        file_path = os.path.join(project_path, file)
                        if os.path.exists(file_path):
                            print(f"   ✅ {file}: Existe")
                        else:
                            print(f"   ❌ {file}: No existe")
                    
                    return True
                else:
                    print("❌ Los archivos del proyecto no se generaron")
                    return False
            else:
                print(f"❌ Error creando proyecto: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error en creación de proyecto: {e}")
        return False

def test_idea_analysis_flow():
    """Test 4: Simular el flujo completo de análisis de idea"""
    print("\n🧪 TEST 4: Flujo de Análisis de Idea")
    
    # Simular una idea de usuario
    user_ideas = [
        "Quiero una aplicación móvil para gestionar tareas con chat en tiempo real",
        "Necesito un dashboard para administrar ventas con gráficos y reportes",
        "Busco crear una tienda online con carrito de compras y pasarela de pagos",
        "Quiero una API REST para gestionar usuarios y permisos"
    ]
    
    print("💡 Ideas de prueba:")
    for i, idea in enumerate(user_ideas, 1):
        print(f"   {i}. {idea}")
    
    # Probar con la primera idea
    test_idea = user_ideas[0]
    print(f"\n🔍 Analizando idea: '{test_idea}'")
    
    # Simular análisis (esto sería llamado desde la UI)
    analysis_result = simulate_idea_analysis(test_idea)
    
    if analysis_result:
        print("✅ Análisis completado:")
        print(f"   Tipo: {analysis_result['projectType']}")
        print(f"   Arquitectura: {analysis_result['architecture']}")
        print(f"   Características: {analysis_result['features']}")
        print(f"   Tecnologías: {analysis_result['technologies']}")
        print(f"   Complejidad: {analysis_result['complexity']}")
        print(f"   Tiempo estimado: {analysis_result['estimatedTime']} días")
        
        # Ahora crear el proyecto basado en el análisis
        print("\n🚀 Creando proyecto basado en el análisis...")
        creation_success = create_project_from_analysis(analysis_result, test_idea)
        return creation_success
    else:
        print("❌ Falló el análisis de la idea")
        return False

def simulate_idea_analysis(user_idea):
    """Simular el análisis de IA que hace la UI"""
    # Esta es una simulación - en producción esto se haría con IA real
    time.sleep(1)  # Simular procesamiento
    
    idea_lower = user_idea.lower()
    
    # Lógica simple de análisis (igual que en el frontend)
    if 'móvil' in idea_lower or 'mobile' in idea_lower or 'app' in idea_lower:
        project_type = 'react_native_mobile'
        architecture = 'Aplicación móvil nativa'
    elif 'api' in idea_lower or 'backend' in idea_lower:
        project_type = 'fastapi_service' 
        architecture = 'API REST con autenticación JWT'
    else:
        project_type = 'react_web_app'
        architecture = 'SPA (Single Page Application)'
    
    features = ['auth']
    if 'tiempo real' in idea_lower or 'chat' in idea_lower:
        features.append('real_time')
        architecture += ' + WebSockets'
    if 'pago' in idea_lower or 'venta' in idea_lower:
        features.append('payment')
    
    technologies = ['react', 'typescript']
    if project_type == 'fastapi_service':
        technologies.extend(['python', 'postgresql'])
    elif project_type == 'react_native_mobile':
        technologies.append('nodejs')
    else:
        technologies.extend(['tailwind', 'nodejs'])
    
    estimated_time = 3 + len(features) * 2
    complexity = 'Alta' if len(features) > 3 else 'Media' if len(features) > 1 else 'Baja'
    
    return {
        'projectType': project_type,
        'description': f'Proyecto basado en: {user_idea}',
        'features': features,
        'technologies': technologies,
        'architecture': architecture,
        'estimatedTime': estimated_time,
        'complexity': complexity,
        'userIdea': user_idea
    }

def create_project_from_analysis(analysis, original_idea):
    """Crear proyecto basado en el análisis"""
    project_data = {
        "name": f"Proyecto Analizado: {original_idea[:30]}...",
        "description": analysis['description'],
        "project_type": analysis['projectType'],
        "features": analysis['features'],
        "technologies": analysis['technologies'],
        "auth_required": 'auth' in analysis['features'],
        "payment_integration": 'payment' in analysis['features'],
        "deployment_target": "vercel"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/projects/create",
            json=project_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                print("✅ Proyecto creado desde análisis!")
                print(f"   Ruta: {result.get('project_path')}")
                return True
            else:
                print(f"❌ Error: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Ejecutar todos los tests"""
    print("🚀 INICIANDO TEST END-TO-END COMPLETO")
    print("=" * 50)
    
    tests = [
        test_backend_health,
        test_api_endpoints, 
        test_project_creation,
        test_idea_analysis_flow
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} falló con excepción: {e}")
            results.append(False)
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE TESTS:")
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"   {i}. {test.__name__}: {status}")
    
    print(f"\n🎯 RESULTADO: {passed}/{total} tests exitosos")
    
    if passed == total:
        print("�� ¡TODOS LOS TESTS PASARON! El flujo está funcionando.")
        print("\n📝 Próximos pasos:")
        print("   1. La UI necesita conectar el botón 'Confirmar' con la API")
        print("   2. Implementar IA real para el análisis")
        print("   3. Mejorar el manejo de errores en la UI")
    else:
        print("⚠️  Algunos tests fallaron. Revisa los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

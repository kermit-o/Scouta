import requests
import json

def explore_api():
    base_url = "http://localhost:8000"
    
    print("🔍 EXPLORANDO API FORGE SAAS")
    print("=" * 50)
    
    # Endpoints a probar
    endpoints = [
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/api/v1/projects",
        "/api/v1/projects/",
        "/api/v1/ui-api",
        "/api/v1/ui-api/",
        "/api/v1/ai-analysis",
        "/api/v1/ai-analysis/",
        "/api/v1/auth",
        "/api/v1/billing"
    ]
    
    # Métodos a probar
    methods = ['GET', 'POST']
    
    for endpoint in endpoints:
        for method in methods:
            try:
                if method == 'GET':
                    response = requests.get(f"{base_url}{endpoint}", timeout=5)
                else:
                    response = requests.post(f"{base_url}{endpoint}", json={}, timeout=5)
                
                if response.status_code != 404:
                    print(f"✅ {method} {endpoint}: {response.status_code}")
                    
                    # Si es 200, mostrar algo del contenido
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            if isinstance(data, dict) and 'message' in data:
                                print(f"   📝 Mensaje: {data['message']}")
                        except:
                            if len(response.text) < 100:
                                print(f"   📄 Contenido: {response.text}")
            except Exception as e:
                pass  # Silenciar errores de conexión
    
    print("\n🎯 ENDPOINTS DISPONIBLES PARA GENERACIÓN:")
    print("Basado en la estructura del proyecto, prueba estos:")
    
    test_endpoints = [
        ("/api/v1/ui-api/generate-project", "POST", {
            "user_input": "Crear app de tareas",
            "project_type": "web_app"
        }),
        ("/api/v1/projects/create", "POST", {
            "description": "Sistema de gestión de tareas",
            "project_type": "web_app"
        }),
        ("/api/v1/ai-analysis/analyze-requirements", "POST", {
            "requirements": "App web moderna",
            "project_type": "web_app"
        })
    ]
    
    for endpoint, method, data in test_endpoints:
        try:
            if method == 'POST':
                response = requests.post(f"{base_url}{endpoint}", json=data, timeout=10)
                print(f"🔧 {method} {endpoint}: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ Funciona! Proyecto: {result.get('project_id', 'N/A')}")
        except Exception as e:
            print(f"❌ {method} {endpoint}: Error - {e}")

if __name__ == "__main__":
    explore_api()

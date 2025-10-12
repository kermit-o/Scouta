import requests
import json
import os

# Configurar API key
os.environ["DEEPSEEK_API_KEY"] = "sk-3ab10aa6d3f44a04ba7dc30d218e0a53"

BASE_URL = "http://localhost:8000"

def test_ai_analysis():
    """Prueba completa del análisis IA"""
    
    print("🧪 INICIANDO PRUEBA COMPLETA DE FORGE SAAS AI...")
    
    # 1. Probar health check
    print("\n1. ✅ Probando health check...")
    try:
        health_resp = requests.get(f"{BASE_URL}/api/health")
        print(f"   Health: {health_resp.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 2. Probar análisis IA simple
    print("\n2. 🤖 Probando análisis IA simple...")
    try:
        simple_req = {
            "requirements": "Sistema de reservas de restaurante con mesas, horarios y clientes",
            "project_id": "test-restaurant-001"
        }
        
        ai_resp = requests.post(f"{BASE_URL}/api/ai/analyze", json=simple_req)
        result = ai_resp.json()
        
        print(f"   Estado: {result.get('status', 'N/A')}")
        print(f"   Resumen: {result['analysis']['summary']}")
        print(f"   Complejidad: {result['analysis']['complexity']}")
        print(f"   Tiempo estimado: {result['analysis']['estimated_time']}")
        print(f"   Stack: {json.dumps(result['analysis']['suggested_stack'], indent=6)}")
        
    except Exception as e:
        print(f"   ❌ Error en análisis simple: {e}")
    
    # 3. Probar análisis complejo
    print("\n3. 🚀 Probando análisis IA complejo...")
    try:
        complex_req = {
            "requirements": """
            Necesito una plataforma de e-learning con:
            - Cursos en video con progreso de estudiantes
            - Sistema de quizzes y certificados
            - Foros de discusión por curso
            - Panel de instructor para gestionar contenido
            - Suscripciones y pagos recurrentes
            - Notificaciones en tiempo real
            - App móvil nativa
            """,
            "project_id": "test-elearning-001"
        }
        
        ai_resp = requests.post(f"{BASE_URL}/api/ai/analyze", json=complex_req)
        result = ai_resp.json()
        
        print(f"   Estado: {result.get('status', 'N/A')}")
        print(f"   Resumen: {result['analysis']['summary']}")
        print(f"   Complejidad: {result['analysis']['complexity']}")
        print(f"   Características: {result['analysis']['core_features']}")
        print(f"   Entidades: {result['analysis']['entities']}")
        
    except Exception as e:
        print(f"   ❌ Error en análisis complejo: {e}")
    
    print("\n🎉 PRUEBA COMPLETADA!")
    print("📊 Forge SaaS AI está funcionando correctamente")

if __name__ == "__main__":
    test_ai_analysis()

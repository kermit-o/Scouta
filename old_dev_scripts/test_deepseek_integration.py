#!/usr/bin/env python3
"""
Test de integración con DeepSeek
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_deepseek_analysis():
    """Test del análisis con DeepSeek"""
    print("🧪 TEST: Integración DeepSeek")
    
    try:
        from agents.deepseek_client import deepseek_client
        from config.ai_config import ai_config
        
        # Verificar configuración
        if not ai_config.is_available():
            print("❌ DeepSeek no configurado - añade DEEPSEEK_API_KEY al .env")
            print("💡 Obtén una API key en: https://platform.deepseek.com/")
            return False
        
        print("✅ DeepSeek configurado correctamente")
        
        # Probar análisis
        test_idea = "Quiero crear una aplicación móvil para delivery de comida con chat en tiempo real y sistema de pagos"
        
        print(f"💡 Analizando idea: {test_idea}")
        analysis = await deepseek_client.analyze_idea(test_idea)
        
        print("✅ Análisis completado:")
        print(f"   Tipo: {analysis.get('project_type')}")
        print(f"   Arquitectura: {analysis.get('architecture')}")
        print(f"   Stack: {analysis.get('recommended_stack')}")
        print(f"   Características: {analysis.get('features')}")
        print(f"   Complejidad: {analysis.get('complexity')}")
        print(f"   Semanas estimadas: {analysis.get('estimated_weeks')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_api_endpoint():
    """Test del endpoint de API"""
    print("\n🧪 TEST: Endpoint de API")
    
    import requests
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ai/analyze-idea",
            json={"idea": "Necesito un dashboard para analytics con gráficos en tiempo real"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Endpoint API: FUNCIONA")
                print(f"   AI Used: {result.get('ai_used')}")
                return True
            else:
                print(f"❌ Endpoint API falló: {result.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error API: {e}")
        return False

async def main():
    """Ejecutar todos los tests"""
    print("🚀 TESTEANDO INTEGRACIÓN DEEPSEEK")
    print("=" * 50)
    
    deepseek_ok = await test_deepseek_analysis()
    api_ok = await test_api_endpoint()
    
    print(f"\n📊 RESULTADOS:")
    print(f"   DeepSeek: {'✅ OK' if deepseek_ok else '❌ FALLIDO'}")
    print(f"   API: {'✅ OK' if api_ok else '❌ FALLIDO'}")
    
    if deepseek_ok and api_ok:
        print("🎉 ¡INTEGRACIÓN DEEPSEEK COMPLETADA!")
        print("\n🚀 FORGE SAAS AHORA INCLUYE:")
        print("   ✅ Análisis inteligente con DeepSeek")
        print("   ✅ Recomendaciones técnicas específicas")
        print("   ✅ Estimaciones de tiempo realistas")
        print("   ✅ Consideraciones arquitectónicas")
    else:
        print("⚠️  La integración necesita ajustes")

if __name__ == "__main__":
    asyncio.run(main())

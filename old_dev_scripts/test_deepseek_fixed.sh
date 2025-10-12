# test_deepseek_fixed.py
import asyncio
import os
import sys
from dotenv import load_dotenv

# Cargar .env explícitamente
load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_fixed_integration():
    """Test corregido de integración DeepSeek"""
    print("🧪 TEST CORREGIDO DEEPSEEK")
    print("=" * 40)
    
    # Verificar carga de .env primero
    api_key_from_env = os.getenv("DEEPSEEK_API_KEY")
    print(f"🔑 API Key desde .env: {api_key_from_env[:10]}..." if api_key_from_env else "❌ No encontrada")
    
    if not api_key_from_env:
        print("❌ ERROR: DEEPSEEK_API_KEY no encontrada en .env")
        return False
    
    try:
        # Importar después de cargar .env
        from config.ai_config import ai_config
        from agents.deepseek_client import deepseek_client
        
        print(f"🤖 ai_config disponible: {ai_config.is_available()}")
        print(f"🔧 Cliente API key: {deepseek_client.api_key[:10]}..." if deepseek_client.api_key else "❌ No configurada")
        
        if not ai_config.is_available():
            print("❌ ai_config no está disponible")
            return False
        
        # Test de análisis
        test_idea = "Una aplicación para gestionar tareas diarias"
        print(f"💡 Probando con: '{test_idea}'")
        
        analysis = await deepseek_client.analyze_idea(test_idea)
        
        if analysis and "project_type" in analysis:
            print("✅ ANÁLISIS EXITOSO!")
            print(f"   📊 Tipo: {analysis['project_type']}")
            print(f"   🏗️  Arquitectura: {analysis['architecture']}")
            print(f"   🛠️  Stack: {', '.join(analysis['recommended_stack'][:3])}")
            print(f"   ⚡ Complejidad: {analysis['complexity']}")
            return True
        else:
            print("❌ Análisis falló o usó fallback")
            return False
            
    except Exception as e:
        print(f"❌ Error durante el test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_integration())
    print("\n" + "=" * 40)
    print("🎯 RESULTADO FINAL:", "✅ ÉXITO" if success else "❌ FALLO")
    sys.exit(0 if success else 1)
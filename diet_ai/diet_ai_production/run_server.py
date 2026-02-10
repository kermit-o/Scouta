#!/usr/bin/env python3
"""
Run DietAI server
"""
import uvicorn
import sys
import os

sys.path.insert(0, '.')

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DIET AI - SERVIDOR INICIANDO")
    print("=" * 60)
    print("📊 Configuración:")
    
    from core.config import settings
    print(f"   • Proyecto: {settings.PROJECT_NAME}")
    print(f"   • Debug: {settings.DEBUG}")
    print(f"   • Base de datos: {settings.DATABASE_URL[:50]}...")
    
    print("\n🌐 Endpoints:")
    print(f"   • API Docs: http://localhost:8000/docs")
    print(f"   • Health: http://localhost:8000/health")
    print(f"   • OpenAPI: http://localhost:8000/openapi.json")
    
    print("\n" + "=" * 60)
    print("🛑 Presiona Ctrl+C para detener el servidor")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

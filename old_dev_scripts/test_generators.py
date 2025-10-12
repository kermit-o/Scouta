import sys
import os
sys.path.insert(0, '/workspaces/Scouta/forge_saas')

try:
    from backend.generators.fastapi_generator import FastAPIGenerator
    from backend.generators.react_generator import ReactGenerator
    from backend.generators.database_generator import DatabaseGenerator
    
    print("✅ Todos los generadores importados correctamente")
    
    # Probar generación de ejemplo
    test_spec = {
        "name": "test_project",
        "main_entities": [
            {
                "name": "User",
                "fields": [
                    {"name": "id", "type": "int", "primary_key": True},
                    {"name": "name", "type": "str"},
                    {"name": "email", "type": "str"}
                ]
            }
        ]
    }
    
    # Probar FastAPI generator
    fastapi_gen = FastAPIGenerator()
    fastapi_code = fastapi_gen.generate(test_spec)
    print(f"✅ FastAPI Generator: {len(fastapi_code)} archivos generados")
    
    # Probar React generator  
    react_gen = ReactGenerator()
    react_code = react_gen.generate(test_spec)
    print(f"✅ React Generator: {len(react_code)} archivos generados")
    
    print("🎉 Generadores listos para producción!")
    
except Exception as e:
    print(f"❌ Error en generadores: {e}")
    import traceback
    traceback.print_exc()

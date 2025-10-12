import sys
import os
sys.path.insert(0, '/workspaces/Scouta/forge_saas')

try:
    from core.services.ui_orchestrator_real import ui_orchestrator_real
    
    print("🧪 Probando generación REAL de proyecto...")
    
    # Test project
    test_data = {
        "project_name": "Test Real Project",
        "description": "Sistema de gestión de tareas con usuarios, proyectos, tareas y reportes. Debe tener autenticación y API REST.",
        "user_id": "test_user"
    }
    
    # Create project
    result = ui_orchestrator_real.create_project(test_data)
    
    if result["success"]:
        print(f"✅ Proyecto creado: {result['project_id']}")
        
        # Generate real project
        gen_result = ui_orchestrator_real.generate_real_project(result["project_id"])
        
        if gen_result["success"]:
            print(f"🎉 ¡PROYECTO REAL GENERADO!")
            print(f"   - Archivos: {gen_result['file_count']}")
            print(f"   - Descarga: {gen_result.get('download_path', 'N/A')}")
            print(f"   - Estado: {gen_result['status']}")
            
            # Check if download file exists
            if gen_result.get('download_path') and os.path.exists(gen_result['download_path']):
                file_size = os.path.getsize(gen_result['download_path'])
                print(f"   - Tamaño ZIP: {file_size} bytes")
                print("🚀 ¡Generación REAL exitosa!")
            else:
                print("⚠️  Archivo de descarga no encontrado")
        else:
            print(f"❌ Error en generación: {gen_result.get('error')}")
    else:
        print(f"❌ Error creando proyecto: {result.get('error')}")
        
except Exception as e:
    print(f"❌ Error en prueba: {e}")
    import traceback
    traceback.print_exc()

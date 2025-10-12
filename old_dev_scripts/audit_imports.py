# audit_imports.py

import os
import re

def audit_project_imports(root_dir="."):
    """Escanea el proyecto en busca de importaciones que necesitan ser actualizadas."""
    
    # Patrones que deben ser reemplazados después de la refactorización
    OLD_PATTERNS = [
        r"from\s+\.?\s*legacy_agents\s*import",
        r"from\s+\.?\s*app\.routes\s*import",
        r"import\s+\.?\s*planning_agent",
        r"from\s+\.?\s*services\.scheduler\s*import"
    ]
    
    # Archivos a ignorar durante el escaneo
    IGNORE_DIRS = ['.git', '.venv', '__pycache__', 'generated', 'migrations']
    
    files_to_update = {}

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Modificar dirnames in-place para ignorar directorios
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS]

        for filename in filenames:
            if filename.endswith(".py") or filename.endswith(".sh"): # Incluir scripts bash por si acaso
                filepath = os.path.join(dirpath, filename)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        found_patterns = []
                        for pattern in OLD_PATTERNS:
                            if re.search(pattern, content):
                                found_patterns.append(pattern)
                        
                        if found_patterns:
                            files_to_update[filepath] = found_patterns
                            
                except Exception as e:
                    print(f"Error leyendo {filepath}: {e}")

    return files_to_update

if __name__ == "__main__":
    print("🚀 Iniciando Auditoría de Importaciones...")
    
    # Escanear solo el directorio 'backend' y la raíz del proyecto
    audit_results = audit_project_imports(root_dir="./backend")
    
    if audit_results:
        print("\n--- ⚠️ ARCHIVOS QUE NECESITAN ACTUALIZACIÓN DE IMPORTS ⚠️ ---")
        
        for file, patterns in audit_results.items():
            print(f"\nArchivo: {file}")
            print("  Patrones antiguos encontrados:")
            
            for pattern in patterns:
                # Ejemplo de cómo sería el reemplazo
                if "legacy_agents" in pattern:
                    print(f"  - Debería cambiarse: {re.search(r'legacy_agents\s*import\s*(\w+)', content).group(1) if re.search(r'legacy_agents\s*import\s*(\w+)', content) else 'N/A'} (Ahora en app.agents)")
                elif "app\.routes" in pattern:
                    print("  - 'app.routes' -> 'app.routers'")
                elif "planning_agent" in pattern:
                    print("  - 'planning_agent' (raíz de app) -> 'app.agents.planning_agent'")
                elif "scheduler" in pattern:
                     print("  - 'services.scheduler' -> 'services.scheduler_service'")
                        
    else:
        print("\n🎉 ¡Auditoría Completa! No se encontraron importaciones antiguas en el backend.")
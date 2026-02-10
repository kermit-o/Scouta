import os
import re

# Mapeo de imports viejos a nuevos
IMPORT_MAPPINGS = {
    # Backend imports
    "from ": "from ",
    "from ": "from ",
    
    # Core imports específicos
    "from core.": "from core.",
    "from services.": "from services.",
    "from utils.": "from utils.", 
    "from models.": "from models.",
    "from config.": "from config.",
    "from api.": "from api.",
    "from core.auth.auth": "from core.auth.auth",
    "from core.auth.user_manager": "from core.auth.user_manager",
    
    # Database imports
    "from core.database.": "from core.database.",
    "from core.database.": "from core.database.",
    
    # Agents imports
    "from agents.": "from core.agents.",
    "from core.agents.": "from core.agents.",
    
    # Config imports
    "from config.": "from config.",
    "from config.": "from config.",
}

def fix_imports_in_file(filepath):
    """Corrige imports en un archivo específico"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Aplicar mapeos
        for old, new in IMPORT_MAPPINGS.items():
            content = content.replace(old, new)
        
        # Si el contenido cambió, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Corregido: {filepath}")
            return True
        
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
    
    return False

def fix_all_imports():
    """Corrige imports en todos los archivos Python"""
    fixed_count = 0
    total_files = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                total_files += 1
                if fix_imports_in_file(filepath):
                    fixed_count += 1
    
    print(f"\n✅ Corrección completada: {fixed_count}/{total_files} archivos modificados")

if __name__ == "__main__":
    fix_all_imports()

import os
import re

def fix_database_imports(filepath):
    """Corrige imports de database"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir imports de database
        content = content.replace('from core.database', 'from core.database')
        content = content.replace('from models', 'from models')
        content = content.replace('from core.database', 'from core.database')
        
        # Si el contenido cambió, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Database imports corregidos: {filepath}")
            return True
            
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
    
    return False

def fix_auth_imports(filepath):
    """Corrige imports específicos de auth"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Corregir imports de auth manager
        content = content.replace('from core.auth.auth import AuthManager', 'from core.auth.auth import AuthManager')
        content = content.replace('from core.auth.auth import AuthManager', 'from core.auth.auth import AuthManager')
        
        # Si el contenido cambió, guardar
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Auth imports corregidos: {filepath}")
            return True
            
    except Exception as e:
        print(f"✗ Error en {filepath}: {e}")
    
    return False

def fix_all_files():
    """Corrige todos los archivos"""
    fixed_count = 0
    
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_database_imports(filepath):
                    fixed_count += 1
                if fix_auth_imports(filepath):
                    fixed_count += 1
    
    print(f"\n✅ Corrección completada: {fixed_count} archivos modificados")

if __name__ == "__main__":
    fix_all_files()

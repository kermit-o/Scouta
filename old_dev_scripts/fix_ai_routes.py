import re

# Leer el archivo main.py actual
with open('backend/app/main.py', 'r') as f:
    content = f.read()

# Verificar si ya tiene las rutas AI
if 'ai_bp' in content and 'ai_analysis' in content:
    print("✅ Las rutas AI ya están en main.py")
else:
    print("🔧 Agregando rutas AI a main.py...")
    
    # Encontrar donde agregar los imports (después de los imports existentes)
    lines = content.split('\n')
    new_lines = []
    imports_added = False
    registration_added = False
    
    for line in lines:
        new_lines.append(line)
        
        # Agregar import después de otros imports de routes
        if 'from app.routes.' in line and not imports_added:
            new_lines.append('from app.routes.ai_analysis import ai_bp')
            imports_added = True
            
        # Agregar registro después de otros blueprints
        if 'app.register_blueprint' in line and not registration_added:
            new_lines.append('app.register_blueprint(ai_bp)')
            registration_added = True
    
    # Si no se encontraron los puntos de inserción, agregar al final de los imports
    if not imports_added:
        # Buscar el último import y agregar después
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                continue
            else:
                # Insertar antes de la primera línea que no es import
                lines.insert(i, 'from app.routes.ai_analysis import ai_bp')
                break
        new_lines = lines
    
    if not registration_added:
        # Buscar donde agregar el registro (después de app = Flask)
        for i, line in enumerate(new_lines):
            if 'app = Flask' in line:
                # Encontrar el final de las configuraciones
                for j in range(i+1, len(new_lines)):
                    if 'app.register_blueprint' in new_lines[j]:
                        # Insertar después del primer blueprint
                        new_lines.insert(j+1, 'app.register_blueprint(ai_bp)')
                        registration_added = True
                        break
                break
    
    # Escribir el archivo corregido
    with open('backend/app/main.py', 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("✅ Rutas AI agregadas a main.py")

print("\n📋 Resumen de cambios:")
with open('backend/app/main.py', 'r') as f:
    content = f.read()
    if 'ai_bp' in content:
        print("✅ ai_bp encontrado en main.py")
    if 'ai_analysis' in content:
        print("✅ ai_analysis encontrado en main.py")
    if 'app.register_blueprint(ai_bp)' in content:
        print("✅ Registro de ai_bp encontrado")

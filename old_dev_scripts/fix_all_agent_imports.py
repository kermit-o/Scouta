import os
import glob

# Encontrar todos los archivos Python
python_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py') and '__pycache__' not in root:
            python_files.append(os.path.join(root, file))

# Corregir imports en cada archivo
fixed_files = []
for file_path in python_files:
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Verificar si tiene imports incorrectos
        if 'from core.app.agents' in content:
            # Corregir el import
            new_content = content.replace('from core.app.agents', 'from core.app.agents')
            
            # Escribir el archivo corregido
            with open(file_path, 'w') as f:
                f.write(new_content)
            
            fixed_files.append(file_path)
            print(f"✅ Corregido: {file_path}")
            
    except Exception as e:
        print(f"❌ Error en {file_path}: {e}")

print(f"\n🎉 Total de archivos corregidos: {len(fixed_files)}")
if fixed_files:
    print("Archivos corregidos:")
    for f in fixed_files:
        print(f"  - {f}")

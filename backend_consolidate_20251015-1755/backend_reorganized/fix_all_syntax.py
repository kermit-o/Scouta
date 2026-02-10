import re

# Leer el archivo
with open('services/smart_deepseek_client.py', 'r') as f:
    lines = f.readlines()

# Buscar y corregir f-strings problemáticos
corrected_lines = []
for i, line in enumerate(lines, 1):
    if 'Funcionalidad implementada' in line:
        print(f"🔧 Corrigiendo línea {i}: {line.strip()}")
        # Corregir las llaves anidadas
        line = line.replace("})}}>", "})}>")
        print(f"   Corregido: {line.strip()}")
    corrected_lines.append(line)

# Escribir archivo corregido
with open('services/smart_deepseek_client.py', 'w') as f:
    f.writelines(corrected_lines)

print("✅ Todas las líneas corregidas")

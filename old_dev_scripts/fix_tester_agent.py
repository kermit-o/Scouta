# Agregar import de uuid en tester_agent.py
with open('core/app/agents/tester_agent.py', 'r') as f:
    content = f.read()

# Agregar import uuid si no existe
if 'import uuid' not in content:
    # Buscar dónde agregar el import (después de los otros imports)
    lines = content.split('\n')
    new_lines = []
    imports_added = False
    
    for line in lines:
        new_lines.append(line)
        # Agregar import uuid después de los imports existentes
        if not imports_added and line.startswith('from ') and 'import' in line and 'uuid' not in line:
            # Encontrar el final de los imports
            next_lines = lines[lines.index(line) + 1:]
            if next_lines and (not next_lines[0].startswith(('from ', 'import')) or next_lines[0].strip() == ''):
                new_lines.append('import uuid  # CORREGIDO: import faltante')
                imports_added = True
    
    # Si no se encontró lugar, agregar al principio después de docstring
    if not imports_added:
        for i, line in enumerate(new_lines):
            if line.strip() and not line.startswith('"""') and not line.startswith("'''"):
                new_lines.insert(i, 'import uuid  # CORREGIDO: import faltante')
                break
    
    content = '\n'.join(new_lines)

with open('core/app/agents/tester_agent.py', 'w') as f:
    f.write(content)

print("✅ tester_agent.py corregido - import uuid agregado")

# Script para corregir el error de sintaxis en el f-string
import re

with open('services/smart_deepseek_client.py', 'r') as f:
    content = f.read()

# Encontrar y corregir el f-string problemático
# La línea 698 tiene un f-string con llaves anidadas incorrectas
pattern = r"<button onClick={() => console\.log\('Funcionalidad implementada'\)}}>"

# Reemplazar con la versión corregida
replacement = '''<button onClick={() => console.log('Funcionalidad implementada')}>'''

content_corrected = re.sub(pattern, replacement, content)

# Escribir el archivo corregido
with open('services/smart_deepseek_client.py', 'w') as f:
    f.write(content_corrected)

print("✅ Error de sintaxis corregido")

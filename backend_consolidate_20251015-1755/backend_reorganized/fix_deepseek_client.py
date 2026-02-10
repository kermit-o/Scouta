# Script para corregir el error toLowerCase en robust_deepseek_client.py

with open('services/robust_deepseek_client.py', 'r') as f:
    content = f.read()

# Reemplazar toLowerCase() por lower()
content_fixed = content.replace("toLowerCase()", "lower()")

# Escribir el archivo corregido
with open('services/robust_deepseek_client.py', 'w') as f:
    f.write(content_fixed)

print("✅ Error toLowerCase corregido - cambiado a lower()")

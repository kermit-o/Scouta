# Leer backend_final.py
with open('backend_final.py', 'r') as f:
    content = f.read()

# Corregir el path del endpoint AI
old_path = '@app.post("/api/v1/ai/analyze")'
new_path = '@app.post("/api/v1/ai/analyze-idea")'

if old_path in content:
    content = content.replace(old_path, new_path)
    print("✅ Path del endpoint AI corregido: /api/v1/ai/analyze-idea")
else:
    print("❌ No se encontró el path a corregir")

# Escribir archivo corregido
with open('backend_final.py', 'w') as f:
    f.write(content)

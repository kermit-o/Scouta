# Leer el archivo actual
with open('backend_final.py', 'r') as f:
    content = f.read()

# Reemplazar solo la línea problemática
old_line = '@app.post("/api/v1/ai/analyze")'
new_line = '@app.api_route("/api/v1/ai/analyze", methods=["GET", "POST"])'

if old_line in content:
    content = content.replace(old_line, new_line)
    print("✅ Endpoint AI corregido para aceptar GET y POST")
else:
    print("❌ No se encontró la línea a corregir")

# Escribir el archivo corregido
with open('backend_final.py', 'w') as f:
    f.write(content)

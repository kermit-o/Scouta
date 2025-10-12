import re

# Leer models.py
with open('core/database/models.py', 'r') as f:
    content = f.read()

# Verificar si las columnas usan UUID correctamente
if "Column(UUID" not in content:
    print("❌ Las columnas no están usando UUID - necesitan corrección")
    
    # Buscar definiciones de columnas ID
    id_columns = re.findall(r'id = Column\([^)]+\)', content)
    print("Definiciones de columnas id encontradas:")
    for col in id_columns:
        print(" ", col)
        
    # Sugerir corrección
    print("\n💡 Las columnas id deberían usar: Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)")
else:
    print("✅ Modelos ya usan UUID correctamente")

# Mostrar primeras líneas de cada definición de clase
classes = re.findall(r'class \w+\(.*?\):.*?(?=class|\Z)', content, re.DOTALL)
for cls in classes[:3]:
    lines = cls.split('\n')[:10]
    print("\nClase:", lines[0])
    for line in lines[1:6]:
        if 'id = Column' in line or 'class' in line:
            print(" ", line.strip())

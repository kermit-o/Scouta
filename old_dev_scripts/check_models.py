import re

# Leer models.py
with open('core/database/models.py', 'r') as f:
    content = f.read()

# Verificar que use UUID de PostgreSQL correctamente
if "UUID(as_uuid=True)" in content and "from sqlalchemy.dialects.postgresql import UUID" in content:
    print("✅ Modelos configurados correctamente para PostgreSQL")
else:
    print("❌ Los modelos necesitan ajustes para PostgreSQL")
    
# Mostrar imports
imports = re.findall(r'^from.*$', content, re.MULTILINE)
print("Imports encontrados:")
for imp in imports[:10]:
    print(" ", imp)

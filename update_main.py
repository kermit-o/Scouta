# Script para actualizar main.py
import re

with open('main.py', 'r') as f:
    content = f.read()

# Reemplazar la importación problemática de payments
new_content = content.replace(
    'from core.app.routers import payments', 
    'from core.app.routers.payments_fixed import router as payments_router'
)

# Reemplazar la línea de include_router
new_content = new_content.replace(
    'app.include_router(payments.router, prefix="/api/v1")',
    'app.include_router(payments_router, prefix="/api/v1")'
)

with open('main.py', 'w') as f:
    f.write(new_content)

print("✅ main.py actualizado para usar payments_fixed")

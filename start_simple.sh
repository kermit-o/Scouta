#!/bin/bash
echo "🚀 Iniciando Forge SaaS - Modo Simple"
echo "======================================"

# Instalar dependencias críticas si faltan
pip install stripe > /dev/null 2>&1 && echo "✅ Stripe instalado"

# Verificar dependencias
python -c "import stripe, sqlalchemy, fastapi" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Todas las dependencias OK"
else
    echo "❌ Faltan dependencias - instalando..."
    pip install -r requirements.txt
fi

# Iniciar servidor
echo "🌐 Iniciando servidor en http://localhost:8001"
python main.py

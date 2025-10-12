#!/bin/bash

echo "🚀 Iniciando Forge SaaS AI Dashboard..."
echo "📁 Directorio: /workspaces/Scouta/forge_saas"

cd /workspaces/Scouta/forge_saas

# Set Python path
export PYTHONPATH="/workspaces/Scouta/forge_saas:$PYTHONPATH"

echo "🔧 Configurando entorno Python..."
python -c "import sys; print('Python path:', sys.path[:2])"

echo "🌐 Iniciando Streamlit Dashboard..."
streamlit run ui/dashboard_simple.py

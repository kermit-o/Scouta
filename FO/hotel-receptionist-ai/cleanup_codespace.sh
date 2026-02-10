#!/bin/bash

echo "🧹 INICIANDO LIMPIEZA DE CODESPACE 🧹"
echo "======================================"

# 1. Docker
echo "🗑️  Limpiando Docker..."
docker system prune -a --volumes --force 2>/dev/null || true

# 2. Python
echo "🐍 Limpiando Python..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete
rm -rf ~/.cache/pip 2>/dev/null

# 3. Node
echo "📦 Limpiando Node.js..."
npm cache clean --force 2>/dev/null || true

# 4. Sistema
echo "⚙️  Limpiando sistema..."
sudo apt-get clean 2>/dev/null || true
sudo apt-get autoclean 2>/dev/null || true

# 5. Logs y temporales
echo "📝 Limpiando logs..."
find . -name "*.log" -type f -size +1M -delete 2>/dev/null
find . -name "*.tmp" -type f -delete 2>/dev/null

# 6. Proyecto específico
echo "🎯 Limpiando proyecto..."
rm -rf .next build dist *.egg-info 2>/dev/null

# Mostrar espacio liberado
echo ""
echo "✅ LIMPIEZA COMPLETADA"
echo "======================================"
df -h | grep "/workspaces"

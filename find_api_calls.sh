#!/bin/bash

# Directorio donde se encuentra el código frontend
FRONTEND_DIR="./frontend"

# Patrones a buscar: 'getProjects' o 'createProject'
PATTERNS="getProjects|createProject"

echo "--- 🔎 Buscando archivos que llaman a '$PATTERNS' en $FRONTEND_DIR ---"
echo "--- Excluyendo 'node_modules' por velocidad ---"
echo ""

# Utiliza 'grep' de forma recursiva (r) e insensible a mayúsculas/minúsculas (i)
# La opción --include filtra solo archivos .ts y .tsx (o .js/.jsx si los usas)
# La opción --exclude-dir excluye el directorio node_modules
grep -r -i \
    --include=\*.{ts,tsx,js,jsx} \
    --exclude-dir=node_modules \
    --color=always \
    -e "$PATTERNS" \
    "$FRONTEND_DIR"

echo ""
echo "--- ✅ Búsqueda completada. ---"
echo "Los archivos listados deben ser modificados para usar 'ProjectAPI.list()' y 'ProjectAPI.create()'."
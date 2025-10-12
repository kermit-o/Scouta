#!/bin/bash

# ===============================================
# SCRIPT: create_ui_structure.sh
# DESCRIPCIÓN: Crea la estructura de directorios y archivos base para el frontend Next.js.
# ===============================================

# Variables
UI_DIR="ui"
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN} Iniciando creación de la estructura del Frontend (Next.js) ${NC}"
echo -e "${CYAN}======================================================${NC}\n"

# 1. Crear el directorio principal si no existe
if [ -d "$UI_DIR" ]; then
    echo -e "${YELLOW}Advertencia: El directorio '$UI_DIR/' ya existe. Continuando...${NC}"
else
    mkdir "$UI_DIR"
    echo -e "${GREEN}✅ Directorio '$UI_DIR/' creado.${NC}"
fi

# Navegar al directorio 'ui'
cd "$UI_DIR"

# 2. Crear todos los directorios anidados con -p (modo recursivo)
echo -e "${CYAN}Creando directorios...${NC}"

mkdir -p app/{'(auth)'/{login,signup},'(app)'/{dashboard,create,billing},'(app)'/project/'[id]'}
mkdir -p components/{ui,Layout,Auth,Agent,Project}

echo -e "${GREEN}✅ Directorios de Next.js y componentes creados.${NC}"

# 3. Crear archivos de configuración base (vacíos o con placeholders)
echo -e "${CYAN}Creando archivos de configuración...${NC}"

# Archivos de configuración
touch next.config.mjs postcss.config.js tailwind.config.ts package.json

# Archivo de entorno crucial
echo -e "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo -e "${GREEN}✅ Archivos de configuración creados (.env.local llenado con API_URL).${NC}"

# 4. Crear archivos .tsx y .css (marcadores de posición)
echo -e "${CYAN}Creando archivos de rutas y estilos...${NC}"

# Archivos de App Router
touch app/layout.tsx
touch app/globals.css
touch app/page.tsx # Landing Page

# Rutas de Autenticación
touch app/'(auth)'/login/page.tsx
touch app/'(auth)'/signup/page.tsx

# Rutas Protegidas (Dashboard)
touch app/'(app)'/layout.tsx # Layout de rutas protegidas
touch app/'(app)'/dashboard/page.tsx
touch app/'(app)'/create/page.tsx
touch app/'(app)'/billing/page.tsx
touch app/'(app)'/project/'[id]'/page.tsx

# Archivos de Componentes clave (marcadores de posición .tsx)
touch components/Auth/AuthProvider.tsx
touch components/Agent/PromptEditor.tsx
touch components/Project/CodeEditor.tsx
touch components/Layout/Navbar.tsx

echo -e "${GREEN}✅ Archivos de rutas y componentes creados.${NC}"

echo -e "\n${CYAN}======================================================${NC}"
echo -e "${GREEN}🎉 ESTRUCTURA DE UI CREADA CON ÉXITO en './ui'${NC}"
echo -e "======================================================${NC}"
echo -e "${YELLOW}NOTA IMPORTANTE:${NC} Ahora debe ejecutar los comandos de instalación de Next.js y Tailwind (npm install, npx tailwindcss init, etc.)."

cd ..
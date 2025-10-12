#!/bin/bash

# project_scanner.sh - Escanea estructura de proyectos excluyendo system files y dependencias

# Colores para mejor visualización
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuración
PROJECT_DIR="${1:-.}"
OUTPUT_FILE="${2:-project_structure.txt}"
MAX_DEPTH=6

# Patrones para excluir (archivos del sistema y dependencias)
EXCLUDE_PATTERNS=(
    "node_modules" ".git" "__pycache__" ".vscode" ".idea" "dist" "build"
    "*.log" "*.tmp" "*.temp" ".DS_Store" "Thumbs.db" "*.swp" "*.swo"
    "package-lock.json" "yarn.lock" "*.min.js" "*.min.css"
    ".env" ".env.local" ".env.production" ".npm" ".cache"
    "coverage" ".nyc_output" "*.seed" "*.sqlite" "*.db"
)

# Función para generar tree con exclusiones
generate_project_tree() {
    local dir="$1"
    local depth="${2:-0}"
    local prefix="${3:-}"
    
    # Solo mostrar hasta MAX_DEPTH niveles
    if [ $depth -gt $MAX_DEPTH ]; then
        return
    fi
    
    # Leer elementos del directorio, excluyendo patrones
    local items=()
    while IFS= read -r -d $'\0' item; do
        local exclude=0
        for pattern in "${EXCLUDE_PATTERNS[@]}"; do
            if [[ "$(basename "$item")" == $pattern ]] || 
               [[ "$item" == *"/$pattern"* ]] ||
               [[ "$(basename "$item")" == .* && "$pattern" == \.* ]]; then
                exclude=1
                break
            fi
        done
        
        if [ $exclude -eq 0 ]; then
            items+=("$item")
        fi
    done < <(find "$dir" -maxdepth 1 -mindepth 1 -print0 2>/dev/null | sort -z)
    
    local count=${#items[@]}
    local i=0
    
    for item in "${items[@]}"; do
        i=$((i + 1))
        local name=$(basename "$item")
        
        # Determinar el prefijo visual
        if [ $i -eq $count ]; then
            echo -e "${prefix}└── ${get_file_color "$item"}${name}${NC}"
            local new_prefix="${prefix}    "
        else
            echo -e "${prefix}├── ${get_file_color "$item"}${name}${NC}"
            local new_prefix="${prefix}│   "
        fi
        
        # Si es directorio, llamar recursivamente
        if [ -d "$item" ]; then
            generate_project_tree "$item" $((depth + 1)) "$new_prefix"
        fi
    done
}

# Función para colorear según tipo de archivo
get_file_color() {
    local file="$1"
    
    if [ -d "$file" ]; then
        echo -e "${BLUE}"  # Directorios en azul
    elif [ -x "$file" ]; then
        echo -e "${GREEN}"  # Ejecutables en verde
    elif [[ "$file" == *.js ]] || [[ "$file" == *.jsx ]]; then
        echo -e "${YELLOW}"  # JavaScript en amarillo
    elif [[ "$file" == *.ts ]] || [[ "$file" == *.tsx ]]; then
        echo -e "${CYAN}"  # TypeScript en cian
    elif [[ "$file" == *.py ]]; then
        echo -e "${GREEN}"  # Python en verde
    elif [[ "$file" == *.java ]]; then
        echo -e "${RED}"  # Java en rojo
    elif [[ "$file" == *.html ]] || [[ "$file" == *.htm ]]; then
        echo -e "${PURPLE}"  # HTML en morado
    elif [[ "$file" == *.css ]] || [[ "$file" == *.scss ]]; then
        echo -e "${PURPLE}"  # CSS en morado
    elif [[ "$file" == *.json ]]; then
        echo -e "${YELLOW}"  # JSON en amarillo
    elif [[ "$file" == *.md ]] || [[ "$file" == *.txt ]]; then
        echo -e "${CYAN}"  # Documentación en cian
    else
        echo -e "${NC}"  # Por defecto sin color
    fi
}

# Función para analizar tecnologías del proyecto
detect_technologies() {
    echo -e "\n${PURPLE}🔍 TECNOLOGÍAS DETECTADAS:${NC}"
    
    if [ -f "package.json" ]; then
        echo -e "${GREEN}📦 Node.js Project${NC}"
        if [ -f "package.json" ]; then
            echo -e "   Dependencies:"
            jq -r '.dependencies | keys[]' package.json 2>/dev/null | head -5 | while read dep; do
                echo -e "   - ${YELLOW}$dep${NC}"
            done
        fi
    fi
    
    if [ -f "requirements.txt" ] || [ -f "Pipfile" ] || [ -f "pyproject.toml" ]; then
        echo -e "${GREEN}🐍 Python Project${NC}"
    fi
    
    if [ -f "pom.xml" ]; then
        echo -e "${RED}☕ Java Project${NC}"
    fi
    
    if [ -f "composer.json" ]; then
        echo -e "${BLUE}🐘 PHP Project${NC}"
    fi
    
    if [ -f "go.mod" ]; then
        echo -e "${CYAN}🐹 Go Project${NC}"
    fi
    
    if [ -f "Cargo.toml" ]; then
        echo -e "${RED}🦀 Rust Project${NC}"
    fi
}

# Función para mostrar estadísticas
show_statistics() {
    echo -e "\n${PURPLE}📊 ESTADÍSTICAS DEL PROYECTO:${NC}"
    
    local total_files=$(find "$PROJECT_DIR" -type f ! -name ".*" | grep -v node_modules | grep -v .git | wc -l)
    local total_dirs=$(find "$PROJECT_DIR" -type d ! -name ".*" | grep -v node_modules | grep -v .git | wc -l)
    local js_files=$(find "$PROJECT_DIR" -name "*.js" -o -name "*.jsx" 2>/dev/null | wc -l)
    local ts_files=$(find "$PROJECT_DIR" -name "*.ts" -o -name "*.tsx" 2>/dev/null | wc -l)
    local py_files=$(find "$PROJECT_DIR" -name "*.py" 2>/dev/null | wc -l)
    local css_files=$(find "$PROJECT_DIR" -name "*.css" -o -name "*.scss" 2>/dev/null | wc -l)
    
    echo -e "Total archivos: ${GREEN}$total_files${NC}"
    echo -e "Total directorios: ${BLUE}$total_dirs${NC}"
    echo -e "JavaScript/JSX: ${YELLOW}$js_files${NC}"
    echo -e "TypeScript/TSX: ${CYAN}$ts_files${NC}"
    echo -e "Python: ${GREEN}$py_files${NC}"
    echo -e "CSS/SCSS: ${PURPLE}$css_files${NC}"
}

# MAIN EXECUTION
echo -e "${BLUE}🌳 ESCANEANDO ESTRUCTURA DEL PROYECTO...${NC}"
echo -e "Directorio: ${GREEN}$(realpath "$PROJECT_DIR")${NC}"
echo -e "Excluyendo: ${YELLOW}node_modules, .git, cache files, dependencies${NC}\n"

# Generar tree structure
generate_project_tree "$PROJECT_DIR"

# Mostrar tecnologías detectadas
detect_technologies

# Mostrar estadísticas
show_statistics

# Guardar en archivo si se solicita
if [ "$OUTPUT_FILE" != "none" ]; then
    {
        echo "PROJECT STRUCTURE - $(date)"
        echo "Directory: $(realpath "$PROJECT_DIR")"
        echo "=========================================="
        generate_project_tree "$PROJECT_DIR"
        echo ""
        detect_technologies
        show_statistics
    } > "$OUTPUT_FILE"
    echo -e "\n${GREEN}✅ Estructura guardada en: $OUTPUT_FILE${NC}"
fi

echo -e "\n${GREEN}🎯 TIP: Usa 'cat project_structure.txt' para ver el resultado${NC}"

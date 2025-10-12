#!/bin/bash

# Script para levantar todo el sistema Scouta/Forge SaaS
# Backend, Servidor y UI

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Funciones de logging
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

# Función para mostrar header
section_header() {
    echo ""
    echo "=================================================="
    echo "$1"
    echo "=================================================="
    echo ""
}

# Función para verificar dependencias
check_dependencies() {
    section_header "VERIFICANDO DEPENDENCIAS"
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker no está instalado"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose no está instalado"
        exit 1
    fi
    
    log_success "✓ Docker verificado"
    
    # Verificar que el archivo docker-compose.yml existe
    if [ ! -f "docker-compose.yml" ] && [ ! -f "docker-compose.yaml" ]; then
        log_error "No se encuentra docker-compose.yml"
        exit 1
    fi
    
    log_success "✓ docker-compose.yml encontrado"
}

# Función para limpiar servicios previos
cleanup_previous() {
    section_header "LIMPIANDO SERVICIOS PREVIOS"
    
    log_info "Deteniendo servicios existentes..."
    docker compose down 2>/dev/null || true
    
    log_info "Limpiando contenedores huérfanos..."
    docker system prune -f 2>/dev/null || true
    
    log_success "Limpieza completada"
}

# Función para construir imágenes
build_images() {
    section_header "CONSTRUYENDO IMÁGENES DOCKER"
    
    log_info "Construyendo imágenes (esto puede tomar unos minutos)..."
    
    if docker compose build --no-cache; then
        log_success "✓ Imágenes construidas correctamente"
    else
        log_error "✗ Error construyendo imágenes"
        exit 1
    fi
}

# Función para levantar base de datos y servicios de apoyo
start_dependencies() {
    section_header "INICIANDO SERVICIOS DE APOYO"
    
    log_step "1. Iniciando base de datos..."
    if docker compose up -d db; then
        log_success "✓ Base de datos iniciada"
    else
        log_error "✗ Error iniciando base de datos"
        exit 1
    fi
    
    # Esperar a que la base de datos esté lista
    log_info "Esperando a que la base de datos esté lista..."
    sleep 10
    
    # Verificar si hay Redis en la configuración
    if grep -q "redis:" docker-compose.yml 2>/dev/null || grep -q "redis:" docker-compose.yaml 2>/dev/null; then
        log_step "2. Iniciando Redis..."
        docker compose up -d redis
        log_success "✓ Redis iniciado"
        sleep 2
    else
        log_info "Redis no configurado, omitiendo..."
    fi
    
    # Verificar si hay otros servicios de apoyo
    if grep -q "queue\|worker\|celery" docker-compose.yml 2>/dev/null || grep -q "queue\|worker\|celery" docker-compose.yaml 2>/dev/null; then
        log_step "3. Iniciando servicios de cola..."
        docker compose up -d queue worker
        log_success "✓ Servicios de cola iniciados"
    fi
}

# Función para aplicar migraciones de base de datos
run_migrations() {
    section_header "APLICANDO MIGRACIONES DE BASE DE DATOS"
    
    log_info "Ejecutando migraciones..."
    
    if docker compose exec -T backend alembic upgrade head 2>/dev/null || \
       docker compose exec -T backend python -m alembic upgrade head 2>/dev/null || \
       docker compose exec -T backend python -c "
from app.db import engine
from app.models import Base
Base.metadata.create_all(bind=engine)
print('✓ Tablas creadas correctamente')
" 2>/dev/null; then
        log_success "✓ Migraciones aplicadas correctamente"
    else
        log_warn "⚠ No se pudieron aplicar migraciones automáticamente"
        log_info "Puedes aplicar migraciones manualmente después con:"
        log_info "docker compose exec backend alembic upgrade head"
    fi
}

# Función para levantar el backend
start_backend() {
    section_header "INICIANDO BACKEND"
    
    log_step "1. Iniciando servidor backend..."
    if docker compose up -d backend; then
        log_success "✓ Backend iniciado"
    else
        log_error "✗ Error iniciando backend"
        exit 1
    fi
    
    # Esperar a que el backend esté listo
    log_step "2. Esperando a que el backend esté listo..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -fs http://localhost:8000/api/health >/dev/null 2>&1; then
            log_success "✓ Backend respondiendo correctamente"
            break
        fi
        
        log_info "Intento $attempt/$max_attempts - Esperando..."
        sleep 5
        ((attempt++))
        
        if [ $attempt -gt $max_attempts ]; then
            log_error "✗ Backend no respondió después de $max_attempts intentos"
            log_info "Revisando logs del backend..."
            docker compose logs backend --tail=20
            exit 1
        fi
    done
    
    # Mostrar información del backend
    log_step "3. Información del backend:"
    echo "   URL: http://localhost:8000"
    echo "   API Health: http://localhost:8000/api/health"
    echo "   Documentación: http://localhost:8000/docs"
    echo "   Admin: http://localhost:8000/admin"
}

# Función para levantar el frontend/UI
start_frontend() {
    section_header "INICIANDO FRONTEND/UI"
    
    # Verificar si existe un servicio frontend en docker-compose
    if grep -q "frontend\|ui\|web\|client" docker-compose.yml 2>/dev/null || grep -q "frontend\|ui\|web\|client" docker-compose.yaml 2>/dev/null; then
        log_step "1. Iniciando frontend con Docker..."
        docker compose up -d frontend
        
        # Esperar a que el frontend esté listo
        log_step "2. Esperando a que el frontend esté listo..."
        sleep 15
        
        if curl -fs http://localhost:3000 >/dev/null 2>&1 || curl -fs http://localhost:8080 >/dev/null 2>&1; then
            log_success "✓ Frontend iniciado correctamente"
        else
            log_warn "⚠ Frontend iniciado pero no responde inmediatamente"
        fi
        
        log_step "3. Información del frontend:"
        echo "   URL: http://localhost:3000 (o puerto configurado en docker-compose)"
        
    else
        log_info "No se encontró servicio frontend en docker-compose"
        log_info "Buscando directorio frontend/ para desarrollo..."
        
        # Buscar directorio frontend
        if [ -d "frontend" ]; then
            log_step "1. Iniciando frontend en modo desarrollo..."
            log_info "Directorio frontend encontrado"
            log_info "Para desarrollo frontend, ejecuta manualmente:"
            echo ""
            echo "cd frontend"
            echo "npm install && npm run dev"
            echo "# o"
            echo "yarn install && yarn dev"
            echo ""
        elif [ -d "ui" ]; then
            log_step "1. Iniciando UI en modo desarrollo..."
            log_info "Directorio ui encontrado"
            log_info "Para desarrollo UI, ejecuta manualmente:"
            echo ""
            echo "cd ui"
            echo "npm install && npm run dev"
            echo "# o"
            echo "yarn install && yarn dev"
            echo ""
        else
            log_warn "No se encontró directorio frontend/ ni ui/"
            log_info "El frontend puede estar integrado en el backend o no configurado"
        fi
    fi
}

# Función para levantar servicios adicionales
start_additional_services() {
    section_header "INICIANDO SERVICIOS ADICIONALES"
    
    # Buscar y levantar otros servicios
    local additional_services=$(grep -E "^  [a-zA-Z]+:" docker-compose.yml 2>/dev/null | grep -vE "backend|db|redis|frontend|ui|web|client|queue|worker" | sed 's/^  //; s/://' | tr '\n' ' ' || echo "")
    
    if [ ! -z "$additional_services" ]; then
        log_info "Servicios adicionales encontrados: $additional_services"
        
        for service in $additional_services; do
            log_step "Iniciando $service..."
            if docker compose up -d "$service"; then
                log_success "✓ $service iniciado"
            else
                log_warn "⚠ Error iniciando $service"
            fi
        done
    else
        log_info "No se encontraron servicios adicionales"
    fi
}

# Función para mostrar resumen final
show_summary() {
    section_header "🎉 SISTEMA LEVANTADO EXITOSAMENTE"
    
    log_success "Todos los servicios están en ejecución:"
    echo ""
    
    # Mostrar estado de contenedores
    log_info "Estado de los servicios:"
    docker compose ps
    
    echo ""
    log_info "📋 URLs DE ACCESO:"
    echo ""
    
    # Backend URLs
    echo "   🔧 BACKEND:"
    echo "      API:          http://localhost:8000"
    echo "      Health Check: http://localhost:8000/api/health"
    echo "      Documentación: http://localhost:8000/docs"
    echo "      Admin Panel:   http://localhost:8000/admin"
    echo ""
    
    # Frontend URLs
    if docker compose ps | grep -q "frontend"; then
        echo "   🎨 FRONTEND:"
        echo "      Aplicación: http://localhost:3000"
        echo ""
    elif docker compose ps | grep -q "ui"; then
        echo "   🎨 UI:"
        echo "      Aplicación: http://localhost:8080"
        echo ""
    else
        echo "   🎨 FRONTEND: (modo desarrollo - ejecutar manualmente)"
        echo "      Ver instrucciones arriba"
        echo ""
    fi
    
    # Database URLs
    if docker compose ps | grep -q "db"; then
        echo "   💾 BASE DE DATOS:"
        echo "      Puerto: localhost:5432 (PostgreSQL)"
        echo "      Admin:   docker compose exec db psql -U postgres"
        echo ""
    fi
    
    # Comandos útiles
    log_info "🛠️  COMANDOS ÚTILES:"
    echo ""
    echo "   Ver logs del backend:    docker compose logs backend -f"
    echo "   Ver todos los logs:      docker compose logs -f"
    echo "   Detener servicios:       docker compose down"
    echo "   Reiniciar backend:       docker compose restart backend"
    echo "   Estado de servicios:     docker compose ps"
    echo "   Ejecutar migraciones:    docker compose exec backend alembic upgrade head"
    echo ""
    
    log_info "⏰ Prueba el sistema abriendo: http://localhost:8000/docs"
}

# Función principal
main() {
    section_header "🚀 LEVANTANDO SISTEMA SCOUTA/FORGE SAAS"
    
    local skip_build=false
    local skip_deps=false
    
    # Parsear argumentos
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                skip_build=true
                shift
                ;;
            --skip-deps)
                skip_deps=true
                shift
                ;;
            *)
                log_error "Argumento desconocido: $1"
                echo "Uso: $0 [--skip-build] [--skip-deps]"
                exit 1
                ;;
        esac
    done
    
    # Ejecutar pasos
    check_dependencies
    cleanup_previous
    
    if [ "$skip_build" = false ]; then
        build_images
    else
        log_info "Omitiendo construcción de imágenes (--skip-build)"
    fi
    
    if [ "$skip_deps" = false ]; then
        start_dependencies
        run_migrations
    else
        log_info "Omitiendo servicios de apoyo (--skip-deps)"
    fi
    
    start_backend
    start_frontend
    start_additional_services
    show_summary
}

# Manejo de señales
trap 'log_error "Script interrumpido por el usuario"; exit 1' INT

# Ejecutar función principal
main "$@"
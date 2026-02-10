#!/bin/bash

echo "🔍 VERIFICACIÓN COMPLETA DEL SISTEMA DIET AI"
echo "============================================"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo "${BLUE}1. ESTADO DE CONTAINERS DOCKER:${NC}"
docker-compose ps

echo ""
echo "${BLUE}2. HEALTH CHECK DE LA API:${NC}"
HEALTH_RESPONSE=$(curl -s http://localhost:8000/health)
echo "$HEALTH_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$HEALTH_RESPONSE"

echo ""
echo "${BLUE}3. VERIFICACIÓN DE POSTGRESQL:${NC}"
if docker exec dieta-postgres pg_isready -U dietai &> /dev/null; then
    echo -e "${GREEN}✅ PostgreSQL está corriendo${NC}"
    
    # Verificar tablas
    TABLES=$(docker exec dieta-postgres psql -U dietai -d dietai -c "\dt" 2>/dev/null)
    if echo "$TABLES" | grep -q "users"; then
        echo -e "${GREEN}✅ Tabla 'users' existe${NC}"
    else
        echo -e "${YELLOW}⚠️  Tabla 'users' no existe (se creará al primer registro)${NC}"
    fi
else
    echo -e "${RED}❌ PostgreSQL no está disponible${NC}"
fi

echo ""
echo "${BLUE}4. VERIFICACIÓN DE REDIS:${NC}"
if docker exec dieta-redis redis-cli ping &> /dev/null; then
    echo -e "${GREEN}✅ Redis está corriendo${NC}"
else
    echo -e "${RED}❌ Redis no está disponible${NC}"
fi

echo ""
echo "${BLUE}5. ENDPOINTS DISPONIBLES:${NC}"
echo -e "${GREEN}✅ http://localhost:8000/ ${NC}- Página principal"
echo -e "${GREEN}✅ http://localhost:8000/docs ${NC}- Documentación Swagger"
echo -e "${GREEN}✅ http://localhost:8000/health ${NC}- Health check"
echo -e "${BLUE}🔧 http://localhost:8000/api/v1/auth/register ${NC}- Registrar usuario (POST)"
echo -e "${BLUE}🔧 http://localhost:8000/api/v1/auth/login ${NC}- Login (POST)"
echo -e "${BLUE}🔧 http://localhost:8000/api/v1/users/me ${NC}- Perfil de usuario (GET, necesita auth)"

echo ""
echo "${BLUE}6. PRUEBA RÁPIDA DE REGISTRO:${NC}"
read -p "¿Quieres crear un usuario de prueba? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
        -H "Content-Type: application/json" \
        -d '{
            "username": "demo",
            "email": "demo@dietai.com",
            "password": "demo123",
            "full_name": "Usuario Demo"
        }')
    
    if echo "$RESPONSE" | grep -q "username"; then
        echo -e "${GREEN}✅ Usuario creado exitosamente${NC}"
        echo "Respuesta: $RESPONSE"
        
        echo ""
        echo "${BLUE}7. PRUEBA DE LOGIN:${NC}"
        LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=demo&password=demo123")
        
        if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
            echo -e "${GREEN}✅ Login exitoso${NC}"
            TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
            echo "Token obtenido: ${TOKEN:0:30}..."
            
            echo ""
            echo "${BLUE}8. PRUEBA DE ENDPOINT PROTEGIDO:${NC}"
            ME_RESPONSE=$(curl -s http://localhost:8000/api/v1/users/me \
                -H "Authorization: Bearer $TOKEN")
            echo "Perfil de usuario: $ME_RESPONSE"
        else
            echo -e "${RED}❌ Error en login${NC}"
            echo "Respuesta: $LOGIN_RESPONSE"
        fi
    else
        echo -e "${YELLOW}⚠️  Posible error o usuario ya existe${NC}"
        echo "Respuesta: $RESPONSE"
    fi
fi

echo ""
echo "${GREEN}============================================${NC}"
echo "${GREEN}✅ VERIFICACIÓN COMPLETADA${NC}"
echo "${GREEN}============================================${NC}"
echo ""
echo "${BLUE}🎯 SIGUIENTES PASOS:${NC}"
echo "1. Accede a http://localhost:8000/docs para ver la documentación completa"
echo "2. Implementa más endpoints (perfiles, dietas, alimentos)"
echo "3. Agrega algoritmos de cálculo nutricional"
echo "4. Implementa reconocimiento de alimentos por IA"

#!/bin/bash
echo "=== PRUEBA COMPLETA DE LA API ==="
echo ""

# Función para hacer requests con formato
make_request() {
    echo "➡️  $1"
    if [ "$2" = "POST" ]; then
        curl -s -X POST "$3" -H "Content-Type: application/json" -d "$4"
    else
        curl -s "$3"
    fi | python3 -m json.tool 2>/dev/null || echo "  ❌ Respuesta no JSON o error"
    echo ""
}

# Esperar un poco más
sleep 3

# 1. Health check
make_request "1. Health Check" "GET" "http://localhost:8000/health"

# 2. Raíz
make_request "2. Endpoint raíz" "GET" "http://localhost:8000/"

# 3. Foods (sin categoría)
make_request "3. Todos los alimentos" "GET" "http://localhost:8000/foods"

# 4. Foods con categoría
make_request "4. Alimentos por categoría" "GET" "http://localhost:8000/foods?category=proteina"

# 5. Test endpoint
make_request "5. Test" "GET" "http://localhost:8000/test"

# 6. Calcular TDEE (POST)
TDEE_DATA='{
    "age": 30,
    "weight_kg": 70,
    "height_cm": 175,
    "gender": "male",
    "activity_level": "moderate"
}'
make_request "6. Calcular TDEE" "POST" "http://localhost:8000/calculate/tdee" "$TDEE_DATA"

echo "=== PRUEBA COMPLETADA ==="

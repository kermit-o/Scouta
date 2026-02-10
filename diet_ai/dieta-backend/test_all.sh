#!/bin/bash
echo "🚀 PRUEBA COMPLETA DE DIETA API 🚀"
echo "=================================="
echo ""

# Configuración
API_URL="http://localhost:8001"

# Función para hacer requests
request() {
    echo "➡️  $1"
    echo "   URL: $2"
    if [ "$3" = "POST" ]; then
        response=$(curl -s -X POST "$2" -H "Content-Type: application/json" -d "$4" 2>/dev/null)
    else
        response=$(curl -s "$2" 2>/dev/null)
    fi
    
    if [ $? -eq 0 ] && [ -n "$response" ]; then
        echo "   ✅ Response:"
        echo "$response" | python3 -m json.tool 2>/dev/null || echo "   📝 $response"
    else
        echo "   ❌ No response or error"
    fi
    echo ""
}

# Esperar un poco más
sleep 5

# 1. Health check
request "1. Health Check" "$API_URL/health" "GET"

# 2. Root endpoint
request "2. Root Endpoint" "$API_URL/" "GET"

# 3. Test endpoint
request "3. Test General" "$API_URL/test" "GET"

# 4. Foods endpoint
request "4. Todos los alimentos" "$API_URL/foods" "GET"
request "5. Alimentos por categoría" "$API_URL/foods?category=proteina" "GET"

# 5. Test TDEE (GET)
request "6. Test TDEE (GET)" "$API_URL/test/tdee" "GET"

# 6. Test Diet (GET)
request "7. Test Dieta (GET)" "$API_URL/test/diet" "GET"

# 7. Calcular TDEE (POST)
TDEE_DATA='{
    "age": 30,
    "weight_kg": 70,
    "height_cm": 175,
    "gender": "male",
    "activity_level": "moderate",
    "goal": "weight_loss"
}'
request "8. Calcular TDEE (POST)" "$API_URL/calculate/tdee" "POST" "$TDEE_DATA"

# 8. Generar Dieta (POST)
DIET_DATA='{
    "profile": {
        "age": 30,
        "weight_kg": 70,
        "height_cm": 175,
        "gender": "male",
        "activity_level": "moderate",
        "goal": "weight_loss"
    },
    "meal_count": 3
}'
request "9. Generar Dieta (POST)" "$API_URL/diet/generate" "POST" "$DIET_DATA"

# 9. Calcular comida (POST)
MEAL_DATA='[
    {"name": "Pollo", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6},
    {"name": "Arroz", "calories": 111, "protein_g": 2.6, "carbs_g": 23, "fat_g": 0.9}
]'
request "10. Calcular Comida (POST)" "$API_URL/calculate/meal" "POST" "$MEAL_DATA"

echo "=================================="
echo "✅ PRUEBA COMPLETADA"
echo ""
echo "📊 Resumen:"
echo "   API: $API_URL"
echo "   PostgreSQL: localhost:5433"
echo "   Swagger UI: $API_URL/docs"

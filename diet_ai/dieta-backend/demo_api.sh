#!/bin/bash
echo "🎬 DEMOSTRACIÓN COMPLETA - DIETA API 🎬"
echo "========================================="
echo ""

API_URL="http://localhost:8001"

# Función para mostrar resultados bonitos
demo() {
    echo "🎯 $1"
    echo "📤 Request: $2"
    
    if [ "$3" = "POST" ]; then
        response=$(curl -s -X POST "$API_URL$2" \
          -H "Content-Type: application/json" \
          -d "$4")
    else
        response=$(curl -s "$API_URL$2")
    fi
    
    if python3 -c "import json; json.loads('''$response''')" 2>/dev/null; then
        echo "✅ Success!"
        echo "📥 Response (resumen):"
        
        # Extraer información clave según el endpoint
        case "$2" in
            "/health")
                echo "   Status: $(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['status'])")"
                echo "   Service: $(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['service'])")"
                ;;
            "/")
                echo "   Message: $(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['message'])")"
                echo "   Endpoints disponibles:"
                echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); 
                    for endpoint, desc in d['endpoints'].items():
                        print(f'     • {endpoint}: {desc}')"
                ;;
            "/foods"*)
                count=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('count', 'N/A'))")
                echo "   Total alimentos: $count"
                ;;
            "/calculate/tdee")
                success=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('success', 'N/A'))")
                if [ "$success" = "True" ]; then
                    tdee=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['tdee'])")
                    calories=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['target_calories'])")
                    echo "   TDEE: $tdee kcal"
                    echo "   Calorías objetivo: $calories kcal"
                fi
                ;;
            "/diet/generate")
                success=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('success', 'N/A'))")
                if [ "$success" = "True" ]; then
                    diet_id=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['diet_id'][:8])")
                    meal_count=$(echo $response | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['data']['summary']['meal_count'])")
                    echo "   Diet ID: $diet_id"
                    echo "   Comidas: $meal_count"
                fi
                ;;
            *)
                echo "   Response válido recibido"
                ;;
        esac
    else
        echo "❌ Error o respuesta inválida"
        echo "   Raw: $response"
    fi
    echo ""
}

# 1. Health Check
demo "1. Verificar salud del servicio" "/health" "GET"

# 2. Información de la API
demo "2. Información general" "/" "GET"

# 3. Listar todos los alimentos
demo "3. Base de datos de alimentos" "/foods" "GET"

# 4. Alimentos por categoría
demo "4. Alimentos proteicos" "/foods?category=proteina" "GET"

# 5. Calcular TDEE para un usuario
TDEE_DATA='{
    "age": 30,
    "weight_kg": 70,
    "height_cm": 175,
    "gender": "male",
    "activity_level": "moderate",
    "goal": "weight_loss"
}'
demo "5. Calcular necesidades calóricas (TDEE)" "/calculate/tdee" "POST" "$TDEE_DATA"

# 6. Generar plan de dieta completo
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
demo "6. Generar plan de dieta personalizado" "/diet/generate" "POST" "$DIET_DATA"

# 7. Calcular valores de una comida
MEAL_DATA='[
    {"name": "Pechuga de pollo", "calories": 165, "protein_g": 31, "carbs_g": 0, "fat_g": 3.6},
    {"name": "Arroz integral", "calories": 111, "protein_g": 2.6, "carbs_g": 23, "fat_g": 0.9},
    {"name": "Brócoli", "calories": 34, "protein_g": 2.8, "carbs_g": 7, "fat_g": 0.4}
]'
demo "7. Analizar una comida" "/calculate/meal" "POST" "$MEAL_DATA"

echo "========================================="
echo "🎉 DEMOSTRACIÓN COMPLETADA"
echo ""
echo "📊 RESUMEN DE TU API:"
echo "   • URL: $API_URL"
echo "   • Documentación: $API_URL/docs"
echo "   • PostgreSQL: localhost:5433"
echo "   • Status: ✅ OPERACIONAL"
echo ""
echo "🚀 ¡Backend listo para desarrollo!"

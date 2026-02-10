#!/bin/bash
echo "🧪 Probando DietAI API..."
echo ""
echo "1. Health check:"
curl -s http://localhost:8001/health | python3 -m json.tool || curl -s http://localhost:8001/health
echo ""
echo "2. Raíz:"
curl -s http://localhost:8001/ | python3 -m json.tool || curl -s http://localhost:8001/
echo ""
echo "3. Registrar usuario:"
curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario_ejemplo",
    "password": "password123",
    "full_name": "Usuario Ejemplo",
    "age": 30,
    "gender": "male"
  }' | python3 -m json.tool || curl -s -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario_ejemplo",
    "password": "password123",
    "full_name": "Usuario Ejemplo",
    "age": 30,
    "gender": "male"
  }'
echo ""
echo "4. Generar dieta:"
curl -s -X POST http://localhost:8001/diets/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy_token" \
  -d '{
    "profile": {
      "height_cm": 180,
      "weight_kg": 75,
      "goal": "weight_loss",
      "activity_level": "moderate",
      "dietary_restrictions": ["lactose"],
      "allergies": [],
      "workout_days_per_week": 4
    }
  }' | python3 -m json.tool || curl -s -X POST http://localhost:8001/diets/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dummy_token" \
  -d '{
    "profile": {
      "height_cm": 180,
      "weight_kg": 75,
      "goal": "weight_loss",
      "activity_level": "moderate",
      "dietary_restrictions": ["lactose"],
      "allergies": [],
      "workout_days_per_week": 4
    }
  }'
echo ""
echo "✅ Pruebas completadas!"

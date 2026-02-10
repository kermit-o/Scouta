#!/bin/bash
echo "🧪 Probando API DietAI..."
sleep 5

echo "1. Probando health check..."
curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health

echo -e "\n2. Probando raíz..."
curl -s http://localhost:8000/ | jq . || curl -s http://localhost:8000/

echo -e "\n3. Probando registro..."
curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}' \
  | jq . || curl -s -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"test123"}'

echo -e "\n4. Probando generación de dieta..."
curl -s -X POST http://localhost:8000/diets/generate \
  -H "Content-Type: application/json" \
  -d '{"age":30,"gender":"male","height_cm":180,"weight_kg":75,"activity_level":"moderate","goal":"weight_loss","dietary_restrictions":[]}' \
  | jq . || curl -s -X POST http://localhost:8000/diets/generate \
  -H "Content-Type: application/json" \
  -d '{"age":30,"gender":"male","height_cm":180,"weight_kg":75,"activity_level":"moderate","goal":"weight_loss","dietary_restrictions":[]}'

echo -e "\n✅ Pruebas completadas!"

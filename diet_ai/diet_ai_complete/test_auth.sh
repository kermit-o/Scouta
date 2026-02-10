#!/bin/bash
# test_auth.sh

echo "🧪 PRUEBAS DE AUTENTICACIÓN JWT"
echo "==============================="

echo "⏳ Esperando que la API se reinicie..."
sleep 8

echo ""
echo "1. 🔍 Verificando estado de la API:"
curl -s http://localhost:8000/ | python3 -m json.tool 2>/dev/null || curl -s http://localhost:8000/

echo ""
echo "2. 📝 Registrando nuevo usuario:"
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@ejemplo.com",
    "username": "nuevo_usuario",
    "password": "password123",
    "full_name": "Nuevo Usuario"
  }' | python3 -m json.tool 2>/dev/null || curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "nuevo@ejemplo.com",
    "username": "nuevo_usuario",
    "password": "password123",
    "full_name": "Nuevo Usuario"
  }'

echo ""
echo "3. 🔑 Login con el usuario creado:"
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=nuevo@ejemplo.com&password=password123" \
  | python3 -m json.tool 2>/dev/null || curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=nuevo@ejemplo.com&password=password123"

echo ""
echo "4. 👤 Obtener información del usuario actual (requiere token):"
echo "   (Guarda el token del paso anterior y reemplaza TOKEN_AQUI)"
echo ""
echo "   curl -H 'Authorization: Bearer TOKEN_AQUI' http://localhost:8000/auth/me"

echo ""
echo "5. 🍎 Probando endpoint protegido de alimentos:"
echo "   curl -H 'Authorization: Bearer TOKEN_AQUI' http://localhost:8000/foods"

echo ""
echo "6. 📋 Validar token:"
echo "   curl -H 'Authorization: Bearer TOKEN_AQUI' http://localhost:8000/auth/validate"

echo ""
echo "✅ Pruebas configuradas. Usa los comandos anteriores para probar."

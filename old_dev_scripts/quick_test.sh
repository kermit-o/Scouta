#!/bin/bash

echo "🧪 FORGE SAAS - QUICK TEST SUITE"
echo "================================="

# Test 1: Iniciar servidor
echo "1. Iniciando servidor..."
python main.py &
SERVER_PID=$!
sleep 3

if ! ps -p $SERVER_PID > /dev/null; then
    echo "❌ ERROR: No se pudo iniciar el servidor"
    exit 1
fi
echo "✅ Servidor iniciado (PID: $SERVER_PID)"

# Test 2: Endpoints básicos
echo ""
echo "2. Probando endpoints API..."
echo "   - Endpoint raíz:"
curl -s http://localhost:8000/ | grep -q "Welcome" && echo "   ✅ OK" || echo "   ❌ FAIL"

echo "   - Tipos de proyecto:"
curl -s http://localhost:8000/project-types | grep -q "project_types" && echo "   ✅ OK" || echo "   ❌ FAIL"

# Test 3: Project Factory
echo ""
echo "3. Probando Project Factory..."
python -c "
from core.project_factory import ProjectFactory, ProjectRequirements, ProjectType
try:
    factory = ProjectFactory()
    req = ProjectRequirements(
        name='Test App',
        description='Test',
        project_type=ProjectType.REACT_WEB_APP,
        features=['auth']
    )
    project = factory.create_project(req)
    print('   ✅ Project Factory: OK')
    print(f'   Project ID: {project[\"project_id\"]}')
except Exception as e:
    print(f'   ❌ Project Factory FAIL: {e}')
"

# Test 4: Estructura de archivos
echo ""
echo "4. Verificando estructura..."
DIRS=("core" "project_types" "generators" "agents" "shared_components")
for dir in "${DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo "   ✅ $dir: Existe"
    else
        echo "   ❌ $dir: No existe"
    fi
done

# Test 5: Archivos críticos
echo ""
echo "5. Verificando archivos críticos..."
FILES=("core/project_factory.py" "agents/orchestrator/ai_orchestrator.py" "main.py" "config/settings.py")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file: Existe"
    else
        echo "   ❌ $file: No existe"
    fi
done

# Limpiar
echo ""
echo "6. Limpiando..."
kill $SERVER_PID 2>/dev/null
echo "✅ Tests completados!"

echo ""
echo "📊 RESUMEN:"
echo "==========="
echo "Si ves más ✅ que ❌, el sistema está listo!"
echo "Puedes continuar con el siguiente paso del roadmap."

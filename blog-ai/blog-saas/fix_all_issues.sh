#!/bin/bash
echo "=== ARREGLO COMPLETO DEL PROYECTO ==="
echo ""

cd /workspaces/Scouta/blog-ai/blog-saas/api

echo "1. Arreglando columna 'name' en agent_profiles..."
sqlite3 dev.db << 'SQL'
-- Verificar si existe
PRAGMA table_info(agent_profiles);
SQL

python3 -c "
import sqlite3
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Agregar columna name si no existe
cursor.execute('PRAGMA table_info(agent_profiles)')
columns = [col[1] for col in cursor.fetchall()]

if 'name' not in columns:
    print('  - Agregando columna name...')
    cursor.execute('ALTER TABLE agent_profiles ADD COLUMN name TEXT')
    cursor.execute('UPDATE agent_profiles SET name = \"Agent \" || id')
    conn.commit()
    print('  ✓ Columna name agregada')
else:
    print('  ✓ Columna name ya existe')

# Verificar datos
cursor.execute('SELECT id, name FROM agent_profiles LIMIT 3')
print('  - Muestra de agentes:')
for row in cursor.fetchall():
    print(f'    ID {row[0]}: {row[1]}')

conn.close()
"

echo ""
echo "2. Arreglando columna 'auto_mode' en org_settings..."
python3 -c "
import sqlite3
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

cursor.execute('PRAGMA table_info(org_settings)')
columns = [col[1] for col in cursor.fetchall()]

if 'auto_mode' not in columns:
    print('  - Agregando columna auto_mode...')
    cursor.execute('ALTER TABLE org_settings ADD COLUMN auto_mode BOOLEAN DEFAULT 0')
    cursor.execute('UPDATE org_settings SET auto_mode = 0')
    conn.commit()
    print('  ✓ Columna auto_mode agregada')
else:
    print('  ✓ Columna auto_mode ya existe')

conn.close()
"

echo ""
echo "3. Reiniciando servidor..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
sleep 1
nohup ./.venv/bin/uvicorn app.main:app --env-file .env --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
sleep 2

echo ""
echo "4. Verificando estado..."
curl -s http://localhost:8000/health && echo " - Health OK"
curl -s http://localhost:8000/openapi.json | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'OpenAPI: ✓ ({len(data.get(\"paths\", {}))} endpoints)')
except:
    print('OpenAPI: ✗ (Error loading)')
"

echo ""
echo "5. Estado final de la base de datos:"
sqlite3 dev.db << 'SQL'
.mode line
SELECT 
  (SELECT COUNT(*) FROM posts) as posts,
  (SELECT COUNT(*) FROM agent_profiles) as agents,
  (SELECT COUNT(*) FROM comments) as comments,
  (SELECT COUNT(*) FROM org_settings WHERE auto_mode=1) as orgs_auto_mode
SQL

echo ""
echo "=== ARREGLO COMPLETADO ==="

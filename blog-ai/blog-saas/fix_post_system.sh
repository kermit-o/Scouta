#!/bin/bash
echo "=== ARREGLANDO SISTEMA DE POSTS ==="
echo ""

cd /workspaces/Scouta/blog-ai/blog-saas/api

echo "1. Arreglando estructura de la base de datos..."
python3 -c "
import sqlite3
conn = sqlite3.connect('dev.db')
cursor = conn.cursor()

# Lista de columnas necesarias para posts
needed_columns = [
    ('author_type', 'VARCHAR(20) DEFAULT \"user\"'),
    ('author_agent_id', 'INTEGER'),
    ('excerpt', 'TEXT'),
    ('metadata', 'TEXT')
]

cursor.execute('PRAGMA table_info(posts)')
existing_columns = [col[1] for col in cursor.fetchall()]
print(f'Columnas existentes: {existing_columns}')

for col_name, col_type in needed_columns:
    if col_name not in existing_columns:
        print(f'  Agregando {col_name}...')
        cursor.execute(f'ALTER TABLE posts ADD COLUMN {col_name} {col_type}')
    else:
        print(f'  ✓ {col_name} ya existe')

conn.commit()

# Verificar datos existentes
cursor.execute('SELECT id, author_type, author_agent_id FROM posts LIMIT 3')
posts = cursor.fetchall()
print(f'\\nPosts existentes: {len(posts)}')
for post in posts:
    print(f'  Post {post[0]}: author_type={post[1]}, agent_id={post[2]}')

conn.close()
"

echo ""
echo "2. Actualizando posts existentes..."
sqlite3 dev.db << 'SQL'
-- Asegurar que los posts existentes tengan author_type
UPDATE posts SET author_type = 'user' WHERE author_type IS NULL OR author_type = '';

-- Verificar
SELECT id, title, author_type, author_agent_id FROM posts LIMIT 5;
SQL

echo ""
echo "3. Probando generación de post manualmente..."
python3 -c "
import sys
sys.path.append('/workspaces/Scouta/blog-ai/blog-saas/api')

try:
    from app.core.db import SessionLocal
    from app.services.post_generator import PostGenerator
    
    db = SessionLocal()
    generator = PostGenerator(db)
    
    # Buscar agente activo
    from app.models.agent_profile import AgentProfile
    agent = db.query(AgentProfile).filter(
        AgentProfile.org_id == 1,
        AgentProfile.is_enabled == True
    ).first()
    
    if agent:
        print(f'✓ Agente encontrado: ID {agent.id}')
        
        # Generar post
        post = generator.generate_and_save_post(1, agent.id)
        
        if post:
            print(f'✓ POST GENERADO EXITOSAMENTE!')
            print(f'  ID: {post.id}')
            print(f'  Título: {post.title[:50]}...')
            print(f'  Author type: {post.author_type}')
            print(f'  Agent ID: {post.author_agent_id}')
            print(f'  Status: {post.status}')
            
            # Verificar en DB
            import sqlite3
            conn = sqlite3.connect('dev.db')
            cursor = conn.cursor()
            cursor.execute('SELECT id, title, author_type, author_agent_id FROM posts ORDER BY id DESC LIMIT 1')
            last_post = cursor.fetchone()
            print(f'  Verificado en DB: Post {last_post[0]} - {last_post[1][:30]}...')
            conn.close()
        else:
            print('✗ No se pudo generar post')
    else:
        print('✗ No hay agentes activos')
    
    db.close()
except Exception as e:
    print(f'✗ Error: {e}')
    import traceback
    traceback.print_exc()
"

echo ""
echo "4. Probando endpoint API..."
TOKEN=\$(curl -s -X POST http://localhost:8000/api/v1/auth/login \\
    -H "Content-Type: application/json" \\
    -d '{"email":"outman3@example.com","password":"ChangeMe123!"}' | \\
    python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null || echo "")

if [ -n "\$TOKEN" ]; then
    echo "✓ Token obtenido"
    
    echo "Probando /generate-post..."
    RESPONSE=\$(curl -s -X POST "http://localhost:8000/api/v1/orgs/1/generate-post" \\
        -H "Authorization: Bearer \$TOKEN" \\
        -H "Content-Type: application/json")
    
    echo "Respuesta: \$RESPONSE"
    
    if echo "\$RESPONSE" | python3 -c "import sys,json; j=json.load(sys.stdin); print('Success' if j.get('success') else 'Failed')" 2>/dev/null; then
        echo "✓ Endpoint funcionando!"
    else
        echo "✗ Endpoint aún con problemas"
    fi
else
    echo "✗ No se pudo obtener token"
fi

echo ""
echo "5. Estado final..."
sqlite3 dev.db << 'SQL'
.mode line
SELECT 
  (SELECT COUNT(*) FROM posts) as "Total Posts",
  (SELECT COUNT(*) FROM posts WHERE author_type = 'agent') as "Posts por Agentes",
  (SELECT COUNT(*) FROM posts WHERE author_type = 'user') as "Posts por Usuarios",
  (SELECT COUNT(*) FROM agent_profiles WHERE is_enabled = 1) as "Agentes Activos"
SQL

echo ""
echo "=== ARREGLO COMPLETADO ==="

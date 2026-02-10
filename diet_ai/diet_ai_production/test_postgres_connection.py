#!/usr/bin/env python3
"""
Test PostgreSQL connections with different credentials
"""
import psycopg2

# Lista de credenciales comunes a probar
credentials = [
    {'user': 'postgres', 'password': 'postgres'},
    {'user': 'postgres', 'password': ''},
    {'user': 'codespace', 'password': 'codespace'},
    {'user': 'root', 'password': 'root'},
    {'user': 'admin', 'password': 'admin'},
]

for cred in credentials:
    try:
        print(f"🔍 Probando: {cred['user']}:{cred['password']}")
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user=cred['user'],
            password=cred['password'],
            database='postgres'
        )
        print(f"✅ Conectado exitosamente como {cred['user']}")
        
        # Verificar si podemos crear bases de datos
        conn.autocommit = True
        cursor = conn.cursor()
        cursor.execute("SELECT current_user;")
        user = cursor.fetchone()[0]
        print(f"   Usuario actual: {user}")
        
        cursor.close()
        conn.close()
        
        # Usar estas credenciales
        print(f"\n🎯 Usando credenciales: {cred['user']}:{cred['password']}")
        
        # Actualizar config.py
        with open('core/config.py', 'r') as f:
            config_content = f.read()
        
        new_db_url = f"postgresql://{cred['user']}:{cred['password']}@localhost:5432/dietai_db"
        config_content = config_content.replace(
            "DATABASE_URL = \"postgresql://postgres:postgres@localhost:5432/dietai_db\"",
            f"DATABASE_URL = \"{new_db_url}\""
        )
        
        with open('core/config.py', 'w') as f:
            f.write(config_content)
        
        print(f"📝 Actualizado DATABASE_URL en config.py")
        break
        
    except Exception as e:
        print(f"   ❌ Falló: {str(e)[:50]}")

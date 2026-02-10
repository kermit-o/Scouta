#!/usr/bin/env python3
"""
Create database with correct credentials
"""
import sys
sys.path.insert(0, '.')

from core.config import settings
import psycopg2

# Extraer credenciales de DATABASE_URL
db_url = settings.DATABASE_URL
# postgresql://user:password@host:port/database
parts = db_url.replace('postgresql://', '').split('@')
user_pass = parts[0].split(':')
host_port_db = parts[1].split('/')
host_port = host_port_db[0].split(':')

username = user_pass[0]
password = user_pass[1] if len(user_pass) > 1 else ''
host = host_port[0]
port = host_port[1] if len(host_port) > 1 else '5432'
database = host_port_db[1]

print(f"🔧 Configuración de base de datos:")
print(f"   Usuario: {username}")
print(f"   Host: {host}:{port}")
print(f"   Base de datos: {database}")

try:
    # Conectar a PostgreSQL (base de datos por defecto)
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=username,
        password=password,
        database='postgres'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Verificar si existe
    cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}';")
    exists = cursor.fetchone()
    
    if not exists:
        print(f"📦 Creando base de datos: {database}")
        cursor.execute(f'CREATE DATABASE "{database}";')
        print("✅ Base de datos creada exitosamente")
    else:
        print("✅ Base de datos ya existe")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error creando base de datos: {e}")
    
    # Si falla, intentar crear sin contraseña
    try:
        print("🔧 Intentando conexión sin contraseña...")
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='',
            database='postgres'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{database}';")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{database}";')
            print("✅ Base de datos creada (sin contraseña)")
        
        cursor.close()
        conn.close()
        
        # Actualizar config.py
        with open('core/config.py', 'r') as f:
            content = f.read()
        
        new_url = "postgresql://postgres:@localhost:5432/dietai_db"
        content = content.replace(settings.DATABASE_URL, new_url)
        
        with open('core/config.py', 'w') as f:
            f.write(content)
        
        print("📝 Config.py actualizado")
        
    except Exception as e2:
        print(f"❌ También falló sin contraseña: {e2}")

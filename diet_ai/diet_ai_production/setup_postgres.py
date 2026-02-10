#!/usr/bin/env python3
"""
Setup PostgreSQL for DietAI
"""
import subprocess
import os
import getpass

print("=== CONFIGURACIÓN DE POSTGRESQL ===")

# Intentar diferentes métodos para configurar PostgreSQL
methods = [
    # Método 1: Usar sudo para acceder como postgres
    ["sudo", "-u", "postgres", "psql", "-c", "CREATE USER dietai WITH PASSWORD 'dietai123';"],
    ["sudo", "-u", "postgres", "psql", "-c", "CREATE DATABASE dietai_db OWNER dietai;"],
    ["sudo", "-u", "postgres", "psql", "-c", "GRANT ALL PRIVILEGES ON DATABASE dietai_db TO dietai;"],
    
    # Método 2: Si estamos en container, usar conexión directa
    ["psql", "-h", "localhost", "-U", "postgres", "-c", "CREATE USER dietai WITH PASSWORD 'dietai123';"],
    
    # Método 3: Crear usuario sin contraseña para desarrollo
    ["sudo", "-u", "postgres", "psql", "-c", "CREATE USER dietai;"],
    ["sudo", "-u", "postgres", "psql", "-c", "ALTER USER dietai WITH SUPERUSER;"],
]

print("Intentando configurar PostgreSQL...")

for cmd in methods:
    try:
        print(f"Ejecutando: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ Comando exitoso")
            if result.stdout:
                print(f"   Salida: {result.stdout.strip()}")
        else:
            print(f"   ❌ Error: {result.stderr.strip()}")
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

# Probar conexión con nuevo usuario
print("\n=== PROBANDO CONEXIÓN ===")

test_connections = [
    {'user': 'dietai', 'password': 'dietai123', 'dbname': 'dietai_db'},
    {'user': 'dietai', 'password': '', 'dbname': 'dietai_db'},
    {'user': 'postgres', 'password': '', 'dbname': 'dietai_db'},
    {'user': 'postgres', 'password': 'postgres', 'dbname': 'dietai_db'},
]

import psycopg2
for conn_params in test_connections:
    try:
        print(f"Probando: {conn_params['user']}@{conn_params['dbname']}")
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user=conn_params['user'],
            password=conn_params.get('password', ''),
            database=conn_params['dbname']
        )
        print(f"   ✅ Conexión exitosa!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT current_user, current_database();")
        user, db = cursor.fetchone()
        print(f"   Conectado como: {user} en {db}")
        
        cursor.close()
        conn.close()
        
        # Guardar credenciales que funcionan
        with open('.env', 'a') as f:
            f.write(f"\n# PostgreSQL configuration\n")
            f.write(f"DB_USER={conn_params['user']}\n")
            f.write(f"DB_PASSWORD={conn_params.get('password', '')}\n")
            f.write(f"DB_NAME={conn_params['dbname']}\n")
            f.write(f"DB_HOST=localhost\n")
            f.write(f"DB_PORT=5432\n")
            f.write(f"DATABASE_URL=postgresql://{conn_params['user']}:{conn_params.get('password', '')}@localhost:5432/{conn_params['dbname']}\n")
        
        print(f"   📝 Credenciales guardadas en .env")
        break
        
    except Exception as e:
        print(f"   ❌ Error: {str(e)[:60]}")

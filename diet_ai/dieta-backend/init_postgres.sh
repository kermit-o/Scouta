#!/bin/bash

echo "🔧 Inicializando PostgreSQL para Diet AI..."

# Crear usuario y base de datos si no existen
docker exec dieta-postgres psql -U postgres << 'SQL'
-- Crear usuario si no existe
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'dietai') THEN
        CREATE USER dietai WITH PASSWORD 'dietai123';
        RAISE NOTICE 'Usuario dietai creado';
    ELSE
        RAISE NOTICE 'Usuario dietai ya existe';
    END IF;
END
\$\$;

-- Crear base de datos si no existe
SELECT 'CREATE DATABASE dietai OWNER dietai'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'dietai')\gexec

-- Otorgar privilegios
GRANT ALL PRIVILEGES ON DATABASE dietai TO dietai;

-- Conectar a la base de datos dietai
\c dietai

-- Otorgar privilegios en el esquema público
GRANT ALL ON SCHEMA public TO dietai;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO dietai;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO dietai;

-- Crear extensión para UUID si no existe
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Verificar
\du
\l
\dt
SQL

echo "✅ PostgreSQL inicializado"
echo "   Usuario: dietai"
echo "   Password: dietai123"
echo "   Base de datos: dietai"

#!/bin/bash

echo "🔄 Waiting for PostgreSQL to be ready..."
sleep 10

echo "🗄️ Initializing database..."
docker-compose exec backend python -c "
from app.services.database_service import DatabaseService
db = DatabaseService()
if db.init_db():
    print('✅ Database initialized successfully')
else:
    print('❌ Database initialization failed')
"

echo "📊 Verifying tables..."
docker-compose exec postgres psql -U user -d forge_db -c "\dt"

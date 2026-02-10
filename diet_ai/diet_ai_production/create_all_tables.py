#!/usr/bin/env python3
"""
Create all database tables
"""
import asyncio
import sys

sys.path.insert(0, '.')

async def create_tables():
    try:
        from database.database import engine, Base
        from database.models.user import User
        from database.models.diet import Diet, MealPlan
        from database.models.inventory import InventoryItem, Category
        from database.models.recipe import Recipe, Ingredient
        
        print("🗄️ Creando tablas en la base de datos...")
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        print("✅ Todas las tablas creadas exitosamente!")
        
        # Listar tablas creadas
        async with engine.connect() as conn:
            result = await conn.execute(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
            )
            tables = [row[0] for row in result]
            print(f"\n📋 Tablas creadas: {', '.join(tables)}")
        
    except Exception as e:
        print(f"❌ Error creando tablas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_tables())

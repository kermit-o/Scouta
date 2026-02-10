#!/usr/bin/env python3
"""
Script para importar datos de prueba a la base de datos
"""
import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
import uuid
import sys

async def import_test_data():
    """Importar datos de prueba"""
    print("📊 Importando datos de prueba...")
    
    # Configurar conexión a la base de datos
    DATABASE_URL = "postgresql+asyncpg://hotel_admin:hotel_password@postgres:5432/hotel_db"
    engine = create_async_engine(DATABASE_URL, echo=False)
    
    # Crear sesión asíncrona
    AsyncSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        try:
            # 1. Insertar tipos de habitación
            print("🛏️  Insertando tipos de habitación...")
            room_types = [
                {
                    "id": str(uuid.uuid4()),
                    "name": "Estándar",
                    "description": "Habitación cómoda con cama doble",
                    "base_price": 89.99,
                    "max_guests": 2,
                    "available_count": 10
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Deluxe",
                    "description": "Habitación espaciosa con vista",
                    "base_price": 149.99,
                    "max_guests": 3,
                    "available_count": 5
                },
                {
                    "id": str(uuid.uuid4()),
                    "name": "Suite",
                    "description": "Suite de lujo con sala separada",
                    "base_price": 249.99,
                    "max_guests": 4,
                    "available_count": 2
                }
            ]
            
            for rt in room_types:
                await session.execute(text("""
                    INSERT INTO room_types (id, name, description, base_price, max_guests, available_count)
                    VALUES (:id, :name, :description, :base_price, :max_guests, :available_count)
                    ON CONFLICT (id) DO NOTHING
                """), rt)
            
            await session.commit()
            
            # 2. Insertar huéspedes de prueba
            print("👥 Insertando huéspedes de prueba...")
            first_names = ["Juan", "María", "Carlos", "Ana", "Luis", "Laura", "Pedro", "Sofía"]
            last_names = ["García", "Rodríguez", "González", "Fernández", "López", "Martínez", "Pérez", "Sánchez"]
            countries = ["España", "México", "Argentina", "Colombia", "Chile", "Perú"]
            
            guests = []
            for i in range(10):
                guest = {
                    "id": str(uuid.uuid4()),
                    "first_name": random.choice(first_names),
                    "last_name": random.choice(last_names),
                    "email": f"guest{i}@example.com",
                    "phone_number": f"+34{random.randint(600000000, 699999999)}",
                    "country": random.choice(countries),
                    "language_preference": random.choice(["es", "en", "fr"])
                }
                guests.append(guest)
            
            for guest in guests:
                await session.execute(text("""
                    INSERT INTO guests (id, first_name, last_name, email, phone_number, country, language_preference)
                    VALUES (:id, :first_name, :last_name, :email, :phone_number, :country, :language_preference)
                    ON CONFLICT (id) DO NOTHING
                """), guest)
            
            await session.commit()
            
            # 3. Insertar reservas de prueba
            print("📅 Insertando reservas de prueba...")
            room_type_names = ["Estándar", "Deluxe", "Suite"]
            
            for i, guest in enumerate(guests[:8]):  # 8 reservas
                check_in = datetime.now() + timedelta(days=random.randint(1, 30))
                check_out = check_in + timedelta(days=random.randint(1, 14))
                
                reservation = {
                    "id": str(uuid.uuid4()),
                    "guest_id": guest["id"],
                    "room_type": random.choice(room_type_names),
                    "check_in_date": check_in,
                    "check_out_date": check_out,
                    "number_of_guests": random.randint(1, 4),
                    "special_requests": random.choice([
                        "Cuna para bebé",
                        "Habitación sin alergenos",
                        "Vista al mar",
                        "Piso alto",
                        None
                    ]),
                    "status": random.choice(["confirmed", "checked_in", "checked_out"]),
                    "total_price": round(random.uniform(100, 1000), 2),
                    "payment_status": random.choice(["paid", "pending"])
                }
                
                await session.execute(text("""
                    INSERT INTO reservations (
                        id, guest_id, room_type, check_in_date, check_out_date,
                        number_of_guests, special_requests, status, total_price, payment_status
                    )
                    VALUES (
                        :id, :guest_id, :room_type, :check_in_date, :check_out_date,
                        :number_of_guests, :special_requests, :status, :total_price, :payment_status
                    )
                    ON CONFLICT (id) DO NOTHING
                """), reservation)
            
            await session.commit()
            
            # 4. Insertar logs de llamadas de prueba
            print("📞 Insertando logs de llamadas de prueba...")
            for i in range(15):
                call_log = {
                    "id": str(uuid.uuid4()),
                    "caller_number": f"+34{random.randint(600000000, 699999999)}",
                    "call_duration": random.randint(30, 600),
                    "intent_detected": random.choice(["reserva", "información", "check_in", "check_out", "servicios"]),
                    "resolution_status": random.choice(["automated", "transferred", "callback", "abandoned"])
                }
                
                await session.execute(text("""
                    INSERT INTO call_logs (id, caller_number, call_duration, intent_detected, resolution_status)
                    VALUES (:id, :caller_number, :call_duration, :intent_detected, :resolution_status)
                    ON CONFLICT (id) DO NOTHING
                """), call_log)
            
            await session.commit()
            
            print("✅ Datos de prueba importados correctamente")
            print(f"   - {len(room_types)} tipos de habitación")
            print(f"   - {len(guests)} huéspedes")
            print(f"   - 8 reservas")
            print(f"   - 15 logs de llamadas")
            
            return True
            
        except Exception as e:
            print(f"❌ Error importando datos: {e}")
            await session.rollback()
            return False

if __name__ == "__main__":
    success = asyncio.run(import_test_data())
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Script de inicialización de base de datos
"""
import sys
import os

# Agregar el directorio padre al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import create_tables, SessionLocal
from database.models import User
from backend.app.core.user_manager import UserManager

def init_database():
    """Inicializar base de datos con datos de prueba"""
    print("🔄 Inicializando base de datos...")
    
    # Crear tablas
    create_tables()
    print("✅ Tablas creadas")
    
    # Crear usuario admin de prueba
    db = SessionLocal()
    try:
        user_manager = UserManager(db)
        
        # Verificar si ya existe
        admin_user = db.query(User).filter(User.email == "admin@forge-saas.com").first()
        if not admin_user:
            admin_user = user_manager.create_user(
                email="admin@forge-saas.com",
                password="admin123",
                full_name="Admin User"
            )
            print("✅ Usuario admin creado")
        else:
            print("ℹ️  Usuario admin ya existe")
        
        # Estadísticas
        user_count = db.query(User).count()
        print(f"📊 Total usuarios en BD: {user_count}")
        
    finally:
        db.close()
    
    print("🎉 Base de datos inicializada correctamente")

if __name__ == "__main__":
    init_database()
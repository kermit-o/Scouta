import sys
import os
sys.path.append('/workspaces/Scouta/forge_saas')

from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Integer, ForeignKey, Text, Numeric, MetaData, Table
from sqlalchemy.orm import declarative_base
from datetime import datetime
import uuid

print("🔧 Configurando base de datos SQLite...")

# Usar SQLite para desarrollo rápido
SQLITE_PATH = "/tmp/forge_saas_subscriptions.db"
engine = create_engine(f"sqlite:///{SQLITE_PATH}", connect_args={"check_same_thread": False})
Base = declarative_base()

print("📝 Definiendo tablas de suscripción...")

# Definir tabla user_subscriptions
class UserSubscription(Base):
    __tablename__ = 'user_subscriptions'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    stripe_subscription_id = Column(String, unique=True)
    stripe_price_id = Column(String)
    status = Column(String, default='active')
    plan_type = Column(String, default='free')
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    cancel_at_period_end = Column(Boolean, default=False)
    monthly_projects_limit = Column(Integer, default=1)
    monthly_ai_requests_limit = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Definir tabla billing_history
class BillingHistory(Base):
    __tablename__ = 'billing_history'
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False)
    stripe_invoice_id = Column(String, unique=True)
    stripe_payment_intent_id = Column(String)
    stripe_subscription_id = Column(String)
    amount = Column(Numeric(10, 2))
    currency = Column(String(3), default='usd')
    status = Column(String)
    billing_reason = Column(String)
    description = Column(Text)
    invoice_pdf_url = Column(Text)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

print("🗃️ Creando tablas...")
Base.metadata.create_all(engine)

print("✅ ¡Tablas creadas exitosamente!")

# Verificar creación
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()

print(f"�� Tablas en la base de datos: {len(tables)}")
for table in tables:
    print(f"   🟢 {table}")
    
    # Mostrar columnas
    columns = inspector.get_columns(table)
    print(f"   📋 Columnas ({len(columns)}):")
    for col in columns[:5]:  # Mostrar primeras 5 columnas
        print(f"      - {col['name']} ({str(col['type'])[:30]}...)")
    if len(columns) > 5:
        print(f"      ... y {len(columns)-5} más")
    print()

print(f"🎉 Base de datos lista: {SQLITE_PATH}")

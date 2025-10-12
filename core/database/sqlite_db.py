import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLITE_PATH = "/tmp/forge_saas_subscriptions.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{SQLITE_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Para usar en los routers de pagos
def get_subscription_db():
    return get_db()

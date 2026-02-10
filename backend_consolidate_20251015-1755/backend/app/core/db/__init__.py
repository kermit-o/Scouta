"""
Core DB package - imports corregidos
"""
from backend.app.core.db.session import SessionLocal, get_db

# Exportar para uso externo
__all__ = ["SessionLocal", "get_db"]

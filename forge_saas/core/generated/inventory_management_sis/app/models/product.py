from core.db.session import Base
from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

# --- ENUMS GENERADOS ---

# -----------------------

class Product(Base):
    __tablename__ = "products"
    __table_args__ = {'schema': 'generated_inventory_management_sis'} # Esquema dinámico por proyecto

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku = Column(String)
    name = Column(String)
    description = Column(Text, nullable=True)
    quantity = Column(String)
    location_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    def __repr__(self):
        # Aseguramos que la representación siempre use una clave existente (ej. el id)
        first_field = list(model['fields'].keys())[1] if len(model['fields']) > 1 else 'id'
        return f"<Product(id='{self.id}', {first_field}='{getattr(self, first_field)}')>"

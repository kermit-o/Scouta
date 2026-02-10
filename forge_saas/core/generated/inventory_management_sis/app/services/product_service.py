# backend/generated/inventory_management_sis/app/services/product_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid

# Importamos los modelos ORM generados dinámicamente
from backend.generated.inventory_management_sis.app.models.product import Product, Location

# Esquema Pydantic simulado para la creación
class ProductCreate(object): # Usaríamos pydantic.BaseModel
    name: str
    sku: str
    description: Optional[str] = None
    quantity: int
    location_id: str # str porque viene como UUID

def create_product(db: Session, product_data: ProductCreate) -> Product:
    # 1. Verificar si la ubicación existe
    location_id_uuid = uuid.UUID(product_data.location_id)
    location = db.query(Location).filter(Location.id == location_id_uuid).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
        
    # 2. Crear el producto
    db_product = Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        quantity=product_data.quantity,
        location_id=location_id_uuid
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: str) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def move_product_inventory(db: Session, product_id: str, new_location_id: str, quantity_to_move: int) -> Product:
    # Lógica de Negocio: Mover inventario
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_location_uuid = uuid.UUID(new_location_id)
    new_location = db.query(Location).filter(Location.id == new_location_uuid).first()
    if not new_location:
        raise HTTPException(status_code=404, detail="New Location not found")

    if quantity_to_move <= 0:
        raise HTTPException(status_code=400, detail="Quantity to move must be positive")
    
    # 1. Asignar nueva ubicación
    product.location_id = new_location_uuid
    
    # 2. Asumimos que esta función solo re-asigna la ubicación, no ajusta el stock
    # Si fuera complejo, aquí se harían transacciones de stock.
    
    db.commit()
    db.refresh(product)
    return product

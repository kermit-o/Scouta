"""
Generador de Backend FastAPI - API REAL y FUNCIONAL
"""
from typing import Dict, Any, List


class FastAPIGenerator:
    def generate(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Genera un backend FastAPI completo y funcional"""
        print(f"🐍 Generando backend FastAPI para {spec['name']}")
        
        code_files = {}
        
        # Archivos de configuración
        code_files["requirements.txt"] = self._generate_requirements()
        code_files["main.py"] = self._generate_main_app(spec)
        
        # Configuración de base de datos
        code_files["database.py"] = self._generate_database_config()
        
        # Modelos, esquemas y routers para cada entidad
        for entity in spec["main_entities"]:
            code_files.update(self._generate_entity_code(entity))
        
        # Utilidades
        code_files["config.py"] = self._generate_config()
        code_files["__init__.py"] = ""
        
        print(f"✅ Backend FastAPI generado: {len(code_files)} archivos")
        return code_files
    
    def _generate_requirements(self) -> str:
        """Genera requirements.txt con dependencias reales"""
        return '''
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
python-dotenv==1.0.0
python-multipart==0.0.6
'''
    
    def _generate_main_app(self, spec: Dict[str, Any]) -> str:
        """Genera la aplicación principal FastAPI"""
        router_imports = "\n".join([
            f"from routers import {entity['name'].lower()}" for entity in spec["main_entities"]
        ])
        
        router_includes = "\n".join([
            f'app.include_router({entity["name"].lower()}.router, prefix="/api/{entity["name"].lower()}s", tags=["{entity["name"].lower()}s"])' 
            for entity in spec["main_entities"]
        ])
        
        return f'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
{router_imports}

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="{spec['name']} API",
    description="Generated API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
{router_includes}

@app.get("/")
async def root():
    return {{
        "message": "Welcome to {spec['name']} API",
        "version": "1.0.0",
        "endpoints": [{", ".join([f'"/api/{entity["name"].lower()}s"' for entity in spec["main_entities"]])}]
    }}

@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{spec['name']}-api"}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
    
    def _generate_database_config(self) -> str:
        """Genera configuración de base de datos"""
        return '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/app_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
    
    def _generate_entity_code(self, entity: Dict[str, Any]) -> Dict[str, str]:
        """Genera modelo, esquema y router para una entidad"""
        entity_name = entity["name"]
        entity_name_lower = entity_name.lower()
        
        code_files = {}
        
        # Modelo SQLAlchemy
        code_files[f"models/{entity_name_lower}.py"] = self._generate_model(entity)
        
        # Esquemas Pydantic
        code_files[f"schemas/{entity_name_lower}.py"] = self._generate_schemas(entity)
        
        # Router FastAPI
        code_files[f"routers/{entity_name_lower}.py"] = self._generate_router(entity)
        
        return code_files
    
    def _generate_model(self, entity: Dict[str, Any]) -> str:
        """Genera modelo SQLAlchemy"""
        fields = []
        for field in entity["fields"]:
            if field == "id":
                fields.append('    id = Column(String, primary_key=True, index=True)')
            elif field.endswith("_at"):
                fields.append(f'    {field} = Column(DateTime, default=datetime.utcnow)')
            elif field == "email":
                fields.append(f'    {field} = Column(String, unique=True, index=True)')
            else:
                fields.append(f'    {field} = Column(String)')
        
        fields_str = "\n".join(fields)
        
        return f'''
from sqlalchemy import Column, String, DateTime
from datetime import datetime
from database import Base

class {entity["name"]}(Base):
    __tablename__ = "{entity["name"].lower()}s"

{fields_str}

    def __repr__(self):
        return f"<{entity["name"]}(id={{self.id}}, name={{self.name}})>"
'''
    
    def _generate_schemas(self, entity: Dict[str, Any]) -> str:
        """Genera esquemas Pydantic"""
        base_fields = []
        create_fields = []
        
        for field in entity["fields"]:
            if field != "id" and not field.endswith("_at"):
                if field == "email":
                    base_fields.append(f'    {field}: str')
                    create_fields.append(f'    {field}: str')
                else:
                    base_fields.append(f'    {field}: Optional[str] = None')
                    create_fields.append(f'    {field}: Optional[str] = None')
        
        base_fields_str = "\n".join(base_fields)
        create_fields_str = "\n".join(create_fields)
        
        return f'''
from pydantic import BaseModel
from typing import Optional

class {entity["name"]}Base(BaseModel):
{base_fields_str}

class {entity["name"]}Create({entity["name"]}Base):
{create_fields_str}

class {entity["name"]}Response({entity["name"]}Base):
    id: str
    
    class Config:
        from_attributes = True
'''
    
    def _generate_router(self, entity: Dict[str, Any]) -> str:
        """Genera router FastAPI con operaciones CRUD"""
        entity_name = entity["name"]
        entity_name_lower = entity_name.lower()
        
        return f'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from database import get_db
from backend.app.models.{entity_name_lower} import {entity_name}
from schemas.{entity_name_lower} import {entity_name}Create, {entity_name}Response

router = APIRouter()

@router.get("/", response_model=List[{entity_name}Response])
def get_{entity_name_lower}s(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all {entity_name_lower}s"""
    {entity_name_lower}s = db.query({entity_name}).offset(skip).limit(limit).all()
    return {entity_name_lower}s

@router.post("/", response_model={entity_name}Response, status_code=status.HTTP_201_CREATED)
def create_{entity_name_lower}({entity_name_lower}: {entity_name}Create, db: Session = Depends(get_db)):
    """Create a new {entity_name_lower}"""
    db_{entity_name_lower} = {entity_name}(
        id=str(uuid.uuid4()),
        **{entity_name_lower}.dict()
    )
    db.add(db_{entity_name_lower})
    db.commit()
    db.refresh(db_{entity_name_lower})
    return db_{entity_name_lower}

@router.get("/{{{entity_name_lower}_id}}", response_model={entity_name}Response)
def get_{entity_name_lower}({entity_name_lower}_id: str, db: Session = Depends(get_db)):
    """Get a specific {entity_name_lower} by ID"""
    {entity_name_lower} = db.query({entity_name}).filter({entity_name}.id == {entity_name_lower}_id).first()
    if not {entity_name_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    return {entity_name_lower}

@router.put("/{{{entity_name_lower}_id}}", response_model={entity_name}Response)
def update_{entity_name_lower}({entity_name_lower}_id: str, {entity_name_lower}_update: {entity_name}Create, db: Session = Depends(get_db)):
    """Update a {entity_name_lower}"""
    db_{entity_name_lower} = db.query({entity_name}).filter({entity_name}.id == {entity_name_lower}_id).first()
    if not db_{entity_name_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    
    for field, value in {entity_name_lower}_update.dict().items():
        setattr(db_{entity_name_lower}, field, value)
    
    db.commit()
    db.refresh(db_{entity_name_lower})
    return db_{entity_name_lower}

@router.delete("/{{{entity_name_lower}_id}}", status_code=status.HTTP_204_NO_CONTENT)
def delete_{entity_name_lower}({entity_name_lower}_id: str, db: Session = Depends(get_db)):
    """Delete a {entity_name_lower}"""
    db_{entity_name_lower} = db.query({entity_name}).filter({entity_name}.id == {entity_name_lower}_id).first()
    if not db_{entity_name_lower}:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="{entity_name} not found"
        )
    
    db.delete(db_{entity_name_lower})
    db.commit()
    return None
'''
    
    def _generate_config(self) -> str:
        """Genera archivo de configuración"""
        return '''
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/app_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

settings = Settings()
'''
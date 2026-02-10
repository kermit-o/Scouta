"""
GENERADOR de proyectos - CORAZÓN del sistema
Genera proyectos COMPLETOS y FUNCIONALES basados en especificaciones
"""
from typing import Dict, Any
import uuid
import os


class ProjectGenerator:
    def __init__(self):
        self.generators = {}
        self._load_generators()
    
    def _load_generators(self):
        """Carga todos los generadores disponibles"""
        # Importar generadores específicos
        from generators.react_generator import ReactGenerator
        from generators.fastapi_generator import FastAPIGenerator
        from generators.database_generator import DatabaseGenerator
        
        self.generators = {
            "react": ReactGenerator(),
            "fastapi": FastAPIGenerator(),
            "database": DatabaseGenerator()
        }
    
    def generate_working_project(self, spec: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un proyecto COMPLETO y FUNCIONAL"""
        print(f"🚀 Generando proyecto: {spec['name']} ({spec['project_type']})")
        
        project_id = str(uuid.uuid4())
        
        try:
            # Generar cada componente del proyecto
            generated_code = {
                "frontend": self.generators["react"].generate(spec),
                "backend": self.generators["fastapi"].generate(spec),
                "database": self.generators["database"].generate(spec),
                "deployment": self._generate_deployment_config(spec)
            }
            
            # Crear estructura del proyecto
            project_structure = self._create_project_structure(project_id, generated_code)
            
            project = {
                "id": project_id,
                "name": spec["name"],
                "specification": spec,
                "generated_code": generated_code,
                "structure": project_structure,
                "status": "generated",
                "instructions": self._generate_setup_instructions(spec)
            }
            
            print(f"✅ Proyecto generado exitosamente: {project_id}")
            return project
            
        except Exception as e:
            print(f"❌ Error generando proyecto: {e}")
            return {
                "id": project_id,
                "name": spec["name"],
                "status": "error",
                "error": str(e)
            }
    
    def _generate_deployment_config(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Genera configuración de deployment"""
        return {
            "dockerfile": self._generate_dockerfile(spec),
            "docker_compose": self._generate_docker_compose(spec),
            "deployment_guide": self._generate_deployment_guide(spec)
        }
    
    def _generate_dockerfile(self, spec: Dict[str, Any]) -> str:
        """Genera Dockerfile para el proyecto"""
        return f'''
# Dockerfile for {spec['name']}
FROM node:18-alpine as frontend
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim as backend
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
'''
    
    def _generate_docker_compose(self, spec: Dict[str, Any]) -> str:
        """Genera docker-compose.yml"""
        return f'''
version: '3.8'
services:
  frontend:
    build:
      context: .
      dockerfile: Dockerfile
      target: frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend

  backend:
    build:
      context: .
      dockerfile: Dockerfile
      target: backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/{spec['name']}
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB={spec['name']}
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
'''
    
    def _generate_deployment_guide(self, spec: Dict[str, Any]) -> str:
        """Genera guía de despliegue"""
        return f'''
# Deployment Guide for {spec['name']}

## Prerequisites
- Docker and Docker Compose
- Git

## Quick Start
1. Clone the project
2. Run: docker-compose up -d
3. Access frontend: http://localhost:3000
4. Access backend API: http://localhost:8000
5. API documentation: http://localhost:8000/docs

## Production Deployment
1. Set environment variables
2. Configure reverse proxy (nginx)
3. Set up SSL certificates
4. Configure database backups
'''
    
    def _create_project_structure(self, project_id: str, generated_code: Dict[str, Any]) -> Dict[str, Any]:
        """Crea la estructura de archivos del proyecto"""
        structure = {
            "project_root": f"./generated/{project_id}",
            "frontend": f"./generated/{project_id}/frontend",
            "backend": f"./generated/{project_id}/backend", 
            "database": f"./generated/{project_id}/database",
            "deployment": f"./generated/{project_id}/deployment"
        }
        
        # Crear directorios
        for directory in structure.values():
            os.makedirs(directory, exist_ok=True)
        
        return structure
    
    def _generate_setup_instructions(self, spec: Dict[str, Any]) -> str:
        """Genera instrucciones de configuración"""
        return f'''
# Setup Instructions for {spec['name']}

## Development Setup

### Frontend ({spec['tech_stack']['frontend']})
1. cd frontend
2. npm install
3. npm start

### Backend ({spec['tech_stack']['backend']})
1. cd backend  
2. pip install -r requirements.txt
3. uvicorn main:app --reload

### Database
1. Start PostgreSQL
2. Run migrations: alembic upgrade head

## Features Included
{chr(10).join([f"- {feature}" for feature in spec['required_features']])}

## API Endpoints
- GET /api/{{entity}} - List all
- POST /api/{{entity}} - Create new
- GET /api/{{entity}}/{{id}} - Get by ID
- PUT /api/{{entity}}/{{id}} - Update
- DELETE /api/{{entity}}/{{id}} - Delete
'''
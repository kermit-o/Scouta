"""
Manager de Proyectos - Persistencia en base de datos
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from sqlalchemy.orm import Session

from database.models import Project, User
from backend.app.core.requirement_analyzer import RequirementAnalyzer
from backend.app.core.project_generator import ProjectGenerator

class ProjectManager:
    def __init__(self, db: Session):
        self.db = db
        self.analyzer = RequirementAnalyzer()
        self.generator = ProjectGenerator()
    
    async def create_project(self, user: User, requirements: str, project_name: str = None) -> Project:
        """Crear nuevo proyecto para un usuario"""
        # Analizar requerimientos
        specification = await self.analyzer.analyze(requirements)
        
        # Generar proyecto
        generated_project = self.generator.generate_working_project(specification)
        
        # Crear registro en base de datos
        project = Project(
            user_id=user.id,
            name=project_name or specification["name"],
            description=requirements,
            requirements=requirements,
            specification=specification,
            generated_code=generated_project.get("generated_code", {}),
            project_type=specification.get("project_type", "unknown"),
            status="generated",
            downloads_count=0,
            is_public=False
        )
        
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        
        return project
    
    def get_user_projects(self, user: User, limit: int = 50, offset: int = 0) -> List[Project]:
        """Obtener proyectos de un usuario"""
        return self.db.query(Project).filter(
            Project.user_id == user.id
        ).order_by(
            Project.created_at.desc()
        ).offset(offset).limit(limit).all()
    
    def get_project(self, project_id: str, user: User = None) -> Optional[Project]:
        """Obtener proyecto específico"""
        query = self.db.query(Project).filter(Project.id == project_id)
        
        if user:
            # Si se proporciona usuario, verificar propiedad
            query = query.filter(Project.user_id == user.id)
        else:
            # Solo proyectos públicos
            query = query.filter(Project.is_public == True)
        
        return query.first()
    
    def increment_download_count(self, project: Project) -> None:
        """Incrementar contador de descargas"""
        project.downloads_count += 1
        self.db.commit()
    
    def update_project_visibility(self, project: Project, is_public: bool) -> Project:
        """Actualizar visibilidad del proyecto"""
        project.is_public = is_public
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def delete_project(self, project: Project) -> None:
        """Eliminar proyecto"""
        self.db.delete(project)
        self.db.commit()
    
    def get_project_stats(self) -> Dict[str, Any]:
        """Estadísticas generales de proyectos"""
        total_projects = self.db.query(Project).count()
        public_projects = self.db.query(Project).filter(Project.is_public == True).count()
        
        # Proyectos por tipo
        from sqlalchemy import func
        projects_by_type = self.db.query(
            Project.project_type,
            func.count(Project.id)
        ).group_by(Project.project_type).all()
        
        return {
            "total_projects": total_projects,
            "public_projects": public_projects,
            "projects_by_type": dict(projects_by_type)
        }
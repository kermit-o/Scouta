# core/project_factory.py
from typing import Dict, Any, List
from enum import Enum
import json

class ProjectType(Enum):
    REACT_WEB_APP = "react_web_app"
    NEXTJS_APP = "nextjs_app"
    FLASK_API = "flask_api"
    FASTAPI_SERVICE = "fastapi_service"
    REACT_NATIVE_APP = "react_native_app"
    ELECTRON_DESKTOP = "electron_desktop"
    CHROME_EXTENSION = "chrome_extension"
    CUSTOM_AI_AGENT = "custom_ai_agent"

class ProjectFactory:
    def __init__(self):
        self.available_stacks = {
            ProjectType.REACT_WEB_APP: ["react", "typescript", "tailwind"],
            ProjectType.NEXTJS_APP: ["nextjs", "typescript", "tailwind", "prisma"],
            ProjectType.FASTAPI_SERVICE: ["fastapi", "sqlalchemy", "pydantic"],
            # ... más stacks
        }
    
    def generate_project(self, project_type: ProjectType, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Genera cualquier tipo de proyecto basado en requirements"""
        
        # 1. Analizar requirements con AI
        analyzed_req = self._analyze_requirements(requirements)
        
        # 2. Seleccionar stack tecnológico
        stack = self._select_technology_stack(project_type, analyzed_req)
        
        # 3. Generar arquitectura
        architecture = self._generate_architecture(project_type, stack)
        
        # 4. Crear archivos y estructura
        project_structure = self._create_project_structure(architecture)
        
        return project_structure
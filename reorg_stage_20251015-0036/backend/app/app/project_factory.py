from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel
import json

class ProjectType(Enum):
    REACT_WEB_APP = "react_web_app"
    NEXTJS_APP = "nextjs_app"
    VUE_APP = "vue_app"
    FASTAPI_SERVICE = "fastapi_service"
    NODEJS_API = "nodejs_api"
    REACT_NATIVE_MOBILE = "react_native_mobile"
    FLUTTER_APP = "flutter_app"
    ELECTRON_DESKTOP = "electron_desktop"
    TAURI_DESKTOP = "tauri_desktop"
    CHROME_EXTENSION = "chrome_extension"
    AI_AGENT = "ai_agent"
    BLOCKCHAIN_DAPP = "blockchain_dapp"
    IOT_SYSTEM = "iot_system"
    GAME_2D = "game_2d"
    GAME_3D = "game_3d"
    ECOMMERCE_STORE = "ecommerce_store"
    SAAS_BOILERPLATE = "saas_boilerplate"

class ProjectRequirements(BaseModel):
    name: str
    description: str
    project_type: ProjectType
    features: List[str]
    technologies: List[str] = []
    database: str = "postgresql"
    auth_required: bool = True
    payment_integration: bool = False
    deployment_target: str = "vercel"

class ProjectFactory:
    def __init__(self):
        self.technology_stacks = self._initialize_stacks()
    
    def _initialize_stacks(self) -> Dict[ProjectType, Dict[str, Any]]:
        return {
            ProjectType.REACT_WEB_APP: {
                "frontend": ["react", "typescript", "tailwind"],
                "backend": ["nodejs", "express"],
                "database": ["postgresql"],
                "deployment": ["vercel", "netlify"]
            },
            ProjectType.NEXTJS_APP: {
                "frontend": ["nextjs", "typescript", "tailwind"],
                "backend": ["nextjs_api", "prisma"],
                "database": ["postgresql", "mongodb"],
                "deployment": ["vercel", "aws"]
            },
            ProjectType.FASTAPI_SERVICE: {
                "backend": ["fastapi", "python", "sqlalchemy"],
                "database": ["postgresql", "sqlite"],
                "deployment": ["docker", "heroku", "aws"]
            },
            ProjectType.REACT_NATIVE_MOBILE: {
                "mobile": ["react_native", "typescript"],
                "backend": ["nodejs", "fastapi"],
                "database": ["postgresql", "firebase"],
                "deployment": ["app_store", "play_store"]
            },
            ProjectType.CHROME_EXTENSION: {
                "extension": ["manifest_v3", "javascript", "html"],
                "backend": ["optional"],
                "deployment": ["chrome_web_store"]
            },
            ProjectType.AI_AGENT: {
                "ai": ["langchain", "openai", "vector_db"],
                "backend": ["fastapi", "python"],
                "database": ["postgresql", "redis"],
                "deployment": ["docker", "aws"]
            },
            ProjectType.BLOCKCHAIN_DAPP: {
                "blockchain": ["web3", "ethers", "smart_contracts"],
                "frontend": ["react", "web3"],
                "backend": ["nodejs"],
                "deployment": ["ipfs", "ethereum"]
            }
        }
    
    def create_project(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Crea un proyecto completo basado en los requisitos"""
        
        # 1. Validar requisitos
        self._validate_requirements(requirements)
        
        # 2. Seleccionar stack tecnológico
        technology_stack = self._select_technology_stack(requirements)
        
        # 3. Generar arquitectura
        architecture = self._generate_architecture(requirements, technology_stack)
        
        # 4. Crear estructura de archivos
        project_structure = self._create_project_structure(architecture)
        
        return {
            "project_id": self._generate_project_id(),
            "name": requirements.name,
            "type": requirements.project_type,
            "architecture": architecture,
            "file_structure": project_structure,
            "technology_stack": technology_stack,
            "deployment_instructions": self._generate_deployment_instructions(requirements)
        }
    
    def _validate_requirements(self, requirements: ProjectRequirements):
        """Valida que los requisitos sean viables"""
        if not requirements.name:
            raise ValueError("El nombre del proyecto es requerido")
        
        if requirements.project_type not in self.technology_stacks:
            raise ValueError(f"Tipo de proyecto no soportado: {requirements.project_type}")
    
    def _select_technology_stack(self, requirements: ProjectRequirements) -> Dict[str, Any]:
        """Selecciona el stack tecnológico óptimo"""
        base_stack = self.technology_stacks[requirements.project_type].copy()
        
        # Personalizar stack basado en features específicos
        if "real_time" in requirements.features:
            base_stack["backend"].append("websockets")
            base_stack["database"].append("redis")
        
        if "ai_enhanced" in requirements.features:
            base_stack["ai"] = ["openai", "langchain"]
        
        return base_stack
    
    def _generate_architecture(self, requirements: ProjectRequirements, tech_stack: Dict) -> Dict[str, Any]:
        """Genera la arquitectura del proyecto"""
        return {
            "project_structure": self._get_base_structure(requirements.project_type),
            "components": self._select_components(requirements),
            "dependencies": self._get_dependencies(tech_stack),
            "configuration": self._get_configuration_files(requirements)
        }
    
    def _create_project_structure(self, architecture: Dict[str, Any]) -> List[Dict[str, str]]:
        """Crea la estructura de archivos del proyecto"""
        # Esto se integrará con el template engine
        return [
            {"path": "package.json", "type": "configuration", "content": "{}"},
            {"path": "src/index.js", "type": "source", "content": "// Main file"},
            {"path": "README.md", "type": "documentation", "content": "# Project"}
        ]
    
    def _generate_project_id(self) -> str:
        """Genera un ID único para el proyecto"""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_base_structure(self, project_type: ProjectType) -> List[str]:
        """Retorna la estructura base para cada tipo de proyecto"""
        structures = {
            ProjectType.REACT_WEB_APP: [
                "src/components/",
                "src/pages/", 
                "src/styles/",
                "public/",
                "package.json"
            ],
            ProjectType.FASTAPI_SERVICE: [
                "app/",
                "app/api/",
                "app/models/",
                "app/database/",
                "requirements.txt"
            ],
            ProjectType.CHROME_EXTENSION: [
                "manifest.json",
                "popup/",
                "background/",
                "content/",
                "icons/"
            ]
        }
        return structures.get(project_type, [])
    
    def _select_components(self, requirements: ProjectRequirements) -> List[str]:
        """Selecciona componentes basados en features"""
        components = []
        
        if requirements.auth_required:
            components.extend(["auth_system", "user_management"])
        
        if requirements.payment_integration:
            components.extend(["payment_processor", "billing_system"])
        
        if "admin_panel" in requirements.features:
            components.append("admin_dashboard")
        
        return components
    
    def _get_dependencies(self, tech_stack: Dict) -> Dict[str, List[str]]:
        """Genera dependencias basadas en el stack tecnológico"""
        return {
            "frontend": tech_stack.get("frontend", []),
            "backend": tech_stack.get("backend", []),
            "database": tech_stack.get("database", []),
            "devops": tech_stack.get("deployment", [])
        }
    
    def _get_configuration_files(self, requirements: ProjectRequirements) -> List[str]:
        """Lista archivos de configuración necesarios"""
        config_files = ["README.md", ".gitignore"]
        
        if requirements.project_type in [ProjectType.REACT_WEB_APP, ProjectType.NEXTJS_APP]:
            config_files.extend(["package.json", "tsconfig.json"])
        elif requirements.project_type == ProjectType.FASTAPI_SERVICE:
            config_files.extend(["requirements.txt", "alembic.ini"])
        
        return config_files
    
    def _generate_deployment_instructions(self, requirements: ProjectRequirements) -> Dict[str, str]:
        """Genera instrucciones de deployment específicas"""
        deployment_guides = {
            "vercel": "Deploy con: vercel --prod",
            "docker": "docker build -t project . && docker run -p 3000:3000 project",
            "heroku": "git push heroku main",
            "aws": "Configure EB CLI and deploy: eb deploy"
        }
        
        return {
            "target": requirements.deployment_target,
            "instructions": deployment_guides.get(requirements.deployment_target, "Consulta la documentación"),
            "status": "ready"
        }

# Ejemplo de uso
if __name__ == "__main__":
    factory = ProjectFactory()
    
    # Ejemplo: Crear una aplicación React
    requirements = ProjectRequirements(
        name="Mi Startup App",
        description="Una aplicación SaaS moderna con React y FastAPI",
        project_type=ProjectType.REACT_WEB_APP,
        features=["auth", "real_time", "admin_panel"],
        technologies=["react", "typescript", "tailwind"],
        auth_required=True,
        payment_integration=True,
        deployment_target="vercel"
    )
    
    project = factory.create_project(requirements)
    print("🎉 Proyecto creado exitosamente!")
    print(f"ID: {project['project_id']}")
    print(f"Tipo: {project['type']}")
    print(f"Tecnologías: {project['technology_stack']}")

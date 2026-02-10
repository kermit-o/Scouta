# generators/project_factory.py
from enum import Enum
from typing import Dict, Any

class ProjectType(Enum):
    WEB_APP = "web_app"
    MOBILE_APP = "mobile_app" 
    API_SERVICE = "api_service"
    DESKTOP_APP = "desktop_app"
    CHROME_EXTENSION = "chrome_extension"
    AI_AGENT = "ai_agent"
    GAME = "game"
    BLOCKCHAIN = "blockchain"

class ProjectFactory:
    def __init__(self):
        self.templates = self._load_templates()
    
    def create_project(self, project_type: ProjectType, requirements: Dict[str, Any]):
        # Lógica para crear cualquier tipo de proyecto
        pass
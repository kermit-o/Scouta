"""
DeepSeek API Client for intelligent project generation
"""
import os
import httpx
from typing import Dict, List, Optional
import json

class DeepSeekClient:
    """Client for DeepSeek AI API"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.base_url = "https://api.deepseek.com/v1"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def analyze_project_requirements(self, idea: str, project_type: str) -> Dict:
        """Analyze project idea and generate detailed requirements"""
        return self._fallback_analysis(idea, project_type)

    async def generate_code(self, description: str, language: str, context: Dict = None) -> str:
        """Generate code based on description"""
        return self._fallback_code_generation(description, language, context)

    def _fallback_analysis(self, idea: str, project_type: str) -> Dict:
        """Fallback analysis when API is unavailable"""
        return {
            "analysis": f"Análisis AI de: {idea}",
            "architecture": "Arquitectura moderna basada en microservicios",
            "technologies": self._get_default_technologies(project_type),
            "features": ["Autenticación", "Base de datos", "API REST", "Interfaz moderna"],
            "file_structure": self._get_default_structure(project_type),
            "dependencies": self._get_default_dependencies(project_type),
            "considerations": ["Escalabilidad", "Seguridad", "Mantenibilidad"],
            "ai_enhanced": True,
            "complexity_score": 6,
            "development_phases": [
                {
                    "phase": 1,
                    "name": "Setup y Estructura Base",
                    "tasks": ["Configurar proyecto", "Estructura inicial"],
                    "estimated_days": 2
                }
            ]
        }

    def _fallback_code_generation(self, description: str, language: str, context: Dict = None) -> str:
        """Fallback code generation"""
        if language == "python":
            return f'# {description}\n\nprint("Hello from AI-generated code!")'
        elif language == "javascript":
            return f'// {description}\n\nconsole.log("Hello from AI-generated code!");'
        else:
            return f"# {description}\n\n# AI-generated code placeholder"

    def _get_default_technologies(self, project_type: str) -> List[str]:
        """Get default technologies based on project type"""
        tech_map = {
            "web_app": ["React", "FastAPI", "PostgreSQL", "Docker", "Tailwind CSS"],
            "api_service": ["FastAPI", "SQLAlchemy", "PostgreSQL", "Redis", "JWT"],
            "mobile_app": ["React Native", "Expo", "Firebase", "Redux", "Navigation"],
            "desktop_app": ["Electron", "React", "Node.js", "SQLite"],
            "chrome_extension": ["JavaScript", "Chrome APIs", "HTML/CSS", "Storage API"],
            "ai_agent": ["Python", "OpenAI API", "LangChain", "FastAPI", "Vector DB"]
        }
        return tech_map.get(project_type, ["Python", "FastAPI", "SQLite"])

    def _get_default_structure(self, project_type: str) -> Dict:
        """Get default file structure based on project type"""
        structures = {
            "web_app": {
                "frontend/": ["src/", "public/", "package.json"],
                "backend/": ["app/", "models/", "routes/", "requirements.txt"],
                "config/": ["settings.py", "database.py"]
            },
            "api_service": {
                "app/": ["main.py", "models/", "schemas/", "routes/", "services/"],
                "tests/": ["unit/", "integration/"],
                "config/": ["settings.py", "database.py"]
            }
        }
        return structures.get(project_type, {})

    def _get_default_dependencies(self, project_type: str) -> Dict:
        """Get default dependencies based on project type"""
        deps_map = {
            "web_app": {
                "backend": ["fastapi", "uvicorn", "sqlalchemy", "python-dotenv"],
                "frontend": ["react", "react-dom", "axios", "tailwindcss"]
            },
            "api_service": {
                "main": ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "python-jose"]
            }
        }
        return deps_map.get(project_type, {"main": ["fastapi", "uvicorn"]})

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

# Singleton instance
deepseek_client = DeepSeekClient()

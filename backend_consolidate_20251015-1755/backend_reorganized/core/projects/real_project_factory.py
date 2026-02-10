"""
Real Project Factory - Generates actual project structures
"""
import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel

class ProjectType(str, Enum):
    WEB_APP = "web_app"
    API_SERVICE = "api_service"
    MOBILE_APP = "mobile_app"
    DESKTOP_APP = "desktop_app"
    CHROME_EXTENSION = "chrome_extension"
    AI_AGENT = "ai_agent"

class ProjectRequirements(BaseModel):
    name: str
    description: str
    project_type: ProjectType
    features: List[str] = []
    technologies: List[str] = []
    database: str = "sqlite"
    auth_required: bool = False
    payment_integration: bool = False
    deployment_target: str = "vercel"

class RealProjectFactory:
    """Generates real, working project structures"""
    
    def __init__(self):
        self.base_path = "generated_projects"
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load project templates"""
        return {
            ProjectType.WEB_APP: self._web_app_template(),
            ProjectType.API_SERVICE: self._api_service_template(),
            ProjectType.MOBILE_APP: self._mobile_app_template(),
        }
    
    def _web_app_template(self) -> Dict:
        """Template for web applications"""
        return {
            "structure": {
                "frontend/": {
                    "src/": {
                        "components/": {},
                        "pages/": {},
                        "styles/": {},
                        "utils/": {}
                    },
                    "public/": {
                        "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>{{project_name}}</title>\n</head>\n<body>\n    <div id=\"root\"></div>\n</body>\n</html>",
                        "favicon.ico": ""
                    },
                    "package.json": {
                        "name": "{{project_name}}",
                        "version": "1.0.0",
                        "scripts": {
                            "dev": "vite",
                            "build": "vite build",
                            "start": "vite preview"
                        },
                        "dependencies": {
                            "react": "^18.0.0",
                            "react-dom": "^18.0.0"
                        },
                        "devDependencies": {
                            "vite": "^4.0.0",
                            "@vitejs/plugin-react": "^4.0.0"
                        }
                    }
                },
                "backend/": {
                    "app/": {
                        "main.py": "from fastapi import FastAPI\nfrom fastapi.middleware.cors import CORSMiddleware\n\napp = FastAPI(title=\\\"{{project_name}} API\\\")\n\napp.add_middleware(\n    CORSMiddleware,\n    allow_origins=[\\\"*\\\"],\n    allow_credentials=True,\n    allow_methods=[\\\"*\\\"],\n    allow_headers=[\\\"*\\\"],\n)\n\n@app.get(\\\"/\\\")\nasync def root():\n    return {\\\"message\\\": \\\"{{project_name}} API is running\\\"}\n\n@app.get(\\\"/health\\\")\nasync def health():\n    return {\\\"status\\\": \\\"healthy\\\"}",
                        "models/": {},
                        "routes/": {}
                    },
                    "requirements.txt": "fastapi==0.104.1\nuvicorn[standard]==0.24.0\npython-multipart==0.0.6"
                },
                "README.md": "# {{project_name}}\n\n{{description}}\n\n## Getting Started\n\n### Frontend\n```bash\ncd frontend\nnpm install\nnpm run dev\n```\n\n### Backend\n```bash\ncd backend\npip install -r requirements.txt\npython -m app.main\n```"
            }
        }
    
    def _api_service_template(self) -> Dict:
        """Template for API services"""
        return {
            "structure": {
                "app/": {
                    "main.py": "from fastapi import FastAPI\n\napp = FastAPI(title=\\\"{{project_name}} API\\\")\n\n@app.get(\\\"/\\\")\nasync def root():\n    return {\\\"message\\\": \\\"{{project_name}} API is running\\\"}\n\n@app.get(\\\"/health\\\")\nasync def health():\n    return {\\\"status\\\": \\\"healthy\\\"}",
                    "models/": {},
                    "schemas/": {},
                    "routes/": {},
                    "services/": {}
                },
                "requirements.txt": "fastapi==0.104.1\nuvicorn[standard]==0.24.0\nsqlalchemy==2.0.23",
                "Dockerfile": "FROM python:3.11\n\nWORKDIR /app\n\nCOPY requirements.txt .\nRUN pip install --no-cache-dir -r requirements.txt\n\nCOPY . .\n\nCMD [\\\"uvicorn\\\", \\\"app.main:app\\\", \\\"--host\\\", \\\"0.0.0.0\\\", \\\"--port\\\", \\\"8000\\\"]",
                "README.md": "# {{project_name}} API\n\n{{description}}\n\n## Development\n\n```bash\npip install -r requirements.txt\nuvicorn app.main:app --reload\n```\n\n## Docker\n\n```bash\ndocker build -t {{project_name}} .\ndocker run -p 8000:8000 {{project_name}}\n```"
            }
        }
    
    def _mobile_app_template(self) -> Dict:
        """Template for mobile apps"""
        return {
            "structure": {
                "src/": {
                    "screens/": {},
                    "components/": {},
                    "navigation/": {},
                    "services/": {}
                },
                "package.json": {
                    "name": "{{project_name}}",
                    "main": "node_modules/expo/AppEntry.js",
                    "scripts": {
                        "start": "expo start",
                        "android": "expo start --android",
                        "ios": "expo start --ios",
                        "web": "expo start --web"
                    },
                    "dependencies": {
                        "react-native": "0.72.6",
                        "expo": "~49.0.0",
                        "react": "18.2.0"
                    }
                },
                "app.json": {
                    "expo": {
                        "name": "{{project_name}}",
                        "slug": "{{project_name_slug}}"
                    }
                }
            }
        }
    
    def create_project(self, requirements: ProjectRequirements) -> Dict:
        """Create a real project structure"""
        try:
            project_id = self._generate_project_id(requirements.name)
            project_path = os.path.join(self.base_path, project_id)
            
            # Create project directory
            os.makedirs(project_path, exist_ok=True)
            
            # Get template for project type
            template = self.templates.get(requirements.project_type, {})
            
            # Generate project structure
            self._generate_structure(project_path, template.get("structure", {}), requirements)
            
            # Create project metadata
            metadata = {
                "project_id": project_id,
                "name": requirements.name,
                "description": requirements.description,
                "type": requirements.project_type.value,
                "features": requirements.features,
                "technologies": requirements.technologies,
                "created_at": self._get_timestamp()
            }
            
            with open(os.path.join(project_path, "project.json"), "w") as f:
                json.dump(metadata, f, indent=2)
            
            return {
                "success": True,
                "project_id": project_id,
                "project_path": project_path,
                "project_name": requirements.name,
                "message": f"Project '{requirements.name}' created successfully",
                "next_steps": [
                    f"cd {project_path}",
                    "Review the generated structure",
                    "Install dependencies",
                    "Start development"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Project creation failed: {str(e)}",
                "project_id": None
            }
    
    def _generate_structure(self, base_path: str, structure: Dict, requirements: ProjectRequirements):
        """Recursively generate directory and file structure"""
        for name, content in structure.items():
            current_path = os.path.join(base_path, name)
            
            if name.endswith('/'):
                # It's a directory
                dir_name = name.rstrip('/')
                dir_path = os.path.join(base_path, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                if isinstance(content, dict):
                    self._generate_structure(dir_path, content, requirements)
                    
            elif isinstance(content, dict):
                # It's a file with content as dict (like package.json)
                file_path = os.path.join(base_path, name)
                content_str = self._render_template(content, requirements)
                with open(file_path, 'w') as f:
                    if name.endswith('.json'):
                        json.dump(content_str, f, indent=2)
                    else:
                        f.write(str(content_str))
                        
            else:
                # It's a file with string content
                file_path = os.path.join(base_path, name)
                content_str = self._render_template(content, requirements)
                with open(file_path, 'w') as f:
                    f.write(str(content_str))
    
    def _render_template(self, template, requirements: ProjectRequirements):
        """Render template with project data"""
        if isinstance(template, str):
            return (template
                    .replace("{{project_name}}", requirements.name)
                    .replace("{{description}}", requirements.description)
                    .replace("{{project_name_slug}}", requirements.name.lower().replace(' ', '-')))
        elif isinstance(template, dict):
            rendered = {}
            for key, value in template.items():
                rendered[key] = self._render_template(value, requirements)
            return rendered
        else:
            return template
    
    def _generate_project_id(self, project_name: str) -> str:
        """Generate a unique project ID"""
        import uuid
        import hashlib
        name_hash = hashlib.md5(project_name.encode()).hexdigest()[:8]
        return f"{project_name.lower().replace(' ', '-')}-{name_hash}"
    
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

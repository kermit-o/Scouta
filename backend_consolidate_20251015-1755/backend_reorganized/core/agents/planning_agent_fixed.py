"""
Planning Agent - Fixed version with proper inheritance
"""
from typing import Dict, Any, List
from core.agents.agent_base import AgentBase

class PlanningAgent(AgentBase):
    """Agent responsible for creating development plans"""
    
    def __init__(self):
        # Llamar al constructor de la clase padre correctamente
        super().__init__("PlanningAgent")
    
    def run(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Run method required by AgentBase"""
        return self.create_development_plan(project_spec)
    
    def create_development_plan(self, project_spec: Dict[str, Any]) -> Dict[str, Any]:
        """Create a development plan from project specifications"""
        try:
            # Ahora self.log debería funcionar porque hereda de AgentBase
            self.log(f"Creating development plan for: {project_spec.get('description', 'N/A')}")
            
            # Extract basic info
            description = project_spec.get('description', '')
            project_type = project_spec.get('project_type', 'web_app')
            
            # Create a simple but structured plan
            plan = {
                "project_structure": self._generate_project_structure(project_type),
                "tech_stack": self._generate_tech_stack(project_type),
                "development_steps": self._generate_development_steps(description, project_type),
                "file_structure": self._generate_file_structure(project_type),
                "dependencies": self._generate_dependencies(project_type)
            }
            
            result = {
                "status": "success",
                "plan": plan,
                "project_type": project_type,
                "summary": f"Plan generated for {project_type} project",
                "estimated_time": "2-4 weeks"
            }
            
            self.log("Development plan created successfully")
            return result
            
        except Exception as e:
            self.log(f"Error creating development plan: {e}")
            return {
                "status": "error",
                "error": str(e),
                "message": "Failed to create development plan"
            }
    
    def _generate_project_structure(self, project_type: str) -> List[str]:
        """Generate basic project structure"""
        structures = {
            "web_app": [
                "Frontend (React/Vue)",
                "Backend API (FastAPI/Node.js)", 
                "Database (SQLite/PostgreSQL)",
                "Authentication System",
                "UI Components"
            ],
            "mobile_app": [
                "Mobile Frontend (React Native/Flutter)",
                "Backend API",
                "Database",
                "Push Notifications",
                "App Store Deployment"
            ],
            "api": [
                "REST/GraphQL API",
                "Database Layer",
                "Authentication",
                "Documentation",
                "Testing Suite"
            ]
        }
        return structures.get(project_type, structures["web_app"])
    
    def _generate_tech_stack(self, project_type: str) -> Dict[str, List[str]]:
        """Generate technology stack recommendations"""
        stacks = {
            "web_app": {
                "frontend": ["React", "Vue.js", "TypeScript", "Tailwind CSS"],
                "backend": ["FastAPI", "Node.js", "Python", "Express"],
                "database": ["SQLite", "PostgreSQL", "MongoDB"],
                "deployment": ["Vercel", "Netlify", "Railway", "Docker"]
            },
            "mobile_app": {
                "mobile": ["React Native", "Flutter", "Expo"],
                "backend": ["Node.js", "Firebase", "Supabase"],
                "database": ["Firestore", "SQLite", "Realm"],
                "deployment": ["App Store", "Google Play", "TestFlight"]
            }
        }
        return stacks.get(project_type, stacks["web_app"])
    
    def _generate_development_steps(self, description: str, project_type: str) -> List[Dict[str, str]]:
        """Generate development steps"""
        steps = [
            {"step": "1", "title": "Project Setup", "description": "Initialize project structure and dependencies"},
            {"step": "2", "title": "Database Design", "description": "Design and implement database schema"},
            {"step": "3", "title": "Backend API", "description": "Develop REST API endpoints"},
            {"step": "4", "title": "Frontend UI", "description": "Create user interface components"},
            {"step": "5", "title": "Authentication", "description": "Implement user authentication system"},
            {"step": "6", "title": "Testing", "description": "Write and run tests"},
            {"step": "7", "title": "Deployment", "description": "Deploy to production environment"}
        ]
        return steps
    
    def _generate_file_structure(self, project_type: str) -> List[str]:
        """Generate recommended file structure"""
        if project_type == "web_app":
            return [
                "src/",
                "src/components/",
                "src/pages/", 
                "src/services/",
                "backend/",
                "backend/api/",
                "backend/models/",
                "package.json",
                "requirements.txt",
                "README.md"
            ]
        else:
            return [
                "src/",
                "tests/",
                "docs/",
                "config/",
                "package.json",
                "README.md"
            ]
    
    def _generate_dependencies(self, project_type: str) -> Dict[str, List[str]]:
        """Generate dependency recommendations"""
        deps = {
            "web_app": {
                "frontend": ["react", "react-dom", "axios", "tailwindcss"],
                "backend": ["fastapi", "uvicorn", "sqlalchemy", "pydantic"]
            },
            "mobile_app": {
                "dependencies": ["react-native", "expo", "axios", "async-storage"],
                "devDependencies": ["jest", "detox", "eslint"]
            }
        }
        return deps.get(project_type, deps["web_app"])

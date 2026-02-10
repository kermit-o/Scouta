"""
Simple Database Service for compatibility
"""
from typing import Dict, Any, List, Optional

class DatabaseService:
    """Simple database service for development"""
    
    def __init__(self):
        self.projects = {}
        self.users = {}
    
    def save_project(self, project_data: Dict[str, Any]) -> str:
        """Save project to database"""
        project_id = project_data.get('project_id')
        if project_id:
            self.projects[project_id] = project_data
            return project_id
        return None
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project from database"""
        return self.projects.get(project_id)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return list(self.projects.values())
    
    def update_project_status(self, project_id: str, status: str, **updates):
        """Update project status"""
        if project_id in self.projects:
            self.projects[project_id]['status'] = status
            self.projects[project_id].update(updates)
    
    def save_user(self, user_data: Dict[str, Any]) -> str:
        """Save user to database"""
        user_id = user_data.get('user_id')
        if user_id:
            self.users[user_id] = user_data
            return user_id
        return None
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user from database"""
        return self.users.get(user_id)

# Global instance
db_service = DatabaseService()

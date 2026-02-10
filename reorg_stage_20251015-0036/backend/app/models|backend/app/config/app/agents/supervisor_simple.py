import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
﻿import sys
import os
from typing import Dict, Any
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)

class SimpleSupervisor:
    def __init__(self):
        self.db_service = DatabaseService()
    
    def create_project_plan(self, requirements: str) -> Dict[str, Any]:
        """Create a simple project plan without CrewAI"""
        try:
            return {
                "status": "success",
                "project_plan": f"""
# Project Plan Generated

## Requirements Analysis
{requirements}

## Architecture
- Frontend: React with TypeScript
- Backend: Python FastAPI  
- Database: PostgreSQL
- Authentication: JWT

## Timeline
- Week 1: Setup and basic structure
- Week 2: Authentication system
- Week 3: Core functionality
- Week 4: Testing and deployment

## Recommended Team
- 1 Frontend developer
- 1 Backend developer
- 1 DevOps engineer
                """,
                "technology_stack": ["React", "Python", "FastAPI", "PostgreSQL", "JWT"]
            }
        except Exception as e:
            logger.error(f"Error creating project plan: {e}")
            return {"status": "error", "error": str(e)}from app.config.paths import setup_paths; setup_paths()
from app.config.paths import setup_paths; setup_paths()

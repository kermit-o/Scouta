import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
﻿import sys
import os
from typing import List, Dict, Any
import os
import logging
from dotenv import load_dotenv

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.services.database_service import DatabaseService

load_dotenv()
logger = logging.getLogger(__name__)


class SupervisorAgent:
    def __init__(self):
        self.llm_config = {
            "model": "deepseek-coder",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "temperature": 0.1
        }
        self.db_service = DatabaseService()
    
    def create_supervisor_agent(self) -> Agent:
        """Create the supervisor agent that coordinates all departments"""
        return Agent(
            role="Project Supervisor",
            goal="Oversee the entire software development process, coordinate between departments, "
                 "ensure project requirements are met, and maintain quality standards",
            backstory="You are an experienced project manager and technical lead with expertise in "
                     "software development lifecycle. You excel at coordinating multiple teams and "
                     "ensuring projects are delivered on time with high quality.",
            verbose=True,
            allow_delegation=True,
            llm_config=self.llm_config,
            max_iter=15
        )
    
    def orchestrate_project(self, user_id: str, project_name: str, requirements: str) -> Dict[str, Any]:
        """Orchestrate the entire project development process with database integration"""
        try:
            # Create project record in database
            project = self.db_service.create_project(user_id, project_name, requirements)
            
            # Create supervisor agent
            supervisor = self.create_supervisor_agent()
            
            # Create initial planning task
            planning_task = self.create_project_planning_task(requirements)
            
            # Form the crew
            project_crew = Crew(
                agents=[supervisor],
                tasks=[planning_task],
                process=Process.sequential,
                verbose=2
            )
            
            # Execute the initial planning phase
            result = project_crew.kickoff()
            
            # Update project in database
            self.db_service.update_project_result(project.id, result)
            
            return {
                "status": "success",
                "project_id": project.id,
                "result": result,
                "next_steps": "Proceed to design and development phases"
            }
            
        except Exception as e:
            logger.error(f"Error orchestrating project: {e}")
            return {
                "status": "error",
                "error": str(e),
                "next_steps": "Review requirements and try again"
            }from app.config.paths import setup_paths; setup_paths()
from app.config.paths import setup_paths; setup_paths()

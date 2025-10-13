import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
﻿# backend/app/agents/planning_agent.py
from crewai import Agent, Task
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

class PlanningAgent:
    def __init__(self):
        self.llm_config = {
            "model": "deepseek-coder",
            "api_key": os.getenv("DEEPSEEK_API_KEY"),
            "temperature": 0.2
        }
    
    def create_planning_agent(self) -> Agent:
        """Create the planning department agent"""
        return Agent(
            role="Software Project Planner",
            goal="Analyze user requirements and create comprehensive project plans, "
                 "technical specifications, and architecture designs",
            backstory="You are an expert software architect and project planner with "
                     "years of experience in converting business requirements into "
                     "technical specifications. You excel at creating detailed project "
                     "plans that consider scalability, maintainability, and best practices.",
            verbose=True,
            allow_delegation=False,
            llm_config=self.llm_config
        )
    
    def create_requirements_analysis_task(self, user_requirements: str) -> Task:
        """Create task for requirements analysis"""
        return Task(
            description=f"""
            Conduct thorough analysis of the following user requirements:
            
            {user_requirements}
            
            Your analysis should include:
            1. Functional requirements breakdown
            2. Non-functional requirements (performance, security, scalability)
            3. User stories and use cases
            4. Technical constraints and considerations
            5. Dependencies and assumptions
            
            Provide a structured analysis that can be used by other departments.
            """,
            agent=self.create_planning_agent(),
            expected_output="A detailed requirements analysis document in markdown format with clear sections for functional and non-functional requirements."
        )
    
    def create_architecture_design_task(self, requirements_analysis: str) -> Task:
        """Create task for architecture design"""
        return Task(
            description=f"""
            Based on the following requirements analysis, design the system architecture:
            
            {requirements_analysis}
            
            Create a comprehensive architecture design including:
            1. System architecture diagram (describe in text)
            2. Component breakdown
            3. Technology stack recommendations
            4. Database design
            5. API design (if applicable)
            6. Deployment architecture
            
            Ensure the design is scalable, maintainable, and follows best practices.
            """,
            agent=self.create_planning_agent(),
            expected_output="A detailed architecture design document with technology recommendations and system components description."
        )

# Example integration with supervisor
def create_planning_phase_tasks(user_requirements: str):
    """Helper function to create planning phase tasks"""
    planner = PlanningAgent()
    
    requirements_task = planner.create_requirements_analysis_task(user_requirements)
    architecture_task = planner.create_architecture_design_task("{{output of requirements analysis}}")
    
    return [requirements_task, architecture_task]from app.config.paths import setup_paths; setup_paths()
from app.config.paths import setup_paths; setup_paths()

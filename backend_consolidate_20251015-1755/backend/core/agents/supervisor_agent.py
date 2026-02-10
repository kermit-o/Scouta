"""
Project Supervisor Agent - Coordinates the project generation workflow
"""
from typing import Dict, Any, List
import uuid
from datetime import datetime

from core.agents.agent_base import AgentBase
from core.agents.intake_agent import IntakeAgent
from core.agents.enhanced_intake_agent import EnhancedIntakeAgent
from core.agents.specification_agent import SpecificationAgent
from core.agents.data_design_agent import DataDesignAgent
from core.agents.planning_agent import PlanningAgent
from core.agents.builder_agent import BuilderAgent
from core.agents.documenter_agent import DocumenterAgent
from core.agents.tester_agent import TesterAgent
from core.agents.mockup_agent import MockupAgent
from core.agents.security_agent import SecurityAgent
from core.agents.scaffolder_agent import ScaffolderAgent
from core.agents.validation_agent import ValidationAgent

class ProjectSupervisor(AgentBase):
    """Main supervisor that coordinates all agents in the project generation pipeline"""
    
    def __init__(self):
        super().__init__("ProjectSupervisor")
        self.agents = {
            'intake': IntakeAgent(),
            'enhanced_intake': EnhancedIntakeAgent(),
            'specification': SpecificationAgent(),
            'data_design': DataDesignAgent(),
            'planning': PlanningAgent(),
            'scaffolding': ScaffolderAgent(),
            'builder': BuilderAgent(),
            'mockup': MockupAgent(),
            'security': SecurityAgent(),
            'documentation': DocumenterAgent(),
            'testing': TesterAgent(),
            'validation': ValidationAgent()
        }
        
    def create_project(self, user_input: str, project_type: str = "web_app") -> Dict[str, Any]:
        """Main method to create a complete project"""
        try:
            project_id = str(uuid.uuid4())
            self.log(f"Starting project creation: {project_id}")
            
            # Step 1: Enhanced Intake
            self.log("Running Enhanced Intake Agent...")
            intake_result = self.agents['enhanced_intake'].analyze_requirements(user_input, project_type)
            
            # Step 2: Specification
            self.log("Running Specification Agent...")
            spec_result = self.agents['specification'].create_specification(intake_result)
            
            # Step 3: Data Design
            self.log("Running Data Design Agent...")
            data_result = self.agents['data_design'].design_data_models(spec_result)
            
            # Step 4: Planning
            self.log("Running Planning Agent...")
            plan_result = self.agents['planning'].create_development_plan(data_result)
            
            # Step 5: Scaffolding
            self.log("Running Scaffolding Agent...")
            scaffold_result = self.agents['scaffolding'].run(project_id, plan_result, "generated_projects")
            
            # Step 6: Building
            self.log("Running Builder Agent...")
            build_result = self.agents['builder'].build_project(project_id, plan_result, "generated_projects")
            
            # Step 7: Mockup Generation
            self.log("Running Mockup Agent...")
            mockup_result = self.agents['mockup'].generate_mockups(plan_result)
            
            # Step 8: Security Review
            self.log("Running Security Agent...")
            security_result = self.agents['security'].review_security(plan_result)
            
            # Step 9: Documentation
            self.log("Running Documentation Agent...")
            doc_result = self.agents['documentation'].generate_documentation(plan_result)
            
            # Step 10: Testing
            self.log("Running Testing Agent...")
            test_result = self.agents['testing'].create_test_suite(plan_result)
            
            # Step 11: Validation
            self.log("Running Validation Agent...")
            validation_result = self.agents['validation'].validate_project(plan_result)
            
            # Compile final result
            final_result = {
                "project_id": project_id,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
                "results": {
                    "intake": intake_result,
                    "specification": spec_result,
                    "data_design": data_result,
                    "planning": plan_result,
                    "scaffolding": scaffold_result,
                    "building": build_result,
                    "mockups": mockup_result,
                    "security": security_result,
                    "documentation": doc_result,
                    "testing": test_result,
                    "validation": validation_result
                },
                "project_directory": scaffold_result.get("project_dir", f"generated_projects/{project_id}")
            }
            
            self.log(f"Project creation completed: {project_id}")
            return final_result
            
        except Exception as e:
            self.log(f"Project creation failed: {str(e)}")
            return {
                "project_id": project_id if 'project_id' in locals() else str(uuid.uuid4()),
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_agent_status(self) -> Dict[str, str]:
        """Get status of all agents"""
        return {name: "active" for name in self.agents.keys()}

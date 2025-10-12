import logging
import uuid
from typing import Dict, Any, Tuple
from datetime import datetime

from core.services.requirements_validator import requirements_validator
from core.app.agents.supervisor_simple import ProjectSupervisorSimple
from backend.generators.fastapi_generator import FastAPIGenerator
from backend.generators.react_generator import ReactGenerator

logger = logging.getLogger(__name__)

class EthicalProjectGenerator:
    """
    Generates projects ETHICALLY by:
    1. Validating user requirements are feasible
    2. Only generating when confident in delivery
    3. Providing transparent status updates
    4. Not generating demo/fake projects
    """
    
    def __init__(self):
        self.validator = requirements_validator
        self.supervisor = ProjectSupervisorSimple()
        self.fastapi_gen = FastAPIGenerator()
        self.react_gen = ReactGenerator()
        
        # Track projects ethically
        self.projects = {}
    
    def create_ethical_project(self, user_input: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """Create a new project only if requirements are valid and feasible"""
        
        # Step 1: Validate requirements
        is_valid, errors, specifications = self.validator.validate_requirements(user_input)
        
        if not is_valid:
            return False, " | ".join(errors), {}
        
        # Step 2: Check technical feasibility
        feasibility_ok, feasibility_errors = self._check_technical_feasibility(specifications)
        if not feasibility_ok:
            return False, " | ".join(feasibility_errors), {}
        
        # Step 3: Create project record
        project_id = str(uuid.uuid4())
        
        self.projects[project_id] = {
            "id": project_id,
            "name": specifications['project_name'],
            "specifications": specifications,
            "status": "validated",
            "user_input": user_input,
            "created_at": datetime.now().isoformat(),
            "estimated_complexity": specifications.get('complexity', 'medium'),
            "validation_errors": [],
            "generation_attempts": 0
        }
        
        logger.info(f"✅ Project {project_id} validated ethically: {specifications['project_name']}")
        
        return True, project_id, specifications
    
    def generate_ethical_project(self, project_id: str) -> Tuple[bool, str, Dict[str, Any]]:
        """Generate project only if validation passed and system is ready"""
        
        if project_id not in self.projects:
            return False, "Project not found", {}
        
        project = self.projects[project_id]
        
        # Check if project was properly validated
        if project['status'] != 'validated':
            return False, "Project not properly validated", {}
        
        # Check system readiness
        if not self._is_system_ready():
            return False, "AI system not ready for ethical generation", {}
        
        try:
            logger.info(f"🚀 Generating ethical project {project_id}")
            
            # Update status
            project['status'] = 'generating'
            project['generation_attempts'] += 1
            project['generation_started_at'] = datetime.now().isoformat()
            
            # Prepare specifications for generators
            specs = self._prepare_generation_specs(project['specifications'])
            
            # Generate using REAL generators
            backend_code = self.fastapi_gen.generate(specs)
            frontend_code = self.react_gen.generate(specs)
            
            # Combine results
            generated_code = {**backend_code, **frontend_code}
            
            # Update project status
            project['status'] = 'completed'
            project['generated_code'] = generated_code
            project['file_count'] = len(generated_code)
            project['completed_at'] = datetime.now().isoformat()
            project['generation_successful'] = True
            
            logger.info(f"✅ Ethical generation completed for {project_id}: {project['file_count']} files")
            
            return True, "Project generated successfully", {
                "project_id": project_id,
                "file_count": project['file_count'],
                "generated_files": list(generated_code.keys())[:10]  # First 10 files
            }
            
        except Exception as e:
            logger.error(f"❌ Ethical generation failed for {project_id}: {e}")
            
            # Update project status
            project['status'] = 'failed'
            project['generation_error'] = str(e)
            project['completed_at'] = datetime.now().isoformat()
            project['generation_successful'] = False
            
            return False, f"Generation failed: {str(e)}", {}
    
    def _check_technical_feasibility(self, specifications: Dict[str, Any]) -> Tuple[bool, list]:
        """Check if the project is technically feasible with current system"""
        
        errors = []
        
        # Check complexity
        complexity = specifications.get('complexity')
        if complexity == "high":
            errors.append("High complexity projects require manual review")
        
        # Check entity count
        entities = specifications.get('entities', [])
        if len(entities) > 10:
            errors.append("Too many entities for automated generation")
        
        # Check feature complexity
        features = specifications.get('features', [])
        complex_features = ['reports', 'notifications', 'export']
        if any(feat in features for feat in complex_features):
            errors.append("Complex features may require custom implementation")
        
        return len(errors) == 0, errors
    
    def _is_system_ready(self) -> bool:
        """Check if the AI system is ready for ethical generation"""
        
        try:
            # Test if generators are working
            test_spec = {"name": "test", "main_entities": [{"name": "Test", "fields": []}]}
            self.fastapi_gen.generate(test_spec)
            self.react_gen.generate(test_spec)
            
            # Test if agents are available
            if hasattr(self.supervisor, 'agent_sequence'):
                return len(self.supervisor.agent_sequence) > 0
            
            return True
            
        except Exception as e:
            logger.error(f"System readiness check failed: {e}")
            return False
    
    def _prepare_generation_specs(self, specifications: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare specifications for code generators"""
        
        entities = specifications.get('entities', [])
        
        # Convert to generator format
        main_entities = []
        for entity in entities:
            main_entities.append({
                "name": entity["name"],
                "fields": entity["fields"]
            })
        
        return {
            "name": specifications['project_name'],
            "main_entities": main_entities,
            "description": specifications.get('user_input', {}).get('description', ''),
            "technical_requirements": specifications.get('technical_requirements', {})
        }
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get transparent project status"""
        
        if project_id not in self.projects:
            return {"exists": False, "error": "Project not found"}
        
        project = self.projects[project_id]
        
        status_info = {
            "exists": True,
            "project_id": project_id,
            "name": project['name'],
            "status": project['status'],
            "created_at": project['created_at'],
            "complexity": project['estimated_complexity'],
            "validation_passed": project['status'] != 'failed'
        }
        
        if project['status'] == 'completed':
            status_info.update({
                "file_count": project.get('file_count', 0),
                "completed_at": project.get('completed_at'),
                "generation_successful": project.get('generation_successful', False)
            })
        elif project['status'] == 'failed':
            status_info['error'] = project.get('generation_error', 'Unknown error')
        
        return status_info

# Global instance
ethical_generator = EthicalProjectGenerator()

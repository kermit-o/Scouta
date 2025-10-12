from .agent_base import AgentBase
from typing import Dict, Any

class DocumenterAgent(AgentBase):
    """Agent for generating project documentation"""
    
    def __init__(self):
        super().__init__("Documenter Agent")
    
    def run(self, project_id: str, requirements: dict) -> dict:
        """Generate comprehensive project documentation"""
        self.log_activity(f"Generating documentation for project {project_id}")
        
        # Collect all previous outputs
        analysis = requirements.get('analysis', '')
        specifications = requirements.get('specifications', '') 
        architecture = requirements.get('architecture_plan', '')
        generated_code = requirements.get('generated_code', '')
        
        prompt = f"""
        Based on the complete project information, generate comprehensive documentation:
        
        PROJECT ANALYSIS:
        {analysis}
        
        TECHNICAL SPECIFICATIONS:
        {specifications}
        
        ARCHITECTURE PLAN:
        {architecture}
        
        GENERATED CODE:
        {generated_code}
        
        Create complete documentation including:
        1. README.md with setup instructions
        2. API documentation
        3. Architecture overview
        4. Deployment guide
        5. User manual
        """
        
        try:
            documentation = self.generate_ai_response(
                prompt,
                "You are a technical writer specializing in software documentation."
            )
            
            return {
                "project_id": project_id,
                "status": "completed",
                "documentation": documentation,
                "documents_generated": ["README.md", "API_DOCS.md", "ARCHITECTURE.md"]
            }
        except Exception as e:
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }

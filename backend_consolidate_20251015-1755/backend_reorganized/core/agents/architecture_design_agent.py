# core/app/agents/architecture_design_agent.py
from typing import Dict, Any, List
from enum import Enum
from core.agents.agent_base import AgentBase

class ArchitecturePattern(Enum):
    MONOLITH = "monolith"
    MICROSERVICES = "microservices"
    EVENT_DRIVEN = "event_driven"
    CQRS = "cqrs"
    SERVERLESS = "serverless"
    HYBRID = "hybrid"

class ArchitectureDesignAgent(AgentBase):
    """Specialized agent for designing complex architectures"""
    
    def __init__(self):
        super().__init__("Architecture Design Agent")
        self.pattern_decision_matrix = {
            "high_scalability": ArchitecturePattern.MICROSERVICES,
            "real_time_processing": ArchitecturePattern.EVENT_DRIVEN,
            "complex_read_queries": ArchitecturePattern.CQRS,
            "cost_optimization": ArchitecturePattern.SERVERLESS,
            "rapid_development": ArchitecturePattern.MONOLITH,
            "mixed_workloads": ArchitecturePattern.HYBRID
        }
    
    async def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design optimal architecture for complex projects"""
        
        enhanced_analysis = requirements.get('enhanced_analysis', {})
        complexity_score = requirements.get('complexity_score', 5)
        
        self.log_activity(f"Designing architecture for project {project_id} (complexity: {complexity_score})")
        
        architecture_plan = self._design_architecture(enhanced_analysis, complexity_score)
        
        return {
            "project_id": project_id,
            "status": "completed",
            "architecture_design": architecture_plan,
            "recommended_patterns": self._select_architecture_patterns(enhanced_analysis),
            "component_breakdown": self._breakdown_components(architecture_plan),
            "technology_recommendations": self._recommend_technologies(architecture_plan)
        }
    
    def _design_architecture(self, analysis: Dict[str, Any], complexity: int) -> Dict[str, Any]:
        """Design architecture based on analysis and complexity"""
        
        prompt = f"""
        Design a comprehensive software architecture based on this analysis:
        
        ANALYSIS: {analysis}
        COMPLEXITY SCORE: {complexity}/10
        
        Create a detailed architecture design including:
        1. High-level architecture diagram description
        2. Component decomposition
        3. Data flow design
        4. API design strategy
        5. Database architecture
        6. Caching strategy
        7. Message queue/event bus design if needed
        8. Security architecture
        9. Deployment topology
        10. Monitoring and observability strategy
        
        Focus on scalability, maintainability, and performance.
        """
        
        return self.generate_structured_response(
            prompt,
            context="Eres un arquitecto de software empresarial con experiencia en sistemas distribuidos."
        )
    
    def _select_architecture_patterns(self, analysis: Dict[str, Any]) -> List[str]:
        """Select appropriate architecture patterns"""
        selected_patterns = []
        requirements = analysis.get('scalability_requirements', [])
        
        if "alto_trafico" in requirements:
            selected_patterns.append(ArchitecturePattern.MICROSERVICES.value)
        
        if any(req in requirements for req in ["tiempo_real", "event_driven"]):
            selected_patterns.append(ArchitecturePattern.EVENT_DRIVEN.value)
            
        if len(analysis.get('integration_points', [])) > 3:
            selected_patterns.append(ArchitecturePattern.HYBRID.value)
        
        return selected_patterns if selected_patterns else [ArchitecturePattern.MONOLITH.value]
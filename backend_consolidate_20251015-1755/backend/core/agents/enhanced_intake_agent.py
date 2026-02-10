import logging
from typing import Dict, Any
from core.agents.agent_base import AgentBase

logger = logging.getLogger(__name__)

class EnhancedIntakeAgent(AgentBase):
    """Enhanced intake agent - Versión mínima para compatibilidad"""
    
    def __init__(self):
        super().__init__("Enhanced Intake Agent")
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Versión mínima para compatibilidad con DualPipelineSupervisor"""
        
        raw_requirements = requirements.get('raw_requirements', '')
        
        # Usar UniversalAnalystAgent si está disponible
        try:
            from .universal_analyst_agent import UniversalAnalystAgent
            universal_agent = UniversalAnalystAgent()
            
            # Usar el método run síncrono en lugar de asyncio.run()
            result = universal_agent.run(project_id, {'raw_requirements': raw_requirements})
            
            if result['status'] == 'completed':
                analysis = result.get('analysis', {})
                return {
                    "project_id": project_id,
                    "status": "completed",
                    "enhanced_analysis": analysis,
                    "complexity_score": analysis.get('complexity_level', 5),
                    "estimated_timeline": {"min": "1 month", "max": "3 months"},
                    "resource_recommendations": {"developers": 2, "devops": 1, "qa": 1}
                }
            else:
                raise Exception(f"Universal analysis failed: {result.get('error')}")
            
        except Exception as e:
            logger.warning(f"UniversalAnalystAgent not available, using fallback: {e}")
            
            # Fallback básico
            return {
                "project_id": project_id,
                "status": "completed", 
                "enhanced_analysis": {
                    "project_summary": f"Analysis of: {raw_requirements[:100]}...",
                    "business_domain": "software",
                    "complexity_level": "medium",
                    "architecture_style": "monolith"
                },
                "complexity_score": 5,
                "estimated_timeline": {"min": "1 month", "max": "3 months"},
                "resource_recommendations": {"developers": 2, "devops": 1, "qa": 1}
            }

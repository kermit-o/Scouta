# core/ai_orchestrator.py
import openai
from typing import Dict, Any

class AIOrchestrator:
    def __init__(self):
        self.specialized_agents = {
            "architect": "Eres un arquitecto de software experto...",
            "frontend_expert": "Eres un desarrollador frontend senior...", 
            "backend_expert": "Eres un ingeniero backend especializado...",
            "devops_expert": "Eres un ingeniero DevOps...",
            "mobile_expert": "Eres un desarrollador mobile...",
        }
    
    def orchestrate_generation(self, project_type: str, requirements: Dict[str, Any]):
        """Orquestra múltiples agentes AI para generar el proyecto"""
        
        # Agente arquitecto diseña la estructura
        architecture = self._call_agent("architect", {
            "project_type": project_type,
            "requirements": requirements
        })
        
        # Múltiples agentes generan diferentes partes
        components = {}
        for component, prompt in self.specialized_agents.items():
            components[component] = self._call_agent(component, {
                "architecture": architecture,
                "requirements": requirements
            })
        
        return self._merge_components(components)
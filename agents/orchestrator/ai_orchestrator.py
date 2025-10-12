from agents.deepseek_client import DeepSeekClient
from typing import Dict, Any, List
import json

class AIOrchestrator:
    def __init__(self, api_key: str = None):
        self.client = DeepSeekClient() 
        self.specialized_agents = self._initialize_agents()
    
    def _initialize_agents(self) -> Dict[str, Dict]:
        return {
            "architect": {
                "role": "system",
                "content": """Eres un arquitecto de software senior con 15+ años de experiencia.
                Diseñas arquitecturas escalables, mantenibles y seguras.
                Especialista en microservicios, cloud-native y best practices.
                Siempre consideras costos, performance y mantenibilidad."""
            },
            "frontend_expert": {
                "role": "system", 
                "content": """Eres un desarrollador frontend senior experto en React, Vue, Angular, Svelte.
                Conoces todas las mejores prácticas de UI/UX, performance y accesibilidad.
                Especialista en TypeScript, estado global, y optimización."""
            },
            "backend_expert": {
                "role": "system",
                "content": """Eres un ingeniero backend senior experto en APIs, bases de datos y microservicios.
                Dominas FastAPI, Node.js, Python, bases de datos SQL/NoSQL, caching, y seguridad.
                Especialista en diseño de APIs RESTful y GraphQL."""
            },
            "devops_expert": {
                "role": "system",
                "content": """Eres un ingeniero DevOps senior experto en Docker, Kubernetes, CI/CD y cloud.
                Conoces AWS, GCP, Azure, y todas las herramientas modernas de deployment.
                Especialista en infraestructura como código y monitoreo."""
            },
            "mobile_expert": {
                "role": "system",
                "content": """Eres un desarrollador mobile senior experto en React Native, Flutter, iOS nativo y Android nativo.
                Conoces todas las peculiaridades de desarrollo mobile y stores.
                Especialista en performance mobile y UX nativa."""
            },
            "ai_specialist": {
                "role": "system",
                "content": """Eres un científico de datos senior experto en machine learning, LLMs y AI.
                Dominas LangChain, OpenAI, vector databases, y arquitecturas de AI agents.
                Especialista en integrar AI en aplicaciones de producción."""
            }
        }
    
    def orchestrate_project_creation(self, user_prompt: str, project_type: str) -> Dict[str, Any]:
        """Orquestra la creación de un proyecto usando múltiples agentes especializados"""
        
        # 1. Análisis de requisitos con el arquitecto
        architecture = self._consult_architect(user_prompt, project_type)
        
        # 2. Diseño frontend con el experto frontend
        frontend_design = self._consult_frontend_expert(architecture, project_type)
        
        # 3. Diseño backend con el experto backend  
        backend_design = self._consult_backend_expert(architecture, project_type)
        
        # 4. Plan de deployment con DevOps
        deployment_plan = self._consult_devops_expert(architecture, project_type)
        
        # 5. Combinar todos los diseños
        complete_project = self._combine_designs(
            architecture, 
            frontend_design, 
            backend_design, 
            deployment_plan
        )
        
        return complete_project
    
    def _consult_architect(self, user_prompt: str, project_type: str) -> Dict[str, Any]:
        """Consulta al arquitecto para el diseño general"""
        prompt = f"""
        Usuario quiere: {user_prompt}
        Tipo de proyecto: {project_type}
        
        Como arquitecto senior, diseña:
        1. Arquitectura general del sistema
        2. Componentes principales necesarios
        3. Tecnologías recomendadas
        4. Consideraciones de escalabilidad
        5. Posibles desafíos técnicos
        
        Responde en formato JSON con: architecture, components, technologies, challenges
        """
        
        response = self._call_agent("architect", prompt)
        return json.loads(response)
    
    def _consult_frontend_expert(self, architecture: Dict, project_type: str) -> Dict[str, Any]:
        """Consulta al experto frontend"""
        prompt = f"""
        Basado en esta arquitectura: {json.dumps(architecture, indent=2)}
        Tipo de proyecto: {project_type}
        
        Como experto frontend, diseña:
        1. Stack tecnológico frontend específico
        2. Estructura de componentes
        3. Gestión de estado
        4. Estilos y UI framework
        5. Optimizaciones de performance
        
        Responde en formato JSON con: frontend_stack, component_structure, state_management, styling, optimizations
        """
        
        response = self._call_agent("frontend_expert", prompt)
        return json.loads(response)
    
    def _consult_backend_expert(self, architecture: Dict, project_type: str) -> Dict[str, Any]:
        """Consulta al experto backend"""
        prompt = f"""
        Basado en esta arquitectura: {json.dumps(architecture, indent=2)}
        Tipo de proyecto: {project_type}
        
        Como experto backend, diseña:
        1. Stack tecnológico backend
        2. Diseño de API y endpoints
        3. Base de datos y modelos
        4. Autenticación y autorización
        5. Consideraciones de seguridad
        
        Responde en formato JSON con: backend_stack, api_design, database, auth, security
        """
        
        response = self._call_agent("backend_expert", prompt)
        return json.loads(response)
    
    def _consult_devops_expert(self, architecture: Dict, project_type: str) -> Dict[str, Any]:
        """Consulta al experto DevOps"""
        prompt = f"""
        Basado en esta arquitectura: {json.dumps(architecture, indent=2)}
        Tipo de proyecto: {project_type}
        
        Como experto DevOps, diseña:
        1. Estrategia de deployment
        2. Configuración de Docker/Kubernetes
        3. CI/CD pipeline
        4. Monitoreo y logging
        5. Backup y recovery
        
        Responde en formato JSON con: deployment_strategy, docker_config, cicd, monitoring, backup
        """
        
        response = self._call_agent("devops_expert", prompt)
        return json.loads(response)
    
    def _call_agent(self, agent_type: str, prompt: str) -> str:
        """Llama a un agente específico"""
        try:
            agent_config = self.specialized_agents[agent_type]
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": agent_config["role"], "content": agent_config["content"]},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f'{{"error": "Failed to call agent {agent_type}: {str(e)}"}}'
    
    def _combine_designs(self, architecture: Dict, frontend: Dict, backend: Dict, devops: Dict) -> Dict[str, Any]:
        """Combina todos los diseños en un proyecto completo"""
        return {
            "project_architecture": architecture,
            "frontend_design": frontend,
            "backend_design": backend,
            "devops_design": devops,
            "complete_stack": {
                "frontend": frontend.get("frontend_stack", []),
                "backend": backend.get("backend_stack", []),
                "database": backend.get("database", {}),
                "deployment": devops.get("deployment_strategy", {}),
                "infrastructure": devops.get("docker_config", {})
            },
            "implementation_plan": self._generate_implementation_plan(architecture, frontend, backend, devops)
        }
    
    def _generate_implementation_plan(self, architecture: Dict, frontend: Dict, backend: Dict, devops: Dict) -> List[Dict]:
        """Genera un plan de implementación paso a paso"""
        return [
            {
                "phase": "1. Setup Inicial",
                "tasks": [
                    "Crear estructura de proyecto",
                    "Configurar entorno de desarrollo",
                    "Inicializar control de versiones"
                ]
            },
            {
                "phase": "2. Backend",
                "tasks": [
                    "Implementar modelos de datos",
                    "Crear API endpoints",
                    "Configurar autenticación",
                    "Implementar lógica de negocio"
                ]
            },
            {
                "phase": "3. Frontend", 
                "tasks": [
                    "Configurar framework frontend",
                    "Crear componentes base",
                    "Implementar vistas principales",
                    "Conectar con backend API"
                ]
            },
            {
                "phase": "4. Deployment",
                "tasks": [
                    "Configurar CI/CD",
                    "Preparar entorno de producción",
                    "Desplegar aplicación",
                    "Configurar monitoreo"
                ]
            }
        ]

# Ejemplo de uso
if __name__ == "__main__":
    # Nota: Necesitas configurar OPENAI_API_KEY en tus variables de entorno
    orchestrator = AIOrchestrator()
    
    example_project = orchestrator.orchestrate_project_creation(
        "Una aplicación de task management con AI que sugiera tareas automáticamente",
        "react_web_app"
    )
    
    print("✅ Proyecto orquestado exitosamente!")
    print(f"Fases: {len(example_project['implementation_plan'])}")

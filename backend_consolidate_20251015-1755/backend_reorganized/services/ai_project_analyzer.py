"""
AI Project Analyzer - Uses DeepSeek to enhance project generation
"""
from typing import Dict, List, Optional
import json
from services.deepseek_client import deepseek_client

class AIProjectAnalyzer:
    """Analyzes project ideas and enhances generation with AI"""

    def __init__(self):
        self.client = deepseek_client

    async def analyze_idea(self, idea: str, project_type: str) -> Dict:
        """Comprehensive analysis of project idea"""
        analysis = await self.client.analyze_project_requirements(idea, project_type)

        # Enhance with additional AI insights
        enhanced_analysis = {
            **analysis,
            "ai_enhanced": True,
            "complexity_score": self._calculate_complexity(idea, analysis),
            "development_phases": self._generate_development_phases(analysis),
            "risk_assessment": self._assess_risks(analysis)
        }

        return enhanced_analysis

    async def generate_enhanced_structure(self, analysis: Dict, project_type: str) -> Dict:
        """Generate enhanced project structure using AI insights"""
        base_structure = self._get_base_structure(project_type)

        # Enhance structure based on AI analysis
        if "file_structure" in analysis:
            base_structure = {**base_structure, **analysis["file_structure"]}

        # Add AI-recommended files
        if "technologies" in analysis:
            base_structure = self._add_technology_specific_files(base_structure, analysis["technologies"])

        return base_structure

    async def generate_intelligent_readme(self, project_name: str, analysis: Dict, requirements: Dict) -> str:
        """Generate intelligent README using AI"""
        readme_content = await self.client.generate_code(
            f"Genera un README.md completo para {project_name}",
            "markdown",
            {"analysis": analysis, "requirements": requirements}
        )

        return readme_content or self._generate_fallback_readme(project_name, analysis, requirements)

    async def generate_smart_code(self, file_path: str, description: str, context: Dict) -> str:
        """Generate smart code for specific files"""
        return await self.client.generate_code(description, self._get_language_from_path(file_path), context)

    def _calculate_complexity(self, idea: str, analysis: Dict) -> int:
        """Calculate project complexity score (1-10)"""
        complexity_indicators = [
            len(idea.split()),
            len(analysis.get("features", [])),
            len(analysis.get("technologies", [])),
            "database" in str(analysis).lower(),
            "authentication" in str(analysis).lower(),
            "api" in str(analysis).lower(),
        ]

        score = sum(complexity_indicators)
        return min(max(score, 1), 10)

    def _generate_development_phases(self, analysis: Dict) -> List[Dict]:
        """Generate development phases based on analysis"""
        return [
            {
                "phase": 1,
                "name": "Setup y Estructura Base",
                "tasks": ["Configurar proyecto", "Estructura inicial"],
                "estimated_days": 2
            },
            {
                "phase": 2,
                "name": "Funcionalidades Core",
                "tasks": ["Implementar características principales"],
                "estimated_days": 5
            },
            {
                "phase": 3,
                "name": "Integración y Testing",
                "tasks": ["Integrar servicios", "Implementar tests"],
                "estimated_days": 3
            }
        ]

    def _assess_risks(self, analysis: Dict) -> List[Dict]:
        """Assess project risks"""
        return [
            {
                "risk": "Complejidad técnica",
                "level": "medium",
                "mitigation": "Dividir en fases más pequeñas"
            }
        ]

    def _get_base_structure(self, project_type: str) -> Dict:
        """Get base project structure"""
        structures = {
            "web_app": {
                "frontend/src/components/": {},
                "frontend/src/pages/": {},
                "frontend/src/services/": {},
                "frontend/src/utils/": {},
                "backend/app/routes/": {},
                "backend/app/models/": {},
                "backend/app/services/": {},
                "config/": {},
                "docs/": {}
            }
        }
        return structures.get(project_type, {})

    def _add_technology_specific_files(self, structure: Dict, technologies: List[str]) -> Dict:
        """Add technology-specific files to structure"""
        tech_files = {}

        if "react" in [t.lower() for t in technologies]:
            tech_files.update({
                "frontend/src/hooks/": {},
                "frontend/src/context/": {}
            })

        return {**structure, **tech_files}

    def _get_language_from_path(self, file_path: str) -> str:
        """Detect programming language from file path"""
        if file_path.endswith('.py'):
            return 'python'
        elif file_path.endswith('.js') or file_path.endswith('.jsx'):
            return 'javascript'
        elif file_path.endswith('.ts') or file_path.endswith('.tsx'):
            return 'typescript'
        elif file_path.endswith('.md'):
            return 'markdown'
        elif file_path.endswith('.json'):
            return 'json'
        else:
            return 'python'

    def _generate_fallback_readme(self, project_name: str, analysis: Dict, requirements: Dict) -> str:
        """Generate fallback README when AI is unavailable"""
        features_text = "\n".join([f"- {feature}" for feature in analysis.get('features', [])])
        technologies_text = "\n".join([f"- {tech}" for tech in analysis.get('technologies', [])])

        return f"""# {project_name}

{requirements.get('description', '')}

## Características

{features_text}

## Tecnologías

{technologies_text}

## Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python -m app.main
```
"""

# Singleton instance
ai_analyzer = AIProjectAnalyzer()

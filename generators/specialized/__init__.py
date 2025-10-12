from .nextjs_generator import NextJSGenerator
from .fastapi_generator import FastAPIGenerator
from .react_native_generator import ReactNativeGenerator
from .chrome_extension_generator import ChromeExtensionGenerator
from .ai_agent_generator import AIAgentGenerator

class SpecializedGenerator:
    def __init__(self):
        self.generators = {
            'nextjs_app': NextJSGenerator(),
            'fastapi_service': FastAPIGenerator(),
            'react_native_mobile': ReactNativeGenerator(),
            'chrome_extension': ChromeExtensionGenerator(),
            'ai_agent': AIAgentGenerator()
        }
    
    def generate_project(self, project_type, project_name, description, features, technologies):
        if project_type in self.generators:
            print(f"🎯 Usando generador especializado para: {project_type}")
            return self.generators[project_type].generate(
                project_name, description, features, technologies
            )
        else:
            # Fallback al generador React básico
            print(f"⚠️  Usando generador React básico para: {project_type}")
            from ..simple_engine import SimpleTemplateEngine
            engine = SimpleTemplateEngine()
            return engine.generate_react_project(project_name, description)

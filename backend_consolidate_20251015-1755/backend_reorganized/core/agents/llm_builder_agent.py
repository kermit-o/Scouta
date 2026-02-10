from core.llm.async_utils import resolve_text
"""
LLM Builder Agent - Consulta REAL a DeepSeek para GENERAR CÓDIGO
"""
import os
import uuid
import json
from services.robust_deepseek_client import RobustDeepSeekClient

from core.settings import WORKDIR_ROOT


class LLMBuilderAgent:
    def __init__(self):
        self.client = RobustDeepSeekClient()
        self.generated_files = []
    
    def run(self, project_id: str, development_plan: dict) -> dict:
        """Consulta REAL al LLM para GENERAR CÓDIGO de cada archivo"""
        print("🏗️ LLM Builder Agent - Consultando DeepSeek para GENERAR CÓDIGO...")
        
        try:
            # Crear directorio del proyecto
            project_name = development_plan.get('project_name', 'proyecto-llm').replace(' ', '-').lower()
            project_path = f"generated_projects/llm-{project_name}-{project_id[:8]}"
            os.makedirs(project_path, exist_ok=True)
            
            print(f"📁 Proyecto LLM: {project_path}")
            
            # GENERAR CÓDIGO consultando al LLM para CADA archivo
            files_created = self._generate_code_with_llm(project_path, development_plan)
            
            return {
                "status": "built_with_llm",
                "project_id": project_id,
                "project_path": project_path,
                "project_name": project_name,
                "files_created": files_created,
                "total_files": len(files_created),
                "llm_used": True,
                "message": "Proyecto generado con LLM real"
            }
            
        except Exception as e:
            print(f"❌ Error en construcción con LLM: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "llm_used": False
            }
    
    def _generate_code_with_llm(self, project_path: str, plan: dict) -> list:
        """Genera código REAL consultando al LLM para cada archivo"""
        files_created = []
        
        # 1. package.json - Consultar al LLM
        package_prompt = f"""
        Genera un package.json COMPLETO y FUNCIONAL para: {plan.get('project_name')}
        
        Especificaciones: {json.dumps(plan, indent=2)}
        
        Incluye:
        - Scripts de desarrollo, build y start
        - Dependencias necesarias REALES
        - Configuración para el tipo de proyecto
        - Metadatos del proyecto
        
        Solo genera el JSON válido, sin explicaciones.
        """
        
        package_code = self.client.generate_code(package_prompt, "Generación de package.json")
        self._write_file(project_path, "package.json", self._clean_json_response(package_code))
        files_created.append("package.json")
        
        # 2. README.md - Consultar al LLM
        readme_prompt = f"""
        Genera un README.md PROFESIONAL y COMPLETO para: {plan.get('project_name')}
        
        Proyecto: {json.dumps(plan, indent=2)}
        
        Incluye:
        - Descripción del proyecto
        - Características principales
        - Instrucciones de instalación COMPLETAS
        - Guía de uso
        - Stack tecnológico
        - Estructura del proyecto
        
        Solo genera el markdown, sin explicaciones adicionales.
        """
        
        readme_content = self.client.generate_code(readme_prompt, "Generación de README")
        self._write_file(project_path, "README.md", readme_content)
        files_created.append("README.md")
        
        workdir = WORKDIR_ROOT / project_id  # project_id ya existe/lo tienes
        workdir.mkdir(parents=True, exist_ok=True)

        # 3. Archivo principal de la aplicación - Consultar al LLM
        app_prompt = f"""
        Genera el archivo principal de la aplicación para: {plan.get('project_name')}
        
        Especificaciones: {json.dumps(plan, indent=2)}
        Stack: {plan.get('tech_stack', ['React', 'Node.js'])}
        
        Crea un archivo principal FUNCIONAL y COMPLETO que:
        - Sea el punto de entrada de la aplicación
        - Inclua componentes básicos funcionando
        - Tenga estilos básicos
        - Esté listo para ejecutar
        
        Solo genera el código, sin explicaciones.
        """
        
        app_content = self.client.generate_code(app_prompt, "Generación de aplicación principal")
        
        # Determinar extensión basado en el stack
        if any(tech in ['React', 'Next.js'] for tech in plan.get('tech_stack', [])):
            os.makedirs(f"{project_path}/src", exist_ok=True)
            self._write_file(project_path, "src/App.jsx", app_content)
            files_created.append("src/App.jsx")
        else:
            self._write_file(project_path, "app.js", app_content)
            files_created.append("app.js")
        
        # 4. Generar archivos adicionales basados en los componentes del plan
        components = plan.get('components', [])
        for component in components[:3]:  # Limitar a 3 componentes para demo
            component_files = self._generate_component_with_llm(project_path, component, plan)
            files_created.extend(component_files)
        
        print(f"✅ Código generado con LLM: {len(files_created)} archivos")
        return files_created
    
    def _generate_component_with_llm(self, project_path: str, component: dict, plan: dict) -> list:
        """Genera un componente específico consultando al LLM"""
        files = []
        
        component_prompt = f"""
        Genera el código COMPLETO y FUNCIONAL para el componente: {component.get('name')}
        
        DESCRIPCIÓN: {component.get('description', 'Sin descripción')}
        TIPO: {component.get('type', 'component')}
        PROYECTO: {plan.get('project_name')}
        STACK: {plan.get('tech_stack', ['React', 'Node.js'])}
        
        Genera un archivo IMPLEMENTADO COMPLETAMENTE con:
        - Código 100% funcional (no placeholders)
        - Estilos incluidos
        - Lógica de negocio si es necesaria
        - Comentarios claros
        
        Solo genera el código listo para usar.
        """
        
        try:
            component_code = self.client.generate_code(component_prompt, f"Generación de {component.get('name')}")
            
            # Determinar ruta y extensión
            component_type = component.get('type', 'component')
            component_name = component.get('name', 'Component').replace(' ', '')
            
            if component_type == 'frontend':
                os.makedirs(f"{project_path}/src/components", exist_ok=True)
                file_path = f"src/components/{component_name}.jsx"
            elif component_type == 'backend':
                os.makedirs(f"{project_path}/src/api", exist_ok=True)
                file_path = f"src/api/{component_name}.js"
            else:
                file_path = f"src/{component_name}.js"
            
            self._write_file(project_path, file_path, component_code)
            files.append(file_path)
            
        except Exception as e:
            print(f"⚠️ Error generando componente {component.get('name')}: {e}")
        
        return files
    
    def _clean_json_response(self, response: str) -> str:
        """Limpia la respuesta JSON del LLM"""
        try:
            if '{' in response and '}' in response:
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                json_str = response[json_start:json_end]
                # Validar que sea JSON válido
                json.loads(json_str)
                return json_str
        except:
            pass
        
        # Fallback a package.json básico
        return json.dumps({
            "name": "proyecto-llm",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "node app.js",
                "start": "node app.js"
            },
            "dependencies": {
                "express": "^4.18.0"
            }
        }, indent=2)
    
    def _write_file(self, project_path: str, file_path: str, content: str):
        """Escribe archivo en el proyecto"""
        full_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_files.append(file_path)
        print(f"   📄 Generado: {file_path}")

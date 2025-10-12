# Corregir el archivo template_engine.py
cat > generators/template_engine.py << 'EOF'
import os
import json
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template
import shutil

class TemplateEngine:
    def __init__(self):
        self.templates_dir = "templates"
        self.setup_template_environment()
        self.template_registry = self._load_template_registry()
    
    def setup_template_environment(self):
        """Configura el entorno de plantillas Jinja2"""
        # Crear directorio de templates si no existe
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Configurar Jinja2
        self.env = Environment(
            loader=FileSystemLoader(self.templates_dir),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Añadir filtros personalizados
        self.env.filters['to_json'] = json.dumps
        self.env.filters['to_camel_case'] = self._to_camel_case
    
    def _load_template_registry(self) -> Dict[str, Any]:
        """Carga el registro de plantillas disponibles"""
        return {
            "react_web_app": {
                "base_structure": [
                    "package.json",
                    "src/",
                    "src/components/",
                    "src/pages/", 
                    "src/styles/",
                    "public/",
                    "index.html",
                    "README.md"
                ]
            },
            "nextjs_app": {
                "base_structure": [
                    "package.json",
                    "app/",
                    "components/",
                    "lib/",
                    "public/",
                    "next.config.js"
                ]
            },
            "fastapi_service": {
                "base_structure": [
                    "requirements.txt",
                    "app/__init__.py",
                    "app/main.py",
                    "app/api/",
                    "app/models/",
                    "app/database/"
                ]
            }
        }
    
    def generate_project(self, project_data: Dict[str, Any], output_dir: str = "generated_projects") -> Dict[str, Any]:
        """Genera un proyecto completo basado en los datos del proyecto"""
        
        project_name = project_data.get("name", "unnamed_project")
        project_type = project_data.get("type", "").value if hasattr(project_data.get("type"), 'value') else str(project_data.get("type"))
        
        # Crear directorio del proyecto
        project_path = os.path.join(output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        print(f"🚀 Generando proyecto: {project_name}")
        print(f"📍 Ruta: {project_path}")
        print(f"🎯 Tipo: {project_type}")
        
        generated_files = []
        
        # Generar estructura base
        if project_type in self.template_registry:
            structure = self.template_registry[project_type]["base_structure"]
            
            for item in structure:
                item_path = os.path.join(project_path, item)
                
                if item.endswith('/') or item in ['src', 'app', 'public', 'src/components', 'src/pages', 'src/styles', 'app/api', 'app/models', 'app/database']:
                    # Es un directorio
                    os.makedirs(item_path, exist_ok=True)
                    generated_files.append(f"📁 {item}")
                    print(f"  📁 Creando directorio: {item}")
                else:
                    # Es un archivo - crear contenido básico
                    self._create_basic_file(item_path, project_data)
                    generated_files.append(f"📄 {item}")
                    print(f"  📄 Creando: {item}")
        
        # Generar archivos específicos del tipo de proyecto
        self._generate_project_type_files(project_path, project_type, project_data, generated_files)
        
        print(f"✅ Proyecto generado exitosamente!")
        print(f"📊 Total archivos: {len(generated_files)}")
        
        return {
            "project_path": project_path,
            "generated_files": generated_files,
            "total_files": len(generated_files),
            "project_type": project_type,
            "project_name": project_name
        }
    
    def _create_basic_file(self, file_path: str, context: Dict[str, Any]):
        """Crea un archivo básico con contenido apropiado"""
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1]
        
        # Contenido básico para diferentes tipos de archivos
        basic_content = {
            ".json": self._generate_basic_package_json(context),
            ".txt": self._generate_basic_requirements(context),
            ".md": self._generate_basic_readme(context),
            ".js": self._generate_basic_js(context),
            ".jsx": self._generate_basic_jsx(context),
            ".html": self._generate_basic_html(context),
            ".py": self._generate_basic_py(context),
            ".config.js": self._generate_basic_config_js(context)
        }
        
        content = basic_content.get(file_ext, f"# {file_name}\n# Generated by Forge SaaS\n\n")
        
        # Asegurar que el directorio padre existe
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def _generate_basic_package_json(self, context: Dict[str, Any]) -> str:
        """Genera un package.json básico"""
        project_name = context.get("name", "forge-project")
        
        package_data = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": context.get("description", "Project generated by Forge SaaS"),
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "devDependencies": {
                "vite": "^4.4.0",
                "@vitejs/plugin-react": "^4.0.0"
            }
        }
        
        return json.dumps(package_data, indent=2)
    
    def _generate_basic_requirements(self, context: Dict[str, Any]) -> str:
        """Genera un requirements.txt básico"""
        return f"""fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# Project: {context.get('name', 'Unknown')}
# {context.get('description', '')}
"""
    
    def _generate_basic_readme(self, context: Dict[str, Any]) -> str:
        """Genera un README.md básico"""
        name = context.get('name', 'Forge SaaS Project')
        description = context.get('description', 'Project generated by Forge SaaS')
        features = ', '.join(context.get('features', []))
        technologies = ', '.join(context.get('technologies', []))
        
        return f"""# {name}

{description}

## Features
{features}

## Technologies  
{technologies}

## Getting Started

1. Install dependencies:
```bash
npm install
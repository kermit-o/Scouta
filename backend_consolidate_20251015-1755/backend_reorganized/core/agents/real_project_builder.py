"""
Real Project Builder - Genera proyectos COMPLETOS y REALES con LLM
"""
import os
import uuid
import json
import asyncio
from typing import Dict, List, Any
from services.fixed_deepseek_client import FixedDeepSeekClient

class RealProjectBuilder:
    """Builder que genera proyectos COMPLETOS con estructura real"""
    
    def __init__(self):
        self.client = FixedDeepSeekClient()
        self.generated_files = []
    
    async def run(self, project_id: str, development_plan: dict) -> dict:
        """Genera un proyecto COMPLETO y REAL consultando al LLM"""
        print("🏗️ REAL PROJECT BUILDER - Generando proyecto COMPLETO...")
        
        try:
            # Crear directorio del proyecto
            project_name = development_plan.get('project_name', 'proyecto-real').replace(' ', '-').lower()
            project_path = f"generated_projects/real-{project_name}-{project_id[:8]}"
            os.makedirs(project_path, exist_ok=True)
            
            print(f"�� Proyecto REAL: {project_path}")
            
            # GENERAR PROYECTO COMPLETO
            files_created = await self._generate_complete_project(project_path, development_plan)
            
            return {
                "status": "complete_project_built",
                "project_id": project_id,
                "project_path": project_path,
                "project_name": project_name,
                "files_created": files_created,
                "total_files": len(files_created),
                "project_type": development_plan.get('project_type', 'web_app'),
                "message": "Proyecto COMPLETO generado con estructura real"
            }
            
        except Exception as e:
            print(f"❌ Error construyendo proyecto real: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_complete_project(self, project_path: str, plan: dict) -> List[str]:
        """Genera un proyecto COMPLETO con 15-20+ archivos reales"""
        files_created = []
        project_type = plan.get('project_type', 'web_app')
        
        print(f"🔨 Construyendo proyecto {project_type} COMPLETO...")
        
        # 1. CONFIGURACIÓN BASE
        print("   📋 Generando configuración base...")
        base_files = await self._generate_base_configuration(project_path, plan)
        files_created.extend(base_files)
        
        # 2. FRONTEND COMPLETO
        print("   🎨 Generando frontend completo...")
        frontend_files = await self._generate_frontend(project_path, plan)
        files_created.extend(frontend_files)
        
        # 3. BACKEND COMPLETO
        print("   🔧 Generando backend completo...")
        backend_files = await self._generate_backend(project_path, plan)
        files_created.extend(backend_files)
        
        # 4. COMPONENTES ESPECÍFICOS SEGÚN TIPO DE PROYECTO
        print("   🎯 Generando componentes específicos...")
        feature_files = await self._generate_project_features(project_path, plan)
        files_created.extend(feature_files)
        
        # 5. DOCUMENTACIÓN Y DEPLOY
        print("   📚 Generando documentación...")
        docs_files = await self._generate_documentation(project_path, plan)
        files_created.extend(docs_files)
        
        print(f"✅ Proyecto COMPLETO generado: {len(files_created)} archivos")
        return files_created
    
    async def _generate_base_configuration(self, project_path: str, plan: dict) -> List[str]:
        """Genera configuración base del proyecto"""
        files = []
        
        # package.json COMPLETO
        package_prompt = f"""
        Genera un package.json COMPLETO y PROFESIONAL para un proyecto: {plan.get('project_name')}
        
        Tipo: {plan.get('project_type')}
        Stack: {plan.get('tech_stack', ['React', 'Node.js', 'MongoDB'])}
        Características: {plan.get('features', [])}
        
        Incluye:
        - Scripts completos (dev, build, start, test, lint)
        - Dependencias REALES y actualizadas
        - Configuración para el tipo de proyecto
        - Metadatos profesionales
        
        Responde SOLO con el JSON válido.
        """
        
        package_json = await self.client.generate_code(package_prompt, "Package.json completo")
        self._write_file(project_path, "package.json", self._clean_json(package_json))
        files.append("package.json")
        
        # Configuración Next.js/React
        if any(tech in plan.get('tech_stack', []) for tech in ['React', 'Next.js']):
            next_config = await self.client.generate_code(
                "Genera un next.config.js completo para un proyecto profesional",
                "Configuración Next.js"
            )
            self._write_file(project_path, "next.config.js", next_config)
            files.append("next.config.js")
            
            # Tailwind config si está en el stack
            if 'Tailwind' in str(plan.get('tech_stack', [])):
                tailwind_config = await self.client.generate_code(
                    "Genera un tailwind.config.js completo",
                    "Configuración Tailwind"
                )
                self._write_file(project_path, "tailwind.config.js", tailwind_config)
                files.append("tailwind.config.js")
        
        # Environment variables
        env_content = await self.client.generate_code(
            f"Genera un archivo .env.example con variables de entorno para: {plan.get('project_name')}",
            "Variables de entorno"
        )
        self._write_file(project_path, ".env.example", env_content)
        files.append(".env.example")
        
        # Gitignore
        gitignore = await self.client.generate_code(
            "Genera un .gitignore completo para proyecto Node.js/React",
            "Gitignore"
        )
        self._write_file(project_path, ".gitignore", gitignore)
        files.append(".gitignore")
        
        return files
    
    async def _generate_frontend(self, project_path: str, plan: dict) -> List[str]:
        """Genera frontend COMPLETO"""
        files = []
        
        # Crear estructura de directorios
        frontend_dirs = ['src/components', 'src/pages', 'src/hooks', 'src/utils', 'src/styles', 'public']
        for directory in frontend_dirs:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Layout principal
        layout_prompt = f"""
        Genera un layout principal COMPLETO para: {plan.get('project_name')}
        
        Tipo: {plan.get('project_type')}
        Características: {plan.get('features', [])}
        
        Incluye:
        - Estructura HTML semántica
        - Meta tags para SEO
        - Navegación responsive
        - Sistema de rutas
        - Estilos profesionales
        
        Código 100% funcional.
        """
        
        layout_code = await self.client.generate_code(layout_prompt, "Layout principal")
        self._write_file(project_path, "src/components/Layout.jsx", layout_code)
        files.append("src/components/Layout.jsx")
        
        # Página principal
        homepage_prompt = f"""
        Genera una página principal COMPLETA y FUNCIONAL para: {plan.get('project_name')}
        
        Proyecto: {json.dumps(plan, indent=2)}
        
        La página debe incluir:
        - Hero section atractiva
        - Características principales
        - Llamadas a la acción
        - Diseño moderno y responsive
        - Contenido real y relevante
        
        Código listo para usar.
        """
        
        homepage_code = await self.client.generate_code(homepage_prompt, "Página principal")
        self._write_file(project_path, "src/pages/Home.jsx", homepage_code)
        files.append("src/pages/Home.jsx")
        
        # Componentes comunes
        components = ['Header', 'Footer', 'Button', 'Card', 'Modal']
        for component in components:
            component_code = await self.client.generate_code(
                f"Genera un componente {component} profesional y reutilizable para React",
                f"Componente {component}"
            )
            self._write_file(project_path, f"src/components/{component}.jsx", component_code)
            files.append(f"src/components/{component}.jsx")
        
        # Estilos globales
        styles_prompt = "Genera un archivo de estilos CSS global profesional con variables CSS, reset, y estilos base"
        styles_code = await self.client.generate_code(styles_prompt, "Estilos globales")
        self._write_file(project_path, "src/styles/globals.css", styles_code)
        files.append("src/styles/globals.css")
        
        # App principal
        app_code = await self.client.generate_code(
            "Genera un archivo App.jsx principal que importe todos los componentes y configure las rutas",
            "App principal"
        )
        self._write_file(project_path, "src/App.jsx", app_code)
        files.append("src/App.jsx")
        
        # Index.html
        html_code = await self.client.generate_code(
            "Genera un index.html completo para una aplicación React/Next.js moderna",
            "HTML principal"
        )
        self._write_file(project_path, "public/index.html", html_code)
        files.append("public/index.html")
        
        return files
    
    async def _generate_backend(self, project_path: str, plan: dict) -> List[str]:
        """Genera backend COMPLETO"""
        files = []
        
        # Crear estructura de directorios
        backend_dirs = ['server/routes', 'server/controllers', 'server/models', 'server/middleware', 'server/config']
        for directory in backend_dirs:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Server principal
        server_prompt = f"""
        Genera un servidor Node.js/Express COMPLETO y PROFESIONAL para: {plan.get('project_name')}
        
        Características: {plan.get('features', [])}
        Stack: {plan.get('tech_stack', [])}
        
        Incluye:
        - Configuración Express completa
        - Middlewares (CORS, body-parser, helmet, etc.)
        - Manejo de errores
        - Logging
        - Configuración de puerto y entorno
        
        Código 100% funcional y listo para ejecutar.
        """
        
        server_code = await self.client.generate_code(server_prompt, "Servidor principal")
        self._write_file(project_path, "server/index.js", server_code)
        files.append("server/index.js")
        
        # Routes básicas
        routes = ['auth', 'users', 'products'] if 'ecommerce' in plan.get('project_type', '') else ['api', 'health']
        
        for route in routes:
            route_code = await self.client.generate_code(
                f"Genera rutas API completas para {route} con Express",
                f"Rutas {route}"
            )
            self._write_file(project_path, f"server/routes/{route}.js", route_code)
            files.append(f"server/routes/{route}.js")
            
            # Controladores
            controller_code = await self.client.generate_code(
                f"Genera controladores para {route} con lógica de negocio real",
                f"Controladores {route}"
            )
            self._write_file(project_path, f"server/controllers/{route}Controller.js", controller_code)
            files.append(f"server/controllers/{route}Controller.js")
        
        # Configuración de base de datos
        db_prompt = "Genera configuración completa para MongoDB/Mongoose con conexión, modelos y esquemas"
        db_code = await self.client.generate_code(db_prompt, "Configuración DB")
        self._write_file(project_path, "server/config/database.js", db_code)
        files.append("server/config/database.js")
        
        # Modelos de datos
        models = ['User', 'Product', 'Order'] if 'ecommerce' in plan.get('project_type', '') else ['Data']
        
        for model in models:
            model_code = await self.client.generate_code(
                f"Genera un modelo Mongoose completo para {model} con validaciones",
                f"Modelo {model}"
            )
            self._write_file(project_path, f"server/models/{model}.js", model_code)
            files.append(f"server/models/{model}.js")
        
        # Middleware de autenticación
        auth_code = await self.client.generate_code(
            "Genera middleware de autenticación JWT completo para Express",
            "Middleware auth"
        )
        self._write_file(project_path, "server/middleware/auth.js", auth_code)
        files.append("server/middleware/auth.js")
        
        return files
    
    async def _generate_project_features(self, project_path: str, plan: dict) -> List[str]:
        """Genera características específicas del tipo de proyecto"""
        files = []
        project_type = plan.get('project_type', '')
        
        if 'ecommerce' in project_type:
            # Componentes de ecommerce
            ecom_components = ['ProductList', 'ProductCard', 'ShoppingCart', 'Checkout', 'PaymentForm']
            
            for component in ecom_components:
                component_prompt = f"""
                Genera un componente {component} COMPLETO y FUNCIONAL para una tienda online
                
                Características necesarias:
                - Estado reactivo
                - Manejo de eventos
                - Estilos profesionales
                - Integración con APIs
                - Código 100% funcional
                """
                
                component_code = await self.client.generate_code(component_prompt, f"Componente {component}")
                self._write_file(project_path, f"src/components/{component}.jsx", component_code)
                files.append(f"src/components/{component}.jsx")
            
            # Carrito context
            cart_context = await self.client.generate_code(
                "Genera un React Context completo para manejar el carrito de compras con persistencia",
                "Context carrito"
            )
            self._write_file(project_path, "src/context/CartContext.jsx", cart_context)
            files.append("src/context/CartContext.jsx")
            
            # Hooks personalizados
            hooks = ['useCart', 'useProducts', 'useAuth']
            for hook in hooks:
                hook_code = await self.client.generate_code(
                    f"Genera un custom hook {hook} completo y funcional",
                    f"Hook {hook}"
                )
                self._write_file(project_path, f"src/hooks/{hook}.js", hook_code)
                files.append(f"src/hooks/{hook}.js")
        
        return files
    
    async def _generate_documentation(self, project_path: str, plan: dict) -> List[str]:
        """Genera documentación COMPLETA"""
        files = []
        
        # README completo
        readme_prompt = f"""
        Genera un README.md PROFESIONAL y COMPLETO para: {plan.get('project_name')}
        
        Proyecto: {json.dumps(plan, indent=2)}
        
        Incluye:
        # Descripción detallada
        ## Características
        ## Instalación COMPLETA
        ## Uso y ejemplos
        ## API Documentation
        ## Deployment
        ## Tecnologías usadas
        ## Estructura del proyecto
        ## Contribución
        ## Licencia
        
        Documentación profesional y completa.
        """
        
        readme_content = await self.client.generate_code(readme_prompt, "README completo")
        self._write_file(project_path, "README.md", readme_content)
        files.append("README.md")
        
        # Archivos de deployment
        deployment_files = ['Dockerfile', 'docker-compose.yml', '.github/workflows/deploy.yml']
        for file in deployment_files:
            content = await self.client.generate_code(
                f"Genera un {file} completo para deployment del proyecto",
                f"Deployment {file}"
            )
            self._write_file(project_path, file, content)
            files.append(file)
        
        return files
    
    def _clean_json(self, json_str: str) -> str:
        """Limpia y valida JSON"""
        try:
            if '{' in json_str and '}' in json_str:
                json_start = json_str.find('{')
                json_end = json_str.rfind('}') + 1
                json_content = json_str[json_start:json_end]
                # Validar que sea JSON
                parsed = json.loads(json_content)
                return json.dumps(parsed, indent=2)
        except:
            pass
        
        # Fallback básico
        return json.dumps({
            "name": "proyecto-real",
            "version": "1.0.0",
            "description": "Proyecto generado por Forge SaaS",
            "type": "module",
            "scripts": {
                "dev": "node server/index.js",
                "start": "node server/index.js",
                "build": "echo 'Build complete'"
            },
            "dependencies": {
                "express": "^4.18.0",
                "mongoose": "^7.0.0",
                "cors": "^2.8.5"
            }
        }, indent=2)
    
    def _write_file(self, project_path: str, file_path: str, content: str):
        """Escribe archivo en el proyecto"""
        full_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_files.append(file_path)
        print(f"      📄 {file_path}")
EOFcat > core/agents/real_project_builder.py << 'EOF'
"""
Real Project Builder - Genera proyectos COMPLETOS y REALES con LLM
"""
import os
import uuid
import json
import asyncio
from typing import Dict, List, Any
from services.fixed_deepseek_client import FixedDeepSeekClient

class RealProjectBuilder:
    """Builder que genera proyectos COMPLETOS con estructura real"""
    
    def __init__(self):
        self.client = FixedDeepSeekClient()
        self.generated_files = []
    
    async def run(self, project_id: str, development_plan: dict) -> dict:
        """Genera un proyecto COMPLETO y REAL consultando al LLM"""
        print("🏗️ REAL PROJECT BUILDER - Generando proyecto COMPLETO...")
        
        try:
            # Crear directorio del proyecto
            project_name = development_plan.get('project_name', 'proyecto-real').replace(' ', '-').lower()
            project_path = f"generated_projects/real-{project_name}-{project_id[:8]}"
            os.makedirs(project_path, exist_ok=True)
            
            print(f"�� Proyecto REAL: {project_path}")
            
            # GENERAR PROYECTO COMPLETO
            files_created = await self._generate_complete_project(project_path, development_plan)
            
            return {
                "status": "complete_project_built",
                "project_id": project_id,
                "project_path": project_path,
                "project_name": project_name,
                "files_created": files_created,
                "total_files": len(files_created),
                "project_type": development_plan.get('project_type', 'web_app'),
                "message": "Proyecto COMPLETO generado con estructura real"
            }
            
        except Exception as e:
            print(f"❌ Error construyendo proyecto real: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _generate_complete_project(self, project_path: str, plan: dict) -> List[str]:
        """Genera un proyecto COMPLETO con 15-20+ archivos reales"""
        files_created = []
        project_type = plan.get('project_type', 'web_app')
        
        print(f"🔨 Construyendo proyecto {project_type} COMPLETO...")
        
        # 1. CONFIGURACIÓN BASE
        print("   📋 Generando configuración base...")
        base_files = await self._generate_base_configuration(project_path, plan)
        files_created.extend(base_files)
        
        # 2. FRONTEND COMPLETO
        print("   🎨 Generando frontend completo...")
        frontend_files = await self._generate_frontend(project_path, plan)
        files_created.extend(frontend_files)
        
        # 3. BACKEND COMPLETO
        print("   🔧 Generando backend completo...")
        backend_files = await self._generate_backend(project_path, plan)
        files_created.extend(backend_files)
        
        # 4. COMPONENTES ESPECÍFICOS SEGÚN TIPO DE PROYECTO
        print("   🎯 Generando componentes específicos...")
        feature_files = await self._generate_project_features(project_path, plan)
        files_created.extend(feature_files)
        
        # 5. DOCUMENTACIÓN Y DEPLOY
        print("   📚 Generando documentación...")
        docs_files = await self._generate_documentation(project_path, plan)
        files_created.extend(docs_files)
        
        print(f"✅ Proyecto COMPLETO generado: {len(files_created)} archivos")
        return files_created
    
    async def _generate_base_configuration(self, project_path: str, plan: dict) -> List[str]:
        """Genera configuración base del proyecto"""
        files = []
        
        # package.json COMPLETO
        package_prompt = f"""
        Genera un package.json COMPLETO y PROFESIONAL para un proyecto: {plan.get('project_name')}
        
        Tipo: {plan.get('project_type')}
        Stack: {plan.get('tech_stack', ['React', 'Node.js', 'MongoDB'])}
        Características: {plan.get('features', [])}
        
        Incluye:
        - Scripts completos (dev, build, start, test, lint)
        - Dependencias REALES y actualizadas
        - Configuración para el tipo de proyecto
        - Metadatos profesionales
        
        Responde SOLO con el JSON válido.
        """
        
        package_json = await self.client.generate_code(package_prompt, "Package.json completo")
        self._write_file(project_path, "package.json", self._clean_json(package_json))
        files.append("package.json")
        
        # Configuración Next.js/React
        if any(tech in plan.get('tech_stack', []) for tech in ['React', 'Next.js']):
            next_config = await self.client.generate_code(
                "Genera un next.config.js completo para un proyecto profesional",
                "Configuración Next.js"
            )
            self._write_file(project_path, "next.config.js", next_config)
            files.append("next.config.js")
            
            # Tailwind config si está en el stack
            if 'Tailwind' in str(plan.get('tech_stack', [])):
                tailwind_config = await self.client.generate_code(
                    "Genera un tailwind.config.js completo",
                    "Configuración Tailwind"
                )
                self._write_file(project_path, "tailwind.config.js", tailwind_config)
                files.append("tailwind.config.js")
        
        # Environment variables
        env_content = await self.client.generate_code(
            f"Genera un archivo .env.example con variables de entorno para: {plan.get('project_name')}",
            "Variables de entorno"
        )
        self._write_file(project_path, ".env.example", env_content)
        files.append(".env.example")
        
        # Gitignore
        gitignore = await self.client.generate_code(
            "Genera un .gitignore completo para proyecto Node.js/React",
            "Gitignore"
        )
        self._write_file(project_path, ".gitignore", gitignore)
        files.append(".gitignore")
        
        return files
    
    async def _generate_frontend(self, project_path: str, plan: dict) -> List[str]:
        """Genera frontend COMPLETO"""
        files = []
        
        # Crear estructura de directorios
        frontend_dirs = ['src/components', 'src/pages', 'src/hooks', 'src/utils', 'src/styles', 'public']
        for directory in frontend_dirs:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Layout principal
        layout_prompt = f"""
        Genera un layout principal COMPLETO para: {plan.get('project_name')}
        
        Tipo: {plan.get('project_type')}
        Características: {plan.get('features', [])}
        
        Incluye:
        - Estructura HTML semántica
        - Meta tags para SEO
        - Navegación responsive
        - Sistema de rutas
        - Estilos profesionales
        
        Código 100% funcional.
        """
        
        layout_code = await self.client.generate_code(layout_prompt, "Layout principal")
        self._write_file(project_path, "src/components/Layout.jsx", layout_code)
        files.append("src/components/Layout.jsx")
        
        # Página principal
        homepage_prompt = f"""
        Genera una página principal COMPLETA y FUNCIONAL para: {plan.get('project_name')}
        
        Proyecto: {json.dumps(plan, indent=2)}
        
        La página debe incluir:
        - Hero section atractiva
        - Características principales
        - Llamadas a la acción
        - Diseño moderno y responsive
        - Contenido real y relevante
        
        Código listo para usar.
        """
        
        homepage_code = await self.client.generate_code(homepage_prompt, "Página principal")
        self._write_file(project_path, "src/pages/Home.jsx", homepage_code)
        files.append("src/pages/Home.jsx")
        
        # Componentes comunes
        components = ['Header', 'Footer', 'Button', 'Card', 'Modal']
        for component in components:
            component_code = await self.client.generate_code(
                f"Genera un componente {component} profesional y reutilizable para React",
                f"Componente {component}"
            )
            self._write_file(project_path, f"src/components/{component}.jsx", component_code)
            files.append(f"src/components/{component}.jsx")
        
        # Estilos globales
        styles_prompt = "Genera un archivo de estilos CSS global profesional con variables CSS, reset, y estilos base"
        styles_code = await self.client.generate_code(styles_prompt, "Estilos globales")
        self._write_file(project_path, "src/styles/globals.css", styles_code)
        files.append("src/styles/globals.css")
        
        # App principal
        app_code = await self.client.generate_code(
            "Genera un archivo App.jsx principal que importe todos los componentes y configure las rutas",
            "App principal"
        )
        self._write_file(project_path, "src/App.jsx", app_code)
        files.append("src/App.jsx")
        
        # Index.html
        html_code = await self.client.generate_code(
            "Genera un index.html completo para una aplicación React/Next.js moderna",
            "HTML principal"
        )
        self._write_file(project_path, "public/index.html", html_code)
        files.append("public/index.html")
        
        return files
    
    async def _generate_backend(self, project_path: str, plan: dict) -> List[str]:
        """Genera backend COMPLETO"""
        files = []
        
        # Crear estructura de directorios
        backend_dirs = ['server/routes', 'server/controllers', 'server/models', 'server/middleware', 'server/config']
        for directory in backend_dirs:
            os.makedirs(os.path.join(project_path, directory), exist_ok=True)
        
        # Server principal
        server_prompt = f"""
        Genera un servidor Node.js/Express COMPLETO y PROFESIONAL para: {plan.get('project_name')}
        
        Características: {plan.get('features', [])}
        Stack: {plan.get('tech_stack', [])}
        
        Incluye:
        - Configuración Express completa
        - Middlewares (CORS, body-parser, helmet, etc.)
        - Manejo de errores
        - Logging
        - Configuración de puerto y entorno
        
        Código 100% funcional y listo para ejecutar.
        """
        
        server_code = await self.client.generate_code(server_prompt, "Servidor principal")
        self._write_file(project_path, "server/index.js", server_code)
        files.append("server/index.js")
        
        # Routes básicas
        routes = ['auth', 'users', 'products'] if 'ecommerce' in plan.get('project_type', '') else ['api', 'health']
        
        for route in routes:
            route_code = await self.client.generate_code(
                f"Genera rutas API completas para {route} con Express",
                f"Rutas {route}"
            )
            self._write_file(project_path, f"server/routes/{route}.js", route_code)
            files.append(f"server/routes/{route}.js")
            
            # Controladores
            controller_code = await self.client.generate_code(
                f"Genera controladores para {route} con lógica de negocio real",
                f"Controladores {route}"
            )
            self._write_file(project_path, f"server/controllers/{route}Controller.js", controller_code)
            files.append(f"server/controllers/{route}Controller.js")
        
        # Configuración de base de datos
        db_prompt = "Genera configuración completa para MongoDB/Mongoose con conexión, modelos y esquemas"
        db_code = await self.client.generate_code(db_prompt, "Configuración DB")
        self._write_file(project_path, "server/config/database.js", db_code)
        files.append("server/config/database.js")
        
        # Modelos de datos
        models = ['User', 'Product', 'Order'] if 'ecommerce' in plan.get('project_type', '') else ['Data']
        
        for model in models:
            model_code = await self.client.generate_code(
                f"Genera un modelo Mongoose completo para {model} con validaciones",
                f"Modelo {model}"
            )
            self._write_file(project_path, f"server/models/{model}.js", model_code)
            files.append(f"server/models/{model}.js")
        
        # Middleware de autenticación
        auth_code = await self.client.generate_code(
            "Genera middleware de autenticación JWT completo para Express",
            "Middleware auth"
        )
        self._write_file(project_path, "server/middleware/auth.js", auth_code)
        files.append("server/middleware/auth.js")
        
        return files
    
    async def _generate_project_features(self, project_path: str, plan: dict) -> List[str]:
        """Genera características específicas del tipo de proyecto"""
        files = []
        project_type = plan.get('project_type', '')
        
        if 'ecommerce' in project_type:
            # Componentes de ecommerce
            ecom_components = ['ProductList', 'ProductCard', 'ShoppingCart', 'Checkout', 'PaymentForm']
            
            for component in ecom_components:
                component_prompt = f"""
                Genera un componente {component} COMPLETO y FUNCIONAL para una tienda online
                
                Características necesarias:
                - Estado reactivo
                - Manejo de eventos
                - Estilos profesionales
                - Integración con APIs
                - Código 100% funcional
                """
                
                component_code = await self.client.generate_code(component_prompt, f"Componente {component}")
                self._write_file(project_path, f"src/components/{component}.jsx", component_code)
                files.append(f"src/components/{component}.jsx")
            
            # Carrito context
            cart_context = await self.client.generate_code(
                "Genera un React Context completo para manejar el carrito de compras con persistencia",
                "Context carrito"
            )
            self._write_file(project_path, "src/context/CartContext.jsx", cart_context)
            files.append("src/context/CartContext.jsx")
            
            # Hooks personalizados
            hooks = ['useCart', 'useProducts', 'useAuth']
            for hook in hooks:
                hook_code = await self.client.generate_code(
                    f"Genera un custom hook {hook} completo y funcional",
                    f"Hook {hook}"
                )
                self._write_file(project_path, f"src/hooks/{hook}.js", hook_code)
                files.append(f"src/hooks/{hook}.js")
        
        return files
    
    async def _generate_documentation(self, project_path: str, plan: dict) -> List[str]:
        """Genera documentación COMPLETA"""
        files = []
        
        # README completo
        readme_prompt = f"""
        Genera un README.md PROFESIONAL y COMPLETO para: {plan.get('project_name')}
        
        Proyecto: {json.dumps(plan, indent=2)}
        
        Incluye:
        # Descripción detallada
        ## Características
        ## Instalación COMPLETA
        ## Uso y ejemplos
        ## API Documentation
        ## Deployment
        ## Tecnologías usadas
        ## Estructura del proyecto
        ## Contribución
        ## Licencia
        
        Documentación profesional y completa.
        """
        
        readme_content = await self.client.generate_code(readme_prompt, "README completo")
        self._write_file(project_path, "README.md", readme_content)
        files.append("README.md")
        
        # Archivos de deployment
        deployment_files = ['Dockerfile', 'docker-compose.yml', '.github/workflows/deploy.yml']
        for file in deployment_files:
            content = await self.client.generate_code(
                f"Genera un {file} completo para deployment del proyecto",
                f"Deployment {file}"
            )
            self._write_file(project_path, file, content)
            files.append(file)
        
        return files
    
    def _clean_json(self, json_str: str) -> str:
        """Limpia y valida JSON"""
        try:
            if '{' in json_str and '}' in json_str:
                json_start = json_str.find('{')
                json_end = json_str.rfind('}') + 1
                json_content = json_str[json_start:json_end]
                # Validar que sea JSON
                parsed = json.loads(json_content)
                return json.dumps(parsed, indent=2)
        except:
            pass
        
        # Fallback básico
        return json.dumps({
            "name": "proyecto-real",
            "version": "1.0.0",
            "description": "Proyecto generado por Forge SaaS",
            "type": "module",
            "scripts": {
                "dev": "node server/index.js",
                "start": "node server/index.js",
                "build": "echo 'Build complete'"
            },
            "dependencies": {
                "express": "^4.18.0",
                "mongoose": "^7.0.0",
                "cors": "^2.8.5"
            }
        }, indent=2)
    
    def _write_file(self, project_path: str, file_path: str, content: str):
        """Escribe archivo en el proyecto"""
        full_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_files.append(file_path)
        print(f"      📄 {file_path}")

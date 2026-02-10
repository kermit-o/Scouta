# app/main_production.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import uuid
import os
import asyncio
import json
import time
import shutil
import subprocess
import importlib.util  # Import corregido: se usa importlib.util en lugar de importlib directamente

app = FastAPI(
    title="Forge SaaS PRODUCTION - Generador de Proyectos Reales",
    description="Sistema de generación automática de proyectos COMPLETOS y FUNCIONALES con IA",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str = "web"
    features: List[str] = []
    tech_preferences: List[str] = []
    complexity_level: str = "medium"  # simple, medium, complex

class ProjectResponse(BaseModel):
    project_id: str
    status: str
    message: str
    estimated_time: str
    project_path: Optional[str] = None

class RealProjectGenerator:
    def __init__(self):
        self.projects_base_dir = "generated_projects"
        self.templates_dir = "project_templates"
        self.active_generations = {}
        
        os.makedirs(self.projects_base_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Cargar agentes reales
        self.intake_agent = None
        self.generator_agent = None # Asumo que puede haber un agente de generación dedicado
        self._load_real_agents()
    
    def _load_real_agents(self):
        """Carga los agentes que SÍ generan proyectos reales"""
        print("🔄 Cargando agentes de producción...")
        
        # Intentar cargar desde enhanced_intake_standalone_final.py
        try:
            spec = importlib.util.spec_from_file_location(
                "enhanced_intake", 
                "enhanced_intake_standalone_final.py"
            )
            enhanced_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(enhanced_module)
            
            # Buscar la clase real
            for attr_name in dir(enhanced_module):
                attr = getattr(enhanced_module, attr_name)
                if isinstance(attr, type) and 'Intake' in attr_name:
                    self.intake_agent = attr()
                    print(f"✅ Agente de intake cargado: {attr_name}")
                elif isinstance(attr, type) and 'Generator' in attr_name:
                    self.generator_agent = attr()
                    print(f"✅ Agente generador cargado: {attr_name}")
            
        except Exception as e:
            print(f"⚠️ No se pudo cargar agente de intake o generador: {e}")
            self.intake_agent = None
            self.generator_agent = None
    
    def _update_progress(self, project_id: str, progress: int, status_message: str):
        """Actualiza el progreso de la generación"""
        if project_id in self.active_generations:
            self.active_generations[project_id].update({
                "progress": progress,
                "status": status_message
            })
        print(f"[{project_id}] {progress}%: {status_message}")
    
    async def generate_real_project(self, request: ProjectRequest) -> Dict[str, Any]:
        """Genera un proyecto REAL y COMPLETO"""
        
        project_id = str(uuid.uuid4())[:8]
        project_dir = os.path.join(
            self.projects_base_dir, 
            f"{request.name.lower().replace(' ', '-')}-{project_id}"
        )
        
        self.active_generations[project_id] = {
            "status": "processing",
            "progress": 0,
            "start_time": time.time(),
            "project_dir": project_dir
        }
        
        try:
            # 1. ANÁLISIS DE REQUISITOS (20%)
            self._update_progress(project_id, 20, "Analizando requisitos...")
            project_spec = await self._analyze_requirements(request)
            
            # 2. DISEÑO DE ARQUITECTURA (40%)
            self._update_progress(project_id, 40, "Diseñando arquitectura...")
            architecture = await self._design_architecture(project_spec)
            
            # 3. GENERACIÓN DE CÓDIGO REAL (60%)
            self._update_progress(project_id, 60, "Generando código...")
            await self._generate_real_code(project_dir, project_spec, architecture)
            
            # 4. CONFIGURACIÓN Y DOCUMENTACIÓN (80%)
            self._update_progress(project_id, 80, "Configurando proyecto...")
            await self._setup_project_config(project_dir, project_spec)
            
            # 5. VALIDACIÓN Y EMPAQUETADO (100%)
            self._update_progress(project_id, 100, "Finalizando...")
            final_result = await self._finalize_project(project_dir, project_spec)
            
            # Metadata final
            metadata = {
                "project_id": project_id,
                "name": request.name,
                "description": request.description,
                "type": request.project_type,
                "features": request.features,
                "tech_stack": request.tech_preferences,
                "complexity": request.complexity_level,
                "generated_at": time.time(),
                "file_count": self._count_files(project_dir),
                "status": "completed",
                "project_structure": self._get_project_structure(project_dir)
            }
            
            with open(os.path.join(project_dir, "project_metadata.json"), "w") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            self.active_generations[project_id].update({
                "status": "completed",
                "metadata": metadata,
                "final_path": project_dir
            })
            
            print(f"🎉 PROYECTO REAL GENERADO: {request.name}")
            print(f"📍 Ubicación: {project_dir}")
            print(f"📁 Archivos: {metadata['file_count']}")
            
            return {
                "project_id": project_id,
                "status": "completed",
                "project_path": project_dir,
                "file_count": metadata['file_count'],
                "structure": metadata['project_structure']
            }
            
        except Exception as e:
            print(f"❌ ERROR generando proyecto real: {e}")
            if os.path.exists(project_dir):
                shutil.rmtree(project_dir)
            
            self.active_generations[project_id].update({
                "status": "failed",
                "error": str(e)
            })
            raise e
    
    async def _analyze_requirements(self, request: ProjectRequest) -> Dict[str, Any]:
        """Análisis profundo de requisitos"""
        spec = {
            "id": str(uuid.uuid4())[:8],
            "name": request.name,
            "description": request.description,
            "type": request.project_type,
            "features": request.features,
            "tech_stack": request.tech_preferences or self._suggest_tech_stack(request),
            "complexity": request.complexity_level,
            "user_stories": self._generate_user_stories(request),
            "technical_requirements": self._generate_tech_requirements(request)
        }
        
        # Usar agente de intake si está disponible
        if self.intake_agent and hasattr(self.intake_agent, 'analyze_complexity'):
            try:
                complexity = self.intake_agent.analyze_complexity(request.description)
                spec["complexity_analysis"] = complexity
            except Exception as e:
                print(f"⚠️ Error en análisis de complejidad: {e}")
        
        return spec
    
    def _suggest_tech_stack(self, request: ProjectRequest) -> List[str]:
        """Sugiere stack tecnológico basado en el tipo de proyecto"""
        tech_stacks = {
            "web": ["html5", "css3", "javascript", "react", "nodejs", "mongodb"],
            "mobile": ["react-native", "firebase", "javascript", "redux"],
            "api": ["python", "fastapi", "sqlite", "pydantic", "jwt"],
            "saas": ["react", "nodejs", "postgresql", "redis", "docker"],
            "ecommerce": ["nextjs", "stripe", "mongodb", "tailwind", "auth0"]
        }
        
        return tech_stacks.get(request.project_type, ["html5", "css3", "javascript"])
    
    def _generate_user_stories(self, request: ProjectRequest) -> List[str]:
        """Genera user stories realistas"""
        stories = []
        
        # Stories básicas para cualquier proyecto
        base_stories = [
            "Como usuario, quiero ver una página principal atractiva",
            "Como usuario, quiero navegar fácilmente por la aplicación",
            "Como usuario, quiero que la aplicación sea responsive"
        ]
        
        # Stories específicas basadas en características
        feature_stories = {
            "autenticación": [
                "Como usuario, quiero registrarme con email y contraseña",
                "Como usuario, quiero iniciar sesión de forma segura",
                "Como usuario, quiero recuperar mi contraseña si la olvido"
            ],
            "base de datos": [
                "Como usuario, quiero que mis datos se guarden persistentemente",
                "Como administrador, quiero poder gestionar los datos fácilmente"
            ],
            "api": [
                "Como desarrollador, quiero una API REST bien documentada",
                "Como cliente, quiero poder consumir los endpoints fácilmente"
            ]
        }
        
        stories.extend(base_stories)
        
        # Agregar stories basadas en features solicitadas
        for feature in request.features:
            feature_lower = feature.lower()
            for key, feature_story_list in feature_stories.items():
                if key in feature_lower:
                    stories.extend(feature_story_list[:2])  # Máximo 2 por feature
        
        return list(set(stories))[:10]  # Máximo 10 stories
    
    def _generate_tech_requirements(self, request: ProjectRequest) -> List[str]:
        """Genera requisitos técnicos específicos"""
        requirements = [
            "El código debe seguir las mejores prácticas de la industria",
            "La aplicación debe ser responsive y funcionar en móviles",
            "El proyecto debe incluir documentación básica"
        ]
        
        if "base de datos" in request.description.lower():
            requirements.extend([
                "Implementar modelo de datos robusto",
                "Incluir migraciones de base de datos",
                "Configurar conexión segura a la base de datos"
            ])
        
        if "api" in request.description.lower():
            requirements.extend([
                "Implementar endpoints RESTful",
                "Incluir documentación Swagger/OpenAPI",
                "Manejar errores HTTP apropiadamente"
            ])
        
        return requirements
    
    async def _design_architecture(self, project_spec: Dict) -> Dict[str, Any]:
        """Diseña la arquitectura del proyecto"""
        architecture = {
            "structure": self._determine_project_structure(project_spec),
            "components": self._identify_components(project_spec),
            "dependencies": self._determine_dependencies(project_spec),
            "file_organization": self._plan_file_organization(project_spec)
        }
        return architecture
    
    def _determine_project_structure(self, project_spec: Dict) -> str:
        """Determina la estructura de archivos basada en complejidad"""
        if project_spec["complexity"] == "simple":
            return "monolithic"
        elif project_spec["complexity"] == "medium":
            return "modular"
        else:  # complex
            return "microservices"
    
    def _identify_components(self, project_spec: Dict) -> List[str]:
        """Identifica componentes principales del proyecto"""
        components = ["frontend", "backend", "database", "documentation"]
        
        if "autenticación" in str(project_spec["features"]).lower():
            components.append("auth")
        if "api" in project_spec["type"]:
            components.append("api_routes")
        if "base de datos" in str(project_spec["features"]).lower():
            components.append("data_models")
            
        return components
    
    def _determine_dependencies(self, project_spec: Dict) -> List[str]:
        """Determina dependencias del proyecto"""
        deps = []
        
        if "react" in project_spec["tech_stack"]:
            deps.extend(["react", "react-dom", "react-router-dom"])
        if "nodejs" in project_spec["tech_stack"]:
            deps.extend(["express", "cors", "dotenv"])
        if "mongodb" in project_spec["tech_stack"]:
            deps.append("mongoose")
        if "fastapi" in project_spec["tech_stack"]:
            deps.extend(["fastapi", "uvicorn", "pydantic"])
            
        return deps
    
    def _plan_file_organization(self, project_spec: Dict) -> Dict[str, List[str]]:
        """Planifica la organización de archivos"""
        structure = {
            "frontend": ["src/", "public/", "package.json"],
            "backend": ["app/", "models/", "routes/", "config/"],
            "docs": ["README.md", "API.md", "DEPLOYMENT.md"]
        }
        
        if project_spec["complexity"] == "simple":
            structure = {"src": ["components/", "styles/", "index.html"]}
        elif project_spec["complexity"] == "complex":
            structure["tests"] = ["unit/", "integration/", "e2e/"]
            structure["deployment"] = ["Dockerfile", "docker-compose.yml", "nginx.conf"]
            
        return structure
    
    # Funciones auxiliares para la generación de código
    def _generate_feature_cards_jsx(self, features: List[str]) -> str:
        """Genera el JSX para las tarjetas de características."""
        cards = []
        for i, feature in enumerate(features[:6]):
            # Se usa JSX anidado en Python con comillas simples/dobles para evitar conflictos
            card = f"""
          <div key="{i}" className="feature-card">
            <h3>{'{'}{'"'}{feature}{'"'}{'}'}</h3>
            <p>Característica implementada</p>
          </div>"""
            cards.append(card)
        return "\n".join(cards)
    
    def _generate_mobile_feature_cards_jsx(self, features: List[str]) -> str:
        """Genera el JSX para las tarjetas de características móviles (React Native)."""
        cards = []
        for i, feature in enumerate(features[:5]):
            card = f"""
          <View key="{i}" style={{styles.featureCard}}>
            <Text style={{styles.featureText}}>{{'{feature}'}}</Text>
          </View>"""
            cards.append(card)
        return "".join(cards)
    
    async def _generate_real_code(self, project_dir: str, project_spec: Dict, architecture: Dict):
        """Genera código REAL y completo"""
        
        # Crear estructura base según el tipo de proyecto
        if project_spec["type"] == "web":
            await self._generate_web_project(project_dir, project_spec, architecture)
        elif project_spec["type"] == "api":
            await self._generate_api_project(project_dir, project_spec, architecture)
        elif project_spec["type"] == "mobile":
            await self._generate_mobile_project(project_dir, project_spec, architecture)
        else:
            await self._generate_fullstack_project(project_dir, project_spec, architecture)
    
    async def _generate_web_project(self, project_dir: str, project_spec: Dict, architecture: Dict):
        """Genera un proyecto web completo"""
        
        frontend_dir = os.path.join(project_dir, "frontend")
        os.makedirs(frontend_dir, exist_ok=True)
        
        # --- package.json completo (Sin cambios) ---
        package_json = {
            "name": project_spec["name"].lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": project_spec["description"],
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.0"
            },
            "devDependencies": {
                "vite": "^4.1.0",
                "eslint": "^8.35.0",
                "eslint-plugin-react": "^7.32.0",
                "eslint-plugin-react-hooks": "^4.6.0",
                "eslint-plugin-react-refresh": "^0.3.4"
            }
        }
        
        with open(os.path.join(frontend_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # --- Vite config (Sin cambios) ---
        vite_config = """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
"""
        with open(os.path.join(frontend_dir, "vite.config.js"), "w") as f:
            f.write(vite_config)
        
        src_dir = os.path.join(frontend_dir, "src")
        os.makedirs(src_dir, exist_ok=True)
        
        # --- App.jsx principal (Sin cambios) ---
        app_jsx = """import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import Home from './pages/Home'
import './App.css'

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  )
}

export default App
"""
        with open(os.path.join(src_dir, "App.jsx"), "w") as f:
            f.write(app_jsx)
        
        # Crear componentes básicos
        components_dir = os.path.join(src_dir, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        # --- Header component (usando triple comilla para mejor legibilidad) ---
        header_jsx = f"""import React from 'react'
import './Header.css'

const Header = () => {{
  return (
    <header className="header">
      <nav className="nav">
        <div className="logo">
          <h2>{project_spec["name"]}</h2>
        </div>
        <ul className="nav-links">
          <li><a href="/">Inicio</a></li>
          <li><a href="/about">Acerca</a></li>
          <li><a href="/contact">Contacto</a></li>
        </ul>
      </nav>
    </header>
  )
}}

export default Header
"""
        with open(os.path.join(components_dir, "Header.jsx"), "w") as f:
            f.write(header_jsx)
        
        # --- Footer component (Sin cambios) ---
        footer_jsx = """import React from 'react'
import './Footer.css'

const Footer = () => {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p>&copy; 2024 Todos los derechos reservados</p>
      </div>
    </footer>
  )
}

export default Footer
"""
        with open(os.path.join(components_dir, "Footer.jsx"), "w") as f:
            f.write(footer_jsx)
        
        # Página Home
        pages_dir = os.path.join(src_dir, "pages")
        os.makedirs(pages_dir, exist_ok=True)
        
        # --- Home.jsx (USANDO FUNCIÓN AUXILIAR PARA FEATURES) ---
        feature_cards = self._generate_feature_cards_jsx(project_spec["features"])
        home_jsx = f"""import React from 'react'
import './Home.css'

const Home = () => {{
  return (
    <div className="home">
      <section className="hero">
        <h1>Bienvenido a {project_spec["name"]}</h1>
        <p>{project_spec["description"]}</p>
        <button className="cta-button">Comenzar</button>
      </section>
      
      <section className="features">
        <h2>Características Principales</h2>
        <div className="features-grid">
{feature_cards}
        </div>
      </section>
    </div>
  )
}}

export default Home
"""
        with open(os.path.join(pages_dir, "Home.jsx"), "w") as f:
            f.write(home_jsx)
        
        # --- Archivos CSS (Sin cambios) ---
        app_css = """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  line-height: 1.6;
  color: #333;
}

.App {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

main {
  flex: 1;
}

/* Header Styles */
.header {
  background: #fff;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.logo h2 {
  color: #2563eb;
}

.nav-links {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.nav-links a {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.nav-links a:hover {
  color: #2563eb;
}

/* Home Styles */
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 1rem;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-button {
  background: white;
  color: #667eea;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  font-weight: 600;
  transition: transform 0.3s;
}

.cta-button:hover {
  transform: translateY(-2px);
}

.features h2 {
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.5rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: white;
  padding: 2rem;
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  text-align: center;
  transition: transform 0.3s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-card h3 {
  color: #2563eb;
  margin-bottom: 1rem;
}

/* Footer Styles */
.footer {
  background: #1f2937;
  color: white;
  text-align: center;
  padding: 2rem;
  margin-top: auto;
}

@media (max-width: 768px) {
  .nav {
    flex-direction: column;
    gap: 1rem;
  }
  
  .hero h1 {
    font-size: 2rem;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
}
"""
        with open(os.path.join(src_dir, "App.css"), "w") as f:
            f.write(app_css)
        
        # --- HTML principal (usando triple comilla) ---
        index_html = f"""<!DOCTYPE html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_spec["name"]}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
"""
        with open(os.path.join(frontend_dir, "index.html"), "w") as f:
            f.write(index_html)
        
        # --- Main.jsx (Sin cambios) ---
        main_jsx = """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
"""
        with open(os.path.join(src_dir, "main.jsx"), "w") as f:
            f.write(main_jsx)
        
        # --- index.css básico (Sin cambios) ---
        index_css = """:root {
  font-family: Inter, system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

#root {
  width: 100%;
}
"""
        with open(os.path.join(src_dir, "index.css"), "w") as f:
            f.write(index_css)
    
    async def _generate_api_project(self, project_dir: str, project_spec: Dict, architecture: Dict):
        """Genera un proyecto API completo"""
        backend_dir = os.path.join(project_dir, "backend")
        os.makedirs(backend_dir, exist_ok=True)
        
        # --- requirements.txt (Sin cambios) ---
        requirements = """fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
"""
        with open(os.path.join(backend_dir, "requirements.txt"), "w") as f:
            f.write(requirements)
        
        # --- main.py completo (usando triple comilla) ---
        main_py = f'''from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uuid
import time

app = FastAPI(
    title="{project_spec["name"]}",
    description="{project_spec["description"]}",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: float

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    created_at: float

# Security
security = HTTPBearer()

# Mock database
users_db = {{}}

@app.get("/")
async def root():
    return {{"message": "{project_spec["name"]} API is running!", "version": "1.0.0"}}

@app.get("/health")
async def health():
    return {{"status": "healthy", "timestamp": time.time()}}

@app.post("/users", response_model=UserResponse)
async def create_user(user: UserCreate):
    user_id = str(uuid.uuid4())
    new_user = User(
        id=user_id,
        email=user.email,
        name=user.name,
        created_at=time.time()
    )
    users_db[user_id] = new_user
    return new_user

@app.get("/users", response_model=List[UserResponse])
async def get_users():
    return list(users_db.values())

@app.get("/users/{{user_id}}", response_model=UserResponse)
async def get_user(user_id: str):
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return users_db[user_id]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        with open(os.path.join(backend_dir, "main.py"), "w") as f:
            f.write(main_py)
    
    async def _generate_mobile_project(self, project_dir: str, project_spec: Dict, architecture: Dict):
        """Genera un proyecto móvil completo"""
        mobile_dir = os.path.join(project_dir, "mobile")
        os.makedirs(mobile_dir, exist_ok=True)
        
        # --- package.json para React Native (Sin cambios) ---
        package_json = {
            "name": project_spec["name"].lower().replace(" ", "-") + "-mobile",
            "version": "1.0.0",
            "description": project_spec["description"],
            "main": "index.js",
            "scripts": {
                "start": "expo start",
                "android": "expo start --android",
                "ios": "expo start --ios",
                "web": "expo start --web"
            },
            "dependencies": {
                "expo": "~49.0.0",
                "expo-status-bar": "~1.6.0",
                "react": "18.2.0",
                "react-native": "0.72.3"
            }
        }
        
        with open(os.path.join(mobile_dir, "package.json"), "w") as f:
            json.dump(package_json, f, indent=2)
        
        # --- App.js principal (USANDO FUNCIÓN AUXILIAR PARA FEATURES MÓVILES) ---
        mobile_feature_cards = self._generate_mobile_feature_cards_jsx(project_spec["features"])
        app_js = f'''import React from 'react';
import {{ StyleSheet, Text, View, ScrollView }} from 'react-native';
import {{ StatusBar }} from 'expo-status-bar';

export default function App() {{
  return (
    <View style={{styles.container}}>
      <StatusBar style="auto" />
      <ScrollView contentContainerStyle={{styles.scrollView}}>
        <View style={{styles.header}}>
          <Text style={{styles.title}}>{project_spec["name"]}</Text>
          <Text style={{styles.subtitle}}>{project_spec["description"]}</Text>
        </View>
        
        <View style={{styles.features}}>
          <Text style={{styles.sectionTitle}}>Características</Text>
          {mobile_feature_cards}
        </View>
      </ScrollView>
    </View>
  );
}}

const styles = StyleSheet.create({{
  container: {{
    flex: 1,
    backgroundColor: '#fff',
  }},
  scrollView: {{
    padding: 20,
  }},
  header: {{
    alignItems: 'center',
    marginBottom: 30,
  }},
  title: {{
    fontSize: 28,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 10,
  }},
  subtitle: {{
    fontSize: 16,
    color: '#6b7280',
    textAlign: 'center',
  }},
  features: {{
    marginTop: 20,
  }},
  sectionTitle: {{
    fontSize: 22,
    fontWeight: '600',
    marginBottom: 15,
    color: '#1f2937',
  }},
  featureCard: {{
    backgroundColor: '#f3f4f6',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
  }},
  featureText: {{
    fontSize: 16,
    color: '#374151',
  }},
}});
'''
        with open(os.path.join(mobile_dir, "App.js"), "w") as f:
            f.write(app_js)
    
    async def _generate_fullstack_project(self, project_dir: str, project_spec: Dict, architecture: Dict):
        """Genera un proyecto fullstack completo"""
        await self._generate_web_project(os.path.join(project_dir, 'frontend'), project_spec, architecture)
        await self._generate_api_project(os.path.join(project_dir, 'backend'), project_spec, architecture)
    
    async def _setup_project_config(self, project_dir: str, project_spec: Dict):
        """Configuración final del proyecto"""
        
        # Generar listas de contenido para el README
        features_list = '\n'.join([f'- {feature}' for feature in project_spec['features']])
        tech_stack_list = '\n'.join([f'- {tech}' for tech in project_spec['tech_stack']])
        user_stories_list = '\n'.join([f'- {story}' for story in project_spec.get('user_stories', [])])
        
        # --- README profesional (Formato de f-string mejorado) ---
        readme_content = f"""# {project_spec['name']}

{project_spec['description']}

## 🚀 Características

{features_list}

## 🛠️ Stack Tecnológico

{tech_stack_list}

## 📁 Estructura del Proyecto
{project_spec['name'].lower().replace(' ', '-')}/ ├── frontend/ │   ├── src/ │   │   ├── components/ │   │   ├── pages/ │   │   ├── App.jsx │   │   └── main.jsx │   ├── package.json │   └── vite.config.js └── README.md

## 🏃‍♂️ Desarrollo

### Prerrequisitos
- Node.js 16+
- npm o yarn

### Instalación
```bash
cd frontend
npm install
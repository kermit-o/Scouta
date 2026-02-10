"""
Generador de Frontend React - Código REAL y FUNCIONAL
VERSIÓN CORREGIDA
"""
from typing import Dict, Any, List
import os


class ReactGenerator:
    def generate(self, spec: Dict[str, Any]) -> Dict[str, str]:
        """Genera una aplicación React completa y funcional"""
        print(f"⚛️  Generando frontend React para {spec['name']}")
        
        code_files = {}
        
        # Archivos de configuración del proyecto
        code_files["package.json"] = self._generate_package_json(spec)
        
        # Archivos de configuración
        code_files["public/index.html"] = self._generate_index_html(spec)
        
        # Componentes principales
        code_files["src/index.js"] = self._generate_index_js()
        code_files["src/App.js"] = self._generate_app_js(spec)
        code_files["src/App.css"] = self._generate_app_css()
        
        # Componentes de entidades
        for entity in spec["main_entities"]:
            code_files.update(self._generate_entity_components(entity))
        
        # Servicios API
        code_files["src/services/api.js"] = self._generate_api_service(spec)
        
        print(f"✅ Frontend React generado: {len(code_files)} archivos")
        return code_files
    
    def _generate_package_json(self, spec: Dict[str, Any]) -> str:
        """Genera package.json con dependencias reales"""
        return f'''
{{
  "name": "{spec['name']}-frontend",
  "version": "1.0.0",
  "description": "Frontend for {spec['name']}",
  "type": "module",
  "scripts": {{
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  }},
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.5.0",
    "react-router-dom": "^6.15.0"
  }},
  "devDependencies": {{
    "vite": "^4.4.5",
    "@vitejs/plugin-react": "^4.0.3"
  }}
}}
'''
    
    def _generate_index_html(self, spec: Dict[str, Any]) -> str:
        """Genera index.html"""
        return f'''
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{spec['name']}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
  </body>
</html>
'''
    
    def _generate_index_js(self) -> str:
        """Genera index.js"""
        return '''
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.js'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
'''
    
    def _generate_app_js(self, spec: Dict[str, Any]) -> str:
        """Genera el componente principal App.js"""
        entities_imports = "\n".join([
            f"import {entity['name']}List from './components/{entity['name']}List'" 
            for entity in spec["main_entities"]
        ])
        
        entities_routes = "\n        ".join([
            f'<Route path="/{entity["name"].lower()}s" element={{<{entity["name"]}List />}} />'
            for entity in spec["main_entities"]
        ])
        
        nav_links = "".join([
            f'<Link to="/{entity["name"].lower()}s">{entity["name"]}s</Link>' 
            for entity in spec["main_entities"]
        ])
        
        feature_list = "".join([
            f'<li>Manage {entity["name"]}s</li>' 
            for entity in spec["main_entities"]
        ])
        
        return f'''
import React from 'react'
import {{ BrowserRouter as Router, Routes, Route, Link }} from 'react-router-dom'
import './App.css'
{entities_imports}

function App() {{
  return (
    <Router>
      <div className="App">
        <nav className="navbar">
          <h1>{spec['name']}</h1>
          <div className="nav-links">
            <Link to="/">Home</Link>
            {nav_links}
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={{
              <div className="home">
                <h2>Welcome to {spec['name']}</h2>
                <p>This application was automatically generated.</p>
                <div className="features">
                  <h3>Available Features:</h3>
                  <ul>
                    {feature_list}
                  </ul>
                </div>
              </div>
            }} />
            {entities_routes}
          </Routes>
        </main>
      </div>
    </Router>
  )
}}

export default App
'''
    
    def _generate_app_css(self) -> str:
        """Genera estilos CSS básicos"""
        return '''
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
  background-color: #f5f5f5;
}

.App {
  min-height: 100vh;
}

.navbar {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.nav-links {
  display: flex;
  gap: 2rem;
}

.nav-links a {
  color: white;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-links a:hover {
  background-color: #34495e;
}

.main-content {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.home {
  text-align: center;
  padding: 2rem;
}

.home h2 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.features {
  margin-top: 2rem;
  text-align: left;
  display: inline-block;
}

.features ul {
  list-style-position: inside;
}

.entity-list {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.entity-list h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
}

.entity-item {
  padding: 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 1rem;
  background: #f8f9fa;
}

.entity-item h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.loading {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.error {
  background: #e74c3c;
  color: white;
  padding: 1rem;
  border-radius: 4px;
  margin-bottom: 1rem;
}
'''
    
    def _generate_entity_components(self, entity: Dict[str, Any]) -> Dict[str, str]:
        """Genera componentes React para una entidad - VERSIÓN SIMPLIFICADA"""
        entity_name = entity["name"]
        entity_name_lower = entity_name.lower()
        
        components = {}
        
        # Generar campos para mostrar (excluyendo id)
        display_fields = [field for field in entity["fields"] if field != "id"]
        field_displays = "\n              ".join([
            f'<p><strong>{field}:</strong> {{{entity_name_lower}.{field}}}</p>'
            for field in display_fields
        ])
        
        # Componente de lista - VERSIÓN SIMPLIFICADA Y CORREGIDA
        components[f"src/components/{entity_name}List.js"] = f'''
import React, {{ useState, useEffect }} from 'react'
import axios from 'axios'
import './{entity_name}List.css'

const {entity_name}List = () => {{
  const [{entity_name_lower}s, set{entity_name}s] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {{
    fetch{entity_name}s()
  }}, [])

  const fetch{entity_name}s = async () => {{
    try {{
      setLoading(true)
      const response = await axios.get('http://localhost:8000/api/{entity_name_lower}s')
      set{entity_name}s(response.data)
      setError(null)
    }} catch (err) {{
      setError('Failed to fetch {entity_name_lower}s: ' + err.message)
      console.error('Error fetching {entity_name_lower}s:', err)
    }} finally {{
      setLoading(false)
    }}
  }}

  if (loading) return <div className="loading">Loading {entity_name_lower}s...</div>
  if (error) return <div className="error">{{error}}</div>

  return (
    <div className="{entity_name_lower}-list entity-list">
      <h2>{entity_name} Management</h2>
      <div className="entity-count">
        Total: {{ {entity_name_lower}s.length }} {entity_name_lower}s
      </div>
      <div className="entity-items">
        {{ {entity_name_lower}s.map({entity_name_lower} => (
          <div key={{ {entity_name_lower}.id }} className="entity-item">
            <h3>{{ {entity_name_lower}.name || '{entity_name} #' + {entity_name_lower}.id }}</h3>
            <div className="entity-details">
              {field_displays}
            </div>
          </div>
        )) }}
      </div>
    </div>
  )
}}

export default {entity_name}List
'''
        
        # Estilos del componente
        components[f"src/components/{entity_name}List.css"] = f'''
.{entity_name_lower}-list {{
  max-width: 800px;
  margin: 0 auto;
}}

.entity-count {{
  background: #3498db;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  display: inline-block;
  margin-bottom: 1rem;
}}

.entity-items {{
  display: flex;
  flex-direction: column;
  gap: 1rem;
}}
'''
        
        return components
    
    def _generate_api_service(self, spec: Dict[str, Any]) -> str:
        """Genera servicio para llamadas API"""
        return '''
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log('Making API request:', config)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default api
'''

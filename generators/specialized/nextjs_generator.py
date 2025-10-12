import os
import json
import shutil

class NextJSGenerator:
    def generate(self, project_name, description, features, technologies):
        project_path = f"generated_projects/{project_name}"
        
        # Limpiar si existe
        if os.path.exists(project_path):
            shutil.rmtree(project_path)
        
        os.makedirs(project_path, exist_ok=True)
        
        print(f"🚀 Generando proyecto Next.js: {project_name}")
        
        try:
            # 1. package.json avanzado
            self._create_package_json(project_path, project_name, description, technologies, features)
            
            # 2. Configuración Next.js
            self._create_next_config(project_path, technologies)
            
            # 3. Estructura de páginas
            self._create_pages_structure(project_path, project_name, description, features)
            
            # 4. Componentes base
            self._create_components(project_path, features)
            
            # 5. Estilos y assets
            self._create_styling(project_path, technologies)
            
            print(f"✅ Next.js project '{project_name}' generado exitosamente!")
            
            return {
                "success": True,
                "project_path": project_path,
                "type": "nextjs_app",
                "features": features,
                "technologies": technologies,
                "next_steps": [
                    f"cd {project_path}",
                    "npm install",
                    "npm run dev",
                    "Abre http://localhost:3000"
                ]
            }
            
        except Exception as e:
            print(f"❌ Error generando Next.js project: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def _create_package_json(self, project_path, project_name, description, technologies, features):
        package_data = {
            "name": project_name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "description": description,
            "private": True,
            "scripts": {
                "dev": "next dev",
                "build": "next build",
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            }
        }
        
        # Inicializar devDependencies como dict vacío
        dev_dependencies = {}
        
        # Añadir TypeScript si está seleccionado
        if "typescript" in technologies:
            dev_dependencies.update({
                "typescript": "^5.0.0",
                "@types/react": "^18.0.0",
                "@types/node": "^20.0.0",
                "@types/react-dom": "^18.0.0"
            })
        
        # Añadir Tailwind CSS si está seleccionado
        if "tailwind" in technologies:
            dev_dependencies.update({
                "tailwindcss": "^3.3.0",
                "autoprefixer": "^10.0.1",
                "postcss": "^8.4.0"
            })
        
        # Solo añadir devDependencies si hay alguna
        if dev_dependencies:
            package_data["devDependencies"] = dev_dependencies
        
        # Dependencias basadas en features
        if "auth" in features:
            package_data["dependencies"]["next-auth"] = "^4.24.0"
        
        if "payment" in features:
            package_data["dependencies"]["stripe"] = "^13.0.0"
        
        with open(os.path.join(project_path, "package.json"), "w") as f:
            json.dump(package_data, f, indent=2)
    
    def _create_next_config(self, project_path, technologies):
        config_content = '''/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig
'''
        
        with open(os.path.join(project_path, "next.config.js"), "w") as f:
            f.write(config_content)
        
        # TypeScript config si es necesario - CORREGIDO: usar Python booleanos
        if "typescript" in technologies:
            tsconfig = {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "es6"],
                    "allowJs": True,  # CORREGIDO: True en lugar de true
                    "skipLibCheck": True,
                    "strict": True,
                    "noEmit": True,
                    "esModuleInterop": True,
                    "module": "esnext",
                    "moduleResolution": "bundler",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "jsx": "preserve",
                    "incremental": True,
                    "plugins": [{"name": "next"}]
                },
                "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
                "exclude": ["node_modules"]
            }
            
            with open(os.path.join(project_path, "tsconfig.json"), "w") as f:
                json.dump(tsconfig, f, indent=2)
    
    def _create_pages_structure(self, project_path, project_name, description, features):
        # Usar App Router (nuevo en Next.js 13+)
        app_dir = os.path.join(project_path, "app")
        os.makedirs(app_dir, exist_ok=True)
        
        # Layout principal
        layout_content = f'''export const metadata = {{
  title: '{project_name}',
  description: '{description}',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  )
}}
'''
        with open(os.path.join(app_dir, "layout.tsx"), "w") as f:
            f.write(layout_content)
        
        # Página principal
        page_content = f'''export default function Home() {{
  return (
    <main>
      <div className="container">
        <h1>🚀 {project_name}</h1>
        <p>{description}</p>
        <p>✨ Generado automáticamente con <strong>Forge SaaS</strong></p>
        
        <div className="features">
          {'<div className="feature">' + 
           '<h3>🔐 Autenticación</h3>' +
           '<p>Sistema de login y registro incluido</p>' +
           '</div>' if 'auth' in features else ''}

          {'<div className="feature">' +
           '<h3>💳 Pagos</h3>' +
           '<p>Integración con Stripe lista</p>' +
           '</div>' if 'payment' in features else ''}

          {'<div className="feature">' +
           '<h3>⚙️ Admin</h3>' +
           '<p>Panel de administración</p>' +
           '</div>' if 'admin_panel' in features else ''}
        </div>

        <div className="next-steps">
          <h2>¡Listo para comenzar!</h2>
          <div className="steps">
            <p>📦 <code>npm install</code></p>
            <p>🚀 <code>npm run dev</code></p>
            <p>🏗️ <code>npm run build</code></p>
          </div>
        </div>
      </div>
    </main>
  )
}}
'''
        with open(os.path.join(app_dir, "page.tsx"), "w") as f:
            f.write(page_content)
    
    def _create_components(self, project_path, features):
        components_dir = os.path.join(project_path, "components")
        os.makedirs(components_dir, exist_ok=True)
        
        # Componente Header básico
        header_content = '''export default function Header() {
  return (
    <header>
      <nav>
        <div className="logo">Mi App</div>
        <div className="links">
          <a href="/">Inicio</a>
          <a href="/about">Acerca</a>
        </div>
      </nav>
    </header>
  )
}
'''
        with open(os.path.join(components_dir, "Header.tsx"), "w") as f:
            f.write(header_content)
    
    def _create_styling(self, project_path, technologies):
        if "tailwind" in technologies:
            # tailwind.config.js
            tailwind_config = '''/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
'''
            with open(os.path.join(project_path, "tailwind.config.js"), "w") as f:
                f.write(tailwind_config)
            
            # postcss.config.js
            postcss_config = '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
'''
            with open(os.path.join(project_path, "postcss.config.js"), "w") as f:
                f.write(postcss_config)
            
            # CSS global con Tailwind
            css_content = '''@tailwind base;
@tailwind components;
@tailwind utilities;
'''
            with open(os.path.join(project_path, "app", "globals.css"), "w") as f:
                f.write(css_content)
        else:
            # CSS básico si no hay Tailwind
            css_content = '''body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 20px;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.features {
  display: grid;
  gap: 1rem;
  margin: 2rem 0;
}

.feature {
  border: 1px solid #e2e8f0;
  padding: 1rem;
  border-radius: 8px;
}

.next-steps {
  background: #f7fafc;
  padding: 1.5rem;
  border-radius: 8px;
  margin-top: 2rem;
}
'''
            with open(os.path.join(project_path, "app", "globals.css"), "w") as f:
                f.write(css_content)

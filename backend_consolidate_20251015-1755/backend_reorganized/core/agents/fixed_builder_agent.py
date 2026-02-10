"""
Fixed Builder Agent - Versión corregida sin errores internos
"""
import os
import uuid
import json
from typing import Dict, Any

class FixedBuilderAgent:
    """Builder Agent corregido - genera proyectos REALES"""
    
    def __init__(self):
        self.generated_files = []
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Método run corregido - genera proyecto real"""
        print("🏗️ Fixed Builder Agent - Generando proyecto...")
        
        try:
            # Crear directorio del proyecto
            project_name = requirements.get('project_name', 'mi-proyecto').replace(' ', '-').lower()
            project_path = f"generated_projects/{project_name}-{project_id[:8]}"
            
            os.makedirs(project_path, exist_ok=True)
            print(f"📁 Creando proyecto en: {project_path}")
            
            # Generar archivos del proyecto
            files_created = self._generate_project_files(project_path, requirements)
            
            result = {
                "status": "built",
                "project_id": project_id,
                "project_path": project_path,
                "project_name": requirements.get('project_name', 'Mi Proyecto'),
                "files_created": files_created,
                "total_files": len(files_created),
                "message": "Proyecto generado exitosamente"
            }
            
            print(f"✅ Proyecto generado: {len(files_created)} archivos")
            return result
            
        except Exception as e:
            print(f"❌ Error en BuilderAgent: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": "error",
                "error": str(e),
                "project_id": project_id
            }
    
    def _generate_project_files(self, project_path: str, requirements: Dict[str, Any]) -> list:
        """Genera archivos REALES del proyecto"""
        files_created = []
        
        # 1. package.json
        package_json = {
            "name": requirements.get('project_name', 'mi-proyecto').lower().replace(' ', '-'),
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "next dev",
                "build": "next build", 
                "start": "next start",
                "lint": "next lint"
            },
            "dependencies": {
                "next": "14.0.0",
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "devDependencies": {
                "typescript": "^5.0.0",
                "@types/node": "^20.0.0",
                "@types/react": "^18.0.0",
                "@types/react-dom": "^18.0.0",
                "eslint": "^8.0.0",
                "eslint-config-next": "14.0.0"
            }
        }
        
        self._write_file(project_path, "package.json", json.dumps(package_json, indent=2))
        files_created.append("package.json")
        
        # 2. README.md
        readme_content = f"""# {requirements.get('project_name', 'Mi Proyecto')}

## Descripción
{requirements.get('description', 'Proyecto generado automáticamente por Forge SaaS')}

## Características
{chr(10).join(['- ' + feature for feature in requirements.get('features', ['Funcionalidad básica'])])}

## Stack Tecnológico
{chr(10).join(['- ' + tech for tech in requirements.get('tech_stack', ['React', 'Next.js'])])}

## Instalación

\\`\\`\\`bash
npm install
npm run dev
\\`\\`\\`

## Estructura

\\`\\`\\`
{project_path}/
├── app/
│   └── page.jsx
├── package.json
└── README.md
\\`\\`\\`

---
*Generado automáticamente por Forge SaaS*
"""
        self._write_file(project_path, "README.md", readme_content)
        files_created.append("README.md")
        
        # 3. Next.js Config
        next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
}

module.exports = nextConfig
"""
        self._write_file(project_path, "next.config.js", next_config)
        files_created.append("next.config.js")
        
        # 4. Página principal (app/page.jsx)
        app_content = """// Página principal - Generada por Forge SaaS
import React from 'react';

export default function Home() {
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>¡Bienvenido a tu proyecto!</h1>
      <p>Este proyecto fue generado automáticamente por <strong>Forge SaaS</strong></p>
      
      <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ddd', borderRadius: '8px' }}>
        <h2>🚀 Características incluidas:</h2>
        <ul>
          <li>✅ Estructura Next.js 14</li>
          <li>✅ Configuración lista para desarrollo</li>
          <li>✅ Documentación completa</li>
          <li>✅ Fácil de personalizar</li>
        </ul>
      </div>
      
      <div style={{ marginTop: '2rem' }}>
        <h3>📁 Para empezar:</h3>
        <code>npm install && npm run dev</code>
      </div>
    </div>
  );
}
"""
        os.makedirs(f"{project_path}/app", exist_ok=True)
        self._write_file(project_path, "app/page.jsx", app_content)
        files_created.append("app/page.jsx")
        
        # 5. Layout principal (app/layout.jsx)
        layout_content = """// Layout principal
import React from 'react';

export const metadata = {
  title: 'Mi Proyecto - Forge SaaS',
  description: 'Proyecto generado automáticamente',
};

export default function RootLayout({ children }) {
  return (
    <html lang="es">
      <body>
        <nav style={{ padding: '1rem', borderBottom: '1px solid #eee' }}>
          <strong>Forge SaaS</strong> - Proyecto Generado
        </nav>
        <main>
          {children}
        </main>
      </body>
    </html>
  );
}
"""
        self._write_file(project_path, "app/layout.jsx", layout_content)
        files_created.append("app/layout.jsx")
        
        return files_created
    
    def _write_file(self, project_path: str, file_path: str, content: str):
        """Escribe un archivo en el proyecto"""
        full_path = os.path.join(project_path, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.generated_files.append(file_path)

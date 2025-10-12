import os
import json

class SimpleTemplateEngine:
    def generate_react_project(self, project_name, description, output_dir="generated_projects", validate=True):
        """Genera un proyecto React básico pero funcional"""
        
        project_path = os.path.join(output_dir, project_name)
        
        # Limpiar proyecto existente si existe
        if os.path.exists(project_path):
            import shutil
            shutil.rmtree(project_path)
        
        os.makedirs(project_path, exist_ok=True)
        
        print(f"🚀 Generando proyecto React: {project_name}")
        print(f"📝 Descripción: {description}")
        
        try:
            # 1. Crear package.json
            package_json = {
                "name": project_name.lower().replace(" ", "-"),
                "version": "1.0.0",
                "description": description,
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
            
            with open(os.path.join(project_path, "package.json"), "w") as f:
                json.dump(package_json, f, indent=2)
            print("✅ package.json creado")
            
            # 2. Crear index.html
            index_html = f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''
            
            with open(os.path.join(project_path, "index.html"), "w") as f:
                f.write(index_html)
            print("✅ index.html creado")
            
            # 3. Crear directorio src y archivos
            src_dir = os.path.join(project_path, "src")
            os.makedirs(src_dir, exist_ok=True)
            
            # main.jsx - SIMPLIFICADO
            main_jsx = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''
            
            with open(os.path.join(src_dir, "main.jsx"), "w") as f:
                f.write(main_jsx)
            print("✅ src/main.jsx creado")
            
            # App.jsx - CORREGIDO (sin error de f-string)
            app_jsx = f'''import {{ useState }} from 'react'

function App() {{
  const [count, setCount] = useState(0)

  return (
    <div style={{{{padding: '40px', textAlign: 'center', backgroundColor: '#f5f5f5', minHeight: '100vh'}}}}>
      <h1 style={{{{color: '#333'}}}}>🎉 {project_name}</h1>
      <p style={{{{color: '#666', fontSize: '18px'}}}}>{description}</p>
      
      <div style={{{{margin: '30px 0', padding: '20px', backgroundColor: 'white', borderRadius: '10px', display: 'inline-block'}}}}>
        <button 
          onClick={{() => setCount(count + 1)}}
          style={{{{padding: '12px 24px', fontSize: '16px', backgroundColor: '#007acc', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', marginBottom: '10px'}}}}
        >
          Clickeame! Count: {{count}}
        </button>
        <p style={{{{margin: 0, color: '#666'}}}}>
          ¡Funciona! Generado por <strong>Forge SaaS</strong>
        </p>
      </div>
    </div>
  )
}}

export default App'''
            
            with open(os.path.join(src_dir, "App.jsx"), "w") as f:
                f.write(app_jsx)
            print("✅ src/App.jsx creado")
            
            # 4. Crear vite.config.js
            vite_config = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})'''
            
            with open(os.path.join(project_path, "vite.config.js"), "w") as f:
                f.write(vite_config)
            print("✅ vite.config.js creado")
            
            print(f"\\n✅ PROYECTO GENERADO EXITOSAMENTE!")
            print(f"📍 Ubicación: {project_path}")
            
            # Validación básica
            if validate:
                print("\\n🧪 VALIDACIÓN BÁSICA:")
                files_created = [
                    "package.json", "index.html", "src/main.jsx", 
                    "src/App.jsx", "vite.config.js"
                ]
                all_ok = True
                for file in files_created:
                    file_path = os.path.join(project_path, file)
                    if os.path.exists(file_path):
                        size = os.path.getsize(file_path)
                        print(f"   ✅ {file}: {size} bytes")
                    else:
                        print(f"   ❌ {file}: NO EXISTE")
                        all_ok = False
                
                if all_ok:
                    print("🎉 ¡PROYECTO VALIDADO CORRECTAMENTE!")
                else:
                    print("⚠️  El proyecto tiene problemas")
            
            print("\\n🎯 COMANDOS PARA EJECUTAR:")
            print(f"   cd {project_path}")
            print("   npm install")
            print("   npm run dev")
            
            return {
                "project_path": project_path,
                "success": True,
                "files_created": files_created if validate else []
            }
            
        except Exception as e:
            print(f"❌ Error generando proyecto: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "project_path": project_path,
                "error": str(e),
                "success": False
            }

if __name__ == "__main__":
    engine = SimpleTemplateEngine()
    result = engine.generate_react_project(
        "Mi App React Forge", 
        "Una aplicación React generada automáticamente por Forge SaaS",
        validate=True
    )

"""
SERVIDOR DE RESPALDO - VERSIÓN ULTRA ROBUSTA
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import uvicorn
import uuid
import os

app = FastAPI(title="Backup Project Generator", version="1.0")

class ProjectRequest(BaseModel):
    name: str
    description: str
    project_type: str = "web_app"

@app.post("/api/backup/projects")
async def create_backup_project(request: ProjectRequest):
    """Endpoint de respaldo que siempre funciona"""
    try:
        project_id = str(uuid.uuid4())
        project_path = f"generated_projects/backup-{request.name}-{project_id[:8]}"
        
        # Crear directorio del proyecto
        os.makedirs(project_path, exist_ok=True)
        
        # Crear archivos básicos
        files_created = []
        
        # README.md
        readme_path = f"{project_path}/README.md"
        with open(readme_path, 'w') as f:
            f.write(f"# {request.name}\n\n{request.description}\n\nGenerado automáticamente.")
        files_created.append(readme_path)
        
        # requirements.txt
        req_path = f"{project_path}/requirements.txt"
        with open(req_path, 'w') as f:
            f.write("fastapi==0.104.1\nuvicorn==0.24.0\npydantic==2.5.0")
        files_created.append(req_path)
        
        # main.py
        main_path = f"{project_path}/main.py"
        with open(main_path, 'w') as f:
            f.write('''from fastapi import FastAPI

app = FastAPI(title="Generated API")

@app.get("/")
async def root():
    return {"message": "API generada automáticamente"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
''')
        files_created.append(main_path)
        
        return {
            "status": "success",
            "system": "backup_generator",
            "project_id": project_id,
            "project_name": request.name,
            "project_path": project_path,
            "files_created": files_created,
            "total_files": len(files_created),
            "message": "Proyecto generado exitosamente (modo respaldo)"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Error en modo respaldo"
        }

@app.get("/backup/health")
async def backup_health():
    return {"status": "healthy", "service": "backup_generator"}

if __name__ == "__main__":
    print("🚀 INICIANDO SERVIDOR DE RESPALDO en puerto 8001")
    uvicorn.run(app, host="0.0.0.0", port=8001)

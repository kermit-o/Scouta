#!/usr/bin/env python3
import subprocess
import json
import time
import os
from datetime import datetime
import psutil

try:
    import docker
    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    print("⚠️  Docker module not available, using fallback methods")

class SystemMonitor:
    def obtener_estado(self):
        return {
            "timestamp": datetime.now().isoformat(),
            "docker": self.estado_docker(),
            "archivos": self.estado_archivos(),
            "imports": self.verificar_imports(),
            "logs": self.ultimos_logs(),
            "recursos": self.estado_recursos(),
            "docker_available": DOCKER_AVAILABLE
        }
    
    def estado_docker(self):
        if not DOCKER_AVAILABLE:
            return {"error": "Docker module not installed", "fallback": self.estado_docker_fallback()}
        
        try:
            client = docker.from_env()
            containers = client.containers.list()
            return {
                "contenedores": [{
                    "nombre": c.name,
                    "estado": c.status,
                    "puertos": c.ports
                } for c in containers],
                "redes": [n.name for n in client.networks.list()],
                "imagenes": [i.tags for i in client.images.list()]
            }
        except Exception as e:
            return {"error": str(e), "fallback": self.estado_docker_fallback()}
    
    def estado_docker_fallback(self):
        """Fallback method using docker-compose commands"""
        try:
            # Get containers using docker-compose
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, timeout=10)
            containers = []
            for line in result.stdout.split('\n')[2:]:  # Skip header
                if line.strip():
                    parts = line.split()
                    containers.append({
                        "nombre": parts[0],
                        "estado": parts[3] if len(parts) > 3 else "unknown"
                    })
            
            return {
                "contenedores": containers,
                "metodo": "fallback_docker_compose"
            }
        except Exception as e:
            return {"error": f"Fallback also failed: {str(e)}"}
    
    def estado_archivos(self):
        estructura = {}
        for root, dirs, files in os.walk("."):
            if any(x in root for x in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']):
                continue
            estructura[root] = {
                "directorios": dirs,
                "archivos": [f for f in files if f.endswith(('.py', '.yml', '.yaml', '.json', '.md', '.txt', '.sh'))]
            }
        return estructura
    
    def verificar_imports(self):
        problemas = []
        python_dirs = ['backend/app', 'oracle_scripts']
        
        for base_dir in python_dirs:
            if not os.path.exists(base_dir):
                problemas.append({
                    "archivo": base_dir,
                    "problema": "Directorio no encontrado",
                    "tipo": "DIRECTORIO_FALTANTE"
                })
                continue
                
            for root, _, files in os.walk(base_dir):
                for file in files:
                    if file.endswith('.py'):
                        ruta = os.path.join(root, file)
                        try:
                            with open(ruta, 'r', encoding='utf-8') as f:
                                contenido = f.read()
                                if 'from ..' in contenido or 'from .' in contenido:
                                    lineas_problematicas = [f"{i+1}: {line.strip()}" for i, line in enumerate(contenido.split('\n')) 
                                                          if 'from .' in line and not line.strip().startswith('#')]
                                    if lineas_problematicas:
                                        problemas.append({
                                            "archivo": ruta,
                                            "problema": "Import relativo detectado",
                                            "lineas": lineas_problematicas,
                                            "tipo": "IMPORT_RELATIVO"
                                        })
                        except Exception as e:
                            problemas.append({"archivo": ruta, "error": str(e), "tipo": "ERROR_LECTURA"})
        return problemas
    
    def ultimos_logs(self):
        try:
            result = subprocess.run(['docker-compose', 'logs', '--tail=10'], 
                                  capture_output=True, text=True, timeout=15)
            return result.stdout.split('\n')[-15:]  # Last 15 lines
        except subprocess.TimeoutExpired:
            return ["Timeout al obtener logs"]
        except Exception as e:
            return [f"Error obteniendo logs: {str(e)}"]
    
    def estado_recursos(self):
        return {
            "cpu": psutil.cpu_percent(),
            "memoria": psutil.virtual_memory().percent,
            "disco": psutil.disk_usage('.').percent,
            "disco_espacio": f"{psutil.disk_usage('.').free / (1024**3):.1f} GB libres"
        }

if __name__ == "__main__":
    monitor = SystemMonitor()
    estado = monitor.obtener_estado()
    print(json.dumps(estado, indent=2, ensure_ascii=False))

#!/usr/bin/env python3
import json
import re

class DiagnosticEngine:
    def analizar(self, estado):
        problemas = []
        
        # Diagnosticar Docker
        problemas.extend(self.diagnosticar_docker(estado['docker']))
        
        # Diagnosticar archivos
        problemas.extend(self.diagnosticar_archivos(estado['archivos']))
        
        # Diagnosticar imports
        problemas.extend(self.diagnosticar_imports(estado['imports']))
        
        # Diagnosticar logs
        problemas.extend(self.diagnosticar_logs(estado['logs']))
        
        return problemas
    
    def diagnosticar_docker(self, estado_docker):
        problemas = []
        if 'error' in estado_docker:
            problemas.append({"tipo": "DOCKER_ERROR", "gravedad": "ALTA", "mensaje": estado_docker['error']})
            return problemas
        
        for contenedor in estado_docker.get('contenedores', []):
            if 'unhealthy' in contenedor['estado'].lower():
                problemas.append({
                    "tipo": "CONTENEDOR_UNHEALTHY",
                    "gravedad": "ALTA", 
                    "mensaje": f"Contenedor {contenedor['nombre']} no saludable"
                })
        
        return problemas
    
    def diagnosticar_archivos(self, estructura):
        problemas = []
        required_dirs = ['backend/app', 'backend/app/agents', 'backend/app/services', 'ui']
        
        for dir in required_dirs:
            if dir not in estructura:
                problemas.append({
                    "tipo": "DIRECTORIO_FALTANTE",
                    "gravedad": "MEDIA",
                    "mensaje": f"Directorio requerido faltante: {dir}"
                })
        
        return problemas
    
    def diagnosticar_imports(self, imports_problematicos):
        problemas = []
        for import_problem in imports_problematicos:
            problemas.append({
                "tipo": "IMPORT_RELATIVO",
                "gravedad": "ALTA",
                "mensaje": f"Import relativo en {import_problem['archivo']}",
                "detalles": import_problem
            })
        return problemas
    
    def diagnosticar_logs(self, logs):
        problemas = []
        error_patterns = [
            r'ImportError', r'ModuleNotFoundError', r'SyntaxError',
            r'connection refused', r'port already allocated', r'failed to start'
        ]
        
        for log in logs:
            for pattern in error_patterns:
                if re.search(pattern, log, re.IGNORECASE):
                    problemas.append({
                        "tipo": "ERROR_LOG",
                        "gravedad": "ALTA",
                        "mensaje": f"Error en log: {log[:100]}...",
                        "log_completo": log
                    })
        return problemas

if __name__ == "__main__":
    with open('estado_sistema.json', 'r') as f:
        estado = json.load(f)
    
    diagnostico = DiagnosticEngine()
    problemas = diagnostico.analizar(estado)
    print(json.dumps(problemas, indent=2))

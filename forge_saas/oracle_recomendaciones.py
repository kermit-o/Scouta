#!/usr/bin/env python3
import json

class RecommendationEngine:
    def generar(self, problemas):
        recomendaciones = []
        
        for problema in problemas:
            rec = self.generar_recomendacion(problema)
            if rec:
                recomendaciones.append(rec)
        
        return recomendaciones
    
    def generar_recomendacion(self, problema):
        soluciones = {
            "IMPORT_RELATIVO": self.solucion_imports,
            "CONTENEDOR_UNHEALTHY": self.solucion_contenedor,
            "DIRECTORIO_FALTANTE": self.solucion_directorios,
            "ERROR_LOG": self.solucion_logs,
            "DOCKER_ERROR": self.solucion_docker
        }
        
        solver = soluciones.get(problema['tipo'])
        return solver(problema) if solver else None
    
    def solucion_imports(self, problema):
        archivo = problema['detalles']['archivo']
        return {
            "problema": problema['mensaje'],
            "solucion": "Convertir imports relativos a absolutos",
            "comando": f"sed -i 's/from \\.\\./from app./g' {archivo} && sed -i 's/from \\./from app./g' {archivo}",
            "archivo": archivo,
            "prioridad": "ALTA"
        }
    
    def solucion_contenedor(self, problema):
        return {
            "problema": problema['mensaje'],
            "solucion": "Reiniciar contenedor y verificar logs",
            "comando": "docker-compose restart && docker-compose logs --tail=20",
            "prioridad": "ALTA"
        }
    
    def solucion_directorios(self, problema):
        return {
            "problema": problema['mensaje'],
            "solucion": "Crear directorio faltante",
            "comando": f"mkdir -p {problema['mensaje'].split(': ')[1]}",
            "prioridad": "MEDIA"
        }
    
    def solucion_logs(self, problema):
        return {
            "problema": problema['mensaje'],
            "solucion": "Analizar error específico en logs",
            "comando": f"docker-compose logs | grep -i '{problema['log_completo'][:50]}'",
            "prioridad": problema['gravedad']
        }
    
    def solucion_docker(self, problema):
        return {
            "problema": problema['mensaje'],
            "solucion": "Reiniciar Docker daemon o verificar instalación",
            "comando": "sudo systemctl restart docker && docker-compose up -d",
            "prioridad": "CRITICA"
        }

if __name__ == "__main__":
    with open('problemas.json', 'r') as f:
        problemas = json.load(f)
    
    recomendador = RecommendationEngine()
    soluciones = recomendador.generar(problemas)
    print(json.dumps(soluciones, indent=2))

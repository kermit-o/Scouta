#!/usr/bin/env python3
import json
import subprocess
import os
import time
from datetime import datetime

class OracleSimple:
    def __init__(self):
        self.ciclo_numero = 0
    
    def ejecutar_ciclo(self):
        self.ciclo_numero += 1
        print(f"\n🔮 [Ciclo {self.ciclo_numero}] Oracle Simple")
        
        # Chequear problemas básicos
        problemas = self.detectar_problemas()
        
        if problemas:
            print(f"❌ Detectados {len(problemas)} problemas")
            for problema in problemas:
                print(f"   - {problema['mensaje']}")
                if 'solucion' in problema:
                    print(f"     💡 Solución: {problema['solucion']}")
                    self.aplicar_solucion(problema)
        else:
            print("✅ Sistema saludable")
        
        return len(problemas)
    
    def detectar_problemas(self):
        problemas = []
        
        # 1. Verificar Docker
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True, timeout=10)
            if 'unhealthy' in result.stdout:
                problemas.append({
                    "tipo": "DOCKER_UNHEALTHY",
                    "mensaje": "Contenedores no saludables detectados",
                    "solucion": "docker-compose restart && docker-compose logs --tail=20"
                })
        except:
            problemas.append({
                "tipo": "DOCKER_ERROR", 
                "mensaje": "Error ejecutando docker-compose"
            })
        
        # 2. Verificar imports problemáticos
        imports_problematicos = []
        for root, _, files in os.walk('backend/app'):
            for file in files:
                if file.endswith('.py'):
                    with open(os.path.join(root, file), 'r') as f:
                        content = f.read()
                        if 'from ..' in content or 'from .' in content:
                            imports_problematicos.append(os.path.join(root, file))
        
        if imports_problematicos:
            problemas.append({
                "tipo": "IMPORTS_RELATIVOS",
                "mensaje": f"Imports relativos en {len(imports_problematicos)} archivos",
                "archivos": imports_problematicos,
                "solucion": "find backend/app -name '*.py' -exec sed -i 's/from \\.\\./from app./g' {} \\; && find backend/app -name '*.py' -exec sed -i 's/from \\./from app./g' {} \\;"
            })
        
        # 3. Verificar servicios ejecutándose
        try:
            result = subprocess.run(['curl', '-s', 'http://localhost:8080/api/health'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0 or 'healthy' not in result.stdout:
                problemas.append({
                    "tipo": "API_DOWN",
                    "mensaje": "API no responde correctamente",
                    "solucion": "docker-compose restart backend"
                })
        except:
            problemas.append({
                "tipo": "API_CHECK_ERROR",
                "mensaje": "No se pudo verificar la API"
            })
        
        return problemas
    
    def aplicar_solucion(self, problema):
        if 'solucion' in problema:
            try:
                print(f"   ⚡ Aplicando: {problema['solucion']}")
                result = subprocess.run(problema['solucion'], shell=True, capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print("     ✅ Solución aplicada exitosamente")
                else:
                    print(f"     ❌ Error aplicando solución: {result.stderr}")
            except Exception as e:
                print(f"     ❌ Excepción: {str(e)}")

if __name__ == "__main__":
    oracle = OracleSimple()
    
    # Ejecutar 3 ciclos máximo
    for i in range(3):
        problemas = oracle.ejecutar_ciclo()
        if problemas == 0:
            print("🎉 Sistema estabilizado!")
            break
        time.sleep(5)

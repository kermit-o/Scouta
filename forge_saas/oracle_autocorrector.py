#!/usr/bin/env python3
import json
import subprocess
import os
from datetime import datetime

class AutoCorrector:
    def aplicar(self, soluciones):
        resultados = []
        
        for solucion in soluciones:
            if solucion['prioridad'] in ['ALTA', 'CRITICA']:
                resultado = self.ejecutar_comando(solucion['comando'])
                resultados.append({
                    "solucion": solucion['solucion'],
                    "comando": solucion['comando'],
                    "resultado": resultado,
                    "timestamp": datetime.now().isoformat()
                })
        
        return resultados
    
    def ejecutar_comando(self, comando):
        try:
            if comando.startswith('sed ') and '&&' in comando:
                # Ejecutar comandos sed secuencialmente
                comandos = comando.split(' && ')
                resultados = []
                for cmd in comandos:
                    resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    resultados.append({
                        "comando": cmd,
                        "returncode": resultado.returncode,
                        "stdout": resultado.stdout,
                        "stderr": resultado.stderr
                    })
                return resultados
            else:
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=30)
                return {
                    "returncode": resultado.returncode,
                    "stdout": resultado.stdout,
                    "stderr": resultado.stderr
                }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout expired"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    with open('soluciones.json', 'r') as f:
        soluciones = json.load(f)
    
    corrector = AutoCorrector()
    resultados = corrector.aplicar(soluciones)
    print(json.dumps(resultados, indent=2))
EOLcat > oracle_autocorrector.py << 'EOL'
#!/usr/bin/env python3
import json
import subprocess
import os
from datetime import datetime

class AutoCorrector:
    def aplicar(self, soluciones):
        resultados = []
        
        for solucion in soluciones:
            if solucion['prioridad'] in ['ALTA', 'CRITICA']:
                resultado = self.ejecutar_comando(solucion['comando'])
                resultados.append({
                    "solucion": solucion['solucion'],
                    "comando": solucion['comando'],
                    "resultado": resultado,
                    "timestamp": datetime.now().isoformat()
                })
        
        return resultados
    
    def ejecutar_comando(self, comando):
        try:
            if comando.startswith('sed ') and '&&' in comando:
                # Ejecutar comandos sed secuencialmente
                comandos = comando.split(' && ')
                resultados = []
                for cmd in comandos:
                    resultado = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                    resultados.append({
                        "comando": cmd,
                        "returncode": resultado.returncode,
                        "stdout": resultado.stdout,
                        "stderr": resultado.stderr
                    })
                return resultados
            else:
                resultado = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=30)
                return {
                    "returncode": resultado.returncode,
                    "stdout": resultado.stdout,
                    "stderr": resultado.stderr
                }
        except subprocess.TimeoutExpired:
            return {"error": "Timeout expired"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    with open('soluciones.json', 'r') as f:
        soluciones = json.load(f)
    
    corrector = AutoCorrector()
    resultados = corrector.aplicar(soluciones)
    print(json.dumps(resultados, indent=2))

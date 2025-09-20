#!/usr/bin/env python3
import json
import time
from oracle_monitor import SystemMonitor
from oracle_diagnostico import DiagnosticEngine
from oracle_recomendaciones import RecommendationEngine
from oracle_autocorrector import AutoCorrector

class OracleAutonomo:
    def __init__(self):
        self.monitor = SystemMonitor()
        self.diagnostico = DiagnosticEngine()
        self.recomendaciones = RecommendationEngine()
        self.autocorrector = AutoCorrector()
        self.ciclo_numero = 0
    
    def ejecutar_ciclo(self):
        self.ciclo_numero += 1
        print(f"\n🔮 [Ciclo {self.ciclo_numero}] Ejecutando Oráculo Autónomo...")
        
        # 1. Monitorear
        print("📊 Monitoreando sistema...")
        estado = self.monitor.obtener_estado()
        with open(f'estado_{self.ciclo_numero}.json', 'w') as f:
            json.dump(estado, f, indent=2)
        
        # 2. Diagnosticar
        print("🔍 Diagnosticando problemas...")
        problemas = self.diagnostico.analizar(estado)
        with open(f'problemas_{self.ciclo_numero}.json', 'w') as f:
            json.dump(problemas, f, indent=2)
        
        if problemas:
            print(f"❌ Detectados {len(problemas)} problemas")
            
            # 3. Generar recomendaciones
            print("💡 Generando soluciones...")
            soluciones = self.recomendaciones.generar(problemas)
            with open(f'soluciones_{self.ciclo_numero}.json', 'w') as f:
                json.dump(soluciones, f, indent=2)
            
            # 4. Aplicar correcciones automáticas
            print("⚡ Aplicando correcciones automáticas...")
            resultados = self.autocorrector.aplicar(soluciones)
            with open(f'resultados_{self.ciclo_numero}.json', 'w') as f:
                json.dump(resultados, f, indent=2)
            
            print("✅ Ciclo completado con correcciones")
        else:
            print("✅ Sistema saludable - No se requieren correcciones")
        
        return len(problemas)

if __name__ == "__main__":
    oracle = OracleAutonomo()
    
    # Ejecutar ciclos cada 10 segundos
    while True:
        problemas = oracle.ejecutar_ciclo()
        if problemas == 0:
            print("🎉 Sistema estabilizado - Oráculo en modo monitor")
            break
        time.sleep(10)

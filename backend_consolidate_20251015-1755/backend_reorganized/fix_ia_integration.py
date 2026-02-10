#!/usr/bin/env python3
import os

def propose_fix():
    print("🔧 PLAN PARA HABILITAR LA IA REAL")
    print("=" * 50)
    
    print("1. 🐛 CORREGIR ERRORES EN AGENTES:")
    print("   • PlanningAgent: Corregir 'DPSK_API_KY' → 'DPSK_API_KEY'")
    print("   • PlanningAgent: Corregir 'temperatre' → 'temperature'") 
    print("   • PlanningAgent: Corregir 'Tre' → 'True', 'alse' → 'False'")
    print("   • PlanningAgent: Corregir 'ser reqirements' → 'user requirements'")
    print("   • PlanningAgent: Corregir 'otpt' → 'output'")
    
    print("\n2. �� CONFIGURAR ENTORNO:")
    print("   • Crear archivo .env con DPSK_API_KEY=tu_clave_real")
    print("   • Verificar que la clave de DeepSeek esté activa")
    
    print("\n3. 🔗 INTEGRAR AGENTES EN SERVIDOR:")
    print("   • Modificar persistent_server_fixed.py")
    print("   • Importar y usar PlanningAgent, BuilderAgent reales")
    print("   • Reemplazar la simulación actual con agentes de IA real")
    
    print("\n4. 🧪 PROBAR INTEGRACIÓN:")
    print("   • Verificar que los agentes se cargan correctamente")
    print("   • Probar generación de proyectos con IA real")
    print("   • Validar que el código generado es adaptativo")
    
    print("\n5. 🚀 DESPLIEGUE:")
    print("   • Una vez funcionando, reemplazar sistema actual")
    print("   • Mantener compatibilidad con proyectos existentes")
    
    print("\n⏱️  ESTIMACIÓN DE ESFUERZO:")
    print("   • Corrección de errores: 1-2 horas")
    print("   • Integración: 2-3 horas") 
    print("   • Pruebas: 1-2 horas")
    print("   • Total: 4-7 horas para tener IA real funcionando")

if __name__ == "__main__":
    propose_fix()

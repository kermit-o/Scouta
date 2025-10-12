"""
SISTEMA DE MONITORIZACIÓN FORGE SAAS
Observa backend, frontend, base de datos y rendimiento
"""
import time
import requests
import psutil
import logging
import json
from datetime import datetime
import subprocess
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - MONITOR - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitoring.log'),
        logging.StreamHandler()
    ]
)

class SystemMonitor:
    def __init__(self):
        self.backend_url = "http://localhost:8010"
        self.frontend_url = "http://localhost:8501"
        self.checks = {
            'backend_api': self.check_backend,
            'frontend_streamlit': self.check_frontend,
            'postgresql': self.check_postgresql,
            'system_resources': self.check_system_resources,
            'api_endpoints': self.check_api_endpoints
        }
        
    def check_backend(self):
        """Verificar estado del backend FastAPI"""
        try:
            start_time = time.time()
            response = requests.get(f"{self.backend_url}/api/v1/payments/health", timeout=5)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                return {
                    'status': 'HEALTHY',
                    'response_time_ms': round(response_time, 2),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'ERROR',
                    'status_code': response.status_code,
                    'error': response.text
                }
        except Exception as e:
            return {
                'status': 'DOWN',
                'error': str(e)
            }
    
    def check_frontend(self):
        """Verificar estado del frontend Streamlit"""
        try:
            response = requests.get(self.frontend_url, timeout=10)
            if response.status_code == 200:
                return {'status': 'HEALTHY', 'title': 'Streamlit'}
            else:
                return {'status': 'ERROR', 'status_code': response.status_code}
        except Exception as e:
            return {'status': 'DOWN', 'error': str(e)}
    
    def check_postgresql(self):
        """Verificar estado de PostgreSQL"""
        try:
            # Verificar si el contenedor está corriendo
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=postgres-forge", "--format", "{{.Names}}"],
                capture_output=True, text=True, timeout=5
            )
            if "postgres-forge" in result.stdout:
                return {'status': 'HEALTHY', 'container': 'running'}
            else:
                return {'status': 'DOWN', 'error': 'Container not found'}
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_system_resources(self):
        """Verificar recursos del sistema"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'status': 'HEALTHY',
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used_gb': round(memory.used / (1024**3), 2),
                'disk_percent': disk.percent,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            return {'status': 'ERROR', 'error': str(e)}
    
    def check_api_endpoints(self):
        """Verificar endpoints críticos de la API"""
        endpoints = {
            'payments_plans': '/api/v1/payments/plans',
            'ai_analyze': '/api/v1/ai/analyze',
            'projects': '/api/v1/projects'
        }
        
        results = {}
        for name, endpoint in endpoints.items():
            try:
                start_time = time.time()
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=10)
                response_time = (time.time() - start_time) * 1000
                
                results[name] = {
                    'status_code': response.status_code,
                    'response_time_ms': round(response_time, 2),
                    'content_type': response.headers.get('content-type', ''),
                    'success': response.status_code == 200
                }
            except Exception as e:
                results[name] = {
                    'error': str(e),
                    'success': False
                }
        
        healthy_endpoints = sum(1 for r in results.values() if r.get('success'))
        return {
            'status': 'HEALTHY' if healthy_endpoints == len(endpoints) else 'DEGRADED',
            'endpoints_tested': len(endpoints),
            'endpoints_healthy': healthy_endpoints,
            'details': results
        }
    
    def run_health_check(self):
        """Ejecutar chequeo completo del sistema"""
        logging.info("🔍 Ejecutando chequeo completo del sistema...")
        
        results = {}
        for check_name, check_func in self.checks.items():
            try:
                results[check_name] = check_func()
                status = results[check_name]['status']
                logging.info(f"  {check_name}: {status}")
            except Exception as e:
                results[check_name] = {'status': 'ERROR', 'error': str(e)}
                logging.error(f"  {check_name}: ERROR - {e}")
        
        # Guardar resultados
        with open('logs/health_check.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'results': results
            }, f, indent=2)
        
        return results
    
    def start_monitoring(self):
        """Iniciar monitorización continua"""
        logging.info("🚀 Iniciando sistema de monitorización Forge SaaS")
        logging.info(f"📊 Chequeos cada 30 segundos")
        logging.info(f"📁 Logs en: ./logs/")
        
        check_count = 0
        while True:
            check_count += 1
            logging.info(f"\n📈 CHEQUEO #{check_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            results = self.run_health_check()
            
            # Alertas críticas
            critical_issues = []
            for service, result in results.items():
                if result.get('status') in ['DOWN', 'ERROR']:
                    critical_issues.append(f"{service}: {result.get('error', 'Unknown error')}")
            
            if critical_issues:
                logging.error(f"🚨 ISSUES CRÍTICAS: {', '.join(critical_issues)}")
            
            time.sleep(30)  # Chequear cada 30 segundos

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.start_monitoring()

import logging
import json
from typing import Dict, Any, Optional
import time
import requests
import uuid
from datetime import datetime

# Asumiendo que esta es la clase base
from .agent_base import AgentBase 

logger = logging.getLogger(__name__)

# --- Configuración de la API y el modelo ---
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"{API_BASE_URL}/{MODEL_NAME}:generateContent"
# La clave API se asume que se proporciona en el entorno de ejecución o es inyectada.
API_KEY = "" 
# --------------------------------------------

class SecurityAgent(AgentBase):
    """
    Agente encargado de realizar un Análisis Estático de Seguridad de Aplicaciones (SAST)
    para identificar vulnerabilidades en el código generado.
    """

    def __init__(self):
        super().__init__("SecurityAgent")
        # Definición del esquema JSON estricto para el reporte de seguridad
        self.security_schema = {
            "type": "OBJECT",
            "properties": {
                "overall_risk_level": {"type": "STRING", "description": "Overall risk: LOW, MEDIUM, HIGH, or CRITICAL."},
                "critical_vulnerabilities": {"type": "INTEGER", "description": "Count of HIGH or CRITICAL severity vulnerabilities found. This number forces a re-build if > 0."},
                "vulnerability_summary": {"type": "STRING", "description": "A concise summary of the most important security findings."},
                "vulnerability_list": {
                    "type": "ARRAY",
                    "description": "List of all identified security issues.",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING", "description": "Vulnerability name (e.g., SQL Injection, XSS)."},
                            "severity": {"type": "STRING", "description": "Severity: INFO, LOW, MEDIUM, HIGH, CRITICAL."},
                            "file_path": {"type": "STRING", "description": "File where the vulnerability was found."},
                            "line_number": {"type": "INTEGER", "description": "Approximate line number."},
                            "remediation_suggestion": {"type": "STRING", "description": "Clear instruction for the BuilderAgent to fix this issue."}
                        },
                        "required": ["name", "severity", "file_path", "remediation_suggestion"]
                    }
                }
            },
            "required": ["overall_risk_level", "critical_vulnerabilities", "vulnerability_summary", "vulnerability_list"]
        }

    def run(self, project_id: uuid.UUID, current_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta la auditoría de seguridad sobre el código generado.
        """
        self.log_activity(f"SecurityAgent starting SAST for project {project_id}.")
        
        generated_code = current_requirements.get("generated_code")

        if not generated_code:
            self.log_activity("No code found for security analysis.")
            return self._create_failure_result("Missing generated code for security analysis.")

        # --- Creación del Prompt de Instrucción ---
        system_prompt = (
            "You are a leading expert in application security (AppSec) and a master of Static Analysis Security Testing (SAST). "
            "Your mission is to perform a thorough security audit of the provided code, focusing on common web vulnerabilities "
            "(e.g., XSS, SQLi, insecure deserialization, API endpoint flaws, weak authentication/authorization). "
            "Generate the security report in the required JSON schema. ONLY count 'HIGH' and 'CRITICAL' severity findings in the 'critical_vulnerabilities' field."
        )

        user_prompt = (
            "Perform a security audit (SAST) on the following code structure and content. "
            "The code uses Python/FastAPI/SQLAlchemy. Focus on input validation, ORM misuse, and API exposure issues."
            "\n\n--- GENERATED CODE ---\n\n"
            f"{generated_code}"
            "\n\n--- END OF CODE ---\n\n"
            "Generate the complete security report according to the JSON schema."
        )

        # --- Llamada a la API con esquema JSON y reintentos ---
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": self.security_schema
            }
        }

        max_retries = 5
        for attempt in range(max_retries):
            try:
                # El manejo de reintentos con backoff exponencial es crucial
                response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, json=payload, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                
                if result.get('candidates'):
                    raw_json_text = result['candidates'][0]['content']['parts'][0]['text']
                    security_report = json.loads(raw_json_text)
                    
                    # El Supervisor necesita este campo para saber si reconstruir
                    critical_vulnerabilities = security_report.get("critical_vulnerabilities", 0)
                    
                    self.log_activity(f"Security report generated. Critical findings: {critical_vulnerabilities}")
                    
                    return {
                        "status": "completed" if critical_vulnerabilities == 0 else "rebuild_required",
                        "security_report": security_report,
                        "token_count_in": 0, 
                        "token_count_out": 0,
                    }

            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                self.log_activity(f"Error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    return self._create_failure_result(f"API request failed after {max_retries} attempts.")

        return self._create_failure_result("Security Agent failed to generate a valid report.")

    def _create_failure_result(self, error_message: str) -> Dict[str, Any]:
        """Crea un resultado de fallo estandarizado en caso de error del agente."""
        return {
            "status": "failed",
            "error": error_message,
            "security_report": {
                "overall_risk_level": "CRITICAL",
                "critical_vulnerabilities": 99, # Alto para forzar revisión/paro si el agente falla
                "vulnerability_summary": "Agent failure, manual review required.",
                "vulnerability_list": []
            },
            "token_count_in": 0,
            "token_count_out": 0,
        }

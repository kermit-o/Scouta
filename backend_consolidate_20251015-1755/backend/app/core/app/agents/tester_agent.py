import logging
import json
from typing import Dict, Any, Optional
import time
import requests
from datetime import datetime
import uuid  # CORREGIDO: import faltante

# Asumiendo que esta es la clase base
from backend.app.core.app.agents.agent_base import AgentBase 

logger = logging.getLogger(__name__)

# --- Configuración de la API y el modelo ---
API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
MODEL_NAME = "gemini-2.5-flash-preview-05-20"
API_URL = f"{API_BASE_URL}/{MODEL_NAME}:generateContent"
# La clave API se asume que se proporciona en el entorno de ejecución o es inyectada.
API_KEY = "" 
# --------------------------------------------

class TesterAgent(AgentBase):
    """
    Agente encargado de realizar un análisis de pruebas funcionales (QA) sobre el 
    código generado, verificando que cumpla con las especificaciones.
    """

    def __init__(self):
        super().__init__("TesterAgent")
        # Definición del esquema JSON estricto para el reporte de validación
        self.validation_schema = {
            "type": "OBJECT",
            "properties": {
                "test_status": {"type": "STRING", "description": "Overall status: PASSED or FAILED."},
                "critical_failures": {"type": "INTEGER", "description": "Count of critical failures found. This number forces a re-build if > 0."},
                "test_summary": {"type": "STRING", "description": "A concise summary of the testing process and main findings."},
                "test_cases": {
                    "type": "ARRAY",
                    "description": "List of functional test cases executed.",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "case_name": {"type": "STRING"},
                            "description": {"type": "STRING"},
                            "status": {"type": "STRING", "description": "PASS or FAIL."},
                            "reason": {"type": "STRING", "description": "Detailed reason for failure or confirmation of pass."}
                        },
                        "required": ["case_name", "description", "status"]
                    }
                }
            },
            "required": ["test_status", "critical_failures", "test_summary", "test_cases"]
        }

    def run(self, project_id: uuid.UUID, current_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ejecuta el análisis de pruebas funcionales sobre el código.
        """
        logger.info(f"TesterAgent starting for project {project_id}.")
        
        generated_code = current_requirements.get("generated_code")
        specification = current_requirements.get("specification")

        if not generated_code:
            logger.error("No code found to test.")
            return self._create_failure_result("Missing generated code.")

        # --- Creación del Prompt de Instrucción ---
        system_prompt = (
            "You are a world-class Quality Assurance (QA) Engineer specialized in code validation. "
            "Your task is to analyze the provided code against the project specifications and "
            "generate a detailed functional validation report in the required JSON schema."
            "Focus on business logic, edge cases, and functionality defined in the specification."
            "The 'critical_failures' count must reflect all issues that prevent the core functionality from working."
        )

        user_prompt = (
            "Analyze the following project specification and the corresponding generated code. "
            f"Specification: {json.dumps(specification, indent=2)}\n\n"
            "--- GENERATED CODE ---\n\n"
            f"{generated_code}"
            "\n\n--- END OF CODE ---\n\n"
            "Generate the functional validation report according to the JSON schema."
        )

        # --- Llamada a la API con esquema JSON ---
        payload = {
            "contents": [{"parts": [{"text": user_prompt}]}],
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "generationConfig": {
                "responseMimeType": "application/json",
                "responseSchema": self.validation_schema
            }
        }

        max_retries = 5
        for attempt in range(max_retries):
            try:
                response = requests.post(API_URL, headers={'Content-Type': 'application/json'}, json=payload)
                response.raise_for_status()
                
                result = response.json()
                
                # Procesa la respuesta para extraer el JSON
                if result.get('candidates'):
                    raw_json_text = result['candidates'][0]['content']['parts'][0]['text']
                    validation_report = json.loads(raw_json_text)
                    
                    # El Supervisor necesita este campo para saber si reconstruir
                    critical_failures = validation_report.get("critical_failures", 0)
                    
                    return {
                        "status": "completed" if critical_failures == 0 else "rebuild_required",
                        "validation_report": validation_report,
                        # Token counts should be extracted from 'usageMetadata' if available
                        "token_count_in": 0, 
                        "token_count_out": 0,
                    }

            except requests.exceptions.RequestException as e:
                logger.error(f"API Request failed on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt) # Exponential backoff
                else:
                    return self._create_failure_result(f"API request failed after {max_retries} attempts.")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON response from LLM: {e}")
                # Si falla el JSON, se considera un fallo del LLM, pero se reintenta
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    return self._create_failure_result(f"LLM returned invalid JSON after {max_retries} attempts.")

        return self._create_failure_result("Tester Agent failed to generate a valid report.")

    def _create_failure_result(self, error_message: str) -> Dict[str, Any]:
        """Crea un resultado de fallo estandarizado."""
        return {
            "status": "failed",
            "error": error_message,
            "validation_report": {
                "test_status": "FAILED",
                "critical_failures": 99, # Alto para forzar revisión si el agente falla
                "test_summary": error_message,
                "test_cases": []
            },
            "token_count_in": 0,
            "token_count_out": 0,
        }

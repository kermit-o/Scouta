import json
from typing import Dict, Any, List
from .agent_base import AgentBase
from pydantic import BaseModel, Field

# --- Pydantic Schema para el Informe de Pruebas ---
class TestResult(BaseModel):
    """Representa el resultado de una prueba unitaria o de integración."""
    test_name: str = Field(..., description="Nombre de la función de prueba (ej: test_create_user_success)")
    status: str = Field(..., description="Estado de la prueba: 'passed', 'failed', 'skipped'")
    error_message: str = Field(None, description="Mensaje de error si la prueba falló.")

class ValidationReport(BaseModel):
    """Informe completo de la ejecución de las pruebas."""
    total_tests: int
    tests_passed: int
    tests_failed: int
    test_results: List[TestResult]

# --- CLASE PRINCIPAL DEL AGENTE ---

class ValidationAgent(AgentBase):
    """
    Agente especializado en generar pruebas unitarias y de integración (pytest) 
    para el código recién creado y simular su ejecución para validar la funcionalidad.
    """
    
    def __init__(self):
        super().__init__("Validation Agent")

    def _generate_test_suite_code(self, specifications: str, db_schema: Dict[str, Any]) -> str:
        """
        Genera el código de la suite de pruebas (test_main.py) usando el LLM.
        """
        db_schema_str = json.dumps(db_schema, indent=2)
        
        prompt = f"""
        TAREA: Eres un ingeniero de QA que debe escribir una suite de pruebas completa y de alta calidad 
        utilizando la librería pytest para validar un proyecto FastAPI.

        --- ESPECIFICACIÓN TÉCNICA (API Endpoints y Funcionalidad) ---
        {specifications}

        --- ESQUEMA DE BASE DE DATOS FINAL (Para Mocking de Modelos) ---
        {db_schema_str}

        INSTRUCCIONES:
        1. Escribe la suite de pruebas completa que cubra los endpoints CRUD principales y la lógica de negocio 
           clave especificada.
        2. Incluye pruebas unitarias para las funciones del 'services' y pruebas de integración para los 'routers' (FastAPI).
        3. Simula la conexión a la base de datos (Database) utilizando fixtures de pytest o mocking (ej. 'mock_db_session').
        4. Genera el código completo para un único archivo llamado 'test_suite.py'. 
        5. No incluyas comentarios externos, solo código Python y sus docstrings.
        """
        
        # El LLM genera el código de prueba como una cadena (string)
        test_code = self.generate_ai_response(
            prompt, 
            "You are a test automation engineer specializing in robust Python/FastAPI/Pytest testing."
        )
        return test_code

    def _simulate_test_execution(self, test_code: str) -> ValidationReport:
        """
        Simula la ejecución del código de prueba y produce un informe estructurado.
        
        NOTA: En un entorno de ejecución real, este método ejecutaría el código 
        de prueba real en un sandbox. Aquí lo simulamos con un LLM.
        """
        self.log_activity("Simulando ejecución de la suite de pruebas...")

        # Un prompt de ejecución y reporte más corto
        execution_prompt = f"""
        ANALIZA el siguiente código de prueba Python (pytest) y SIMULA su ejecución 
        contra la especificación técnica. Genera un informe JSON de las pruebas.

        CÓDIGO DE PRUEBA:
        ---
        {test_code}
        ---

        INFORME: Evalúa si el código de prueba cubre los casos de éxito y de borde, 
        y determina el resultado (passed/failed) para cada prueba simulada.
        """

        # Usamos Pydantic para asegurar que la salida de la simulación es estructurada
        report_json = self.generate_structured_ai_response(
            execution_prompt, 
            "You are a QA environment simulator. Your output must strictly follow the ValidationReport Pydantic schema.",
            ValidationReport
        )
        
        return report_json


    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera, ejecuta y reporta los resultados de las pruebas.
        """
        self.log_activity(f"Generando y ejecutando pruebas de validación para {project_id}")

        # Entradas necesarias del pipeline
        specifications_str = requirements.get('specifications', 'No specifications')
        db_schema = requirements.get('database_schema', {'database_schema': []})
        
        # Opcional: El código generado por el BuilderAgent podría ser útil para que el LLM
        # se refiera a las funciones reales.
        generated_code_reference = requirements.get('generated_code', 'No code reference provided.')
        
        # 1. Generar la suite de pruebas
        test_suite_code = self._generate_test_suite_code(specifications_str, db_schema)
        
        # 2. Simular la ejecución de las pruebas
        try:
            validation_report = self._simulate_test_execution(test_suite_code)
            
            # 3. Determinar el estado general
            status = "failed" if validation_report.tests_failed > 0 else "completed"

            # 4. Devolver el resultado completo
            return {
                "project_id": project_id,
                "status": status,
                "validation_report": validation_report.model_dump(), # Pydantic a dict
                "test_suite_code": test_suite_code,
                "summary": f"Validation complete. Passed: {validation_report.tests_passed}, Failed: {validation_report.tests_failed}."
            }
        
        except Exception as e:
            self.log_activity(f"Fallo en la validación: {e}")
            return {
                "project_id": project_id,
                "status": "validation_failed",
                "error": str(e)
            }

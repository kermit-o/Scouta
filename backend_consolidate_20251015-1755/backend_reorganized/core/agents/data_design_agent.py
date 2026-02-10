import json
import time
from typing import Dict, Any

class DataDesignAgent:
    """
    Agente especializado en diseñar el esquema de base de datos (DB Schema)
    basado en la especificación técnica del proyecto.

    Su salida es un objeto JSON detallado con tablas, campos, tipos y relaciones.
    """
    
    def __init__(self, llm_client: Any = None):
        """
        Inicializa el agente. En un entorno real, 'llm_client' sería una instancia
        de la API de Gemini para la generación de contenido estructurado (JSON).
        """
        self.llm_client = llm_client

    def generate_schema(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera el esquema de la base de datos a partir de la especificación técnica.

        Args:
            specification (Dict[str, Any]): La especificación técnica completa 
                                            generada por el SpecAgent (SpecificationAgent).

        Returns:
            Dict[str, Any]: El esquema de la base de datos en formato JSON estructurado.
        """
        
        # ---------------------------------------------------------------
        # 1. Preparación del Prompt (usando la especificación COMPLETA como contexto)
        # ---------------------------------------------------------------
        
        # La especificación del SpecAgent está en specification["specifications"]
        # que asumimos es una gran cadena o JSON. Lo convertimos a una cadena legible:
        try:
            # Si el SpecAgent devuelve un JSON, lo cargamos para una mejor inyección
            spec_content = json.dumps(specification.get("specifications", {}), indent=2)
        except TypeError:
            # Si es una cadena (string) simple, la usamos tal cual
            spec_content = str(specification.get("specifications", "No specification provided."))

        # El prompt ahora le pide a la IA que trabaje sobre la especificación DETALLADA
        prompt = f"""
        TAREA: Valida, optimiza y finaliza el diseño de la base de datos (SQL) basándote 
        en la especificación técnica proporcionada a continuación. Tu objetivo es producir 
        un DDL (Data Definition Language) de alto nivel optimizado para PostgreSQL.

        ESPECIFICACIÓN TÉCNICA PROPORCIONADA:
        ---
        {spec_content}
        ---
        
        El esquema debe estar en formato JSON. Incluye las siguientes propiedades
        para CADA TABLA: 'name', 'columns', y 'relationships'. Asegúrate de:
        1. Utilizar tipos de datos estándar SQL (TEXT, INTEGER, BOOLEAN, TIMESTAMP, etc.).
        2. Aplicar la normalización adecuada (3NF o superior).
        3. Definir claves primarias (id), claves foráneas (FK) y restricciones (NOT NULL, UNIQUE).

        Estructura JSON de Salida REQUERIDA:
        {{
          "database_schema": [
            {{
              "table_name": "Nombre de la Tabla (Plural)",
              "columns": [
                {{"name": "id", "type": "UUID/INTEGER", "is_primary_key": true}},
                {{"name": "nombre_campo", "type": "STRING/INTEGER/BOOLEAN/TIMESTAMP", "constraints": ["NOT NULL", "UNIQUE", "DEFAULT ..."]}},
                // ... otros campos
              ],
              "relationships": [
                {{"type": "FOREIGN_KEY", "column": "fk_id", "references_table": "otra_tabla", "on_delete": "CASCADE"}}
              ]
            }},
            // ... otras tablas
          ]
        }}
        """
        
        # ---------------------------------------------------------------
        # 2. Simulación de la Llamada al LLM
        # ---------------------------------------------------------------
        
        # En un entorno real, aquí harías la llamada a la API de generación (e.g., Gemini)
        # para obtener una respuesta JSON estructurada, utilizando 'self.llm_client'.
        print(f"--- DataDesignAgent: Solicitando esquema final a LLM (prompt de {len(prompt)} caracteres) ---")
        time.sleep(1.5) # Simular latencia de la API del LLM
        
        # Simulación de la respuesta del LLM
        # Esta simulación debe reflejar el formato JSON estricto solicitado en el prompt.
        mock_schema = {
            "database_schema": [
                {
                    "table_name": "users",
                    "columns": [
                        {"name": "id", "type": "UUID", "is_primary_key": True},
                        {"name": "email", "type": "TEXT", "constraints": ["NOT NULL", "UNIQUE"]},
                        {"name": "hashed_password", "type": "TEXT", "constraints": ["NOT NULL"]},
                        {"name": "created_at", "type": "TIMESTAMP", "constraints": ["NOT NULL", "DEFAULT NOW()"]},
                    ],
                    "relationships": []
                },
                {
                    "table_name": "products",
                    "columns": [
                        {"name": "id", "type": "UUID", "is_primary_key": True},
                        {"name": "owner_id", "type": "UUID", "constraints": ["NOT NULL"]},
                        {"name": "name", "type": "TEXT", "constraints": ["NOT NULL"]},
                        {"name": "price", "type": "NUMERIC(10, 2)", "constraints": ["NOT NULL"]},
                        {"name": "description", "type": "TEXT", "constraints": []},
                    ],
                    "relationships": [
                        {"type": "FOREIGN_KEY", "column": "owner_id", "references_table": "users", "on_delete": "CASCADE"}
                    ]
                }
            ]
        }
        
        return mock_schema

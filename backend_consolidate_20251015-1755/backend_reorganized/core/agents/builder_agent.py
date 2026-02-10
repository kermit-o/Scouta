# backend/app/agents/builder.py

import os
import json # Necesario para manejar el JSON del esquema de DB
from typing import Dict, Any, List
from pathlib import Path
from .agent_base import AgentBase

# --- SIMULACIÓN DE UTILS ---

def _read_file_content(file_path: Path) -> str:
    """Lee el contenido de un archivo generado previamente."""
    if not file_path.exists():
        return "" # Retorna vacío si no existe, para simplificar
    return file_path.read_text()

def _write_file_content(file_path: Path, content: str):
    """Escribe el contenido de vuelta al archivo."""
    file_path.write_text(content.strip() + "\n")
    print(f"  ✅ Contenido actualizado en: {file_path.name}")
    
# --- FUNCIÓN CLAVE DEL LLM (SIMULACIÓN) ---

def _llm_generate_product_service(project_id: str) -> str:
    """Simula la generación por LLM del código del servicio Product CRUD."""
    return f"""
# backend/generated/{project_id}/app/services/product_service.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional
import uuid

# Importamos los modelos ORM generados dinámicamente
from core.generated.{project_id}.app.models.product import Product, Location

# Esquema Pydantic simulado para la creación
class ProductCreate(object): # Usaríamos pydantic.BaseModel
    name: str
    sku: str
    description: Optional[str] = None
    quantity: int
    location_id: str # str porque viene como UUID

def create_product(db: Session, product_data: ProductCreate) -> Product:
    # 1. Verificar si la ubicación existe
    location_id_uuid = uuid.UUID(product_data.location_id)
    location = db.query(Location).filter(Location.id == location_id_uuid).first()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
        
    # 2. Crear el producto
    db_product = Product(
        name=product_data.name,
        sku=product_data.sku,
        description=product_data.description,
        quantity=product_data.quantity,
        location_id=location_id_uuid
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: str) -> Optional[Product]:
    return db.query(Product).filter(Product.id == product_id).first()

def move_product_inventory(db: Session, product_id: str, new_location_id: str, quantity_to_move: int) -> Product:
    # Lógica de Negocio: Mover inventario
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    new_location_uuid = uuid.UUID(new_location_id)
    new_location = db.query(Location).filter(Location.id == new_location_uuid).first()
    if not new_location:
        raise HTTPException(status_code=404, detail="New Location not found")

    if quantity_to_move <= 0:
        raise HTTPException(status_code=400, detail="Quantity to move must be positive")
    
    # 1. Asignar nueva ubicación
    product.location_id = new_location_uuid
    
    # 2. Asumimos que esta función solo re-asigna la ubicación, no ajusta el stock
    # Si fuera complejo, aquí se harían transacciones de stock.
    
    db.commit()
    db.refresh(product)
    return product
"""

def _llm_generate_router_injection(project_id: str) -> str:
    """Simula la generación por LLM de la función del router para el movimiento de inventario."""
    return f"""
# Esto reemplaza la función vacía en el router product.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database.session import get_db
# El LLM determina que necesita el servicio y el esquema Pydantic
from core.generated.{project_id}.app.services.product_service import move_product_inventory
import json # Necesario para el retorno de la representación

# Esquema Pydantic simulado para el movimiento
class MoveInventoryRequest(object):
    new_location_id: str
    quantity: int

@router.post("/products/{{product_id}}/move")
def post__products_param_product_id_move(
    product_id: str,
    request_data: MoveInventoryRequest, # Reemplazar por Pydantic
    db: Session = Depends(get_db)
):
    # Llama al servicio de negocio para mover el inventario
    try:
        updated_product = move_product_inventory(
            db=db,
            product_id=product_id,
            new_location_id=request_data.new_location_id,
            quantity_to_move=request_data.quantity
        )
        return {{"message": "Inventory successfully moved", "product": updated_product.name, "new_location_id": str(updated_product.location_id)}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""


# --- AGENTE PRINCIPAL (Función de Ejecución del Pipeline) ---

# Nota: La función 'run' fuera de la clase ha sido mantenida del código original.
# En un sistema real, esta lógica debería estar encapsulada o removida.
def run(project_id: str, specification: Dict[str, Any], generated_path: str) -> dict:
    """
    Agente Builder: Genera el código de servicios y lo inyecta en los routers.
    """
    GENERATED_PATH = Path(generated_path)
    
    # 1. Generar el Servicio de Negocio (Product)
    SERVICE_PATH = GENERATED_PATH / "app" / "services"
    SERVICE_PATH.mkdir(parents=True, exist_ok=True)
    
    product_service_content = _llm_generate_product_service(project_id)
    _write_file_content(SERVICE_PATH / "product_service.py", product_service_content)
    
    # 2. Generar el Router de Productos con la Lógica Inyectada
    router_filename = "product.py" # Usamos el primer modelo como router principal
    router_path = GENERATED_PATH / "app" / "routers" / router_filename
    
    if not router_path.exists():
        return {"status": "error", "message": f"Router file no encontrado: {router_path}"}
        
    # Leemos el router scaffolded
    router_content = _read_file_content(router_path)
    
    # Inyección simulada de la función clave (Mover Inventario)
    injection_code = _llm_generate_router_injection(project_id)
    
    # Estrategia: Reemplazar el bloque vacío para el endpoint /products/{product_id}/move
    search_block = '@router.post("/products/{product_id}/move")\ndef post__products_param_product_id_move(product_id: str):'
    
    # El LLM genera el bloque completo y lo inyectamos (simulando un cambio en el archivo completo)
    final_router_content = f"""
# FastAPI Router CONSTRUIDO para Product

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.database.session import get_db
from core.generated.{project_id}.app.services.product_service import move_product_inventory

# El LLM debería generar estos esquemas Pydantic
class MoveInventoryRequest:
    def __init__(self, new_location_id: str, quantity: int):
        self.new_location_id = new_location_id
        self.quantity = quantity
        
router = APIRouter(
    prefix="/v1",
    tags=["product"]
)

# Endpoint: Mover Inventario
@router.post("/products/{{product_id}}/move")
def post__products_param_product_id_move(
    product_id: str,
    # Simulamos que FastAPI inyecta el cuerpo de la petición
    # En un sistema real se usaría: request_data: MoveInventoryRequest
    new_location_id: str, # Asumimos parámetros simples para la inyección
    quantity: int,        # Asumimos parámetros simples para la inyección
    db: Session = Depends(get_db)
):
    # Llama al servicio de negocio para mover el inventario
    # Nota: Este cuerpo es generado por el LLM
    try:
        updated_product = move_product_inventory(
            db=db,
            product_id=product_id,
            new_location_id=new_location_id,
            quantity_to_move=quantity
        )
        return {{"message": "Inventory successfully moved", "product": updated_product.name, "new_location_id": str(updated_product.location_id)}}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {{str(e)}}")


# [OTRAS FUNCIONES CRUD VACÍAS...]
@router.get("/products")
def get__products():
    # TODO: Implementar lógica (LISTAR)
    return {{"message": "List products (TODO)"}}

@router.get("/locations")
def get__locations():
    # TODO: Implementar lógica (LISTAR)
    return {{"message": "List locations (TODO)"}}
"""
    _write_file_content(router_path, final_router_content)

    return {
        "status": "completed",
        "message": f"Agente Builder completado. Servicio de Product y lógica de movimiento inyectados en {router_path.name}.",
        "file_updated": str(router_path)
    }


# --- AGENTE PRINCIPAL (Clase actualizada para la lógica de corrección) ---

class BuilderAgent(AgentBase):
    """Agent for generating actual code based on specifications, incorporating validation and security feedback."""
    
    def __init__(self):
        super().__init__("Builder Agent")
    
    def run(self, project_id: str, requirements: dict) -> dict:
        """Generate code based on technical specifications, with automatic correction loop."""
        self.log_activity(f"Building project {project_id}")
        
        # 1. Obtener entradas
        specifications = requirements.get('specifications', 'No specifications provided')
        db_schema = requirements.get('database_schema', {'database_schema': []})
        db_schema_str = json.dumps(db_schema, indent=2)
        
        # 2. ** LÓGICA CLAVE DE RETROALIMENTACIÓN (Doble Corrección) **
        validation_report = requirements.get('validation_report')
        security_report_data = requirements.get('security_report')
        previous_generated_code = requirements.get('generated_code', 'No previous code available.')
        
        correction_prompt_modifier = ""
        errors_found = False
        error_details = []

        # A. Revisar Fallos Funcionales
        if validation_report and validation_report.get('tests_failed', 0) > 0:
            errors_found = True
            failing_tests_details = [
                f"Test: {res.get('test_name', 'Unknown')}, Status: {res.get('status', 'N/A')}, Error: {res.get('error_message', 'No message')}"
                for res in validation_report.get('test_results', []) if res.get('status') == 'failed'
            ]
            error_details.append("--- FALLO DE VALIDACIÓN FUNCIONAL ---")
            error_details.extend(failing_tests_details)

        # B. Revisar Fallos de Seguridad (Critical/High)
        # Asumimos que 'security_report' es el diccionario de retorno, y la clave 'status' indica el fallo crítico.
        if security_report_data and security_report_data.get('status') == 'security_critical_failure':
            errors_found = True
            security_findings = security_report_data.get('security_report', {}).get('findings_list', [])
            
            security_findings_details = []
            for finding in security_findings:
                if finding['severity'] in ['Critical', 'High']:
                    detail = (
                        f"SEVERIDAD: {finding['severity']} - TIPO: {finding['vulnerability_type']}\n"
                        f"  ARCHIVO/LÍNEA: {finding['file_path']} (Línea {finding['line_number']})\n"
                        f"  DESCRIPCIÓN: {finding['description']}\n"
                        f"  REMEDIACIÓN SUGERIDA: {finding['remediation_suggestion']}"
                    )
                    security_findings_details.append(detail)
            
            error_details.append("--- FALLO CRÍTICO DE SEGURIDAD (Critical/High) ---")
            error_details.extend(security_findings_details)


        if errors_found:
            self.log_activity("¡Fallaron las pruebas funcionales y/o de seguridad! Iniciando ciclo de corrección automática.")
            
            correction_prompt_modifier = f"""
            --- MODO CORRECCIÓN ACTIVO ---
            El intento de construcción anterior ha FALLADO la validación y/o seguridad.
            Tu tarea es CORREGIR el código anterior para que TODAS las pruebas pasen y se eliminen las vulnerabilidades.

            CÓDIGO GENERADO ANTERIORMENTE (Requiere Corrección):
            -----------------------------------------------------
            {previous_generated_code}
            -----------------------------------------------------

            INFORMES DE FALLO (COMBINADO):
            {chr(10).join(error_details)}

            INSTRUCCIONES DE CORRECCIÓN:
            1. Analiza cuidadosamente los errores funcionales y las vulnerabilidades de seguridad.
            2. Aplica los cambios mínimos necesarios al código existente para resolver AMBOS tipos de problemas.
            3. Vuelve a generar el código COMPLETO, ya corregido.
            4. Asegúrate de que tanto la lógica FUNCIONAL como la SEGURIDAD sean robustas.
            """

        # 3. Construir el prompt final
        prompt = f"""
        INSTRUCCIÓN CLAVE: Genera el código fuente completo del proyecto. Utiliza las fuentes de verdad a continuación.
        
        {correction_prompt_modifier}
        
        --- FUENTE DE VERDAD 1: ESPECIFICACIÓN TÉCNICA COMPLETA ---
        {specifications}

        --- FUENTE DE VERDAD 2: ESQUEMA DE BASE DE DATOS FINAL ---
        {db_schema_str}
        
        REQUISITOS DE GENERACIÓN:
        1. Los Modelos ORM (SQLAlchemy) deben mapearse estrictamente al Esquema de Base de Datos.
        2. Los Routers (FastAPI) y Servicios de Negocio deben implementar todos los Endpoints y la lógica detallada.
        3. Genera código para el Backend (FastAPI, SQLAlchemy), el Frontend y la configuración.

        Proporciona la estructura de archivos completa y el código.
        """
        
        try:
            generated_code = self.generate_ai_response(
                prompt, 
                "You are a senior full-stack developer who writes clean, working code, adheres strictly to the provided specifications and schema, and is skilled at debugging and correcting code based on test and security reports."
            )
            
            return {
                "project_id": project_id,
                "status": "completed", 
                "generated_code": generated_code,
                "files_generated": ["main.py", "models.py", "routers.py", "frontend/"],
                "build_status": "success"
            }
        except Exception as e:
            self.log_activity(f"Error en Builder Agent: {e}")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }

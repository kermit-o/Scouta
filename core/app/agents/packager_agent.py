﻿import logging
import os
import shutil
import uuid
from typing import Dict, Any

# Asumiendo que esta es la clase base
from .agent_base import AgentBase
from pathlib import Path

logger = logging.getLogger(__name__)

# --- Configuración de Paths de Simulación (Ajustar en el entorno real) ---
# Asumimos que los artefactos generados se guardan en un directorio con el ID del proyecto
GENERATED_ARTIFACTS_ROOT = Path("/tmp/generated_projects") 

class PackagerAgent(AgentBase):
    """
    Agente encargado de tomar todos los artefactos del proyecto (código, docs, reportes) 
    y empaquetarlos en un único archivo ZIP para la entrega final al cliente.
    """

    def __init__(self):
        super().__init__("Packager Agent")
        
    def run(self, project_id: uuid.UUID, current_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula el proceso de empaquetado de la construcción final.
        """
        project_id_str = str(project_id)
        self.log_activity(f"PackagerAgent starting final packaging for project {project_id_str}.")
        
        # 1. Definir rutas
        project_dir = GENERATED_ARTIFACTS_ROOT / project_id_str
        output_dir = GENERATED_ARTIFACTS_ROOT / "delivery"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # El nombre final del archivo ZIP (sin la extensión)
        zip_base_name = f"SAAS_Forge_Project_{project_id_str[:8]}"
        final_zip_path_str = str(output_dir / zip_base_name)
        
        if not project_dir.exists():
            self.log_activity(f"WARNING: Project directory {project_dir} does not exist. Creating mock files.")
            project_dir.mkdir(parents=True, exist_ok=True)
            # Crear un archivo de código simulado
            (project_dir / "README.md").write_text("# Proyecto Generado\nAquí va la documentación.")
            (project_dir / "backend" / "main.py").mkdir(parents=True, exist_ok=True)
            (project_dir / "backend" / "main.py").write_text("# Código generado (Simulación)")

        # 2. Guardar reportes finales como artefactos
        self._save_final_reports(project_dir, current_requirements)

        # 3. Empaquetar la carpeta del proyecto
        self.log_activity("Creating ZIP archive of project artifacts...")
        try:
            # shutil.make_archive(nombre_base_sin_ext, formato, directorio_fuente)
            final_zip_path = shutil.make_archive(
                base_name=final_zip_path_str,
                format='zip',
                root_dir=project_dir.parent, # Directorio padre (/tmp/generated_projects)
                base_dir=project_dir.name    # Solo la carpeta del proyecto (UUID)
            )
            
            final_zip_path = Path(final_zip_path)

            self.log_activity(f"✅ Packaging completed. File located at: {final_zip_path.resolve()}")
            
            return {
                "status": "completed",
                "zip_path": str(final_zip_path.resolve()),
                "message": "Project successfully packaged and ready for delivery."
            }
        except Exception as e:
            self.log_activity(f"FATAL Error during packaging: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "zip_path": None
            }
            
    def _save_final_reports(self, project_dir: Path, requirements: Dict[str, Any]):
        """Guarda los reportes finales (Testing, Security, Docs) en la carpeta del proyecto."""
        reports_dir = project_dir / "REPORTS"
        reports_dir.mkdir(exist_ok=True)

        # Reporte de Testing
        validation_report = requirements.get("validation_report")
        if validation_report:
            report_content = json.dumps(validation_report, indent=2)
            (reports_dir / "functional_test_report.json").write_text(report_content)
            self.log_activity("Functional test report saved.")

        # Reporte de Seguridad
        security_report = requirements.get("security_report")
        if security_report:
            report_content = json.dumps(security_report, indent=2)
            (reports_dir / "security_audit_report.json").write_text(report_content)
            self.log_activity("Security audit report saved.")
            
        # Documentación (asumiendo que viene como un string)
        final_documentation = requirements.get("final_documentation")
        if final_documentation:
            (project_dir / "DOCUMENTATION.md").write_text(final_documentation)
            self.log_activity("Final documentation saved.")

# Es necesario importar json para la función _save_final_reports
import json

import logging
from typing import Dict, Any, List, Tuple
import re

logger = logging.getLogger(__name__)

class RequirementsValidator:
    """Validates and analyzes user requirements to ensure project feasibility"""
    
    def __init__(self):
        self.min_description_length = 50
        self.supported_technologies = {
            "backend": ["fastapi", "django", "node.js", "flask"],
            "frontend": ["react", "vue.js", "angular", "streamlit"],
            "database": ["postgresql", "mysql", "sqlite", "mongodb"]
        }
    
    def validate_requirements(self, user_input: Dict[str, Any]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """Validate user requirements and extract specifications"""
        
        description = user_input.get('description', '').strip()
        project_name = user_input.get('name', '').strip()
        
        errors = []
        specifications = {}
        
        # Basic validation
        if len(description) < self.min_description_length:
            errors.append(f"La descripción debe tener al menos {self.min_description_length} caracteres")
        
        if not project_name:
            errors.append("El nombre del proyecto es requerido")
        
        if errors:
            return False, errors, {}
        
        # Extract specifications from description
        try:
            specifications = self._analyze_description(description)
            specifications['project_name'] = project_name
            
            # Validate technical feasibility
            tech_errors = self._validate_technical_feasibility(specifications)
            errors.extend(tech_errors)
            
            return len(errors) == 0, errors, specifications
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {e}")
            errors.append("Error analizando los requisitos")
            return False, errors, {}
    
    def _analyze_description(self, description: str) -> Dict[str, Any]:
        """Analyze user description to extract technical specifications"""
        
        description_lower = description.lower()
        
        specs = {
            "entities": self._extract_entities(description_lower),
            "features": self._extract_features(description_lower),
            "technical_requirements": self._extract_technical_requirements(description_lower),
            "complexity": self._assess_complexity(description)
        }
        
        return specs
    
    def _extract_entities(self, description: str) -> List[Dict[str, Any]]:
        """Extract main entities from description"""
        
        entities = []
        
        # Common entity patterns
        entity_patterns = {
            "user": r"(usuario|user|cuenta|empleado|cliente|admin)",
            "product": r"(producto|product|item|artículo|mercancía)",
            "order": r"(orden|order|pedido|compra|venta)",
            "category": r"(categoría|category|tipo|clase)",
            "inventory": r"(inventario|stock|existencia)",
            "report": r"(reporte|report|informe|estadística)",
            "payment": r"(pago|payment|factura|invoice)"
        }
        
        for entity_type, pattern in entity_patterns.items():
            if re.search(pattern, description):
                entities.append({
                    "type": entity_type,
                    "name": entity_type.title(),
                    "fields": self._get_default_fields(entity_type)
                })
        
        return entities
    
    def _extract_features(self, description: str) -> List[str]:
        """Extract required features from description"""
        
        features = []
        description_lower = description.lower()
        
        feature_patterns = {
            "authentication": r"(auth|login|registro|sesión|contraseña)",
            "crud": r"(crear|leer|editar|eliminar|crud|mantenimiento)",
            "api": r"(api|rest|endpoint|servicio web)",
            "reports": r"(reporte|informe|estadística|gráfico|dashboard)",
            "notifications": r"(notificación|email|correo|alerta|mensaje)",
            "search": r"(buscar|búsqueda|filtrar|filter|search)",
            "export": r"(exportar|descargar|excel|pdf|csv)"
        }
        
        for feature, pattern in feature_patterns.items():
            if re.search(pattern, description_lower):
                features.append(feature)
        
        return features
    
    def _extract_technical_requirements(self, description: str) -> Dict[str, Any]:
        """Extract technical requirements from description"""
        
        tech_reqs = {
            "backend": "fastapi",  # Default
            "frontend": "react",   # Default
            "database": "sqlite",  # Default
            "authentication": False,
            "api": False,
            "deployment": "docker"
        }
        
        desc_lower = description.lower()
        
        # Detect backend preferences
        if any(word in desc_lower for word in ["fastapi", "python"]):
            tech_reqs["backend"] = "fastapi"
        elif any(word in desc_lower for word in ["django"]):
            tech_reqs["backend"] = "django"
        elif any(word in desc_lower for word in ["node", "javascript"]):
            tech_reqs["backend"] = "node.js"
        
        # Detect frontend preferences
        if any(word in desc_lower for word in ["react"]):
            tech_reqs["frontend"] = "react"
        elif any(word in desc_lower for word in ["vue"]):
            tech_reqs["frontend"] = "vue.js"
        elif any(word in desc_lower for word in ["angular"]):
            tech_reqs["frontend"] = "angular"
        
        # Detect database preferences
        if any(word in desc_lower for word in ["postgres", "postgresql"]):
            tech_reqs["database"] = "postgresql"
        elif any(word in desc_lower for word in ["mysql"]):
            tech_reqs["database"] = "mysql"
        elif any(word in desc_lower for word in ["mongodb", "mongo"]):
            tech_reqs["database"] = "mongodb"
        
        # Detect other requirements
        tech_reqs["authentication"] = any(word in desc_lower for word in ["auth", "login", "registro", "sesión"])
        tech_reqs["api"] = any(word in desc_lower for word in ["api", "rest", "endpoint"])
        
        return tech_reqs
    
    def _assess_complexity(self, description: str) -> str:
        """Assess project complexity based on description"""
        
        word_count = len(description.split())
        entity_count = len(self._extract_entities(description.lower()))
        feature_count = len(self._extract_features(description.lower()))
        
        complexity_score = (word_count / 100) + (entity_count * 2) + (feature_count * 1.5)
        
        if complexity_score < 3:
            return "low"
        elif complexity_score < 7:
            return "medium"
        else:
            return "high"
    
    def _get_default_fields(self, entity_type: str) -> List[Dict[str, Any]]:
        """Get default fields for common entity types"""
        
        field_templates = {
            "user": [
                {"name": "id", "type": "int", "primary_key": True},
                {"name": "username", "type": "str", "unique": True},
                {"name": "email", "type": "str", "unique": True},
                {"name": "password_hash", "type": "str"},
                {"name": "role", "type": "str", "default": "user"},
                {"name": "created_at", "type": "datetime"}
            ],
            "product": [
                {"name": "id", "type": "int", "primary_key": True},
                {"name": "name", "type": "str"},
                {"name": "description", "type": "str"},
                {"name": "price", "type": "float"},
                {"name": "stock", "type": "int", "default": 0},
                {"name": "category", "type": "str"},
                {"name": "created_at", "type": "datetime"}
            ],
            "order": [
                {"name": "id", "type": "int", "primary_key": True},
                {"name": "user_id", "type": "int", "foreign_key": "User.id"},
                {"name": "total_amount", "type": "float"},
                {"name": "status", "type": "str", "default": "pending"},
                {"name": "created_at", "type": "datetime"}
            ]
        }
        
        return field_templates.get(entity_type, [
            {"name": "id", "type": "int", "primary_key": True},
            {"name": "name", "type": "str"},
            {"name": "description", "type": "str"},
            {"name": "created_at", "type": "datetime"}
        ])
    
    def _validate_technical_feasibility(self, specs: Dict[str, Any]) -> List[str]:
        """Validate if the technical requirements are feasible"""
        
        errors = []
        tech_reqs = specs.get('technical_requirements', {})
        
        # Check backend
        backend = tech_reqs.get('backend')
        if backend and backend not in self.supported_technologies['backend']:
            errors.append(f"Backend '{backend}' no está completamente soportado")
        
        # Check frontend
        frontend = tech_reqs.get('frontend')
        if frontend and frontend not in self.supported_technologies['frontend']:
            errors.append(f"Frontend '{frontend}' no está completamente soportado")
        
        # Check database
        database = tech_reqs.get('database')
        if database and database not in self.supported_technologies['database']:
            errors.append(f"Base de datos '{database}' no está completamente soportada")
        
        # Check complexity
        complexity = specs.get('complexity')
        if complexity == "high":
            errors.append("Proyectos de alta complejidad requieren revisión manual")
        
        return errors

# Global instance
requirements_validator = RequirementsValidator()

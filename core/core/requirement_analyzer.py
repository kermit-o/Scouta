"""
ANALIZADOR de requerimientos - CEREBRO del sistema
Transforma lenguaje natural → especificación técnica estructurada
"""
from typing import Dict, Any, List
import json
import os


class RequirementAnalyzer:
    def __init__(self):
        # Por ahora usamos análisis basado en reglas
        # Luego integraremos con LLM real (OpenAI, etc.)
        self.domain_keywords = {
            "ecommerce": ["tienda", "productos", "carrito", "pagos", "ecommerce", "ventas"],
            "blog": ["blog", "artículos", "posts", "contenido", "publicar"],
            "crm": ["clientes", "contactos", "ventas", "seguimiento", "crm"],
            "restaurant": ["restaurante", "mesas", "menú", "pedidos", "reservas"],
            "inventory": ["inventario", "stock", "productos", "almacén"],
            "booking": ["reservas", "citas", "agenda", "calendario"]
        }
    
    async def analyze(self, user_input: str) -> Dict[str, Any]:
        """Analiza requerimientos del usuario y devuelve especificación técnica"""
        print(f"🔍 Analizando requerimientos: {user_input}")
        
        # Detectar dominio del proyecto
        domain = self._detect_domain(user_input)
        
        # Extraer entidades principales
        entities = self._extract_entities(user_input, domain)
        
        # Determinar stack técnico
        tech_stack = self._determine_tech_stack(domain)
        
        # Generar especificación completa
        specification = {
            "project_type": domain,
            "name": self._generate_project_name(user_input),
            "description": user_input,
            "main_entities": entities,
            "tech_stack": tech_stack,
            "required_features": self._determine_features(domain, entities),
            "business_rules": self._extract_business_rules(user_input),
            "user_stories": self._generate_user_stories(entities, domain)
        }
        
        print(f"✅ Especificación generada: {specification['project_type']} con {len(entities)} entidades")
        return specification
    
    def _detect_domain(self, user_input: str) -> str:
        """Detecta el dominio del proyecto basado en palabras clave"""
        user_input_lower = user_input.lower()
        
        for domain, keywords in self.domain_keywords.items():
            if any(keyword in user_input_lower for keyword in keywords):
                return domain
        
        return "crud_app"  # Dominio por defecto
    
    def _extract_entities(self, user_input: str, domain: str) -> List[Dict[str, Any]]:
        """Extrae entidades principales del requerimiento"""
        # Por ahora usamos entidades predefinidas por dominio
        # Luego con LLM extraeremos entidades personalizadas
        domain_entities = {
            "ecommerce": [
                {"name": "Product", "fields": ["id", "name", "description", "price", "category", "image_url"]},
                {"name": "Category", "fields": ["id", "name", "description"]},
                {"name": "Order", "fields": ["id", "user_id", "total_amount", "status", "created_at"]},
                {"name": "User", "fields": ["id", "email", "name", "created_at"]}
            ],
            "blog": [
                {"name": "Post", "fields": ["id", "title", "content", "author", "published_at", "tags"]},
                {"name": "Category", "fields": ["id", "name", "description"]},
                {"name": "User", "fields": ["id", "username", "email", "role"]}
            ],
            "restaurant": [
                {"name": "Table", "fields": ["id", "number", "capacity", "status"]},
                {"name": "Reservation", "fields": ["id", "table_id", "customer_name", "date", "time", "guests"]},
                {"name": "Menu", "fields": ["id", "name", "description", "price", "category"]}
            ],
            "inventory": [
                {"name": "Product", "fields": ["id", "name", "sku", "quantity", "price", "category"]},
                {"name": "Category", "fields": ["id", "name", "description"]},
                {"name": "Supplier", "fields": ["id", "name", "contact", "email"]}
            ]
        }
        
        return domain_entities.get(domain, [
            {"name": "Item", "fields": ["id", "name", "description", "created_at"]},
            {"name": "User", "fields": ["id", "email", "name"]}
        ])
    
    def _determine_tech_stack(self, domain: str) -> Dict[str, str]:
        """Determina el stack técnico basado en el dominio"""
        base_stack = {
            "frontend": "react",
            "backend": "fastapi", 
            "database": "postgresql",
            "deployment": "docker"
        }
        
        # Personalizar stack según dominio
        if domain == "mobile":
            base_stack["frontend"] = "react_native"
        
        return base_stack
    
    def _determine_features(self, domain: str, entities: List[Dict]) -> List[str]:
        """Determina características requeridas basado en dominio y entidades"""
        base_features = ["authentication", "crud_operations", "responsive_design"]
        
        domain_features = {
            "ecommerce": ["shopping_cart", "payment_processing", "product_search"],
            "blog": ["content_management", "comments", "tags"],
            "restaurant": ["reservation_system", "menu_management", "table_booking"],
            "crm": ["contact_management", "sales_pipeline", "reporting"]
        }
        
        features = base_features + domain_features.get(domain, [])
        
        # Agregar features basado en entidades
        entity_names = [entity["name"].lower() for entity in entities]
        if "user" in entity_names:
            features.append("user_management")
        if "order" in entity_names or "reservation" in entity_names:
            features.append("status_tracking")
        
        return features
    
    def _extract_business_rules(self, user_input: str) -> List[str]:
        """Extrae reglas de negocio del requerimiento (simplificado)"""
        # Por ahora reglas genéricas, luego con LLM extraeremos específicas
        return [
            "Users must authenticate to access protected resources",
            "Admins can manage all data",
            "Data validation is required for all inputs"
        ]
    
    def _generate_user_stories(self, entities: List[Dict], domain: str) -> List[str]:
        """Genera user stories basado en entidades y dominio"""
        stories = []
        
        for entity in entities:
            entity_name = entity["name"]
            stories.extend([
                f"As a user, I want to view all {entity_name.lower()}s",
                f"As a user, I want to create a new {entity_name.lower()}",
                f"As a user, I want to edit an existing {entity_name.lower()}",
                f"As a user, I want to delete a {entity_name.lower()}"
            ])
        
        return stories
    
    def _generate_project_name(self, user_input: str) -> str:
        """Genera un nombre para el proyecto basado en el requerimiento"""
        words = user_input.lower().split()[:3]
        name = "_".join(words)
        return f"{name}_app"
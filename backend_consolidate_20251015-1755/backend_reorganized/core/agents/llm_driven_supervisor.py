"""
LLM DRIVEN SUPERVISOR - El LLM analiza y decide el proyecto completo
Ciclo correcto: Usuario → LLM (Análisis) → Plan detallado → Ejecución
"""
import asyncio
import json
import uuid
from typing import Dict, Any, List
import os

class LLMDrivenSupervisor:
    """Supervisor que CONSULTA AL LLM para analizar y planificar proyectos"""
    
    def __init__(self):
        try:
            from services.fixed_deepseek_client import FixedDeepSeekClient
            self.llm_client = FixedDeepSeekClient()
            self.llm_available = True
            print("✅ LLM Client disponible para análisis")
        except ImportError:
            self.llm_available = False
            print("⚠️  LLM no disponible - usando análisis básico")
    
    async def analyze_and_plan_project(self, user_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """ANÁLISIS PRINCIPAL: El LLM analiza los requisitos y crea un plan detallado"""
        
        print("🧠 LLM SUPERVISOR - Analizando requisitos con IA...")
        
        if not self.llm_available:
            return await self._create_basic_plan(user_requirements)
        
        try:
            # FASE 1: ANÁLISIS DETALLADO CON LLM
            analysis_prompt = self._create_analysis_prompt(user_requirements)
            print("📋 Consultando al LLM para análisis del proyecto...")
            
            analysis_result = await self.llm_client.generate_response(analysis_prompt, max_tokens=3000)
            print(f"✅ Análisis LLM completado ({len(analysis_result)} caracteres)")
            
            # FASE 2: PLANIFICACIÓN DETALLADA CON LLM
            planning_prompt = self._create_planning_prompt(user_requirements, analysis_result)
            planning_result = await self.llm_client.generate_response(planning_prompt, max_tokens=4000)
            
            # FASE 3: ESTRUCTURA TÉCNICA CON LLM
            tech_prompt = self._create_tech_prompt(user_requirements, analysis_result, planning_result)
            tech_result = await self.llm_client.generate_response(tech_prompt, max_tokens=2000)
            
            # Procesar respuestas del LLM
            project_plan = self._process_llm_responses(
                user_requirements, 
                analysis_result, 
                planning_result, 
                tech_result
            )
            
            print("🎯 Plan de proyecto generado por LLM:")
            print(f"   - Arquitectura: {project_plan.get('architecture', {}).get('type', 'N/A')}")
            print(f"   - Módulos: {len(project_plan.get('modules', []))}")
            print(f"   - Endpoints: {len(project_plan.get('endpoints', []))}")
            print(f"   - Archivos: {len(project_plan.get('file_structure', []))}")
            
            return project_plan
            
        except Exception as e:
            print(f"❌ Error en análisis LLM: {e}")
            return await self._create_basic_plan(user_requirements)
    
    def _create_analysis_prompt(self, requirements: Dict[str, Any]) -> str:
        """Crea prompt para ANÁLISIS del proyecto"""
        project_name = requirements.get('name', 'Proyecto')
        description = requirements.get('description', 'Sin descripción')
        features = requirements.get('features', [])
        technologies = requirements.get('technologies', [])
        
        return f"""
        Eres un arquitecto de software senior. Analiza ESTE PROYECTO y proporciona un análisis detallado:

        PROYECTO: {project_name}
        DESCRIPCIÓN: {description}
        CARACTERÍSTICAS SOLICITADAS: {', '.join(features)}
        TECNOLOGÍAS SUGERIDAS: {', '.join(technologies)}

        Realiza un análisis que incluya:

        1. DOMINIO DEL PROBLEMA
        - ¿Qué problema resuelve este proyecto?
        - ¿Quiénes son los usuarios finales?
        - ¿Qué flujos de trabajo principales debe soportar?

        2. ALCANCE FUNCIONAL
        - ¿Qué funcionalidades CRÍTICAS son necesarias?
        - ¿Qué features son opcionales pero recomendables?
        - ¿Hay dependencias entre features?

        3. COMPLEJIDAD TÉCNICA
        - Nivel de complejidad (Bajo/Medio/Alto)
        - Retos técnicos principales
        - Consideraciones de escalabilidad

        4. CASOS DE USO PRINCIPALES
        - Describe 3-5 casos de uso clave
        - Flujos de usuario principales

        Responde en formato JSON con esta estructura:
        {{
            "domain_analysis": {{
                "problem_statement": "string",
                "target_users": ["string"],
                "core_workflows": ["string"]
            }},
            "functional_scope": {{
                "critical_features": ["string"],
                "recommended_features": ["string"],
                "feature_dependencies": ["string"]
            }},
            "technical_assessment": {{
                "complexity_level": "string",
                "technical_challenges": ["string"],
                "scalability_considerations": ["string"]
            }},
            "use_cases": [
                {{
                    "title": "string",
                    "description": "string",
                    "actors": ["string"],
                    "steps": ["string"]
                }}
            ]
        }}
        """
    
    def _create_planning_prompt(self, requirements: Dict[str, Any], analysis: str) -> str:
        """Crea prompt para PLANIFICACIÓN detallada"""
        project_name = requirements.get('name', 'Proyecto')
        
        return f"""
        Basado en este análisis del proyecto "{project_name}":

        {analysis}

        Ahora crea un PLAN DE DESARROLLO DETALLADO que incluya:

        1. ARQUITECTURA DEL SISTEMA
        - Patrón arquitectónico recomendado
        - Componentes principales del sistema
        - Comunicación entre componentes

        2. MÓDULOS Y COMPONENTES
        - Lista de módulos necesarios
        - Responsabilidades de cada módulo
        - Dependencias entre módulos

        3. ENDPOINTS DE LA API
        - Endpoints REST necesarios
        - Métodos HTTP, parámetros, respuestas
        - Autenticación y autorización requerida

        4. MODELOS DE DATOS
        - Entidades principales
        - Relaciones entre entidades
        - Campos clave para cada entidad

        Responde en formato JSON con esta estructura:
        {{
            "architecture": {{
                "pattern": "string",
                "components": [
                    {{
                        "name": "string",
                        "responsibility": "string",
                        "dependencies": ["string"]
                    }}
                ],
                "communication_flow": "string"
            }},
            "modules": [
                {{
                    "name": "string",
                    "purpose": "string",
                    "functions": ["string"],
                    "dependencies": ["string"]
                }}
            ],
            "endpoints": [
                {{
                    "path": "string",
                    "method": "string",
                    "description": "string",
                    "parameters": [
                        {{
                            "name": "string",
                            "type": "string",
                            "required": boolean,
                            "description": "string"
                        }}
                    ],
                    "responses": [
                        {{
                            "status_code": integer,
                            "description": "string"
                        }}
                    ],
                    "authentication_required": boolean
                }}
            ],
            "data_models": [
                {{
                    "name": "string",
                    "fields": [
                        {{
                            "name": "string",
                            "type": "string",
                            "required": boolean,
                            "description": "string"
                        }}
                    ],
                    "relationships": [
                        {{
                            "with_model": "string",
                            "type": "string",
                            "description": "string"
                        }}
                    ]
                }}
            ]
        }}
        """
    
    def _create_tech_prompt(self, requirements: Dict[str, Any], analysis: str, planning: str) -> str:
        """Crea prompt para ESTRUCTURA TÉCNICA"""
        project_name = requirements.get('name', 'Proyecto')
        
        return f"""
        Basado en el análisis y planificación del proyecto "{project_name}":

        ANÁLISIS:
        {analysis}

        PLANIFICACIÓN:
        {planning}

        Ahora define la ESTRUCTURA TÉCNICA DETALLADA:

        1. ESTRUCTURA DE ARCHIVOS
        - Layout completo del proyecto
        - Archivos y directorios necesarios
        - Organización del código

        2. DEPENDENCIAS Y CONFIGURACIÓN
        - Paquetes Python necesarios
        - Configuraciones del proyecto
        - Variables de entorno

        3. IMPLEMENTACIÓN INICIAL
        - Código boilerplate para empezar
        - Configuración base funcionando

        Responde en formato JSON con esta estructura:
        {{
            "file_structure": [
                {{
                    "path": "string",
                    "type": "file|directory",
                    "content": "string"  // Para archivos: contenido inicial o descripción
                }}
            ],
            "dependencies": {{
                "python_packages": [
                    {{
                        "name": "string",
                        "version": "string",
                        "purpose": "string"
                    }}
                ],
                "configurations": [
                    {{
                        "file": "string",
                        "settings": {{
                            "key": "value"
                        }}
                    }}
                ],
                "environment_variables": [
                    {{
                        "name": "string",
                        "description": "string",
                        "default_value": "string"
                    }}
                ]
            }},
            "implementation_guide": {{
                "setup_steps": ["string"],
                "boilerplate_code": {{
                    "file_path": "string",
                    "content": "string"
                }}
            }}
        }}
        """
    
    def _process_llm_responses(self, requirements: Dict[str, Any], analysis: str, planning: str, tech: str) -> Dict[str, Any]:
        """Procesa las respuestas del LLM y crea el plan final"""
        
        try:
            # Intentar parsear JSON de las respuestas
            analysis_data = self._extract_json_from_response(analysis)
            planning_data = self._extract_json_from_response(planning) 
            tech_data = self._extract_json_from_response(tech)
            
            project_id = str(uuid.uuid4())
            
            # Crear plan consolidado
            project_plan = {
                "project_id": project_id,
                "project_name": requirements.get('name', 'proyecto-llm'),
                "description": requirements.get('description', ''),
                "original_requirements": requirements,
                
                # Análisis del LLM
                "llm_analysis": analysis_data,
                "llm_planning": planning_data,
                "llm_technical": tech_data,
                
                # Plan de ejecución
                "execution_plan": {
                    "architecture": planning_data.get('architecture', {}),
                    "modules": planning_data.get('modules', []),
                    "endpoints": planning_data.get('endpoints', []),
                    "data_models": planning_data.get('data_models', [])
                },
                
                # Estructura técnica
                "technical_specs": {
                    "file_structure": tech_data.get('file_structure', []),
                    "dependencies": tech_data.get('dependencies', {}),
                    "implementation": tech_data.get('implementation_guide', {})
                },
                
                # Metadatos
                "generated_by": "llm_driven_supervisor",
                "llm_used": True,
                "timestamp": "2024-01-01T00:00:00Z"
            }
            
            return project_plan
            
        except Exception as e:
            print(f"❌ Error procesando respuestas LLM: {e}")
            return self._create_fallback_plan(requirements)
    
    def _extract_json_from_response(self, response: str) -> Dict[str, Any]:
        """Extrae JSON de la respuesta del LLM"""
        try:
            # Buscar contenido entre ```json ... ```
            import re
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                return json.loads(json_str)
            
            # Si no hay markdown, intentar parsear directamente
            return json.loads(response)
        except:
            # Si falla, devolver estructura básica
            return {"raw_response": response[:500] + "..." if len(response) > 500 else response}
    
    async def _create_basic_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan básico cuando el LLM no está disponible"""
        project_id = str(uuid.uuid4())
        
        return {
            "project_id": project_id,
            "project_name": requirements.get('name', 'proyecto-basico'),
            "description": requirements.get('description', ''),
            "llm_used": False,
            "execution_plan": {
                "architecture": {
                    "pattern": "MVC",
                    "components": [
                        {
                            "name": "API Layer",
                            "responsibility": "Manejar requests HTTP",
                            "dependencies": []
                        }
                    ]
                },
                "modules": [
                    {
                        "name": "main",
                        "purpose": "Punto de entrada de la aplicación",
                        "functions": ["start_server", "health_check"],
                        "dependencies": []
                    }
                ],
                "endpoints": [
                    {
                        "path": "/",
                        "method": "GET",
                        "description": "Endpoint raíz",
                        "authentication_required": False
                    }
                ]
            },
            "technical_specs": {
                "file_structure": [
                    {
                        "path": "main.py",
                        "type": "file",
                        "content": "FastAPI basic server"
                    }
                ]
            }
        }
    
    def _create_fallback_plan(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Plan de fallback cuando el procesamiento LLM falla"""
        project_id = str(uuid.uuid4())
        
        return {
            "project_id": project_id,
            "project_name": requirements.get('name', 'proyecto-fallback'),
            "description": requirements.get('description', ''),
            "llm_used": False,
            "error": "LLM processing failed",
            "execution_plan": {
                "architecture": {"pattern": "fallback", "components": []},
                "modules": [],
                "endpoints": []
            }
        }

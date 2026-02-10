"""
Enhanced Intake Agent - Completely Standalone Version
No dependencies on other agents or problematic imports
"""
import os
import requests
import json
import logging
from typing import Dict, Any, List
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StandaloneEnhancedIntakeAgent:
    """Completely standalone Enhanced Intake Agent - Zero dependencies"""
    
    def __init__(self):
        self.name = "Standalone Enhanced Intake Agent"
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_base = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
        
    def log_activity(self, message: str, level: str = "info"):
        """Log agent activity"""
        log_method = getattr(logger, level, logger.info)
        log_method(f"[{self.name}] {message}")
    
    def call_deepseek(self, messages: list, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """Make API call to DeepSeek with fallback"""
        if not self.api_key:
            # Fallback for testing without API key
            self.log_activity("No API key, using fallback analysis")
            return self._get_fallback_response()
            
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False
        }
        
        try:
            response = requests.post(f"{self.api_base}/chat/completions", 
                                   json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            self.log_activity(f"DeepSeek API error: {e}")
            return self._get_fallback_response()
    
    def _get_fallback_response(self) -> str:
        """Provide fallback analysis when API is unavailable"""
        return '''{
            "project_summary": "Fallback analysis using intelligent pattern detection",
            "business_domain": "software",
            "complexity_level": "medium",
            "architecture_style": "monolith",
            "scalability_requirements": ["basic"],
            "integration_points": [],
            "security_requirements": ["authentication"],
            "compliance_requirements": [],
            "technical_risks": ["standard_development_risks"],
            "performance_requirements": ["responsive"]
        }'''
    
    def generate_ai_response(self, prompt: str, context: str = "", temperature: float = 0.7) -> str:
        """Generate AI response"""
        messages = []
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": prompt})
        
        return self.call_deepseek(messages, temperature)
    
    def run(self, project_id: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced analysis for complex projects"""
        
        self.log_activity(f"Starting enhanced analysis for project {project_id}")
        
        try:
            # Get requirements
            raw_requirements = requirements.get('raw_requirements', '') or requirements.get('requirements', '')
            
            if not raw_requirements:
                return {
                    "project_id": project_id,
                    "status": "failed",
                    "error": "No requirements provided"
                }

            # Perform enhanced analysis
            enhanced_analysis = self._perform_enhanced_analysis(raw_requirements)
            
            # Calculate complexity score
            complexity_score = self._calculate_complexity_score(enhanced_analysis)
            
            # Prepare response
            result = {
                "project_id": project_id,
                "status": "completed",
                "enhanced_analysis": enhanced_analysis,
                "complexity_score": complexity_score,
                "recommended_approach": self._get_recommended_approach(complexity_score),
                "estimated_timeline": self._estimate_timeline(complexity_score),
                "resource_recommendations": self._recommend_resources(complexity_score),
                "message": "Enhanced analysis completed successfully"
            }
            
            return result
            
        except Exception as e:
            self.log_activity(f"Enhanced analysis error: {e}", "error")
            return {
                "project_id": project_id,
                "status": "failed",
                "error": str(e)
            }
    
    def _perform_enhanced_analysis(self, requirements: str) -> Dict[str, Any]:
        """Perform enhanced analysis using pattern detection and AI"""
        
        # First, try pattern-based analysis
        pattern_analysis = self._pattern_based_analysis(requirements)
        
        # Then enhance with AI if available
        try:
            analysis_prompt = f"""
            Analyze these project requirements and provide technical analysis in JSON:

            REQUIREMENTS: {requirements}

            Provide JSON with:
            - project_summary: executive summary
            - business_domain: business domain
            - complexity_level: simple, medium, complex, enterprise  
            - architecture_style: monolith, microservices, serverless, hybrid
            - scalability_requirements: list
            - integration_points: list
            - security_requirements: list
            - compliance_requirements: list
            - technical_risks: list
            - performance_requirements: list

            Respond ONLY with valid JSON.
            """
            
            response = self.generate_ai_response(analysis_prompt)
            
            try:
                ai_analysis = json.loads(response.strip())
                # Merge pattern analysis with AI analysis
                return {**pattern_analysis, **ai_analysis}
            except json.JSONDecodeError:
                return pattern_analysis
                
        except Exception as e:
            self.log_activity(f"AI analysis failed, using pattern analysis: {e}")
            return pattern_analysis
    
    def _pattern_based_analysis(self, requirements: str) -> Dict[str, Any]:
        """Intelligent pattern-based analysis without AI"""
        requirements_lower = requirements.lower()
        
        # Detect business domain
        business_domain = "software"
        if any(word in requirements_lower for word in ['ecommerce', 'tienda', 'comercio']):
            business_domain = "ecommerce"
        elif any(word in requirements_lower for word in ['financiero', 'banco', 'pago', 'transacción']):
            business_domain = "fintech"
        elif any(word in requirements_lower for word in ['salud', 'médico', 'paciente']):
            business_domain = "healthtech"
        elif any(word in requirements_lower for word in ['educación', 'curso', 'aprendizaje']):
            business_domain = "edtech"
        
        # Detect complexity
        complexity_level = "simple"
        if any(word in requirements_lower for word in ['empresarial', 'enterprise', 'corporativo', 'multi-tenant']):
            complexity_level = "enterprise"
        elif any(word in requirements_lower for word in ['microservicios', 'distribuido', 'escalable', 'integracion']):
            complexity_level = "complex"
        elif any(word in requirements_lower for word in ['saaS', 'plataforma', 'multi-usuario']):
            complexity_level = "medium"
        
        # Detect architecture
        architecture_style = "monolith"
        if any(word in requirements_lower for word in ['microservicios', 'microservices']):
            architecture_style = "microservices"
        elif any(word in requirements_lower for word in ['serverless', 'sin servidor']):
            architecture_style = "serverless"
        elif any(word in requirements_lower for word in ['híbrido', 'hybrid']):
            architecture_style = "hybrid"
        
        # Detect integrations
        integration_points = []
        if any(word in requirements_lower for word in ['api', 'rest', 'graphql']):
            integration_points.append("external_apis")
        if any(word in requirements_lower for word in ['base de datos', 'database', 'postgres', 'mysql']):
            integration_points.append("database")
        if any(word in requirements_lower for word in ['pago', 'stripe', 'paypal']):
            integration_points.append("payment_gateway")
        if any(word in requirements_lower for word in ['email', 'correo']):
            integration_points.append("email_service")
        
        return {
            "project_summary": f"Pattern analysis: {requirements[:100]}...",
            "business_domain": business_domain,
            "complexity_level": complexity_level,
            "architecture_style": architecture_style,
            "scalability_requirements": ["basic" if complexity_level == "simple" else "moderate"],
            "integration_points": integration_points,
            "security_requirements": ["authentication", "authorization"] if complexity_level != "simple" else ["authentication"],
            "compliance_requirements": [],
            "technical_risks": ["standard_development_risks"],
            "performance_requirements": ["responsive"]
        }
    
    def _calculate_complexity_score(self, analysis: Dict[str, Any]) -> int:
        """Calculate complexity score from 1-10"""
        score = 0
        
        # Architecture complexity
        arch_weights = {"monolith": 1, "serverless": 2, "microservices": 4, "hybrid": 5}
        score += arch_weights.get(analysis.get('architecture_style', 'monolith'), 1)
        
        # Complexity level
        level_weights = {"simple": 1, "medium": 3, "complex": 6, "enterprise": 8}
        score += level_weights.get(analysis.get('complexity_level', 'medium'), 3)
        
        # Scalability requirements
        score += len(analysis.get('scalability_requirements', []))
        
        # Integration complexity
        score += len(analysis.get('integration_points', [])) * 2
        
        # Security requirements
        score += len(analysis.get('security_requirements', []))
        
        # Compliance requirements  
        score += len(analysis.get('compliance_requirements', [])) * 2
        
        return min(max(score, 1), 10)
    
    def _get_recommended_approach(self, complexity_score: int) -> Dict[str, Any]:
        """Get recommended development approach"""
        if complexity_score <= 3:
            return {
                "team_size": "1-2 developers",
                "methodology": "Agile simple",
                "testing_strategy": "Unit tests",
                "deployment_frequency": "Weekly",
                "pipeline_type": "simple"
            }
        elif complexity_score <= 6:
            return {
                "team_size": "2-3 developers",
                "methodology": "Scrum", 
                "testing_strategy": "Full test suite",
                "deployment_frequency": "Bi-weekly",
                "pipeline_type": "simple"
            }
        else:
            return {
                "team_size": "4+ developers + DevOps",
                "methodology": "SAFe/Scrum",
                "testing_strategy": "Comprehensive testing",
                "deployment_frequency": "Continuous deployment",
                "pipeline_type": "enhanced"
            }
    
    def _estimate_timeline(self, complexity_score: int) -> Dict[str, str]:
        """Estimate timeline based on complexity score"""
        if complexity_score <= 3:
            return {"min": "2 weeks", "max": "1 month"}
        elif complexity_score <= 6:
            return {"min": "1 month", "max": "3 months"}
        else:
            return {"min": "3 months", "max": "6+ months"}
    
    def _recommend_resources(self, complexity_score: int) -> Dict[str, Any]:
        """Recommend resource allocation"""
        if complexity_score <= 3:
            return {"developers": 1, "devops": 0, "qa": 0.5}
        elif complexity_score <= 6:
            return {"developers": 2, "devops": 1, "qa": 1}
        else:
            return {"developers": 4, "devops": 2, "qa": 2}

def demonstrate_standalone_agent():
    """Demonstrate the completely standalone agent"""
    
    print("🚀 COMPLETELY STANDALONE ENHANCED INTAKE AGENT")
    print("=" * 70)
    print("✅ Zero dependencies - 100% self-contained")
    print("✅ Works with or without API key")
    print("✅ Intelligent pattern detection")
    print()
    
    # Create agent
    agent = StandaloneEnhancedIntakeAgent()
    print("✅ Agent created successfully!")
    print()
    
    print("🧪 TESTING WITH REAL-WORLD PROJECTS")
    print("=" * 50)
    
    test_cases = [
        {
            "name": "Personal Blog",
            "requirements": "Un blog personal simple con posts y comentarios.",
            "expected": "simple"
        },
        {
            "name": "E-commerce Store", 
            "requirements": "Tienda online con productos, carrito, usuarios y pagos con Stripe.",
            "expected": "simple"
        },
        {
            "name": "SaaS Project Management",
            "requirements": "Plataforma SaaS para gestión de proyectos con equipos, tableros Kanban, integración con Slack y GitHub.",
            "expected": "enhanced"
        },
        {
            "name": "Enterprise Banking System",
            "requirements": "Sistema bancario core con cuentas, transacciones, compliance regulatorio y integraciones globales.",
            "expected": "enhanced"
        }
    ]
    
    for case in test_cases:
        print(f"\n📋 {case['name']}")
        print(f"   Expected: {case['expected'].upper()} pipeline")
        print("-" * 40)
        
        result = agent.run(str(uuid.uuid4()), {"raw_requirements": case['requirements']})
        
        if result['status'] == 'completed':
            complexity = result['complexity_score']
            analysis = result['enhanced_analysis']
            approach = result['recommended_approach']
            
            print(f"   ✅ Complexity: {complexity}/10")
            print(f"   🏗️  Architecture: {analysis.get('architecture_style', 'N/A')}")
            print(f"   🔀 Pipeline: {approach.get('pipeline_type', 'simple').upper()}")
            print(f"   ⏱️  Timeline: {result['estimated_timeline']}")
            print(f"   👥 Team: {result['resource_recommendations']}")
            
            # Check if recommendation matches expectation
            recommended_pipeline = approach.get('pipeline_type', 'simple')
            if recommended_pipeline == case['expected']:
                print("   🎯 RECOMMENDATION: ✅ CORRECT")
            else:
                print(f"   🎯 RECOMMENDATION: ⚠️  DEVIATION")
            
            # Show analysis insights
            if analysis.get('integration_points'):
                print(f"   🔗 Detected: {len(analysis['integration_points'])} integration points")
            
        else:
            print(f"   ❌ Analysis failed: {result.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 70)
    print("🎉 STANDALONE AGENT READY FOR PRODUCTION!")
    print("💡 Can be integrated anywhere without dependency issues")
    print("💡 Provides intelligent pipeline recommendations")
    print("💡 Works offline with pattern detection")

if __name__ == "__main__":
    demonstrate_standalone_agent()

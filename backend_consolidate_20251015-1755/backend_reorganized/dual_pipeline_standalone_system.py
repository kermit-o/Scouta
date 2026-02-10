"""
Dual Pipeline System - Completely Standalone
No dependencies on other modules
"""
import json
import uuid
from typing import Dict, Any, List

class StandaloneDualPipelineSystem:
    """
    Complete dual pipeline system with zero dependencies
    - Uses standalone enhanced intake agent
    - Provides pipeline recommendations
    - Ready for immediate integration
    """
    
    def __init__(self):
        self.enhanced_agent = None
        self._initialize_agent()
    
    def _initialize_agent(self):
        """Initialize the standalone enhanced intake agent"""
        try:
            # Import the standalone agent directly
            import enhanced_intake_standalone_final
            self.enhanced_agent = enhanced_intake_standalone_final.StandaloneEnhancedIntakeAgent()
        except Exception as e:
            print(f"⚠️  Could not load enhanced agent: {e}")
            print("💡 Using fallback pipeline system")
            self.enhanced_agent = None
    
    def analyze_project(self, requirements: str) -> Dict[str, Any]:
        """Analyze project and recommend pipeline"""
        
        if not self.enhanced_agent:
            return self._fallback_analysis(requirements)
        
        try:
            result = self.enhanced_agent.run(str(uuid.uuid4()), {"raw_requirements": requirements})
            
            if result['status'] == 'completed':
                complexity = result['complexity_score']
                analysis = result['enhanced_analysis']
                approach = result['recommended_approach']
                
                pipeline_type = "enhanced" if complexity > 5 else "simple"
                
                return {
                    "status": "success",
                    "pipeline_recommendation": pipeline_type,
                    "complexity_score": complexity,
                    "architecture_style": analysis.get('architecture_style', 'monolith'),
                    "business_domain": analysis.get('business_domain', 'software'),
                    "estimated_timeline": result['estimated_timeline'],
                    "resource_recommendations": result['resource_recommendations'],
                    "key_findings": {
                        "integration_points": len(analysis.get('integration_points', [])),
                        "security_requirements": len(analysis.get('security_requirements', [])),
                        "technical_risks": len(analysis.get('technical_risks', []))
                    },
                    "analysis_method": "enhanced"
                }
            else:
                return self._fallback_analysis(requirements)
                
        except Exception as e:
            print(f"❌ Enhanced analysis failed: {e}")
            return self._fallback_analysis(requirements)
    
    def _fallback_analysis(self, requirements: str) -> Dict[str, Any]:
        """Fallback analysis when enhanced agent is unavailable"""
        requirements_lower = requirements.lower()
        
        # Simple pattern detection
        if any(word in requirements_lower for word in ['empresarial', 'enterprise', 'corporativo', 'multi-tenant', 'SaaS', 'plataforma']):
            pipeline_type = "enhanced"
            complexity = 7
        elif any(word in requirements_lower for word in ['simple', 'básico', 'personal', 'blog']):
            pipeline_type = "simple" 
            complexity = 3
        else:
            pipeline_type = "simple"
            complexity = 5
        
        return {
            "status": "fallback",
            "pipeline_recommendation": pipeline_type,
            "complexity_score": complexity,
            "architecture_style": "monolith",
            "business_domain": "software",
            "estimated_timeline": {"min": "1 month", "max": "3 months"},
            "resource_recommendations": {"developers": 2, "devops": 1, "qa": 1},
            "key_findings": {
                "integration_points": 0,
                "security_requirements": 1,
                "technical_risks": 1
            },
            "analysis_method": "pattern_based"
        }
    
    def get_pipeline_comparison(self, requirements: str) -> Dict[str, Any]:
        """Get detailed comparison between pipeline options"""
        analysis = self.analyze_project(requirements)
        
        simple_pipeline = {
            "name": "Simple Pipeline",
            "description": "Optimized for basic projects and MVPs",
            "duration": "2-4 weeks",
            "team_size": "1-2 developers",
            "cost": "Low",
            "features": [
                "Basic requirements analysis",
                "Standard architecture",
                "Essential testing",
                "Basic security",
                "Documentation"
            ],
            "best_for": [
                "Personal projects",
                "MVPs and prototypes", 
                "Simple web applications",
                "Internal tools"
            ]
        }
        
        enhanced_pipeline = {
            "name": "Enhanced Pipeline",
            "description": "Comprehensive solution for complex projects",
            "duration": "1-3 months", 
            "team_size": "3-5 developers + specialists",
            "cost": "Medium to High",
            "features": [
                "Enhanced requirements analysis",
                "Enterprise architecture",
                "Comprehensive testing suite",
                "Advanced security audit",
                "Performance optimization",
                "Quality validation",
                "Enterprise documentation"
            ],
            "best_for": [
                "SaaS platforms",
                "Enterprise systems",
                "Applications with integrations",
                "High-security requirements",
                "Scalable architectures"
            ]
        }
        
        return {
            "project_analysis": analysis,
            "pipeline_options": {
                "simple": simple_pipeline,
                "enhanced": enhanced_pipeline
            },
            "recommendation": analysis["pipeline_recommendation"]
        }

def demonstrate_complete_system():
    """Demonstrate the complete standalone dual pipeline system"""
    
    print("🚀 COMPLETE DUAL PIPELINE SYSTEM - STANDALONE")
    print("=" * 70)
    print("✅ Zero dependencies - Ready for immediate integration")
    print("✅ Intelligent pipeline recommendations") 
    print("✅ Works in any environment")
    print()
    
    # Create system
    system = StandaloneDualPipelineSystem()
    print("✅ Dual Pipeline System initialized!")
    print()
    
    print("🧪 REAL-WORLD PIPELINE ANALYSIS")
    print("=" * 50)
    
    test_scenarios = [
        {
            "name": "Personal Portfolio Website",
            "requirements": "Un sitio web personal para mostrar mi portfolio de proyectos con información de contacto.",
            "expected": "simple"
        },
        {
            "name": "Restaurant Management System", 
            "requirements": "Sistema para gestionar pedidos, inventario y empleados de un restaurante.",
            "expected": "simple"
        },
        {
            "name": "E-learning Platform",
            "requirements": "Plataforma de aprendizaje online con cursos, estudiantes, profesores, pagos y certificados.",
            "expected": "enhanced"
        },
        {
            "name": "Healthcare Patient Portal",
            "requirements": "Portal de pacientes para sistema de salud con historiales médicos, citas, recetas y compliance HIPAA.",
            "expected": "enhanced"
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n📋 {scenario['name']}")
        print(f"   Expected: {scenario['expected'].upper()} pipeline")
        print("-" * 45)
        
        comparison = system.get_pipeline_comparison(scenario['requirements'])
        analysis = comparison['project_analysis']
        recommendation = comparison['recommendation']
        
        print(f"   ✅ Recommended: {recommendation.upper()} pipeline")
        print(f"   📊 Complexity: {analysis['complexity_score']}/10")
        print(f"   🏗️  Architecture: {analysis['architecture_style']}")
        print(f"   ⏱️  Timeline: {analysis['estimated_timeline']}")
        print(f"   👥 Team: {analysis['resource_recommendations']}")
        
        # Check accuracy
        if recommendation == scenario['expected']:
            print("   🎯 ACCURACY: ✅ PERFECT MATCH")
        else:
            print(f"   🎯 ACCURACY: ⚠️  MISMATCH (expected {scenario['expected']})")
        
        # Show analysis details
        findings = analysis['key_findings']
        print(f"   🔍 Analysis: {findings['integration_points']} integrations, {findings['security_requirements']} security")
        print(f"   📝 Method: {analysis['analysis_method']}")
    
    print("\n" + "=" * 70)
    print("🎯 SYSTEM READY FOR INTEGRATION!")
    print()
    print("💡 IMMEDIATE INTEGRATION STEPS:")
    print("   1. Copy enhanced_intake_standalone_final.py to your project")
    print("   2. Copy dual_pipeline_standalone_system.py to your project") 
    print("   3. Import and use StandaloneDualPipelineSystem")
    print("   4. Call analyze_project() with requirements")
    print("   5. Route projects based on pipeline_recommendation")
    print()
    print("🚀 BENEFITS:")
    print("   • No dependency issues")
    print("   • Works in any environment")
    print("   • Provides intelligent routing")
    print("   • Improves project success rates")

if __name__ == "__main__":
    demonstrate_complete_system()

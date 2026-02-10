# test_enhanced_intake.py
import asyncio
import uuid
from core.app.agents.enhanced_intake_agent import EnhancedIntakeAgent

async def test_enhanced_intake():
    """Test the enhanced intake agent with complex requirements"""
    
    # Complex project requirements
    complex_requirements = """
    Necesito una plataforma SaaS empresarial para gestión de recursos humanos multi-tenant.
    
    Requisitos:
    - Soporte para 10,000+ empleados
    - Múltiples compañías (multi-tenant)
    - Integración con ADP, Workday y sistemas de nómina locales
    - Compliance con GDPR, HIPAA y regulaciones laborales locales
    - Dashboard en tiempo real con métricas de HR
    - Sistema de permisos y roles granular
    - API REST para integraciones con otros sistemas
    - Aplicación móvil para empleados
    - Sistema de notificaciones en tiempo real
    - Reporting avanzado con Power BI integration
    - Backup y disaster recovery automático
    - Alta disponibilidad (99.9% SLA)
    
    Tecnología preferida: Microservicios, Kubernetes, PostgreSQL, React, Node.js
    """
    
    agent = EnhancedIntakeAgent()
    
    # Test project ID
    test_project_id = uuid.uuid4()
    
    print("🧪 Testing Enhanced Intake Agent with complex requirements...")
    print("=" * 60)
    
    result = await agent.run(test_project_id, {"raw_requirements": complex_requirements})
    
    print(f"✅ Status: {result['status']}")
    print(f"📊 Complexity Score: {result['complexity_score']}/10")
    print(f"⚠️  Risk Level: {result['risk_level']}")
    print(f"⏱️  Timeline: {result['estimated_timeline']}")
    print(f"👥 Resources: {result['resource_recommendations']}")
    
    print("\n🔍 Enhanced Analysis:")
    analysis = result['enhanced_analysis']
    for key, value in analysis.items():
        print(f"   {key}: {value}")

if __name__ == "__main__":
    asyncio.run(test_enhanced_intake())
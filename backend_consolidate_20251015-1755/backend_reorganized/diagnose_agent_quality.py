import sys
sys.path.append('.')

def diagnose_agent_issues():
    print("🔍 DIAGNÓSTICO DE CALIDAD EN AGENTES")
    print("====================================")
    
    # 1. Revisar qué prompts están usando los agentes
    print("\n1. ANALIZANDO PROMPTS DE AGENTES ACTUALES:")
    
    try:
        from core.agents.builder_agent import BuilderAgent
        builder = BuilderAgent()
        
        # Verificar el método de generación
        if hasattr(builder, 'call_deepseek'):
            print("   ✅ BuilderAgent usa call_deepseek")
        else:
            print("   ❌ BuilderAgent NO tiene método de generación claro")
            
    except Exception as e:
        print(f"   ❌ Error en BuilderAgent: {e}")
    
    # 2. Revisar proyectos existentes para ver patrones
    print("\n2. ANÁLISIS DE PROYECTOS EXISTENTES:")
    import os
    projects_dir = "generated_projects"
    
    if os.path.exists(projects_dir):
        projects = os.listdir(projects_dir)
        print(f"   Total proyectos: {len(projects)}")
        
        # Analizar completitud
        complete_projects = 0
        placeholder_projects = 0
        
        for project in projects[:5]:  # Muestra primeros 5
            project_path = os.path.join(projects_dir, project)
            js_files = [f for f in os.listdir(project_path) if f.endswith(('.js', '.jsx', '.py'))]
            
            total_lines = 0
            for js_file in js_files[:3]:
                try:
                    with open(os.path.join(project_path, js_file), 'r') as f:
                        lines = len(f.readlines())
                        total_lines += lines
                except:
                    pass
            
            avg_lines = total_lines / max(len(js_files), 1)
            status = "✅ COMPLETO" if avg_lines > 50 else "❌ PLACEHOLDER"
            
            print(f"   {project}: {avg_lines:.1f} líneas promedio - {status}")
            
            if avg_lines > 50:
                complete_projects += 1
            else:
                placeholder_projects += 1
        
        print(f"\n   RESUMEN: {complete_projects} completos vs {placeholder_projects} placeholders")

if __name__ == "__main__":
    diagnose_agent_issues()

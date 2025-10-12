# Script para corregir imports del supervisor para DeepSeek
import re

with open('backend/app/agents/supervisor_agent.py', 'r') as f:
    content = f.read()

# Corregir imports rotos
replacements = {
    'from app.agents.intake import run as intake_run': 'from app.agents.intake_agent import IntakeAgent',
    'from app.agents.spec import run as spec_run': 'from app.agents.specification_agent import SpecificationAgent', 
    'from app.agents.builder import run as builder_run': 'from app.agents.builder_agent import BuilderAgent',
    'from app.agents.documenter import run as documenter_run': 'from app.agents.documenter_agent import DocumenterAgent',
    'from app.agents.tester import run as tester_run': 'from app.agents.tester_agent import TesterAgent',
    'from app.agents.planning_agent import run as planning_run': 'from app.agents.planning_agent import PlanningAgent'
}

for old, new in replacements.items():
    content = content.replace(old, new)

# Corregir la secuencia de agentes
content = content.replace('self.agent_sequence = [', '''self.agent_sequence = [
            ("intake", "Requirements Analysis", IntakeAgent()),
            ("spec", "Specification", SpecificationAgent()),
            ("planning", "Architecture Planning", PlanningAgent()),
            ("builder", "Code Generation", BuilderAgent()),
            ("documenter", "Documentation", DocumenterAgent()),
            ("tester", "Testing", TesterAgent())''')

# Actualizar las llamadas a los agentes en el método run_pipeline
content = re.sub(
    r'agent_run = agent_func\(project_id, requirements\)',
    'agent_run = agent_instance.run(project_id, requirements)',
    content
)

with open('backend/app/agents/supervisor_agent.py', 'w') as f:
    f.write(content)

print("✅ Imports del supervisor corregidos para DeepSeek")

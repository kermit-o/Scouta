# Corrección precisa de imports en supervisor_agent.py
with open('core/app/agents/supervisor_agent.py', 'r') as f:
    content = f.read()

# Reemplazar imports incorrectos por los correctos
content = content.replace(
    'from core.models.project import Project',
    'from core.database.models import Project'
)

content = content.replace(
    'from core.models.job import Job', 
    'from core.database.models import Job'
)

content = content.replace(
    'from core.models.agent_run import AgentRun',
    'from core.database.models import AgentRun'  
)

with open('core/app/agents/supervisor_agent.py', 'w') as f:
    f.write(content)

print("✅ supervisor_agent.py corregido - imports de database.models")

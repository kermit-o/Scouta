import os

agent_base_path = 'backend/app/agents/agent_base.py'
if os.path.exists(agent_base_path):
    with open(agent_base_path, 'r') as f:
        content = f.read()
        if 'deepseek' in content.lower() or 'openai' in content.lower():
            print("✅ agent_base.py ya tiene integración AI")
        else:
            print("❌ agent_base.py necesita integración DeepSeek")
else:
    print("❌ agent_base.py no existe")

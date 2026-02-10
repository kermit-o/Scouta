import re

with open('main.py', 'r') as f:
    content = f.read()

# Encontrar y reemplazar toda la función health_check
# Patrón desde @app.get hasta la siguiente función @app
pattern = r'(@app\.get\("/health", response_model=HealthResponse\)\s+async def health_check\(\):.*?)(?=\n@app|\Z)'

new_health_check = '''@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint - Simple working version"""
    from datetime import datetime
    
    services = {
        "api": "healthy",
        "postgres": "checking",
        "redis": "checking"
    }
    
    # Always return a valid HealthResponse
    return HealthResponse(
        status="degraded",  # Default to degraded until we verify services
        timestamp=datetime.now().isoformat(),
        services=services
    )'''

# Reemplazar
new_content = re.sub(pattern, new_health_check, content, flags=re.DOTALL)

with open('main.py', 'w') as f:
    f.write(new_content)

print("✅ health_check reemplazado con versión simple")

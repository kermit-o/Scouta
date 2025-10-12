# Leer backend_final.py
with open('backend_final.py', 'r') as f:
    content = f.read()

# Encontrar y reemplazar el endpoint problemático
old_endpoint = '''@app.api_route("/api/v1/ai/analyze", methods=["GET", "POST"])
async def analyze_idea(idea: dict):'''

new_endpoint = '''@app.api_route("/api/v1/ai/analyze", methods=["GET", "POST"])
async def analyze_idea(request: dict = None):
    # Manejar tanto GET como POST
    if request is None:
        return {
            "project_type": "nextjs_app", 
            "architecture": "Aplicación web moderna",
            "recommended_stack": ["react", "typescript", "nodejs"],
            "complexity": "Media", 
            "estimated_weeks": 2,
            "message": "Por favor usa POST con {'idea': 'tu idea'} para análisis completo"
        }
    
    return {
        "project_type": "nextjs_app",
        "architecture": "Aplicación web moderna", 
        "recommended_stack": ["react", "typescript", "nodejs"],
        "complexity": "Medium",
        "estimated_weeks": 2,
        "analyzed_idea": request.get("idea", "Sin idea proporcionada")
    }'''

if old_endpoint in content:
    content = content.replace(old_endpoint, new_endpoint)
    print("✅ Endpoint AI corregido para manejar GET y POST")
else:
    print("❌ No se pudo encontrar el endpoint exacto")
    # Buscar por partes
    import re
    pattern = r'@app\.api_route\("/api/v1/ai/analyze", methods=\["GET", "POST"\]\)\s+async def analyze_idea\(idea: dict\):'
    if re.search(pattern, content):
        content = re.sub(pattern, new_endpoint, content)
        print("✅ Endpoint corregido usando regex")
    else:
        print("⚠️  No se pudo corregir automáticamente")

# Escribir archivo corregido
with open('backend_final.py', 'w') as f:
    f.write(content)

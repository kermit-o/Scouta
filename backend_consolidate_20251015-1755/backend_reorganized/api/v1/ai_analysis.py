"""
AI Analysis API routes with DeepSeek integration
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_project_analyzer import ai_analyzer

router = APIRouter()

class AnalyzeIdeaRequest(BaseModel):
    idea: str
    project_type: str = "web_app"

@router.post("/analyze-idea")
async def analyze_idea(request: AnalyzeIdeaRequest):
    """Analyze project idea with AI"""
    try:
        analysis = await ai_analyzer.analyze_idea(request.idea, request.project_type)

        return {
            "analysis": analysis,
            "success": True,
            "ai_enhanced": True,
            "recommendations": analysis.get("features", []),
            "technologies": analysis.get("technologies", []),
            "complexity": analysis.get("complexity_score", 5),
            "development_phases": analysis.get("development_phases", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.get("/health")
async def ai_health():
    """AI service health check"""
    return {
        "status": "ai_service_healthy",
        "service": "ai_analysis",
        "deepseek_available": True
    }

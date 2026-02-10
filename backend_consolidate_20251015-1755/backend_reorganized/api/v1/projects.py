"""
Projects API routes with real project generation
"""
from fastapi import APIRouter, HTTPException
from core.projects.enhanced_project_factory import EnhancedProjectFactory
from core.projects.real_project_factory import ProjectRequirements, ProjectType

router = APIRouter()
project_factory = EnhancedProjectFactory()

@router.get("/types")
async def get_project_types():
    """Get available project types"""
    return {
        "project_types": [
            {
                "value": pt.value,
                "label": pt.name.replace("_", " ").title(),
                "description": f"Project type: {pt.name.replace('_', ' ').title()}"
            }
            for pt in ProjectType
        ]
    }

@router.post("/create")
async def create_project(requirements: dict):
    """Create a new real project"""
    try:
        # Convert dict to ProjectRequirements
        project_req = ProjectRequirements(
            name=requirements.get("name", "Untitled Project"),
            description=requirements.get("description", ""),
            project_type=ProjectType(requirements.get("project_type", "web_app")),
            features=requirements.get("features", []),
            technologies=requirements.get("technologies", []),
            database=requirements.get("database", "sqlite"),
            auth_required=requirements.get("auth_required", False),
            payment_integration=requirements.get("payment_integration", False),
            deployment_target=requirements.get("deployment_target", "local")
        )
        
        result = project_factory.create_project(project_req)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project creation failed: {str(e)}")

@router.get("/list")
async def list_projects():
    """List generated projects"""
    import os
    import json
    projects_dir = "generated_projects"
    if not os.path.exists(projects_dir):
        return {"projects": []}
    
    projects = []
    for item in os.listdir(projects_dir):
        item_path = os.path.join(projects_dir, item)
        if os.path.isdir(item_path):
            project_info = {
                "name": item,
                "path": item_path,
                "created_at": str(os.path.getctime(item_path))
            }
            
            # Try to load project metadata
            metadata_file = os.path.join(item_path, "project.json")
            if os.path.exists(metadata_file):
                try:
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    project_info.update(metadata)
                except:
                    pass
            
            projects.append(project_info)
    
    return {"projects": projects, "count": len(projects)}

@router.get("/{project_id}/info")
async def get_project_info(project_id: str):
    """Get specific project information"""
    import os
    import json
    
    project_path = os.path.join("generated_projects", project_id)
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    metadata_file = os.path.join(project_path, "project.json")
    if os.path.exists(metadata_file):
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
            return metadata
        except:
            pass
    
    return {
        "project_id": project_id,
        "path": project_path,
        "exists": os.path.exists(project_path)
    }

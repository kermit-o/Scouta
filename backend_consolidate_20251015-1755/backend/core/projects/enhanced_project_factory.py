"""
Enhanced Project Factory with AI Integration
"""
from typing import Dict
import asyncio
from .real_project_factory import RealProjectFactory, ProjectRequirements, ProjectType
from .project_factory import ProjectFactory as BaseProjectFactory
from services.ai_project_analyzer import ai_analyzer

class EnhancedProjectFactory(BaseProjectFactory):
    """Enhanced factory with AI-powered project generation"""
    
    def __init__(self, openai_api_key: str = None):
        super().__init__()
        self.openai_api_key = openai_api_key
        self.real_factory = RealProjectFactory()
        self.ai_enabled = True
        self._event_loop = None
    
    def create_project(self, requirements: ProjectRequirements):
        """Create a real project with AI enhancements"""
        try:
            # Use the real project factory to generate base structure
            result = self.real_factory.create_project(requirements)
            
            # Add AI enhancements if enabled
            if result.get("success"):
                result = self._run_async_enhancements(result, requirements)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Enhanced project creation failed: {str(e)}",
                "project_id": None
            }
    
    def _run_async_enhancements(self, result: Dict, requirements: ProjectRequirements):
        """Run async enhancements safely"""
        try:
            # Try to get existing event loop or create new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            if loop.is_running():
                # If loop is already running, use task
                task = asyncio.create_task(self._add_ai_enhancements(result, requirements))
                # For simplicity, we'll wait for completion (in real app would use callbacks)
                import time
                while not task.done():
                    time.sleep(0.1)
                return task.result()
            else:
                # If loop is not running, run it
                return loop.run_until_complete(self._add_ai_enhancements(result, requirements))
                
        except Exception as e:
            print(f"Async enhancement error: {e}")
            return result
    
    async def _add_ai_enhancements(self, result: Dict, requirements: ProjectRequirements):
        """Add AI-powered enhancements to the project"""
        try:
            # Analyze project with AI
            analysis = await ai_analyzer.analyze_idea(
                requirements.description, 
                requirements.project_type.value
            )
            
            # Update result with AI insights
            result["ai_analysis"] = analysis
            result["enhanced_features"] = [
                "AI-powered architecture analysis",
                "Intelligent technology recommendations", 
                "Risk assessment and mitigation",
                "Development phase planning"
            ]
            
            # Add AI-generated content to existing project
            if result.get("project_path"):
                await self._enhance_project_files(
                    result["project_path"], 
                    requirements, 
                    analysis
                )
            
            return result
            
        except Exception as e:
            print(f"AI enhancement error: {e}")
            return result
    
    async def _enhance_project_files(self, project_path: str, requirements: ProjectRequirements, analysis: Dict):
        """Enhance project files with AI-generated content"""
        import os
        
        # Generate intelligent README
        readme_content = await ai_analyzer.generate_intelligent_readme(
            requirements.name,
            analysis,
            requirements.dict()
        )
        
        readme_path = os.path.join(project_path, "AI_ENHANCED_README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        # Add AI analysis to project metadata
        metadata_path = os.path.join(project_path, "project.json")
        if os.path.exists(metadata_path):
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            metadata["ai_analysis"] = analysis
            metadata["ai_enhanced"] = True
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

# For backward compatibility
ProjectFactory = EnhancedProjectFactory

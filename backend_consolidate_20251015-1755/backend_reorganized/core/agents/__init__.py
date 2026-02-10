from .universal_analyst_agent import UniversalAnalystAgent
from .agent_base import AgentBase

# Agentes para compatibilidad con DualPipelineSupervisor
from .intake_agent import IntakeAgent
from .enhanced_intake_agent import EnhancedIntakeAgent
from .intelligent_intake_agent import IntelligentIntakeAgent
from .real_intelligent_intake_agent import RealIntelligentIntakeAgent
from .specification_agent import SpecificationAgent
from .data_design_agent import DataDesignAgent
from .planning_agent import PlanningAgent
from .builder_agent import BuilderAgent
from .documenter_agent import DocumenterAgent
from .tester_agent import TesterAgent
from .mockup_agent import MockupAgent
from .security_agent import SecurityAgent
from .scaffolder_agent import ScaffolderAgent
from .validation_agent import ValidationAgent
from .dual_pipeline_supervisor import DualPipelineSupervisor

__all__ = [
    'UniversalAnalystAgent',
    'AgentBase',
    'IntakeAgent',
    'EnhancedIntakeAgent',
    'IntelligentIntakeAgent', 
    'RealIntelligentIntakeAgent',
    'SpecificationAgent',
    'DataDesignAgent',
    'PlanningAgent',
    'BuilderAgent',
    'DocumenterAgent',
    'TesterAgent',
    'MockupAgent',
    'SecurityAgent',
    'ScaffolderAgent',
    'ValidationAgent',
    'DualPipelineSupervisor'
]

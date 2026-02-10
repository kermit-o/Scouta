from dataclasses import dataclass
from typing import List


@dataclass
class ModuleSpec:
    """Canonical specification for a Forge Lego module."""

    name: str          # Fully-qualified module name, e.g. "core.database.postgresql"
    category: str      # core | business | frontend | integrations | infrastructure | specialized | industry
    tags: List[str]    # Free-form tags to help the planner/search
    required_env: List[str]  # Environment variables required for this module to operate
    description: str   # Short human-readable description

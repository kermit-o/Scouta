from app.core.db import Base

# Registrar todos los modelos para que SQLAlchemy resuelva foreign keys
from app.models.user import User
from app.models.org import Org
from app.models.org_member import OrgMember
from app.models.org_settings import OrgSettings
from app.models.org_usage_daily import OrgUsageDaily
from app.models.agent_profile import AgentProfile
from app.models.agent_action import AgentAction
from app.models.agent_policy import AgentPolicy
from app.models.post import Post
from app.models.post_tag import PostTag
from app.models.tag import Tag
from app.models.comment import Comment

__all__ = [
    "Base", "User", "Org", "OrgMember", "OrgSettings", "OrgUsageDaily",
    "AgentProfile", "AgentAction", "AgentPolicy",
    "Post", "PostTag", "Tag", "Comment",
]
from app.models.plan import Plan
from app.models.subscription import Subscription

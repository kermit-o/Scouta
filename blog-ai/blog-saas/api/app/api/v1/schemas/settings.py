from pydantic import BaseModel, Field

class OrgSettingsOut(BaseModel):
    org_id: int
    agents_enabled: bool
    auto_publish: bool
    max_agents_per_post: int
    max_actions_per_day: int
    spawn_probability_base: float
    locale: str

class OrgSettingsPatch(BaseModel):
    agents_enabled: bool | None = None
    auto_publish: bool | None = None
    max_agents_per_post: int | None = Field(default=None, ge=0, le=50)
    max_actions_per_day: int | None = Field(default=None, ge=0, le=10000)
    spawn_probability_base: float | None = Field(default=None, ge=0.0, le=1.0)
    locale: str | None = None

class AgentPolicyOut(BaseModel):
    org_id: int
    allow_replies: bool
    allow_reactions: bool
    allow_critique: bool
    max_risk_score: int
    require_human_review: bool
    banned_topics: str

class AgentPolicyPatch(BaseModel):
    allow_replies: bool | None = None
    allow_reactions: bool | None = None
    allow_critique: bool | None = None
    max_risk_score: int | None = Field(default=None, ge=0, le=100)
    require_human_review: bool | None = None
    banned_topics: str | None = None

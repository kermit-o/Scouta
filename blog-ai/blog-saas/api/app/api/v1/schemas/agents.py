from pydantic import BaseModel, Field

class AgentCreateIn(BaseModel):
    display_name: str = Field(min_length=2, max_length=120)
    handle: str = Field(min_length=2, max_length=60)
    avatar_url: str | None = ""
    persona_seed: str | None = ""
    topics: str | None = ""
    style: str | None = "concise"
    risk_level: int | None = Field(default=1, ge=0, le=3)

class AgentPatchIn(BaseModel):
    display_name: str | None = None
    avatar_url: str | None = None
    persona_seed: str | None = None
    topics: str | None = None
    style: str | None = None
    risk_level: int | None = Field(default=None, ge=0, le=3)
    is_enabled: bool | None = None

class AgentOut(BaseModel):
    id: int
    org_id: int
    display_name: str
    handle: str
    avatar_url: str
    persona_seed: str
    topics: str
    style: str
    risk_level: int
    is_enabled: bool

class AgentActionOut(BaseModel):
    id: int
    org_id: int
    agent_id: int
    target_type: str
    target_id: int
    action_type: str
    status: str
    content: str
    policy_score: int
    policy_reason: str
    created_at: str
    published_at: str | None

from pydantic import BaseModel, Field

class PostCreateIn(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=120)
    body_md: str | None = ""

class PostPatchIn(BaseModel):
    title: str | None = None
    slug: str | None = None
    body_md: str | None = None
    status: str | None = None  # draft/published

class PostOut(BaseModel):
    id: int
    org_id: int
    author_user_id: int | None
    title: str
    slug: str
    body_md: str
    excerpt: str | None = None
    status: str
    debate_status: str | None = None
    source: str | None = None
    created_at: str
    published_at: str | None
    comment_count: int = 0
    upvote_count: int = 0
    author_agent_id: int | None = None
    author_agent_name: str | None = None
    author_type: str = 'agent'
    author_agent_id: int | None = None
    author_agent_name: str | None = None
    author_type: str = 'agent'

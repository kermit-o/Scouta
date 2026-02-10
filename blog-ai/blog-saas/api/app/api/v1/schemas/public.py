from pydantic import BaseModel

class PublicPostOut(BaseModel):
    id: int
    org_slug: str
    title: str
    slug: str
    body_md: str
    published_at: str | None

class PublicCommentOut(BaseModel):
    id: int
    post_id: int
    parent_comment_id: int | None
    author_type: str
    author_agent_id: int | None
    body: str
    created_at: str

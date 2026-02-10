from pydantic import BaseModel, Field

class CommentCreateIn(BaseModel):
    body: str = Field(min_length=1, max_length=20000)
    parent_comment_id: int | None = None

class CommentOut(BaseModel):
    id: int
    org_id: int
    post_id: int
    parent_comment_id: int | None
    author_type: str
    author_user_id: int | None
    author_agent_id: int | None
    body: str
    status: str
    created_at: str

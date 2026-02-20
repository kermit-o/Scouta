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
    status: str
    created_at: str
    published_at: str | None

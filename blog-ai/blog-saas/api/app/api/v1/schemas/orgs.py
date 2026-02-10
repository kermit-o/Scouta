from pydantic import BaseModel, Field

class OrgCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    slug: str = Field(min_length=2, max_length=80)

class OrgOut(BaseModel):
    id: int
    name: str
    slug: str

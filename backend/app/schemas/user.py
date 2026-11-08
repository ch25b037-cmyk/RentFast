"""User profile schemas."""

from pydantic import BaseModel, Field, HttpUrl


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=120)
    department: str | None = Field(default=None, max_length=120)
    hostel: str | None = Field(default=None, max_length=120)
    avatar: HttpUrl | None = None


class PublicUserResponse(BaseModel):
    id: str
    display_name: str
    avatar_url: str | None
    trust_score: int
    trust_tier: str
    completed_loans: int
    recent_reviews: list[dict] = []

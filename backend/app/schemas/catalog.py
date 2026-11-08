"""Catalog, meetup and inventory schemas."""

from pydantic import BaseModel, ConfigDict, Field


class CategoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    slug: str
    name: str
    icon: str
    max_loan_hours: int


class MeetupSpotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    location_hint: str


class ItemCreate(BaseModel):
    category_id: str
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=2000)
    condition: str = Field(pattern=r"^(new|good|fair)$")
    value_tier: str = Field(pattern=r"^(low|mid|high)$")
    photo_urls: list[str] = Field(default_factory=list, max_length=5)


class ItemUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, min_length=2, max_length=2000)
    condition: str | None = Field(default=None, pattern=r"^(new|good|fair)$")
    value_tier: str | None = Field(default=None, pattern=r"^(low|mid|high)$")
    is_available: bool | None = None


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    category_id: str
    title: str
    description: str
    condition: str
    value_tier: str
    photo_urls: list[str]
    is_available: bool


class ItemPage(BaseModel):
    items: list[ItemRead]
    total: int
    limit: int
    offset: int


class UploadRead(BaseModel):
    url: str

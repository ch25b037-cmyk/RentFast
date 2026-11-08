"""Borrow request schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RequestCreate(BaseModel):
    category_id: str
    title: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=2000)
    needed_from: datetime
    needed_until: datetime
    preferred_spot_id: str | None = None


class RequestUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, min_length=2, max_length=2000)
    needed_from: datetime | None = None
    needed_until: datetime | None = None
    preferred_spot_id: str | None = None


class RequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    requester_id: str
    category_id: str
    title: str
    description: str
    needed_from: datetime
    needed_until: datetime
    preferred_spot_id: str | None
    status: str
    expires_at: datetime
    offers_count: int = 0
    loan_id: str | None = None


class RequestPage(BaseModel):
    items: list[RequestRead]
    total: int
    limit: int
    offset: int

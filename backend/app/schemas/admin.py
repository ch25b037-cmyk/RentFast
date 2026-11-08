"""Admin moderation schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class ReportResolve(BaseModel):
    action: str = Field(pattern=r"^(dismiss|warn|suspend)$")
    note: str = Field(min_length=2, max_length=2000)


class DisputeResolve(BaseModel):
    outcome: str = Field(pattern=r"^(borrower_wins|lender_wins|dismiss)$")
    note: str = Field(min_length=2, max_length=2000)


class MeetupSpotCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = Field(min_length=2, max_length=500)
    location_hint: str = Field(min_length=2, max_length=240)
    is_active: bool = True


class MeetupSpotUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = Field(default=None, min_length=2, max_length=500)
    location_hint: str | None = Field(default=None, min_length=2, max_length=240)
    is_active: bool | None = None


class AuditLogRead(BaseModel):
    id: str
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: str
    metadata_json: dict
    created_at: datetime

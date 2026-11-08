"""Reports, blocks and review schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class BlockCreate(BaseModel):
    user_id: str


class BlockRead(BaseModel):
    id: str
    blocked_id: str
    created_at: datetime


class ReportCreate(BaseModel):
    target_user_id: str | None = None
    target_loan_id: str | None = None
    target_message_id: str | None = None
    reason: str = Field(pattern=r"^(no_show|damaged|not_returned|harassment|fake_listing|unsafe_meetup|other)$")
    details: str = Field(min_length=2, max_length=2000)


class ReportRead(BaseModel):
    id: str
    reporter_id: str
    target_user_id: str | None
    target_loan_id: str | None
    target_message_id: str | None
    reason: str
    details: str
    status: str


class ReviewCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    tags: list[str] = Field(default_factory=list, max_length=5)
    comment: str = Field(default="", max_length=1000)


class ReviewRead(BaseModel):
    id: str
    loan_id: str
    reviewer_id: str
    reviewee_id: str
    rating: int
    tags: list[str]
    comment: str

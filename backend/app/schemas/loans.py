"""Loan, agreement, meetup and code schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgreementInput(BaseModel):
    agreement_version: int


class SpotInput(BaseModel):
    spot_id: str
    scheduled_start: datetime


class CodeInput(BaseModel):
    code: str = Field(min_length=6, max_length=6, pattern=r"^\d{6}$")


class DisputeInput(BaseModel):
    reason: str = Field(min_length=2, max_length=120)
    details: str = Field(min_length=2, max_length=2000)


class CodeRead(BaseModel):
    code: str
    purpose: str
    expires_at: datetime


class LoanEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    actor_id: str | None
    type: str
    payload: dict
    created_at: datetime


class LoanRead(BaseModel):
    id: str
    request_id: str
    offer_id: str
    item_id: str | None
    lender_id: str
    borrower_id: str
    spot_id: str | None
    scheduled_start: datetime | None
    due_at: datetime
    status: str
    agreement_version: int
    borrower_agreed_at: datetime | None
    lender_agreed_at: datetime | None
    handed_over_at: datetime | None
    returned_at: datetime | None
    closed_at: datetime | None
    events: list[LoanEventRead] = []


class LoanPage(BaseModel):
    items: list[LoanRead]
    total: int
    limit: int
    offset: int

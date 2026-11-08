"""Offer and chat schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OfferCreate(BaseModel):
    item_id: str | None = None
    message: str = Field(default="", max_length=1000)


class OfferRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    request_id: str
    owner_id: str
    item_id: str | None
    message: str
    status: str
    created_at: datetime


class MessageCreate(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class MessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    offer_id: str
    sender_id: str
    body: str
    masked: bool
    created_at: datetime

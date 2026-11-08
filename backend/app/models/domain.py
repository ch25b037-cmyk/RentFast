"""CampusLend lending-domain persistence models."""

from datetime import datetime

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON, DateTime

from app.db.base import TimestampedModel


class Category(TimestampedModel):
    __tablename__ = "categories"

    slug: Mapped[str] = mapped_column(String(80), unique=True)
    name: Mapped[str] = mapped_column(String(120))
    icon: Mapped[str] = mapped_column(String(80))
    max_loan_hours: Mapped[int] = mapped_column(Integer)
    is_prohibited: Mapped[bool] = mapped_column(Boolean, default=False)


class MeetupSpot(TimestampedModel):
    __tablename__ = "meetup_spots"

    name: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    location_hint: Mapped[str] = mapped_column(String(240))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Item(TimestampedModel):
    __tablename__ = "items"

    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    condition: Mapped[str] = mapped_column(String(20))
    value_tier: Mapped[str] = mapped_column(String(20))
    photo_urls: Mapped[list] = mapped_column(JSON, default=list)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BorrowRequest(TimestampedModel):
    __tablename__ = "requests"
    __table_args__ = (
        Index("ix_requests_status_needed_from", "status", "needed_from"),
        Index("ix_requests_category_status", "category_id", "status"),
    )

    requester_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(Text)
    needed_from: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    needed_until: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    preferred_spot_id: Mapped[str | None] = mapped_column(ForeignKey("meetup_spots.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Offer(TimestampedModel):
    __tablename__ = "offers"
    __table_args__ = (
        UniqueConstraint("request_id", "owner_id", "status", name="uq_pending_offer_owner"),
        Index("ix_offers_request_status", "request_id", "status"),
    )

    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id"), index=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    item_id: Mapped[str | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    message: Mapped[str] = mapped_column(String(1000), default="")
    status: Mapped[str] = mapped_column(String(20), default="pending")


class Loan(TimestampedModel):
    __tablename__ = "loans"
    __table_args__ = (
        Index("ix_loans_lender_status", "lender_id", "status"),
        Index("ix_loans_borrower_status", "borrower_id", "status"),
        Index("ix_loans_status_due_at", "status", "due_at"),
    )

    request_id: Mapped[str] = mapped_column(ForeignKey("requests.id"), unique=True)
    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id"), unique=True)
    item_id: Mapped[str | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    lender_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    borrower_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    spot_id: Mapped[str | None] = mapped_column(ForeignKey("meetup_spots.id"), nullable=True)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), default="pending_handover", index=True)
    agreement_version: Mapped[int] = mapped_column(Integer, default=1)
    borrower_agreed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    lender_agreed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    handed_over_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    late_penalty_applied: Mapped[bool] = mapped_column(Boolean, default=False)


class LoanCode(TimestampedModel):
    __tablename__ = "loan_codes"

    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"), index=True)
    purpose: Mapped[str] = mapped_column(String(20))
    code_hash: Mapped[str] = mapped_column(String(128))
    shown_to_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class LoanEvent(TimestampedModel):
    __tablename__ = "loan_events"
    __table_args__ = (Index("ix_loan_events_loan_created", "loan_id", "created_at"),)

    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"), index=True)
    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    type: Mapped[str] = mapped_column(String(80))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)


class Message(TimestampedModel):
    __tablename__ = "messages"

    offer_id: Mapped[str] = mapped_column(ForeignKey("offers.id"), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(String(1000))
    masked: Mapped[bool] = mapped_column(Boolean, default=False)
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)


class Review(TimestampedModel):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("loan_id", "reviewer_id", name="uq_review_reviewer"),)

    loan_id: Mapped[str] = mapped_column(ForeignKey("loans.id"), index=True)
    reviewer_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    reviewee_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    comment: Mapped[str] = mapped_column(String(1000), default="")


class Report(TimestampedModel):
    __tablename__ = "reports"

    reporter_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    target_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    target_loan_id: Mapped[str | None] = mapped_column(ForeignKey("loans.id"), nullable=True)
    target_message_id: Mapped[str | None] = mapped_column(ForeignKey("messages.id"), nullable=True)
    reason: Mapped[str] = mapped_column(String(40))
    details: Mapped[str] = mapped_column(String(2000))
    status: Mapped[str] = mapped_column(String(20), default="open", index=True)
    resolved_by: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Block(TimestampedModel):
    __tablename__ = "blocks"
    __table_args__ = (UniqueConstraint("blocker_id", "blocked_id", name="uq_block_pair"),)

    blocker_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    blocked_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)


class Notification(TimestampedModel):
    __tablename__ = "notifications"
    __table_args__ = (Index("ix_notifications_user_read", "user_id", "read_at"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(80))
    title: Mapped[str] = mapped_column(String(160))
    body: Mapped[str] = mapped_column(String(1000))
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(TimestampedModel):
    __tablename__ = "audit_logs"

    actor_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[str] = mapped_column(String(36))
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    ip_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)

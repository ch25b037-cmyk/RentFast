"""Borrow request business rules and feed queries."""

from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.clock import as_utc, now_utc
from app.core.config import get_settings
from app.core.errors import DomainError, NotFoundError
from app.models.domain import Block, BorrowRequest, Category, Loan, MeetupSpot, Offer
from app.models.user import User
from app.services.user import trust_tier


def _validate_window(category: Category, start: datetime, end: datetime) -> None:
    start = as_utc(start)
    end = as_utc(end)
    if start < now_utc() or end <= start:
        raise DomainError("VALIDATION_ERROR", "Choose a future, positive lending window.")
    if (end - start).total_seconds() > category.max_loan_hours * 3600:
        raise DomainError("VALIDATION_ERROR", "This window is longer than the category allows.")


def loan_id_for_request(db: Session, request_id: str) -> str | None:
    return db.scalar(select(Loan.id).where(Loan.request_id == request_id))


def create_request(db: Session, user: User, values: dict) -> BorrowRequest:
    category = db.get(Category, values["category_id"])
    if category is None or category.is_prohibited:
        raise DomainError("PROHIBITED_ITEM", "Choose an allowed item category.")
    _validate_window(category, values["needed_from"], values["needed_until"])
    if values.get("preferred_spot_id") and db.get(MeetupSpot, values["preferred_spot_id"]) is None:
        raise NotFoundError("Meetup spot not found")
    tier = trust_tier(user.trust_score)
    max_open = {"Member": get_settings().max_open_requests_member, "Trusted": get_settings().max_open_requests_trusted}.get(tier, 0)
    open_count = db.scalar(select(func.count()).select_from(BorrowRequest).where(BorrowRequest.requester_id == user.id, BorrowRequest.status == "open")) or 0
    if open_count >= max_open:
        raise DomainError("TRUST_LIMIT_REACHED", "Your trust tier has reached its open request limit.")
    request = BorrowRequest(requester_id=user.id, expires_at=as_utc(values["needed_from"]), **values)
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def _visible_query(db: Session, user: User, status: str, category: str | None, q: str | None, mine: bool):
    query = select(BorrowRequest)
    if status != "all":
        query = query.where(BorrowRequest.status == status)
    blocked = select(Block.blocked_id).where(Block.blocker_id == user.id).union_all(select(Block.blocker_id).where(Block.blocked_id == user.id))
    query = query.where(~BorrowRequest.requester_id.in_(blocked))
    if mine:
        query = query.where(BorrowRequest.requester_id == user.id)
    if category:
        query = query.where(BorrowRequest.category_id == category)
    if q:
        query = query.where(or_(BorrowRequest.title.ilike(f"%{q}%"), BorrowRequest.description.ilike(f"%{q}%")))
    return query.order_by(BorrowRequest.needed_from)


def list_requests(db: Session, user: User, limit: int, offset: int, status: str, category: str | None, q: str | None, mine: bool, urgent: bool) -> tuple[list[BorrowRequest], int]:
    query = _visible_query(db, user, status, category, q, mine)
    values = list(db.scalars(query))
    if urgent:
        values = [item for item in values if (as_utc(item.needed_from) - now_utc()).total_seconds() <= 86400]
    return values[offset : offset + limit], len(values)


def get_request(db: Session, user: User, request_id: str) -> BorrowRequest:
    request = db.get(BorrowRequest, request_id)
    if request is None:
        raise NotFoundError()
    if request.requester_id != user.id:
        blocked = db.scalar(select(Block).where(or_(Block.blocker_id == user.id, Block.blocked_id == user.id), or_(Block.blocked_id == request.requester_id, Block.blocker_id == request.requester_id)))
        if blocked:
            raise NotFoundError()
    return request


def update_request(db: Session, request: BorrowRequest, values: dict) -> BorrowRequest:
    if request.status != "open":
        raise DomainError("REQUEST_NOT_OPEN", "Only open requests can be edited.")
    for key, value in values.items():
        if value is not None:
            setattr(request, key, value)
    db.commit()
    db.refresh(request)
    return request


def cancel_request(db: Session, request: BorrowRequest) -> BorrowRequest:
    if request.status != "open":
        raise DomainError("REQUEST_NOT_OPEN", "Only open requests can be cancelled.")
    request.status = "cancelled"
    db.commit()
    db.refresh(request)
    return request


def expire_requests(db: Session, at: datetime | None = None) -> int:
    at = at or now_utc()
    values = list(db.scalars(select(BorrowRequest).where(BorrowRequest.status == "open", BorrowRequest.expires_at < at)))
    for request in values:
        request.status = "expired"
        for offer in db.scalars(select(Offer).where(Offer.request_id == request.id, Offer.status == "pending")):
            offer.status = "expired"
    db.commit()
    return len(values)

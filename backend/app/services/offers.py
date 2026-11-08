"""Offer, chat and transactional loan-creation services."""

import re

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.clock import as_utc
from app.core.config import get_settings
from app.core.errors import DomainError, NotFoundError
from app.models.domain import (
    Block,
    BorrowRequest,
    Item,
    Loan,
    LoanEvent,
    Message,
    Notification,
    Offer,
)
from app.models.user import User


def _blocked(db: Session, first: str, second: str) -> bool:
    return db.scalar(select(Block).where(or_(Block.blocker_id == first, Block.blocked_id == first), or_(Block.blocked_id == second, Block.blocker_id == second))) is not None


def create_offer(db: Session, request_id: str, user: User, values: dict) -> Offer:
    request = db.get(BorrowRequest, request_id)
    if request is None:
        raise NotFoundError()
    if request.requester_id == user.id or request.status != "open":
        raise DomainError("REQUEST_NOT_OPEN", "This request cannot receive an offer.")
    if _blocked(db, user.id, request.requester_id):
        raise DomainError("BLOCKED", "This interaction is unavailable.")
    item_id = values.get("item_id")
    if item_id:
        item = db.scalar(select(Item).where(Item.id == item_id, Item.owner_id == user.id, Item.deleted_at.is_(None), Item.is_available.is_(True)))
        if item is None:
            raise NotFoundError("Item not found")
    offer = Offer(request_id=request_id, owner_id=user.id, **values)
    db.add(offer)
    db.add(Notification(user_id=request.requester_id, type="offer_received", title="New offer", body="Someone offered an item for your request.", data={"request_id": request_id, "offer_id": offer.id}))
    db.commit()
    db.refresh(offer)
    return offer


def get_offer_for_party(db: Session, offer_id: str, user: User) -> Offer:
    offer = db.get(Offer, offer_id)
    if offer is None:
        raise NotFoundError()
    request = db.get(BorrowRequest, offer.request_id)
    if request is None or user.id not in {offer.owner_id, request.requester_id}:
        raise NotFoundError()
    if _blocked(db, user.id, offer.owner_id if user.id == request.requester_id else request.requester_id):
        raise NotFoundError()
    return offer


def list_offers_for_request(db: Session, request_id: str, user: User) -> list[Offer]:
    request = db.get(BorrowRequest, request_id)
    if request is None or request.requester_id != user.id:
        raise NotFoundError()
    return list(db.scalars(select(Offer).where(Offer.request_id == request_id).order_by(Offer.created_at)))


def list_my_offers(db: Session, user: User) -> list[Offer]:
    return list(db.scalars(select(Offer).where(Offer.owner_id == user.id).order_by(Offer.created_at.desc())))


def accept_offer(db: Session, offer: Offer, borrower: User) -> Loan:
    request = db.get(BorrowRequest, offer.request_id)
    if request is None or request.requester_id != borrower.id:
        raise NotFoundError()
    if offer.status != "pending" or request.status != "open":
        raise DomainError("OFFER_NOT_PENDING", "This offer is no longer available.")
    if _blocked(db, borrower.id, offer.owner_id):
        raise DomainError("BLOCKED", "This interaction is unavailable.")
    offer.status = "accepted"
    for other in db.scalars(select(Offer).where(Offer.request_id == request.id, Offer.id != offer.id, Offer.status == "pending")):
        other.status = "declined"
    request.status = "matched"
    loan = Loan(
        request_id=request.id,
        offer_id=offer.id,
        item_id=offer.item_id,
        lender_id=offer.owner_id,
        borrower_id=borrower.id,
        spot_id=request.preferred_spot_id,
        scheduled_start=as_utc(request.needed_from),
        due_at=as_utc(request.needed_until),
        agreement_version=get_settings().agreement_version,
    )
    db.add(loan)
    db.flush()
    if offer.item_id:
        item = db.get(Item, offer.item_id)
        if item:
            item.is_available = False
    db.add(LoanEvent(loan_id=loan.id, actor_id=borrower.id, type="loan_created", payload={"offer_id": offer.id}))
    db.add(Notification(user_id=offer.owner_id, type="offer_accepted", title="Offer accepted", body="Your offer was accepted. Agree on the loan details.", data={"loan_id": loan.id}))
    db.commit()
    db.refresh(loan)
    return loan


def decline_offer(db: Session, offer: Offer, user: User) -> Offer:
    request = db.get(BorrowRequest, offer.request_id)
    if request is None or request.requester_id != user.id:
        raise NotFoundError()
    if offer.status != "pending":
        raise DomainError("OFFER_NOT_PENDING", "This offer is no longer pending.")
    offer.status = "declined"
    db.commit()
    return offer


def withdraw_offer(db: Session, offer: Offer, user: User) -> Offer:
    if offer.owner_id != user.id:
        raise NotFoundError()
    if offer.status != "pending":
        raise DomainError("OFFER_NOT_PENDING", "This offer is no longer pending.")
    offer.status = "withdrawn"
    db.commit()
    return offer


CONTACT_PATTERN = re.compile(r"(?:[\w.+-]+@[\w-]+\.[\w.-]+)|(?:\+?\d[\d\s().-]{7,}\d)")


def mask_contacts(body: str) -> tuple[str, bool]:
    masked = CONTACT_PATTERN.sub("[contact hidden]", body)
    return masked, masked != body


def add_message(db: Session, offer: Offer, user: User, body: str) -> Message:
    request = db.get(BorrowRequest, offer.request_id)
    if request is None or user.id not in {offer.owner_id, request.requester_id}:
        raise NotFoundError()
    if _blocked(db, user.id, offer.owner_id if user.id == request.requester_id else request.requester_id):
        raise DomainError("BLOCKED", "This interaction is unavailable.")
    clean, masked = mask_contacts(body) if offer.status != "accepted" else (body.strip(), False)
    message = Message(offer_id=offer.id, sender_id=user.id, body=clean, masked=masked)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def list_messages(db: Session, offer: Offer, user: User) -> list[Message]:
    get_offer_for_party(db, offer.id, user)
    return list(db.scalars(select(Message).where(Message.offer_id == offer.id).order_by(Message.created_at)))

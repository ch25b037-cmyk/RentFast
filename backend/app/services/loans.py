"""Loan lifecycle, agreement and two-person code services."""

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import as_utc, now_utc
from app.core.config import get_settings
from app.core.errors import DomainError, NotFoundError
from app.core.security import compare_value, generate_numeric_code, hash_value
from app.models.domain import Loan, LoanCode, LoanEvent, MeetupSpot
from app.models.user import User
from app.services.loan_state import transition


def get_loan(db: Session, loan_id: str, user: User) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None or (user.role != "admin" and user.id not in {loan.borrower_id, loan.lender_id}):
        raise NotFoundError()
    return loan


def list_loans(db: Session, user: User, status: str | None, role: str | None) -> list[Loan]:
    from sqlalchemy import or_, select

    query = select(Loan).where(or_(Loan.borrower_id == user.id, Loan.lender_id == user.id))
    if status:
        query = query.where(Loan.status == status)
    if role == "borrower":
        query = query.where(Loan.borrower_id == user.id)
    if role == "lender":
        query = query.where(Loan.lender_id == user.id)
    return list(db.scalars(query.order_by(Loan.created_at.desc())))


def events(db: Session, loan_id: str) -> list[LoanEvent]:
    return list(db.scalars(select(LoanEvent).where(LoanEvent.loan_id == loan_id).order_by(LoanEvent.created_at)))


def agree(db: Session, loan: Loan, user: User, version: int) -> Loan:
    if loan.status != "pending_handover":
        raise DomainError("LOAN_INVALID_STATE", "The agreement can only be accepted before handover.")
    if version != get_settings().agreement_version:
        raise DomainError("AGREEMENT_REQUIRED", "This agreement version is no longer current.")
    if user.id == loan.borrower_id:
        loan.borrower_agreed_at = now_utc()
    elif user.id == loan.lender_id:
        loan.lender_agreed_at = now_utc()
    else:
        raise NotFoundError()
    db.add(LoanEvent(loan_id=loan.id, actor_id=user.id, type="agreement_accepted", payload={"version": version}))
    db.commit()
    db.refresh(loan)
    return loan


def set_spot(db: Session, loan: Loan, user: User, spot_id: str, scheduled_start) -> Loan:
    if loan.status != "pending_handover" or user.id not in {loan.borrower_id, loan.lender_id}:
        raise DomainError("LOAN_INVALID_STATE", "The meetup can only be set before handover.")
    spot = db.scalar(select(MeetupSpot).where(MeetupSpot.id == spot_id, MeetupSpot.is_active.is_(True)))
    if spot is None:
        raise DomainError("VALIDATION_ERROR", "Choose an active campus meetup spot.")
    if as_utc(scheduled_start) < now_utc():
        raise DomainError("VALIDATION_ERROR", "Meetup time must be in the future.")
    loan.spot_id = spot.id
    loan.scheduled_start = as_utc(scheduled_start)
    db.add(LoanEvent(loan_id=loan.id, actor_id=user.id, type="meetup_scheduled", payload={"spot_id": spot.id}))
    db.commit()
    db.refresh(loan)
    return loan


def _code_roles(loan: Loan, purpose: str) -> tuple[str, str, str]:
    if purpose == "handover":
        return loan.borrower_id, loan.lender_id, "pending_handover"
    return loan.lender_id, loan.borrower_id, "active"


def issue_code(db: Session, loan: Loan, user: User, purpose: str) -> tuple[str, LoanCode]:
    receiver, _, required_state = _code_roles(loan, purpose)
    if user.id != receiver:
        raise DomainError("FORBIDDEN", "Only the receiver can show this code.")
    if loan.status != required_state and not (purpose == "return" and loan.status == "overdue"):
        raise DomainError("LOAN_INVALID_STATE", "This code is not available in the current loan state.")
    if not loan.borrower_agreed_at or not loan.lender_agreed_at or not loan.spot_id:
        raise DomainError("AGREEMENT_REQUIRED", "Both parties must agree and choose a meetup spot first.")
    for old in db.scalars(select(LoanCode).where(LoanCode.loan_id == loan.id, LoanCode.purpose == purpose, LoanCode.consumed_at.is_(None))):
        old.consumed_at = now_utc()
    code = generate_numeric_code()
    record = LoanCode(loan_id=loan.id, purpose=purpose, code_hash=hash_value(code), shown_to_id=receiver, expires_at=now_utc() + timedelta(minutes=get_settings().handover_code_ttl_minutes))
    db.add(record)
    db.add(LoanEvent(loan_id=loan.id, actor_id=user.id, type=f"{purpose}_code_issued", payload={"shown_to_id": receiver}))
    db.commit()
    db.refresh(record)
    return code, record


def confirm_code(db: Session, loan: Loan, user: User, purpose: str, code: str) -> Loan:
    receiver, giver, _ = _code_roles(loan, purpose)
    if user.id != giver:
        raise DomainError("FORBIDDEN", "Only the giver can enter this code.")
    record = db.scalar(select(LoanCode).where(LoanCode.loan_id == loan.id, LoanCode.purpose == purpose, LoanCode.consumed_at.is_(None)).order_by(LoanCode.created_at.desc()))
    if record is None or record.shown_to_id != receiver:
        raise DomainError("CODE_INVALID", "That code is not valid for this loan.")
    if record.attempts >= get_settings().code_max_attempts:
        raise DomainError("CODE_LOCKED", "Too many attempts. Generate a new code.")
    if as_utc(record.expires_at) < now_utc():
        raise DomainError("CODE_EXPIRED", "That code has expired.")
    if not compare_value(code, record.code_hash):
        record.attempts += 1
        db.commit()
        if record.attempts >= get_settings().code_max_attempts:
            raise DomainError("CODE_LOCKED", "Too many attempts. Generate a new code.")
        raise DomainError("CODE_INVALID", "That code is not valid.")
    record.consumed_at = now_utc()
    target = "active" if purpose == "handover" else "returned"
    transition(loan, target, user.id, {"purpose": purpose}, db)
    db.commit()
    db.refresh(loan)
    return loan


def cancel_loan(db: Session, loan: Loan, user: User) -> Loan:
    if user.id not in {loan.borrower_id, loan.lender_id}:
        raise NotFoundError()
    transition(loan, "cancelled", user.id, {}, db)
    db.commit()
    return loan


def dispute_loan(db: Session, loan: Loan, user: User, reason: str, details: str) -> Loan:
    if user.id not in {loan.borrower_id, loan.lender_id}:
        raise NotFoundError()
    transition(loan, "disputed", user.id, {"reason": reason, "details": details}, db)
    db.commit()
    return loan


def return_claim(db: Session, loan: Loan, user: User) -> Loan:
    if user.id != loan.borrower_id or loan.status not in {"active", "overdue"}:
        raise DomainError("LOAN_INVALID_STATE", "A return claim is not available for this loan.")
    db.add(LoanEvent(loan_id=loan.id, actor_id=user.id, type="return_claimed", payload={"auto_accept_at": (now_utc() + timedelta(hours=get_settings().return_claim_auto_accept_hours)).isoformat()}))
    db.commit()
    return loan


def auto_accept_return_claims(db: Session, at=None) -> int:
    """Complete borrower return claims whose 24-hour acceptance window elapsed."""
    at = at or now_utc()
    loans = list(db.scalars(select(Loan).where(Loan.status.in_(["active", "overdue"]))))
    changed = 0
    for loan in loans:
        claims = list(
            db.scalars(
                select(LoanEvent)
                .where(LoanEvent.loan_id == loan.id, LoanEvent.type == "return_claimed")
                .order_by(LoanEvent.created_at.desc())
            )
        )
        if not claims:
            continue
        payload = claims[0].payload or {}
        auto_accept_at = payload.get("auto_accept_at")
        if not auto_accept_at:
            continue
        due = datetime.fromisoformat(auto_accept_at)
        if as_utc(due) <= at:
            transition(loan, "returned", None, {"reason": "return_claim_auto_accepted"}, db)
            changed += 1
    if changed:
        db.commit()
    return changed

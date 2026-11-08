"""Profile and trust tier service."""

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import DomainError, NotFoundError
from app.models.domain import Loan
from app.models.user import User


def trust_tier(score: int) -> str:
    settings = get_settings()
    if score < settings.trust_tier_restricted_below:
        return "Restricted"
    if score >= settings.trust_tier_trusted_from:
        return "Trusted"
    return "Member"


def get_current(db: Session, user_id: str) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise NotFoundError()
    if user.status != "active":
        raise DomainError("ACCOUNT_SUSPENDED", "This account is not active.")
    return user


def update_profile(db: Session, user: User, values: dict) -> User:
    for field, value in values.items():
        if value is not None:
            setattr(user, "avatar_url" if field == "avatar" else field, str(value))
    db.commit()
    db.refresh(user)
    return user


def delete_account(db: Session, user: User) -> None:
    active = db.scalar(select(Loan).where(or_(Loan.borrower_id == user.id, Loan.lender_id == user.id), Loan.status.in_(["pending_handover", "active", "overdue", "disputed"])))
    if active:
        raise DomainError("CONFLICT", "Finish or resolve active loans before deleting your account.")
    user.status = "deleted"
    user.email = f"deleted+{user.id}@redacted.invalid"
    user.display_name = "Deleted student"
    user.department = None
    user.hostel = None
    user.avatar_url = None
    db.commit()

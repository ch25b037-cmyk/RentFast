"""Trust, review, report and block services."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import as_utc, now_utc
from app.core.config import get_settings
from app.core.errors import DomainError, NotFoundError
from app.models.domain import Block, BorrowRequest, Loan, Report, Review
from app.models.user import User
from app.services.loan_state import transition


def adjust_trust(user: User, change: int) -> None:
    user.trust_score = max(0, min(100, user.trust_score + change))


def create_review(db: Session, loan: Loan, user: User, values: dict) -> Review:
    if loan.status != "returned" or user.id not in {loan.borrower_id, loan.lender_id}:
        raise DomainError("LOAN_INVALID_STATE", "Reviews are available after a return.")
    reviewee_id = loan.lender_id if user.id == loan.borrower_id else loan.borrower_id
    if db.scalar(select(Review).where(Review.loan_id == loan.id, Review.reviewer_id == user.id)):
        raise DomainError("CONFLICT", "You already reviewed this loan.")
    review = Review(loan_id=loan.id, reviewer_id=user.id, reviewee_id=reviewee_id, **values)
    db.add(review)
    reviewee = db.get(User, reviewee_id)
    if reviewee:
        adjust_trust(reviewee, (values["rating"] - 3) * 2)
    if db.scalar(select(Review).where(Review.loan_id == loan.id, Review.reviewer_id != user.id)):
        transition(loan, "closed", user.id, {"reason": "both_reviews"}, db)
        borrower = db.get(User, loan.borrower_id)
        if borrower:
            borrower.completed_loans += 1
        request = db.get(BorrowRequest, loan.request_id)
        if request:
            request.status = "fulfilled"
    db.commit()
    db.refresh(review)
    return review


def sweep_overdue(db: Session, at=None) -> int:
    at = at or now_utc()
    loans = list(db.scalars(select(Loan).where(Loan.status == "active")))
    changed = 0
    for loan in loans:
        if as_utc(loan.due_at) < at:
            transition(loan, "overdue", None, {"due_at": loan.due_at.isoformat()}, db)
            if not loan.late_penalty_applied:
                borrower = db.get(User, loan.borrower_id)
                if borrower:
                    adjust_trust(borrower, get_settings().trust_late)
                    borrower.late_returns += 1
                loan.late_penalty_applied = True
            changed += 1
    db.commit()
    return changed


def create_report(db: Session, reporter: User, values: dict) -> Report:
    if not any(values.get(key) for key in ("target_user_id", "target_loan_id", "target_message_id")):
        raise DomainError("VALIDATION_ERROR", "A report needs a target.")
    report = Report(reporter_id=reporter.id, **values)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def block_user(db: Session, user: User, blocked_id: str) -> Block:
    if user.id == blocked_id or db.get(User, blocked_id) is None:
        raise NotFoundError()
    if db.scalar(select(Block).where(Block.blocker_id == user.id, Block.blocked_id == blocked_id)):
        raise DomainError("CONFLICT", "This user is already blocked.")
    block = Block(blocker_id=user.id, blocked_id=blocked_id)
    db.add(block)
    db.commit()
    db.refresh(block)
    return block


def unblock_user(db: Session, user: User, blocked_id: str) -> None:
    block = db.scalar(select(Block).where(Block.blocker_id == user.id, Block.blocked_id == blocked_id))
    if block:
        db.delete(block)
        db.commit()


def list_blocks(db: Session, user: User) -> list[Block]:
    return list(db.scalars(select(Block).where(Block.blocker_id == user.id).order_by(Block.created_at.desc())))

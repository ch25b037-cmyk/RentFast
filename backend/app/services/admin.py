"""Admin moderation and dispute services."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import now_utc
from app.core.errors import DomainError, NotFoundError
from app.models.domain import AuditLog, Loan, MeetupSpot, Report
from app.models.user import User
from app.services.loan_state import transition
from app.services.safety import adjust_trust


def audit(db: Session, actor_id: str | None, action: str, entity_type: str, entity_id: str, metadata: dict) -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, entity_type=entity_type, entity_id=entity_id, metadata_json=metadata))


def list_reports(db: Session, status: str | None) -> list[Report]:
    query = select(Report)
    if status:
        query = query.where(Report.status == status)
    return list(db.scalars(query.order_by(Report.created_at)))


def resolve_report(db: Session, admin: User, report_id: str, action: str, note: str) -> Report:
    report = db.get(Report, report_id)
    if report is None:
        raise NotFoundError()
    if report.status in {"actioned", "dismissed"}:
        raise DomainError("CONFLICT", "This report is already resolved.")
    report.status = "dismissed" if action == "dismiss" else "actioned"
    report.resolved_by = admin.id
    report.resolved_at = now_utc()
    if action == "suspend" and report.target_user_id:
        target = db.get(User, report.target_user_id)
        if target:
            target.status = "suspended"
            adjust_trust(target, -15)
    audit(db, admin.id, f"report_{action}", "report", report.id, {"note": note})
    db.commit()
    db.refresh(report)
    return report


def list_disputes(db: Session) -> list[Loan]:
    return list(db.scalars(select(Loan).where(Loan.status == "disputed").order_by(Loan.created_at)))


def resolve_dispute(db: Session, admin: User, loan_id: str, outcome: str, note: str) -> Loan:
    loan = db.get(Loan, loan_id)
    if loan is None or loan.status != "disputed":
        raise NotFoundError()
    if outcome == "borrower_wins":
        adjust_trust(db.get(User, loan.borrower_id), 5)
        adjust_trust(db.get(User, loan.lender_id), -25)
    elif outcome == "lender_wins":
        adjust_trust(db.get(User, loan.lender_id), 5)
        adjust_trust(db.get(User, loan.borrower_id), -25)
    transition(loan, "closed", admin.id, {"outcome": outcome, "note": note}, db)
    audit(db, admin.id, "dispute_resolved", "loan", loan.id, {"outcome": outcome, "note": note})
    db.commit()
    db.refresh(loan)
    return loan


def set_user_status(db: Session, admin: User, user_id: str, status: str) -> User:
    target = db.get(User, user_id)
    if target is None:
        raise NotFoundError()
    if target.id == admin.id:
        raise DomainError("FORBIDDEN", "You cannot suspend your own admin account.")
    target.status = status
    audit(db, admin.id, f"user_{status}", "user", target.id, {})
    db.commit()
    return target


def list_audit_logs(db: Session, entity: str | None) -> list[AuditLog]:
    query = select(AuditLog)
    if entity:
        query = query.where(AuditLog.entity_type == entity)
    return list(db.scalars(query.order_by(AuditLog.created_at.desc())))


def list_spots(db: Session) -> list[MeetupSpot]:
    return list(db.scalars(select(MeetupSpot).order_by(MeetupSpot.name)))


def create_spot(db: Session, admin: User, values: dict) -> MeetupSpot:
    spot = MeetupSpot(**values)
    db.add(spot)
    audit(db, admin.id, "meetup_spot_created", "meetup_spot", spot.id, {})
    db.commit()
    db.refresh(spot)
    return spot


def update_spot(db: Session, admin: User, spot_id: str, values: dict) -> MeetupSpot:
    spot = db.get(MeetupSpot, spot_id)
    if spot is None:
        raise NotFoundError()
    for key, value in values.items():
        if value is not None:
            setattr(spot, key, value)
    audit(db, admin.id, "meetup_spot_updated", "meetup_spot", spot.id, {})
    db.commit()
    db.refresh(spot)
    return spot

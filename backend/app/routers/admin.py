"""Admin-only moderation routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import require_admin
from app.models.user import User
from app.schemas.admin import (
    AuditLogRead,
    DisputeResolve,
    MeetupSpotCreate,
    MeetupSpotUpdate,
    ReportResolve,
)
from app.schemas.loans import LoanRead
from app.schemas.safety import ReportRead
from app.services.admin import (
    create_spot,
    list_audit_logs,
    list_disputes,
    list_reports,
    list_spots,
    resolve_dispute,
    resolve_report,
    set_user_status,
    update_spot,
)
from app.services.loans import events

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/reports", response_model=list[ReportRead])
def reports(status: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list:
    return list_reports(db, status)


@router.post("/reports/{report_id}/resolve", response_model=ReportRead)
def resolve_report_route(report_id: str, payload: ReportResolve, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> ReportRead:
    return resolve_report(db, admin, report_id, payload.action, payload.note)


@router.get("/disputes", response_model=list[LoanRead])
def disputes(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[LoanRead]:
    return [LoanRead.model_validate({**loan.__dict__, "events": events(db, loan.id)}) for loan in list_disputes(db)]


@router.post("/disputes/{loan_id}/resolve", response_model=LoanRead)
def resolve_dispute_route(loan_id: str, payload: DisputeResolve, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> LoanRead:
    loan = resolve_dispute(db, admin, loan_id, payload.outcome, payload.note)
    return LoanRead.model_validate({**loan.__dict__, "events": events(db, loan.id)})


@router.post("/users/{user_id}/suspend", response_model=dict)
def suspend(user_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict[str, str]:
    return {"status": set_user_status(db, admin, user_id, "suspended").status}


@router.post("/users/{user_id}/unsuspend", response_model=dict)
def unsuspend(user_id: str, db: Session = Depends(get_db), admin: User = Depends(require_admin)) -> dict[str, str]:
    return {"status": set_user_status(db, admin, user_id, "active").status}


@router.get("/meetup-spots")
def spots(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list:
    return list_spots(db)


@router.post("/meetup-spots")
def create_meetup_spot(payload: MeetupSpotCreate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return create_spot(db, admin, payload.model_dump())


@router.patch("/meetup-spots/{spot_id}")
def update_meetup_spot(spot_id: str, payload: MeetupSpotUpdate, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    return update_spot(db, admin, spot_id, payload.model_dump(exclude_unset=True))


@router.get("/audit-log", response_model=list[AuditLogRead])
def audit_log(entity: str | None = None, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list:
    return list_audit_logs(db, entity)

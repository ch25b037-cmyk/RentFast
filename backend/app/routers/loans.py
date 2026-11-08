"""Loan lifecycle routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.domain import Loan
from app.models.user import User
from app.schemas.loans import (
    AgreementInput,
    CodeInput,
    CodeRead,
    DisputeInput,
    LoanPage,
    LoanRead,
    SpotInput,
)
from app.schemas.safety import ReviewCreate, ReviewRead
from app.services.loans import (
    agree,
    cancel_loan,
    confirm_code,
    dispute_loan,
    events,
    get_loan,
    issue_code,
    return_claim,
    set_spot,
)
from app.services.loans import (
    list_loans as list_loans_service,
)
from app.services.safety import create_review

router = APIRouter(prefix="/loans", tags=["loans"])


def read(db: Session, loan: Loan) -> LoanRead:
    return LoanRead.model_validate({**loan.__dict__, "events": events(db, loan.id)})


@router.get("", response_model=LoanPage)
def list_loans(status: str | None = None, role: str | None = None, limit: int = 20, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanPage:
    values = list_loans_service(db, user, status, role)
    limit, offset = min(max(limit, 1), 50), max(offset, 0)
    return LoanPage(items=[read(db, item) for item in values[offset : offset + limit]], total=len(values), limit=limit, offset=offset)


@router.get("/{loan_id}", response_model=LoanRead)
def detail(loan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, get_loan(db, loan_id, user))


@router.post("/{loan_id}/agree", response_model=LoanRead)
def agreement(loan_id: str, payload: AgreementInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, agree(db, get_loan(db, loan_id, user), user, payload.agreement_version))


@router.post("/{loan_id}/spot", response_model=LoanRead)
def spot(loan_id: str, payload: SpotInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, set_spot(db, get_loan(db, loan_id, user), user, payload.spot_id, payload.scheduled_start))


@router.post("/{loan_id}/codes/handover", response_model=CodeRead)
def handover_code(loan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> CodeRead:
    code, record = issue_code(db, get_loan(db, loan_id, user), user, "handover")
    return CodeRead(code=code, purpose="handover", expires_at=record.expires_at)


@router.post("/{loan_id}/confirm-handover", response_model=LoanRead)
def handover_confirm(loan_id: str, payload: CodeInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, confirm_code(db, get_loan(db, loan_id, user), user, "handover", payload.code))


@router.post("/{loan_id}/codes/return", response_model=CodeRead)
def return_code(loan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> CodeRead:
    code, record = issue_code(db, get_loan(db, loan_id, user), user, "return")
    return CodeRead(code=code, purpose="return", expires_at=record.expires_at)


@router.post("/{loan_id}/confirm-return", response_model=LoanRead)
def return_confirm(loan_id: str, payload: CodeInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, confirm_code(db, get_loan(db, loan_id, user), user, "return", payload.code))


@router.post("/{loan_id}/return-claim", response_model=LoanRead)
def claim(loan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, return_claim(db, get_loan(db, loan_id, user), user))


@router.post("/{loan_id}/cancel", response_model=LoanRead)
def cancel(loan_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, cancel_loan(db, get_loan(db, loan_id, user), user))


@router.post("/{loan_id}/dispute", response_model=LoanRead)
def dispute(loan_id: str, payload: DisputeInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> LoanRead:
    return read(db, dispute_loan(db, get_loan(db, loan_id, user), user, payload.reason, payload.details))


@router.post("/{loan_id}/reviews", response_model=ReviewRead)
def review(loan_id: str, payload: ReviewCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> ReviewRead:
    created = create_review(db, get_loan(db, loan_id, user), user, payload.model_dump())
    return ReviewRead.model_validate(created, from_attributes=True)

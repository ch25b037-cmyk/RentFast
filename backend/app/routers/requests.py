"""Borrow request routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.requests import RequestCreate, RequestPage, RequestRead, RequestUpdate
from app.services.requests import (
    cancel_request,
    create_request,
    get_request,
    list_requests,
    loan_id_for_request,
    update_request,
)

router = APIRouter(prefix="/requests", tags=["requests"])


def read(db: Session, request) -> RequestRead:
    return RequestRead.model_validate({**request.as_dict(), "loan_id": loan_id_for_request(db, request.id)})


@router.get("", response_model=RequestPage)
def feed(status: str = "open", category: str | None = None, q: str | None = None, urgent: bool = False, mine: bool = False, limit: int = 20, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RequestPage:
    limit = min(max(limit, 1), 50)
    values, total = list_requests(db, user, limit, max(offset, 0), status, category, q, mine, urgent)
    return RequestPage(items=[read(db, item) for item in values], total=total, limit=limit, offset=max(offset, 0))


@router.post("", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create(payload: RequestCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RequestRead:
    return read(db, create_request(db, user, payload.model_dump()))


@router.get("/{request_id}", response_model=RequestRead)
def detail(request_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RequestRead:
    return read(db, get_request(db, user, request_id))


@router.patch("/{request_id}", response_model=RequestRead)
def edit(request_id: str, payload: RequestUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RequestRead:
    request = get_request(db, user, request_id)
    if request.requester_id != user.id:
        from app.core.errors import NotFoundError
        raise NotFoundError()
    return read(db, update_request(db, request, payload.model_dump(exclude_unset=True)))


@router.post("/{request_id}/cancel", response_model=RequestRead)
def cancel(request_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> RequestRead:
    request = get_request(db, user, request_id)
    if request.requester_id != user.id:
        from app.core.errors import NotFoundError
        raise NotFoundError()
    return read(db, cancel_request(db, request))

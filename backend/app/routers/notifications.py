"""Polling-based notification routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.deps import get_current_user
from app.models.domain import Notification
from app.models.user import User
from app.schemas.notifications import NotificationPage, NotificationRead
from app.services.notifications import list_notifications as list_notification_service
from app.services.notifications import mark_all_read as mark_all_read_service
from app.services.notifications import mark_read as mark_read_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationPage)
def list_notifications(unread: bool = False, limit: int = 20, offset: int = 0, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> NotificationPage:
    values, total, limit, offset = list_notification_service(db, user, unread, limit, offset)
    return NotificationPage(items=values, total=total, limit=limit, offset=offset)


@router.post("/{notification_id}/read", response_model=NotificationRead)
def mark_read(notification_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Notification:
    return mark_read_service(db, user, notification_id)


@router.post("/read-all", response_model=dict)
def mark_all_read(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> dict[str, int]:
    return {"updated": mark_all_read_service(db, user)}

"""Notification persistence and read-state services."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.clock import now_utc
from app.core.errors import NotFoundError
from app.models.domain import Notification
from app.models.user import User


def list_notifications(db: Session, user: User, unread: bool, limit: int, offset: int) -> tuple[list[Notification], int, int, int]:
    query = select(Notification).where(Notification.user_id == user.id)
    if unread:
        query = query.where(Notification.read_at.is_(None))
    values = list(db.scalars(query.order_by(Notification.created_at.desc())))
    limit = min(max(limit, 1), 50)
    offset = max(offset, 0)
    return values[offset : offset + limit], len(values), limit, offset


def mark_read(db: Session, user: User, notification_id: str) -> Notification:
    notification = db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user.id))
    if notification is None:
        raise NotFoundError()
    notification.read_at = now_utc()
    db.commit()
    db.refresh(notification)
    return notification


def mark_all_read(db: Session, user: User) -> int:
    values = list(db.scalars(select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))))
    for notification in values:
        notification.read_at = now_utc()
    db.commit()
    return len(values)

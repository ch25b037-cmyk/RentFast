"""FastAPI dependencies shared by routers."""

from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.models.user import User
from app.services.auth import user_id_from_access_token
from app.services.user import get_current

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise DomainError("UNAUTHENTICATED", "Sign in to continue.")
    return get_current(db, user_id_from_access_token(credentials.credentials))


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "admin":
        raise DomainError("FORBIDDEN", "Admin access is required.")
    return user


def rate_limit_auth(request_key: str) -> None:
    enforce_rate_limit(f"auth:{request_key}", get_settings().rate_limit_auth_per_min)


def rate_limit_write(user: User = Depends(get_current_user)) -> User:
    enforce_rate_limit(f"write:{user.id}", get_settings().rate_limit_write_per_min)
    return user

__all__ = ["Generator", "Session", "get_db", "get_current_user", "require_admin", "rate_limit_write"]

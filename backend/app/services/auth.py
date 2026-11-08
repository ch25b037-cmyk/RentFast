"""Passwordless authentication business rules."""

from datetime import timedelta

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.clock import as_utc, now_utc
from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.security import (
    compare_value,
    create_access_token,
    decode_access_token,
    generate_numeric_code,
    hash_value,
    new_refresh_token,
)
from app.models.user import EmailOTP, RefreshToken, User


def _allowed_email(email: str) -> bool:
    domain = email.lower().split("@")[-1]
    return domain in get_settings().allowed_email_domains


def request_otp(db: Session, email: str, ip: str) -> str:
    email = email.lower().strip()
    if not _allowed_email(email):
        raise DomainError("EMAIL_DOMAIN_NOT_ALLOWED", "Use your college email address.")
    code = generate_numeric_code()
    otp = EmailOTP(
        email=email,
        code_hash=hash_value(code),
        expires_at=now_utc() + timedelta(minutes=get_settings().otp_ttl_minutes),
        ip_hash=hash_value(ip),
    )
    db.add(otp)
    db.commit()
    return code


def verify_otp(db: Session, email: str, code: str, ip: str, user_agent: str) -> tuple[str, User, str]:
    email = email.lower().strip()
    otp = db.scalar(select(EmailOTP).where(EmailOTP.email == email).order_by(EmailOTP.created_at.desc()))
    if otp is None:
        raise DomainError("OTP_INVALID", "That code is not valid.")
    if otp.consumed_at is not None:
        raise DomainError("OTP_INVALID", "That code has already been used.")
    if as_utc(otp.expires_at) < now_utc():
        raise DomainError("OTP_EXPIRED", "That code has expired.")
    if otp.attempts >= get_settings().otp_max_attempts:
        raise DomainError("OTP_LOCKED", "Too many attempts. Request a new code.")
    if not compare_value(code, otp.code_hash):
        otp.attempts += 1
        db.commit()
        if otp.attempts >= get_settings().otp_max_attempts:
            raise DomainError("OTP_LOCKED", "Too many attempts. Request a new code.")
        raise DomainError("OTP_INVALID", "That code is not valid.")
    otp.consumed_at = now_utc()
    user = db.scalar(select(User).where(User.email == email))
    if user is None:
        user = User(email=email, email_verified_at=now_utc(), trust_score=get_settings().trust_start)
        if email in get_settings().admin_emails:
            user.role = "admin"
        db.add(user)
        db.flush()
    elif user.status == "deleted":
        raise DomainError("FORBIDDEN", "This account is deleted.")
    user.email_verified_at = now_utc()
    user.last_seen_at = now_utc()
    raw_refresh, family_id = new_refresh_token()
    refresh = RefreshToken(
        user_id=user.id,
        token_hash=hash_value(raw_refresh),
        family_id=family_id,
        expires_at=now_utc() + timedelta(days=get_settings().refresh_token_expire_days),
        user_agent=user_agent[:500],
    )
    db.add(refresh)
    db.commit()
    return create_access_token(user.id), user, raw_refresh


def refresh_access_token(db: Session, raw_token: str) -> tuple[str, str]:
    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_value(raw_token)))
    if token is None or as_utc(token.expires_at) < now_utc():
        raise DomainError("UNAUTHENTICATED", "Refresh token is invalid or expired.")
    if token.revoked_at is not None:
        db.execute(update(RefreshToken).where(RefreshToken.family_id == token.family_id).values(revoked_at=now_utc()))
        db.commit()
        raise DomainError("UNAUTHENTICATED", "Refresh token reuse detected.")
    user = db.get(User, token.user_id)
    if user is None or user.status != "active":
        raise DomainError("ACCOUNT_SUSPENDED", "This account cannot sign in.")
    token.revoked_at = now_utc()
    raw_new, _ = new_refresh_token()
    replacement = RefreshToken(
        user_id=user.id,
        token_hash=hash_value(raw_new),
        family_id=token.family_id,
        expires_at=now_utc() + timedelta(days=get_settings().refresh_token_expire_days),
        user_agent=token.user_agent,
    )
    db.add(replacement)
    db.flush()
    token.replaced_by_id = replacement.id
    db.commit()
    return create_access_token(user.id), raw_new


def logout_refresh_token(db: Session, raw_token: str) -> None:
    from sqlalchemy import select

    token = db.scalar(select(RefreshToken).where(RefreshToken.token_hash == hash_value(raw_token)))
    if token:
        token.revoked_at = now_utc()
        db.commit()


def user_id_from_access_token(token: str) -> str:
    try:
        return decode_access_token(token)
    except Exception as exc:
        raise DomainError("UNAUTHENTICATED", "Sign in to continue.") from exc

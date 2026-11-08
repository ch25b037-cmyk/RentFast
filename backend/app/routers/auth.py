"""OTP authentication routes."""

from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.mail import deliver_otp
from app.core.rate_limit import enforce_rate_limit
from app.db.session import get_db
from app.schemas.auth import OTPRequest, OTPVerify, RefreshResponse, TokenResponse, UserResponse
from app.services.auth import logout_refresh_token, refresh_access_token, request_otp, verify_otp
from app.services.user import trust_tier

router = APIRouter(prefix="/auth", tags=["auth"])


def _user_response(user) -> UserResponse:
    return UserResponse.model_validate({**user.as_dict(), "trust_tier": trust_tier(user.trust_score)})


@router.post("/otp/request", status_code=status.HTTP_202_ACCEPTED)
def otp_request(payload: OTPRequest, request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    enforce_rate_limit(f"auth:{request.client.host if request.client else 'unknown'}", get_settings().rate_limit_auth_per_min)
    code = request_otp(db, str(payload.email), request.client.host if request.client else "unknown")
    request.app.state.last_otp = code
    deliver_otp(str(payload.email), code)
    return {"status": "accepted"}


@router.post("/otp/verify", response_model=TokenResponse)
def otp_verify(payload: OTPVerify, request: Request, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    access, user, refresh = verify_otp(
        db, str(payload.email), payload.code, request.client.host if request.client else "unknown", request.headers.get("user-agent", "")
    )
    settings = get_settings()
    response.set_cookie("refresh_token", refresh, httponly=True, secure=settings.cookie_secure, samesite=settings.cookie_samesite, max_age=settings.refresh_token_expire_days * 86400)
    return TokenResponse(access_token=access, user=_user_response(user))


@router.post("/refresh", response_model=RefreshResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_db)) -> RefreshResponse:
    raw = request.cookies.get("refresh_token")
    if not raw:
        raise DomainError("UNAUTHENTICATED", "Refresh token is missing.")
    access, replacement = refresh_access_token(db, raw)
    settings = get_settings()
    response.set_cookie("refresh_token", replacement, httponly=True, secure=settings.cookie_secure, samesite=settings.cookie_samesite, max_age=settings.refresh_token_expire_days * 86400)
    return RefreshResponse(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(request: Request, response: Response, db: Session = Depends(get_db)) -> None:
    raw = request.cookies.get("refresh_token")
    if raw:
        logout_refresh_token(db, raw)
    response.delete_cookie("refresh_token")

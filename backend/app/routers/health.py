"""Public health endpoint."""

from fastapi import APIRouter

from app.core.clock import now_utc
from app.core.config import get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok", version=get_settings().app_name, time=now_utc())

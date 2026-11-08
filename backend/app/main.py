"""CampusLend FastAPI application factory."""

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.core.errors import DomainError
from app.core.logging import configure_logging
from app.core.rate_limit import enforce_rate_limit
from app.jobs.scheduler import build_scheduler
from app.routers import admin, auth, catalog, health, loans, notifications, offers, safety, users
from app.routers import requests as requests_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        scheduler = build_scheduler()
        scheduler.start()
        application.state.scheduler = scheduler
        try:
            yield
        finally:
            if scheduler.running:
                scheduler.shutdown(wait=False)

    application = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    application.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )

    @application.middleware("http")
    async def request_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        if request.url.path.startswith(settings.api_prefix):
            if request.url.path.startswith(f"{settings.api_prefix}/auth"):
                bucket, limit = "auth", settings.rate_limit_auth_per_min
            elif request.method in {"POST", "PUT", "PATCH", "DELETE"}:
                bucket, limit = "write", settings.rate_limit_write_per_min
            else:
                bucket, limit = "read", settings.rate_limit_read_per_min
            try:
                enforce_rate_limit(f"{bucket}:{request.client.host if request.client else 'unknown'}", limit)
            except DomainError as exc:
                return JSONResponse(
                    status_code=429,
                    headers={"X-Request-ID": request_id, "Retry-After": "60"},
                    content={"error": {"code": exc.code, "message": exc.message, "details": {}, "request_id": request_id}},
                )
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @application.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(
            status_code=404 if exc.code == "NOT_FOUND" else 400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                    "request_id": getattr(request.state, "request_id", str(uuid4())),
                }
            },
        )

    application.include_router(health.router, prefix=settings.api_prefix)
    application.include_router(auth.router, prefix=settings.api_prefix)
    application.include_router(users.router, prefix=settings.api_prefix)
    application.include_router(catalog.router, prefix=settings.api_prefix)
    application.include_router(requests_router.router, prefix=settings.api_prefix)
    application.include_router(offers.router, prefix=settings.api_prefix)
    application.include_router(notifications.router, prefix=settings.api_prefix)
    application.include_router(loans.router, prefix=settings.api_prefix)
    application.include_router(safety.router, prefix=settings.api_prefix)
    application.include_router(admin.router, prefix=settings.api_prefix)
    return application


app = create_app()

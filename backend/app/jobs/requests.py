"""Request expiry job entrypoint."""

from app.db.session import SessionLocal
from app.services.requests import expire_requests


def run_expire_requests() -> int:
    with SessionLocal() as db:
        return expire_requests(db)

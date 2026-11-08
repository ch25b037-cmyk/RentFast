"""Scheduled overdue and reminder job entrypoints."""

from app.db.session import SessionLocal
from app.services.safety import sweep_overdue


def run_sweep_overdue() -> int:
    with SessionLocal() as db:
        return sweep_overdue(db)

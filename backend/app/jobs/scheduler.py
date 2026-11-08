"""Application scheduler wiring for lifecycle and safety jobs."""

from apscheduler.schedulers.background import BackgroundScheduler

from app.db.session import SessionLocal
from app.jobs.loans import run_sweep_overdue
from app.jobs.requests import run_expire_requests
from app.services.loans import auto_accept_return_claims


def run_auto_accept_returns() -> int:
    with SessionLocal() as db:
        return auto_accept_return_claims(db)


def build_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(run_expire_requests, "interval", minutes=5, id="expire_requests", replace_existing=True)
    scheduler.add_job(run_sweep_overdue, "interval", minutes=15, id="sweep_overdue", replace_existing=True)
    scheduler.add_job(run_auto_accept_returns, "interval", minutes=15, id="auto_accept_returns", replace_existing=True)
    return scheduler

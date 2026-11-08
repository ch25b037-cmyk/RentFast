"""Central clock helper so time-dependent tests can freeze time."""

from datetime import UTC, datetime


def now_utc() -> datetime:
    return datetime.now(UTC)


def as_utc(value: datetime) -> datetime:
    """Normalise SQLite's naive datetime values to the UTC comparison domain."""
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)

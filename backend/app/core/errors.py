"""Domain errors and the public error response shape."""

from typing import Any


class DomainError(Exception):
    def __init__(self, code: str, message: str, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or {}


class NotFoundError(DomainError):
    def __init__(self, message: str = "The requested resource was not found") -> None:
        super().__init__("NOT_FOUND", message)


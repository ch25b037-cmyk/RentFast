import os

import pytest

# Tests use synthetic example.edu identities and must not depend on a developer's local domain.
os.environ["ALLOWED_EMAIL_DOMAINS"] = "example.edu"

from app.core.rate_limit import _events


@pytest.fixture(autouse=True)
def reset_process_rate_limits() -> None:
    _events.clear()

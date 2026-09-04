import random
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

BASE_DELAY_SECONDS = 1.0
MAX_DELAY_SECONDS = 8.0

RETRYABLE_STATUSES = {408, 409, 429}
NEVER_RETRY_STATUSES = {400, 401, 403, 404, 422}


def is_retryable(status):
    if status is None:
        return True
    if status in NEVER_RETRY_STATUSES:
        return False
    if status in RETRYABLE_STATUSES:
        return True
    return status >= 500


def retry_after_seconds(headers) -> float | None:
    if not headers:
        return None
    value = headers.get("retry-after") or headers.get("Retry-After")
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        pass
    try:
        moment = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        return None
    if moment is None:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return max(0.0, (moment - datetime.now(timezone.utc)).total_seconds())


def backoff_delay(attempt: int) -> float:
    delay = min(BASE_DELAY_SECONDS * (2 ** (attempt - 1)), MAX_DELAY_SECONDS)
    return delay + random.uniform(0, 0.25 * delay)


def wait(attempt: int, headers=None):
    hinted = retry_after_seconds(headers)
    delay = hinted if hinted is not None else backoff_delay(attempt)
    time.sleep(min(delay, MAX_DELAY_SECONDS))
    return delay

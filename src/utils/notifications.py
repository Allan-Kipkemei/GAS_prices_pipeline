import logging
from typing import Iterable

logger = logging.getLogger(__name__)


def send_alert_email(subject: str, body: str, recipients: Iterable[str] | None = None) -> bool:
    """Placeholder notifier used by non-Airflow modules/tests."""
    logger.info(
        "send_alert_email called",
        extra={
            'subject': subject,
            'recipients': list(recipients or []),
        },
    )
    logger.debug(body)
    return True

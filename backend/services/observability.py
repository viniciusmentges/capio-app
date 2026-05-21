import json
import logging
from typing import Any, Dict

logger = logging.getLogger("services.metrics")


def log_event(event_name: str, **properties: Any) -> None:
    payload: Dict[str, Any] = {
        "event": event_name,
        "app": "capio",
        **properties,
    }
    logger.info(json.dumps(payload, default=str, ensure_ascii=False))


def capture_exception(error: Exception, **context: Any) -> None:
    try:
        import sentry_sdk
        sentry_sdk.capture_exception(error)
    except Exception:
        pass

    logger.exception(
        json.dumps({
            "event": "exception_captured",
            "app": "capio",
            "error_type": type(error).__name__,
            "error": str(error),
            **context,
        }, default=str, ensure_ascii=False)
    )

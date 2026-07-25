"""Safe, structured observability helpers for the public API."""

import json
import logging
from uuid import uuid4

from app.models.schemas import ChatResponse

logger = logging.getLogger(__name__)


def create_run_id() -> str:
    """Create an opaque identifier for correlating one chat request in logs."""

    return uuid4().hex


def log_chat_completed(
    *,
    run_id: str,
    duration_ms: float,
    response: ChatResponse,
) -> None:
    """Log safe chat metadata without recording user or model content."""

    _log_event(
        {
            "event": "chat_completed",
            "run_id": run_id,
            "duration_ms": duration_ms,
            "intent": response.intent,
            "mode": response.mode,
            "source_count": len(response.sources),
            "observation_count": len(response.observations),
            "anomaly_count": len(response.anomaly_flags),
            "warning_count": len(response.warnings),
            "status_code": 200,
        }
    )


def log_chat_failed(
    *,
    run_id: str,
    duration_ms: float,
    status_code: int,
    error_type: str,
) -> None:
    """Log safe failure metadata without provider or request details."""

    _log_event(
        {
            "event": "chat_failed",
            "run_id": run_id,
            "duration_ms": duration_ms,
            "status_code": status_code,
            "error_type": error_type,
        }
    )


def _log_event(event: dict[str, str | int | float]) -> None:
    logger.info("chat_event=%s", json.dumps(event, sort_keys=True))

"""Structured JSON logging with PII redaction.

The redaction list enforces `project-context.md` Abschnitt 6 Datenschutz:
no PII, no secrets, no raw coordinates in log output.
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Mapping
from typing import Any, Final

REDACTED_FIELDS: Final[frozenset[str]] = frozenset(
    {
        "password",
        "password_hash",
        "access_code",
        "access_code_hash",
        "secret_key",
        "session_cookie",
        "tomtom_api_key",
        "maptiler_api_key",
        "email",
        "coordinate_lat",
        "coordinate_lng",
    }
)
REDACTED_VALUE: Final[str] = "<redacted>"

# Attributes that the stdlib places on every LogRecord. Anything outside this
# set is treated as caller-supplied `extra=` data and subject to redaction.
_STANDARD_LOGRECORD_ATTRS: Final[frozenset[str]] = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "message",
        "module",
        "msecs",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "taskName",
        "thread",
        "threadName",
    }
)


def _redact(value: Any) -> Any:  # noqa: ANN401  # log extras are intentionally unbounded
    """Recursively replace values whose key is in REDACTED_FIELDS."""
    if isinstance(value, Mapping):
        return {
            key: REDACTED_VALUE if key in REDACTED_FIELDS else _redact(inner)
            for key, inner in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class JsonLogFormatter(logging.Formatter):
    """Render LogRecords as one JSON object per line."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key, value in record.__dict__.items():
            if key in _STANDARD_LOGRECORD_ATTRS:
                continue
            payload[key] = REDACTED_VALUE if key in REDACTED_FIELDS else _redact(value)
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str, ensure_ascii=False)


def configure_logging(level: str) -> None:
    """Replace root handlers with a single JSON stdout handler at the given level."""
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(JsonLogFormatter())
    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level.upper())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

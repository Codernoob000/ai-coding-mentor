import logging
import sys
import json
from datetime import datetime, UTC
from contextvars import ContextVar
from typing import Any, Dict
from app.core.config import settings

# ContextVar for request tracing
correlation_id: ContextVar[str] = ContextVar("correlation_id", default="system")

class GCPStructuredFormatter(logging.Formatter):
    """
    Formatter that outputs JSON formatted logs compatible with Google Cloud Logging.
    Includes automatic redaction for sensitive settings values.
    """
    LEVEL_MAP = {
        "DEBUG": "DEBUG",
        "INFO": "INFO",
        "WARNING": "WARNING",
        "ERROR": "ERROR",
        "CRITICAL": "CRITICAL",
    }
    
    # Values to redact from logs if they appear as strings
    REDACT_KEYS = {"GEMINI_API_KEY", "DATABASE_URL"}

    def _redact(self, data: Any) -> Any:
        """Recursively redacts sensitive values from log metadata."""
        if isinstance(data, dict):
            return {k: self._redact(v) for k, v in data.items()}
        if isinstance(data, str):
            # Check if any sensitive setting value is in the string
            for key in self.REDACT_KEYS:
                val = getattr(settings, key, None)
                if val and hasattr(val, "get_secret_value"):
                    val = val.get_secret_value()
                if val and str(val) in data:
                    return data.replace(str(val), "[REDACTED]")
        return data

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "severity": self.LEVEL_MAP.get(record.levelname, "DEFAULT"),
            "message": self._redact(record.getMessage()),
            "logging.googleapis.com/labels": {
                "request_id": correlation_id.get(),
                "environment": settings.ENVIRONMENT,
                "app": settings.APP_NAME,
            },
            "logging.googleapis.com/sourceLocation": {
                "file": record.pathname,
                "line": record.lineno,
                "function": record.funcName,
            },
            "module": record.module,
        }

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        standard_attrs = {
            "args", "asctime", "created", "exc_info", "exc_text", "filename",
            "funcName", "levelname", "levelno", "lineno", "module", "msecs",
            "message", "msg", "name", "pathname", "process", "processName",
            "relativeCreated", "stack_info", "thread", "threadName"
        }
        
        # Merge 'extra' attributes with redaction
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith("_"):
                log_entry[key] = self._redact(value)

        return json.dumps(log_entry)

def setup_logging():
    root_logger = logging.getLogger()
    root_logger.handlers = []
    
    # 1. Create a universal filter for correlation IDs
    class CorrelationFilter(logging.Filter):
        def filter(self, record):
            try:
                record.correlation_id = correlation_id.get()
            except (LookupError, NameError):
                record.correlation_id = "system"
            return True

    correlation_filter = CorrelationFilter()
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(correlation_filter) # Attach to handler directly
    
    if settings.ENVIRONMENT == "production":
        handler.setFormatter(GCPStructuredFormatter())
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [ID:%(correlation_id)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)

    root_logger.addHandler(handler)
    root_logger.setLevel(settings.LOG_LEVEL)

    # Ensure app logger also uses these settings
    logger = logging.getLogger("ai_mentor")
    return logger

logger = logging.getLogger("ai_mentor")

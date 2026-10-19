"""Logging configuration for RepoSense AI backend."""

import logging
import sys
from typing import Optional


class SensitiveDataFilter(logging.Filter):
    """Filter that masks sensitive tokens or keys in log messages."""

    SENSITIVE_KEYS = ("authorization", "token", "password", "secret", "api_key")

    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        for key in self.SENSITIVE_KEYS:
            if key in message.lower():
                # Redact if suspected
                record.msg = f"[REDACTED LOG RECORD - contains potential sensitive keyword: {key}]"
                record.args = ()
                break
        return True


def setup_logging(level: Optional[str] = "INFO") -> None:
    """Configure console logging with a standard format and sensitivity filter."""
    log_level = getattr(logging, level.upper(), logging.INFO) if level else logging.INFO

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

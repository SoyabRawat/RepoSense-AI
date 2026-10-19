"""Automated tests for configuration management and logging."""

import logging
from app.core.config import Settings
from app.core.logging import SensitiveDataFilter


def test_default_settings() -> None:
    """Verify default settings values for local development."""
    settings = Settings()
    assert settings.app_name == "RepoSense AI Backend"
    assert settings.app_env in ["development", "test"]
    assert "http://localhost:5173" in settings.cors_origins
    assert settings.api_port == 8000


def test_cors_origins_parsing() -> None:
    """Verify that comma-separated string input is properly parsed into a list."""
    settings = Settings(cors_origins="http://example.com,http://localhost:3000")
    assert settings.cors_origins == ["http://example.com", "http://localhost:3000"]


def test_sensitive_data_filter() -> None:
    """Verify that log filter redacts records containing sensitive keywords."""
    log_filter = SensitiveDataFilter()

    # Record with sensitive token
    record_leak = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Leaked api_key=xyz123",
        args=(),
        exc_info=None,
    )
    log_filter.filter(record_leak)
    assert "[REDACTED LOG RECORD" in record_leak.msg

    # Harmless record
    record_safe = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Service running normally",
        args=(),
        exc_info=None,
    )
    log_filter.filter(record_safe)
    assert record_safe.msg == "Service running normally"

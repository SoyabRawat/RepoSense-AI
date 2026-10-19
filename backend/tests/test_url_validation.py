"""Automated tests for GitHub URL validation, SSRF defense, and path safety."""

import pytest
from app.services.github_url import (
    InvalidRepositoryURLError,
    parse_and_validate_github_url,
)
from app.services.github_ingestion import validate_path_safety


def test_valid_github_urls() -> None:
    """Verify that standard public GitHub URLs parse and normalize correctly."""
    cases = [
        ("https://github.com/pallets/flask", "pallets", "flask", "https://github.com/pallets/flask"),
        ("https://github.com/fastapi/fastapi.git", "fastapi", "fastapi", "https://github.com/fastapi/fastapi"),
        ("https://github.com/facebook/react/", "facebook", "react", "https://github.com/facebook/react"),
        ("https://www.github.com/python/cpython", "python", "cpython", "https://github.com/python/cpython"),
    ]
    for raw, exp_owner, exp_repo, exp_canonical in cases:
        owner, repo, canonical = parse_and_validate_github_url(raw)
        assert owner == exp_owner
        assert repo == exp_repo
        assert canonical == exp_canonical


def test_invalid_scheme_rejected() -> None:
    """Reject schemes other than https / http."""
    for bad_url in [
        "ftp://github.com/owner/repo",
        "ssh://git@github.com/owner/repo",
        "file:///etc/passwd",
        "javascript:alert(1)",
    ]:
        with pytest.raises(InvalidRepositoryURLError, match="Unsupported URL scheme"):
            parse_and_validate_github_url(bad_url)


def test_credentials_in_url_rejected() -> None:
    """Reject embedded credentials."""
    with pytest.raises(InvalidRepositoryURLError, match="embedded authentication credentials"):
        parse_and_validate_github_url("https://user:password@github.com/owner/repo")


def test_ssrf_and_private_hostnames_rejected() -> None:
    """Reject loopback, LAN, and cloud metadata targets."""
    for bad_url in [
        "https://localhost/owner/repo",
        "https://127.0.0.1/owner/repo",
        "https://169.254.169.254/latest/meta-data",
        "https://metadata.google.internal/computeMetadata",
        "https://10.0.0.1/owner/repo",
        "https://192.168.1.1/owner/repo",
        "https://evil-github.com/owner/repo",
        "https://github.com.attacker.com/owner/repo",
    ]:
        with pytest.raises(InvalidRepositoryURLError):
            parse_and_validate_github_url(bad_url)


def test_non_standard_ports_rejected() -> None:
    """Reject unusual ports to prevent port scanning via URL."""
    with pytest.raises(InvalidRepositoryURLError, match="Non-standard port"):
        parse_and_validate_github_url("https://github.com:8443/owner/repo")


def test_incomplete_path_rejected() -> None:
    """Reject URLs missing owner or repo."""
    for incomplete in ["https://github.com", "https://github.com/", "https://github.com/owner"]:
        with pytest.raises(InvalidRepositoryURLError):
            parse_and_validate_github_url(incomplete)


def test_path_safety_validation() -> None:
    """Verify that path traversal sequences and unsafe paths are rejected."""
    # Safe paths
    assert validate_path_safety("src/main.py") is True
    assert validate_path_safety("backend/app/core/config.py") is True
    assert validate_path_safety("README.md") is True

    # Unsafe paths - traversals, root, drive paths, encoded sequences
    assert validate_path_safety("../etc/passwd") is False
    assert validate_path_safety("src/../../secret.txt") is False
    assert validate_path_safety("/root/file.py") is False
    assert validate_path_safety("\\windows\\system32") is False
    assert validate_path_safety("src/null\0byte.py") is False
    assert validate_path_safety("C:\\Windows\\win.ini") is False
    assert validate_path_safety("C:secrets.txt") is False
    assert validate_path_safety("D:/data/key.pem") is False
    assert validate_path_safety("%2e%2e/etc/passwd") is False
    assert validate_path_safety("src/%2e%2e/secret.py") is False
    assert validate_path_safety("foo%2fbar") is False
    assert validate_path_safety("foo%5cbar") is False
    assert validate_path_safety("a" * 600) is False
    assert validate_path_safety("") is False

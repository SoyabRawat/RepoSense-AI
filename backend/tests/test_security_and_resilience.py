"""Comprehensive automated security, boundary, and error-resilience tests for RepoSense AI."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.services.github_ingestion import (
    IngestionError,
    ingest_and_analyze_repository,
    validate_path_safety,
)
from app.services.repository_store import StoredRepository, repo_store
from app.schemas.repository import (
    ArchitectureGraph,
    FileNode,
    LanguageBreakdown,
    RepoMetadata,
)

client = TestClient(app)


def test_file_content_path_traversal_rejected() -> None:
    """Verify that path traversal attempts via the API are rejected with HTTP 400."""
    # Seed mock repository
    meta = RepoMetadata(
        repository_id="test:security@123",
        owner="test",
        name="security",
        full_name="test/security",
        canonical_url="https://github.com/test/security",
        default_branch="main",
        commit_sha="123",
        stars=1,
        forks=0,
        file_count=1,
        total_bytes=100,
        analysis_status="completed",
        limits_exceeded=[],
    )
    stored = StoredRepository(
        metadata=meta,
        files={"src/main.py": "print('safe')"},
        file_tree=FileNode(path="", name="root", type="directory", size=0, is_supported=True, children=[]),
        languages=LanguageBreakdown(languages={}, percentages={}, byte_counts={}, total_supported_files=1, total_repository_files=1),
        entry_points=[],
        relationships=[],
        graph=ArchitectureGraph(nodes=[], edges=[], entry_points=[], total_modules=0, total_dependencies=0),
    )
    repo_store.put("test:security@123", stored)

    # Traversal queries
    traversals = [
        "../etc/passwd",
        "../../secret.env",
        "/root/secret.txt",
        "C:\\Windows\\win.ini",
        "C:secrets.txt",
        "%2e%2e/passwd",
        "src/%2e%2e/secret.py",
        "foo%2fbar",
    ]
    for bad_path in traversals:
        resp = client.get(
            "/api/v1/repositories/test:security@123/files/content",
            params={"path": bad_path},
        )
        assert resp.status_code == 400
        assert "traversal" in resp.json()["error"].lower()

    # Direct validation check on null byte
    assert validate_path_safety("src/main.py\0.txt") is False


@pytest.mark.anyio
async def test_empty_repository_handling() -> None:
    """Verify that empty repositories returning HTTP 409 or 0 bytes trigger EMPTY_REPOSITORY."""
    mock_meta_resp = MagicMock()
    mock_meta_resp.status_code = 200
    mock_meta_resp.json.return_value = {
        "default_branch": "main",
        "description": "Empty test repo",
        "stargazers_count": 0,
        "forks_count": 0,
        "language": None,
        "size": 0,
    }

    mock_commit_resp = MagicMock()
    mock_commit_resp.status_code = 409
    mock_commit_resp.json.return_value = {"message": "Git Repository is empty."}

    mock_client = AsyncMock()
    mock_client.get.side_effect = [mock_meta_resp, mock_commit_resp]

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(IngestionError) as exc_info:
            await ingest_and_analyze_repository("https://github.com/test-org/empty-repo")

        assert exc_info.value.code == "EMPTY_REPOSITORY"
        assert exc_info.value.status_code == 400
        assert "empty" in exc_info.value.message.lower()


@pytest.mark.anyio
async def test_github_timeout_handling() -> None:
    """Verify that network timeouts are mapped cleanly to HTTP 504 REQUEST_TIMEOUT."""
    mock_client = AsyncMock()
    mock_client.get.side_effect = httpx.TimeoutException("Connection timed out")

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(IngestionError) as exc_info:
            await ingest_and_analyze_repository("https://github.com/timeout-org/timeout-repo")

        assert exc_info.value.code == "REQUEST_TIMEOUT"
        assert exc_info.value.status_code == 504
        assert "timed out" in exc_info.value.message.lower()


@pytest.mark.anyio
async def test_rate_limit_exceeded_handling() -> None:
    """Verify that rate limits return 429 and include reset header context."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_resp.headers = {
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": "1730000000",
    }
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_resp

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client_cls.return_value.__aexit__.return_value = None

        with pytest.raises(IngestionError) as exc_info:
            await ingest_and_analyze_repository("https://github.com/busy-org/busy-repo")

        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"
        assert exc_info.value.status_code == 429
        assert "rate limit exceeded" in exc_info.value.message.lower()
        assert "GITHUB_TOKEN" in exc_info.value.message

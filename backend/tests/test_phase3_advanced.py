"""Phase 3 Comprehensive automated test suite: AI providers, resource bounds, advanced SSRF, and edge cases."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.repository import (
    ArchitectureGraph,
    Citation,
    FileNode,
    LanguageBreakdown,
    RepoMetadata,
)
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAICompatibleProvider
from app.services.ai.provider_factory import get_ai_provider
from app.services.github_url import (
    InvalidRepositoryURLError,
    parse_and_validate_github_url,
)
from app.services.repository_store import StoredRepository, repo_store
from app.services.search_engine import search_repository_files
from app.services.static_analysis import (
    resolve_jsts_import,
    resolve_python_import,
)

client = TestClient(app)


# ==============================================================================
# 1. AI PROVIDER INTEGRATION & SECURITY TESTS
# ==============================================================================

def test_ai_provider_factory_and_defaults() -> None:
    """Verify provider factory returns appropriate provider type and safe defaults."""
    none_prov = get_ai_provider("none")
    assert none_prov.is_configured is False
    assert "none" in none_prov.name.lower()

    gemini_prov = get_ai_provider("gemini")
    assert isinstance(gemini_prov, GeminiProvider)
    assert gemini_prov.is_configured is False

    openai_prov = get_ai_provider("openai")
    assert isinstance(openai_prov, OpenAICompatibleProvider)

    ollama_prov = get_ai_provider("ollama")
    assert isinstance(ollama_prov, OpenAICompatibleProvider)
    assert "ollama" in ollama_prov.name.lower()


@pytest.mark.anyio
async def test_gemini_provider_uses_header_for_api_key() -> None:
    """Verify GeminiProvider passes API key via x-goog-api-key header and NOT in query string."""
    prov = GeminiProvider(api_key="test-gemini-key-12345", model="gemini-1.5-flash")
    assert prov.is_configured is True

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": "This project handles ingestion in [FILE: src/ingest.py LINES: 10-25]."
                        }
                    ]
                }
            }
        ]
    }

    mock_meta = RepoMetadata(
        repository_id="test:repo@sha",
        owner="test",
        name="repo",
        full_name="test/repo",
        canonical_url="https://github.com/test/repo",
        commit_sha="sha999",
    )

    evidence = [
        Citation(
            file_path="src/ingest.py",
            start_line=10,
            end_line=25,
            repository_revision="sha999",
            snippet="def ingest(): pass",
        )
    ]

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        answer, citations = await prov.explain(
            question="Where is ingestion?",
            mode="developer",
            evidence=evidence,
            metadata=mock_meta,
        )

        assert mock_post.called
        call_args = mock_post.call_args
        url_called = call_args[0][0]
        headers_called = call_args[1].get("headers", {})

        # Security assertion: key must NOT be in URL
        assert "key=" not in url_called
        assert "test-gemini-key-12345" not in url_called
        # Key MUST be in headers
        assert headers_called.get("x-goog-api-key") == "test-gemini-key-12345"

        assert "This project handles ingestion" in answer
        assert len(citations) >= 1
        assert citations[0].file_path == "src/ingest.py"


@pytest.mark.anyio
async def test_gemini_provider_error_handling() -> None:
    """Verify GeminiProvider handles upstream errors gracefully without crashing."""
    prov = GeminiProvider(api_key="valid-key", model="gemini-1.5-flash")

    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.text = "API_KEY_INVALID"

    mock_meta = RepoMetadata(
        repository_id="test:repo@sha",
        owner="test",
        name="repo",
        full_name="test/repo",
        canonical_url="https://github.com/test/repo",
        commit_sha="sha999",
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        answer, citations = await prov.explain(
            question="Explain app",
            mode="beginner",
            evidence=[],
            metadata=mock_meta,
        )

        assert "Gemini API returned error (403)" in answer
        assert citations == []


@pytest.mark.anyio
async def test_openai_provider_response_and_citations() -> None:
    """Verify OpenAICompatibleProvider executes request and parses citations."""
    prov = OpenAICompatibleProvider(api_key="sk-test-openai-key", model="gpt-4o-mini")
    assert prov.is_configured is True

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": "The entry point starts at [FILE: main.py LINES: 1-15]."
                }
            }
        ]
    }

    mock_meta = RepoMetadata(
        repository_id="test:repo@sha",
        owner="test",
        name="repo",
        full_name="test/repo",
        canonical_url="https://github.com/test/repo",
        commit_sha="sha111",
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp
        answer, citations = await prov.explain(
            question="Where is start?",
            mode="developer",
            evidence=[],
            metadata=mock_meta,
        )

        assert mock_post.called
        headers_called = mock_post.call_args[1].get("headers", {})
        assert headers_called.get("Authorization") == "Bearer sk-test-openai-key"
        assert "The entry point starts at" in answer
        assert len(citations) == 1
        assert citations[0].file_path == "main.py"
        assert citations[0].start_line == 1
        assert citations[0].end_line == 15


# ==============================================================================
# 2. ADVANCED SSRF & INPUT VALIDATION TESTS
# ==============================================================================

def test_ssrf_advanced_payloads() -> None:
    """Verify that complex SSRF vectors and protocol tricks are blocked."""
    evil_urls = [
        "https://127.0.0.1:8000/foo/bar",
        "https://127.1/foo/bar",
        "https://10.255.255.1/foo/bar",
        "https://192.168.1.1/foo/bar",
        "https://169.254.169.254/latest/meta-data",
        "https://metadata.google.internal/computeMetadata/v1",
        "https://instance-data/latest/meta-data",
        "https://admin:secret@github.com/org/repo",
        "https://github.com:8443/org/repo",
        "https://github.com:22/org/repo",
        "ftp://github.com/org/repo",
        "file:///etc/passwd",
        "gopher://github.com/org/repo",
        "https://gitlab.com/org/repo",
        "https://bitbucket.org/org/repo",
        "https://evil-github.com/org/repo",
        "https://github.com/..%2f../etc/passwd",
    ]

    for evil in evil_urls:
        with pytest.raises(InvalidRepositoryURLError):
            parse_and_validate_github_url(evil)


# ==============================================================================
# 3. IMPORT RESOLUTION & PATH TRAVERSAL DEFENSE
# ==============================================================================

def test_python_relative_import_escaping_package_blocked() -> None:
    """Verify that relative imports attempting to navigate beyond top-level package return None."""
    all_files = {"pkg/mod.py", "pkg/__init__.py", "main.py"}

    # from .. import main in pkg/mod.py -> 2 levels up escapes pkg to root (cur becomes "")
    res = resolve_python_import(
        source_file="pkg/mod.py",
        module_name="main",
        level=3,  # 3 levels up from pkg/mod.py would escape beyond repository root!
        all_files=all_files,
    )
    assert res is None

    # from . import other from root main.py (source_dir="")
    res_root = resolve_python_import(
        source_file="main.py",
        module_name="nonexistent",
        level=2,
        all_files=all_files,
    )
    assert res_root is None


def test_jsts_relative_import_escaping_repo_blocked() -> None:
    """Verify that JS/TS imports with ../../../ escaping repository root return None."""
    all_files = {"src/App.tsx", "src/index.ts"}

    res = resolve_jsts_import(
        source_file="src/App.tsx",
        import_path="../../../../etc/passwd",
        all_files=all_files,
    )
    assert res is None


# ==============================================================================
# 4. FULL-TEXT SEARCH ROBUSTNESS TESTS
# ==============================================================================

def test_search_special_characters_and_symbols() -> None:
    """Verify that search handles regex symbols and punctuation without errors."""
    files = {
        "src/util.ts": "const re = /^[a-z0-9]+$/;\nfunction test(a: number, b: number[]) { return a + b[0]; }",
        "README.md": "# Title\nCheck `[link](url)` and *italic* text.",
    }

    # Special regex metacharacters
    symbols = ["[a-z0-9]", "b: number[]", "function test(", "b[0]", "`[link](url)`", "*italic*"]
    for sym in symbols:
        resp = search_repository_files(files=files, query=sym)
        assert resp.total_matches >= 1
        assert resp.results[0].line_number >= 1

    # Empty and whitespace queries
    resp_empty = search_repository_files(files=files, query="   ")
    assert resp_empty.total_matches == 0
    assert len(resp_empty.results) == 0


# ==============================================================================
# 5. API ERROR FORMAT & 404 RESILIENCE
# ==============================================================================

def test_404_error_contains_both_error_and_detail() -> None:
    """Verify that HTTPException handler returns both 'error' and 'detail' fields."""
    res = client.get("/api/v1/repositories/nonexistent:repo/tree")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert "detail" in data
    assert "not found" in data["detail"].lower()
    assert "not found" in data["error"].lower()

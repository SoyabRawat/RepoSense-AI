"""Automated tests for full-text repository code search engine."""

from app.services.search_engine import search_repository_files


def test_keyword_and_line_matching() -> None:
    """Verify that search finds exact line numbers and matches."""
    files = {
        "src/auth.py": "def login():\n    token = create_jwt()\n    return token\n",
        "src/database.py": "def get_db():\n    return 'db_session'\n",
    }

    resp = search_repository_files(files, query="create_jwt")
    assert resp.total_matches == 1
    assert len(resp.results) == 1

    res = resp.results[0]
    assert res.file_path == "src/auth.py"
    assert res.line_number == 2
    assert "token = create_jwt()" in res.line_content
    assert res.context_before == ["def login():"]
    assert res.context_after == ["    return token"]


def test_case_sensitivity() -> None:
    """Verify case sensitivity option."""
    files = {"config.py": "API_KEY = 'secret'\napi_key_test = 'none'\n"}

    # Insensitive
    resp_ins = search_repository_files(files, query="api_key", case_sensitive=False)
    assert resp_ins.total_matches == 2

    # Sensitive
    resp_sens = search_repository_files(files, query="API_KEY", case_sensitive=True)
    assert resp_sens.total_matches == 1
    assert resp_sens.results[0].line_number == 1


def test_path_and_language_filtering() -> None:
    """Verify path filter and language filter constraints."""
    files = {
        "frontend/src/App.tsx": "const title = 'RepoSense';",
        "backend/app/main.py": "title = 'RepoSense'",
    }

    # Path filter
    resp_fe = search_repository_files(files, query="RepoSense", path_filter="frontend")
    assert resp_fe.total_matches == 1
    assert resp_fe.results[0].file_path == "frontend/src/App.tsx"

    # Language filter
    resp_py = search_repository_files(files, query="RepoSense", language_filter="Python")
    assert resp_py.total_matches == 1
    assert resp_py.results[0].file_path == "backend/app/main.py"


def test_empty_query_and_no_match() -> None:
    """Verify clean response on empty or non-matching query."""
    files = {"src/app.py": "print('hello world')"}

    empty_res = search_repository_files(files, query="")
    assert empty_res.total_matches == 0
    assert len(empty_res.results) == 0

    no_match = search_repository_files(files, query="nonexistent_string_12345")
    assert no_match.total_matches == 0
    assert len(no_match.results) == 0

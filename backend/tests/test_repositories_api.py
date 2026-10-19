"""Integration tests for repository endpoints (tree, files, graph, search, ask)."""

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.repository import (
    ArchitectureGraph,
    EntryPointInfo,
    FileNode,
    LanguageBreakdown,
    RepoMetadata,
)
from app.services.repository_store import StoredRepository, repo_store

client = TestClient(app)


def setup_test_repository() -> str:
    """Helper to populate test repository in store."""
    repo_id = "testorg:testrepo@sha12345"
    metadata = RepoMetadata(
        repository_id=repo_id,
        owner="testorg",
        name="testrepo",
        full_name="testorg/testrepo",
        canonical_url="https://github.com/testorg/testrepo",
        commit_sha="sha12345",
        primary_language="Python",
        stars=42,
        forks=5,
        file_count=2,
    )
    files = {
        "main.py": "from config import SETTINGS\n\nif __name__ == '__main__':\n    print('start')\n",
        "config.py": "SETTINGS = {'debug': True}\n",
    }
    file_tree = FileNode(
        path="",
        name="root",
        type="directory",
        children=[
            FileNode(path="main.py", name="main.py", type="file", size=60, is_entry_point=True),
            FileNode(path="config.py", name="config.py", type="file", size=26),
        ],
    )
    languages = LanguageBreakdown(
        languages={"Python": 2},
        percentages={"Python": 100.0},
        total_supported_files=2,
        total_repository_files=2,
    )
    entry_points = [
        EntryPointInfo(
            file_path="main.py",
            language="Python",
            detection_method="Execution guard",
            evidence="Line 3: if __name__ == '__main__':",
            confidence="likely",
        )
    ]
    graph = ArchitectureGraph(nodes=[], edges=[])

    stored = StoredRepository(
        metadata=metadata,
        files=files,
        file_tree=file_tree,
        languages=languages,
        entry_points=entry_points,
        relationships=[],
        graph=graph,
    )
    repo_store.put(repo_id, stored)
    return repo_id


def test_repository_endpoints_workflow() -> None:
    """Verify tree, file content, search, languages, entry-points, and Q&A endpoints."""
    repo_id = setup_test_repository()

    # 1. Get metadata
    res = client.get(f"/api/v1/repositories/{repo_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "testrepo"
    assert data["primary_language"] == "Python"

    # 2. Get tree
    tree_res = client.get(f"/api/v1/repositories/{repo_id}/tree")
    assert tree_res.status_code == 200
    tree_data = tree_res.json()
    assert len(tree_data["children"]) == 2

    # 3. Get file content
    content_res = client.get(f"/api/v1/repositories/{repo_id}/files/content?path=main.py")
    assert content_res.status_code == 200
    c_data = content_res.json()
    assert "from config import SETTINGS" in c_data["content"]
    assert c_data["line_count"] == 4

    # 4. Search
    search_res = client.get(f"/api/v1/repositories/{repo_id}/search?q=SETTINGS")
    assert search_res.status_code == 200
    s_data = search_res.json()
    assert s_data["total_matches"] == 2

    # 5. Entry points
    ep_res = client.get(f"/api/v1/repositories/{repo_id}/entry-points")
    assert ep_res.status_code == 200
    ep_data = ep_res.json()
    assert len(ep_data) == 1
    assert ep_data[0]["file_path"] == "main.py"

    # 6. Ask question
    ask_res = client.post(
        f"/api/v1/repositories/{repo_id}/ask",
        json={"question": "Where does the application start?", "mode": "beginner"},
    )
    assert ask_res.status_code == 200
    a_data = ask_res.json()
    assert "answer" in a_data
    assert len(a_data["citations"]) > 0


def test_analyze_invalid_url() -> None:
    """Verify that submitting an invalid URL returns structured 400 error."""
    res = client.post("/api/v1/repositories/analyze", json={"url": "https://notgithub.com/foo/bar"})
    assert res.status_code == 400
    data = res.json()
    assert "detail" in data

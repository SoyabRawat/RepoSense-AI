"""GitHub repository ingestion, tree retrieval, and analysis pipeline."""

import asyncio
import base64
import logging
import posixpath
from typing import Any, Dict, List, Optional, Set, Tuple
import httpx

from app.core.config import get_settings
from app.schemas.repository import (
    FileNode,
    LanguageBreakdown,
    RepoMetadata,
)
from app.services.architecture_graph import build_architecture_graph
from app.services.entry_point_detection import detect_entry_points
from app.services.github_url import (
    InvalidRepositoryURLError,
    parse_and_validate_github_url,
)
from app.services.language_detection import (
    calculate_language_distribution,
    detect_file_language,
    is_binary_or_excluded,
)
from app.services.repository_store import StoredRepository, repo_store
from app.services.static_analysis import analyze_repository_relationships

logger = logging.getLogger("reposense.ingestion")


class IngestionError(Exception):
    """Base exception for repository ingestion failures."""
    def __init__(self, message: str, status_code: int = 400, code: str = "INGESTION_ERROR"):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


def validate_path_safety(file_path: str) -> bool:
    """Validate that repository file path does not contain traversal sequences or invalid characters."""
    if not file_path or "\0" in file_path:
        return False
    if file_path.startswith("/") or file_path.startswith("\\"):
        return False
    if len(file_path) > 500:
        return False

    # Check Windows drive paths like C: or C:\
    if len(file_path) >= 2 and file_path[1] == ":":
        return False

    # Check url-encoded traversal sequences
    lower_path = file_path.lower()
    if "%2e" in lower_path or "%2f" in lower_path or "%5c" in lower_path:
        return False

    parts = file_path.replace("\\", "/").split("/")
    for p in parts:
        if p in ("..", "."):
            return False

    return True


def build_file_tree(
    files_info: List[Dict[str, Any]]
) -> FileNode:
    """
    Transform flat list of analyzed files into a nested FileNode hierarchy.
    """
    root_node = FileNode(
        path="",
        name="root",
        type="directory",
        size=0,
        language=None,
        is_supported=True,
        children=[],
    )

    dir_map: Dict[str, FileNode] = {"": root_node}

    # Ensure directories exist
    for item in sorted(files_info, key=lambda x: x["path"]):
        path = item["path"]
        parts = path.split("/")

        # Ensure parent directories
        cur_dir_path = ""
        for i in range(len(parts) - 1):
            parent_dir_path = cur_dir_path
            cur_dir_path = f"{cur_dir_path}/{parts[i]}" if cur_dir_path else parts[i]

            if cur_dir_path not in dir_map:
                new_dir = FileNode(
                    path=cur_dir_path,
                    name=parts[i],
                    type="directory",
                    size=0,
                    language=None,
                    is_supported=True,
                    children=[],
                )
                dir_map[cur_dir_path] = new_dir
                parent = dir_map[parent_dir_path]
                if parent.children is None:
                    parent.children = []
                parent.children.append(new_dir)

        # Add file node
        parent_dir = "/".join(parts[:-1])
        file_node = FileNode(
            path=path,
            name=parts[-1],
            type="file",
            size=item["size"],
            language=item["language"],
            is_supported=item["is_supported"],
            is_entry_point=item["is_entry_point"],
            children=None,
        )
        parent = dir_map[parent_dir]
        if parent.children is None:
            parent.children = []
        parent.children.append(file_node)

    # Sort children: directories first, then files alphabetically
    def sort_children(node: FileNode) -> None:
        if node.children:
            node.children.sort(key=lambda n: (0 if n.type == "directory" else 1, n.name.lower()))
            for child in node.children:
                if child.type == "directory":
                    sort_children(child)

    sort_children(root_node)
    return root_node


async def ingest_and_analyze_repository(raw_url: str) -> StoredRepository:
    """
    Execute full Phase 2 repository ingestion and analysis pipeline.
    """
    settings = get_settings()

    # 1. Validate URL & SSRF Check
    try:
        owner, repo, canonical_url = parse_and_validate_github_url(raw_url)
    except InvalidRepositoryURLError as exc:
        raise IngestionError(str(exc), status_code=400, code="INVALID_URL")

    # Construct headers for GitHub API
    headers = {
        "User-Agent": "RepoSense-AI/0.3.0",
        "Accept": "application/vnd.github.v3+json",
    }
    if settings.github_token:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    timeout = httpx.Timeout(settings.request_timeout_seconds)

    async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
        # 2. Retrieve Repository Metadata
        repo_api_url = f"https://api.github.com/repos/{owner}/{repo}"
        try:
            repo_res = await client.get(repo_api_url)
        except httpx.TimeoutException:
            raise IngestionError(
                f"Request to GitHub API timed out after {settings.request_timeout_seconds}s.",
                status_code=504,
                code="REQUEST_TIMEOUT",
            )
        except httpx.RequestError as exc:
            raise IngestionError(f"Network error contacting GitHub API: {exc}", status_code=502, code="NETWORK_ERROR")

        if repo_res.status_code == 404:
            raise IngestionError(
                f"Repository '{owner}/{repo}' not found on GitHub. Verify the URL and ensure the repository is public.",
                status_code=404,
                code="REPO_NOT_FOUND",
            )
        elif repo_res.status_code in (403, 429):
            remaining = repo_res.headers.get("x-ratelimit-remaining", "0")
            reset_time = repo_res.headers.get("x-ratelimit-reset", "unknown")
            raise IngestionError(
                f"GitHub API rate limit exceeded (Remaining: {remaining}, Reset: {reset_time}). "
                "Provide a GITHUB_TOKEN in backend/.env for higher rate limits (5,000 req/hr).",
                status_code=429,
                code="RATE_LIMIT_EXCEEDED",
            )
        elif repo_res.status_code != 200:
            raise IngestionError(
                f"GitHub API returned error {repo_res.status_code}: {repo_res.text[:200]}",
                status_code=repo_res.status_code,
                code="GITHUB_API_ERROR",
            )

        repo_data = repo_res.json()
        default_branch = repo_data.get("default_branch") or "main"
        description = repo_data.get("description")
        stars = repo_data.get("stargazers_count", 0)
        forks = repo_data.get("forks_count", 0)
        primary_lang = repo_data.get("language")
        license_info = repo_data.get("license") or {}
        license_name = license_info.get("spdx_id") or license_info.get("name")

        # 3. Retrieve Latest Commit SHA for Default Branch
        commit_url = f"https://api.github.com/repos/{owner}/{repo}/commits/{default_branch}"
        try:
            commit_res = await client.get(commit_url)
        except httpx.TimeoutException:
            raise IngestionError(
                f"Commit resolution timed out after {settings.request_timeout_seconds}s.",
                status_code=504,
                code="REQUEST_TIMEOUT",
            )
        except httpx.RequestError as exc:
            raise IngestionError(f"Network error contacting GitHub API: {exc}", status_code=502, code="NETWORK_ERROR")

        if commit_res.status_code == 409 or (commit_res.status_code == 404 and repo_data.get("size") == 0):
            raise IngestionError(
                f"Repository '{owner}/{repo}' is empty (has no commits).",
                status_code=400,
                code="EMPTY_REPOSITORY",
            )
        elif commit_res.status_code != 200:
            raise IngestionError(
                f"Failed to resolve latest commit SHA for branch '{default_branch}'.",
                status_code=commit_res.status_code,
                code="COMMIT_RESOLUTION_FAILED",
            )
        commit_sha = commit_res.json().get("sha", default_branch)
        canonical_id = f"{owner}:{repo}@{commit_sha}"

        # Check if already analyzed in cache
        cached = repo_store.get(canonical_id)
        if cached:
            logger.info("Serving repository '%s' from cache", canonical_id)
            return cached

        # 4. Retrieve Git Tree Recursively
        tree_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{commit_sha}?recursive=1"
        try:
            tree_res = await client.get(tree_url)
        except httpx.TimeoutException:
            raise IngestionError(
                f"Tree retrieval timed out after {settings.request_timeout_seconds}s.",
                status_code=504,
                code="REQUEST_TIMEOUT",
            )
        except httpx.RequestError as exc:
            raise IngestionError(f"Network error contacting GitHub API: {exc}", status_code=502, code="NETWORK_ERROR")

        if tree_res.status_code == 409:
            raise IngestionError(
                f"Repository '{owner}/{repo}' is empty (git tree unavailable).",
                status_code=400,
                code="EMPTY_REPOSITORY",
            )
        elif tree_res.status_code != 200:
            raise IngestionError(
                f"Failed to fetch repository tree for '{owner}/{repo}'.",
                status_code=tree_res.status_code,
                code="TREE_FETCH_FAILED",
            )

        tree_data = tree_res.json()
        raw_tree_items = tree_data.get("tree", [])
        is_tree_truncated = tree_data.get("truncated", False)

        limits_exceeded: List[str] = []
        if is_tree_truncated or len(raw_tree_items) > settings.max_tree_entries:
            limits_exceeded.append(f"Tree entries exceeded maximum limit ({settings.max_tree_entries})")

        # 5. Filter and Validate Tree Paths
        valid_blobs: List[Tuple[str, int]] = []  # (path, size)

        for item in raw_tree_items:
            if item.get("type") != "blob":
                continue

            file_path = item.get("path", "")
            # Path safety validation (traversal prevention)
            if not validate_path_safety(file_path):
                logger.warning("Skipping unsafe repository path: %s", file_path)
                continue

            # Binary and vendor exclusion
            if is_binary_or_excluded(file_path):
                continue

            size = item.get("size", 0)
            valid_blobs.append((file_path, size))

        # Calculate language distribution across valid blobs
        lang_counts, lang_pcts, lang_bytes, total_supported, total_examined = (
            calculate_language_distribution(valid_blobs)
        )

        language_breakdown = LanguageBreakdown(
            languages=lang_counts,
            percentages=lang_pcts,
            byte_counts=lang_bytes,
            total_supported_files=total_supported,
            total_repository_files=len(raw_tree_items),
        )

        # 6. Controlled Content Retrieval
        # Prioritize key configuration manifests and supported source files
        # Sort files so manifest files and entry points come first, then small files
        def file_priority(item: Tuple[str, int]) -> int:
            path, size = item
            basename = posixpath.basename(path).lower()
            if basename in ("package.json", "requirements.txt", "pyproject.toml", "pom.xml", "cargo.toml"):
                return 0
            if basename in ("main.py", "index.ts", "main.ts", "index.js", "app.py", "app.tsx"):
                return 1
            return 2

        sorted_blobs = sorted(valid_blobs, key=file_priority)

        file_contents: Dict[str, str] = {}
        total_retrieved_bytes = 0
        semaphore = asyncio.Semaphore(10)

        files_to_fetch = sorted_blobs[: settings.max_files_processed]
        if len(sorted_blobs) > settings.max_files_processed:
            limits_exceeded.append(f"Repository file count exceeded max files processed ({settings.max_files_processed})")

        async def fetch_file_content(path: str, size: int) -> Optional[Tuple[str, str]]:
            nonlocal total_retrieved_bytes
            if size > settings.max_file_size_bytes:
                return None
            if total_retrieved_bytes > settings.max_total_source_bytes:
                return None

            async with semaphore:
                raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{commit_sha}/{path}"
                try:
                    res = await client.get(raw_url)
                    if res.status_code == 200:
                        content_text = res.text
                        byte_len = len(content_text.encode("utf-8"))
                        total_retrieved_bytes += byte_len
                        return (path, content_text)
                except Exception:
                    pass
                return None

        tasks = [fetch_file_content(path, size) for path, size in files_to_fetch]
        fetch_results = await asyncio.gather(*tasks, return_exceptions=True)

        for res in fetch_results:
            if isinstance(res, tuple) and res is not None:
                p, c = res
                file_contents[p] = c

        if total_retrieved_bytes > settings.max_total_source_bytes:
            limits_exceeded.append(f"Total source content reached maximum limit ({settings.max_total_source_bytes // (1024*1024)}MB)")

        # 7. Static Code Analysis Pipeline
        # Entry Points Detection
        entry_points = detect_entry_points(file_contents)
        entry_point_paths = {ep.file_path for ep in entry_points}

        # Imports and Dependencies Extraction
        relationships = analyze_repository_relationships(file_contents)

        # Architecture Graph Generation
        graph = build_architecture_graph(relationships, entry_points, file_contents)

        # Hierarchical File Tree Construction
        files_info = []
        for path, size in valid_blobs:
            files_info.append({
                "path": path,
                "size": size,
                "language": detect_file_language(path),
                "is_supported": path in file_contents,
                "is_entry_point": path in entry_point_paths,
            })
        file_tree = build_file_tree(files_info)

        # 8. Assemble Complete Metadata
        analysis_status = "partial" if limits_exceeded else "completed"
        status_message = None
        if limits_exceeded:
            status_message = f"Partial analysis completed: {', '.join(limits_exceeded)}."

        metadata = RepoMetadata(
            repository_id=canonical_id,
            owner=owner,
            name=repo,
            full_name=f"{owner}/{repo}",
            canonical_url=canonical_url,
            default_branch=default_branch,
            commit_sha=commit_sha,
            description=description,
            stars=stars,
            forks=forks,
            primary_language=primary_lang,
            license=license_name,
            file_count=len(file_contents),
            total_bytes=total_retrieved_bytes,
            analysis_status=analysis_status,
            status_message=status_message,
            limits_exceeded=limits_exceeded,
        )

        # 9. Cache in RepositoryStore
        stored_repo = StoredRepository(
            metadata=metadata,
            files=file_contents,
            file_tree=file_tree,
            languages=language_breakdown,
            entry_points=entry_points,
            relationships=relationships,
            graph=graph,
        )
        repo_store.put(canonical_id, stored_repo)
        repo_store.put(f"{owner}:{repo}", stored_repo)

        return stored_repo

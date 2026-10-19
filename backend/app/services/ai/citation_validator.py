"""Citation validation engine verifying that all citations match actual files and line ranges."""

from typing import Dict, List, Optional
from app.schemas.repository import Citation


def validate_and_enrich_citation(
    citation: Citation,
    files: Dict[str, str],  # file_path -> content
    owner: str,
    repo: str,
    commit_sha: str,
) -> Optional[Citation]:
    """
    Validate a single citation against the actual repository files and revision.
    Ensures file exists, lines are bounded, extracts the real snippet, and builds the GitHub URL.
    Returns None if the citation points to a non-existent file.
    """
    path = citation.file_path.strip().lstrip("/")
    if path not in files:
        # File does not exist in analyzed files
        return None

    content = files[path]
    lines = content.splitlines()
    total_lines = len(lines)

    if total_lines == 0:
        start_line = 1
        end_line = 1
        snippet = ""
    else:
        # Clamp line ranges to valid bounds
        start_line = max(1, min(citation.start_line, total_lines))
        end_line = max(start_line, min(citation.end_line, total_lines))
        snippet_lines = lines[start_line - 1 : end_line]
        snippet = "\n".join(snippet_lines[:15])  # Cap snippet to first 15 lines if range is huge

    # Construct verifiable GitHub blob URL with line anchors
    if start_line == end_line:
        github_url = f"https://github.com/{owner}/{repo}/blob/{commit_sha}/{path}#L{start_line}"
    else:
        github_url = f"https://github.com/{owner}/{repo}/blob/{commit_sha}/{path}#L{start_line}-L{end_line}"

    return Citation(
        file_path=path,
        start_line=start_line,
        end_line=end_line,
        repository_revision=commit_sha,
        github_url=github_url,
        snippet=snippet,
        is_valid=True,
    )


def validate_citations(
    citations: List[Citation],
    files: Dict[str, str],
    owner: str,
    repo: str,
    commit_sha: str,
) -> List[Citation]:
    """
    Validate an entire list of citations.
    Filters out fabricated/invalid file paths and clamps line numbers to verified bounds.
    """
    validated: List[Citation] = []
    seen = set()

    for cit in citations:
        enriched = validate_and_enrich_citation(cit, files, owner, repo, commit_sha)
        if enriched:
            key = (enriched.file_path, enriched.start_line, enriched.end_line)
            if key not in seen:
                validated.append(enriched)
                seen.add(key)

    return validated

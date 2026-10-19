"""Context retrieval service gathering verifiable evidence snippets for AI queries."""

import re
from typing import Dict, List, Set
from app.schemas.repository import Citation, EntryPointInfo, RepoMetadata
from app.services.ai.citation_validator import validate_and_enrich_citation

STOPWORDS = {
    "what", "does", "this", "project", "do", "how", "where", "is", "are", "the",
    "a", "an", "and", "or", "in", "on", "at", "to", "for", "with", "about",
    "can", "you", "tell", "me", "show", "explain", "code", "repo", "repository",
}


def extract_search_keywords(question: str) -> List[str]:
    """Extract informative keywords from the user question."""
    tokens = re.findall(r'[a-zA-Z0-9_]{3,}', question.lower())
    keywords = [t for t in tokens if t not in STOPWORDS]
    return keywords[:6]  # Limit to top 6 keywords


def retrieve_relevant_evidence(
    question: str,
    files: Dict[str, str],
    entry_points: List[EntryPointInfo],
    metadata: RepoMetadata,
    max_evidence_files: int = 5,
) -> List[Citation]:
    """
    Retrieve bounded, relevant source code snippets with exact line ranges based on question context.
    """
    keywords = extract_search_keywords(question)
    candidate_files: List[str] = []
    seen_files: Set[str] = set()

    # 1. Always prioritize detected entry points for broad/starter questions
    is_starter_q = any(k in question.lower() for k in ("start", "entry", "do", "overview", "run", "main"))
    if is_starter_q and entry_points:
        for ep in entry_points:
            if ep.file_path in files and ep.file_path not in seen_files:
                candidate_files.append(ep.file_path)
                seen_files.add(ep.file_path)

    # 2. Check manifest files if dependency/setup questions
    if any(k in question.lower() for k in ("dependency", "package", "library", "install", "tech", "stack")):
        for manifest in ("package.json", "requirements.txt", "pyproject.toml", "pom.xml", "Cargo.toml"):
            if manifest in files and manifest not in seen_files:
                candidate_files.append(manifest)
                seen_files.add(manifest)

    # 3. Search files matching question keywords
    for file_path, content in files.items():
        if len(candidate_files) >= max_evidence_files:
            break
        if file_path in seen_files or not content:
            continue

        lower_path = file_path.lower()
        lower_content = content.lower()

        # Score by path match and keyword presence
        match_count = sum(1 for kw in keywords if kw in lower_path or kw in lower_content)
        if match_count > 0:
            candidate_files.append(file_path)
            seen_files.add(file_path)

    # If still empty, grab first 2 representative source files
    if not candidate_files:
        for path in sorted(files.keys()):
            if not path.startswith(".") and "/" in path:
                candidate_files.append(path)
                if len(candidate_files) >= 2:
                    break

    # Build Citation models for the candidate snippets
    evidence_citations: List[Citation] = []

    for path in candidate_files[:max_evidence_files]:
        content = files.get(path, "")
        lines = content.splitlines()
        total_lines = len(lines)
        if total_lines == 0:
            continue

        # Find best starting line based on keywords
        start_line = 1
        for kw in keywords:
            for idx, line in enumerate(lines[:100], start=1):
                if kw in line.lower():
                    start_line = max(1, idx - 2)
                    break
            if start_line > 1:
                break

        end_line = min(total_lines, start_line + 25)

        raw_cit = Citation(
            file_path=path,
            start_line=start_line,
            end_line=end_line,
            repository_revision=metadata.commit_sha,
            is_valid=True,
        )
        enriched = validate_and_enrich_citation(
            raw_cit, files, metadata.owner, metadata.name, metadata.commit_sha
        )
        if enriched:
            evidence_citations.append(enriched)

    return evidence_citations


def format_evidence_prompt_block(evidence: List[Citation]) -> str:
    """
    Format retrieved evidence snippets with strict untrusted data isolation delimiters
    to prevent prompt injection.
    """
    if not evidence:
        return "No specific repository source evidence was retrieved."

    blocks = []
    for cit in evidence:
        blocks.append(
            f"=== UNTRUSTED REPOSITORY SOURCE EVIDENCE: {cit.file_path} (Lines {cit.start_line}-{cit.end_line}) ===\n"
            f"{cit.snippet}\n"
            f"=== END OF EVIDENCE: {cit.file_path} ==="
        )

    return "\n\n".join(blocks)

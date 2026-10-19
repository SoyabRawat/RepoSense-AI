"""Full-text source code search engine across retrieved repository files."""

import re
from typing import Dict, List, Optional
from app.schemas.repository import SearchResponse, SearchResult
from app.services.language_detection import detect_file_language


def search_repository_files(
    files: Dict[str, str],  # file_path -> content
    query: str,
    case_sensitive: bool = False,
    path_filter: Optional[str] = None,
    language_filter: Optional[str] = None,
    max_results: int = 50,
) -> SearchResponse:
    """
    Search indexed repository files for matching text, lines, and context snippets.
    """
    if not query or not query.strip():
        return SearchResponse(query=query, total_matches=0, results=[], is_partial=False)

    trimmed_query = query.strip()
    search_target = trimmed_query if case_sensitive else trimmed_query.lower()

    results: List[SearchResult] = []
    total_found = 0
    is_partial = False

    for file_path, content in files.items():
        if not content:
            continue

        # Path filter
        if path_filter and path_filter.lower() not in file_path.lower():
            continue

        # Language filter
        file_lang = detect_file_language(file_path)
        if language_filter:
            if not file_lang or language_filter.lower() not in file_lang.lower():
                continue

        lines = content.splitlines()

        for line_idx, line in enumerate(lines, start=1):
            check_line = line if case_sensitive else line.lower()
            if search_target in check_line:
                total_found += 1
                if len(results) < max_results:
                    # Capture 2 lines before and 2 lines after for context snippet
                    start_ctx = max(0, line_idx - 3)
                    end_ctx = min(len(lines), line_idx + 2)

                    context_before = lines[start_ctx:line_idx - 1]
                    context_after = lines[line_idx:end_ctx]

                    results.append(
                        SearchResult(
                            file_path=file_path,
                            line_number=line_idx,
                            line_content=line.strip(),
                            context_before=context_before,
                            context_after=context_after,
                            language=file_lang,
                        )
                    )
                else:
                    is_partial = True

    return SearchResponse(
        query=query,
        total_matches=total_found,
        results=results,
        is_partial=is_partial or total_found > max_results,
    )

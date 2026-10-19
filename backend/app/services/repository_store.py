"""Repository storage and cache manager for analyzed repositories."""

import asyncio
from typing import Dict, List, Optional
from app.schemas.repository import (
    ArchitectureGraph,
    EntryPointInfo,
    FileContentResponse,
    FileNode,
    ImportRelationship,
    LanguageBreakdown,
    RepoMetadata,
)


class StoredRepository:
    """In-memory cache record for a fully or partially analyzed repository."""

    def __init__(
        self,
        metadata: RepoMetadata,
        files: Dict[str, str],
        file_tree: FileNode,
        languages: LanguageBreakdown,
        entry_points: List[EntryPointInfo],
        relationships: List[ImportRelationship],
        graph: ArchitectureGraph,
    ):
        self.metadata = metadata
        self.files = files
        self.file_tree = file_tree
        self.languages = languages
        self.entry_points = entry_points
        self.relationships = relationships
        self.graph = graph


class RepositoryStore:
    """Thread-safe store mapping repository identifiers to StoredRepository instances."""

    def __init__(self):
        self._store: Dict[str, StoredRepository] = {}
        self._lock = asyncio.Lock()

    def get(self, repo_id: str) -> Optional[StoredRepository]:
        """Look up by canonical id (e.g., 'owner:repo@sha' or 'owner:repo')."""
        normalized_id = repo_id.strip().lower()
        if normalized_id in self._store:
            return self._store[normalized_id]

        # Check prefix match for owner:repo
        for key, stored in self._store.items():
            if key.startswith(f"{normalized_id}@") or key == normalized_id:
                return stored

        return None

    def put(self, repo_id: str, stored: StoredRepository) -> None:
        """Store repository under its canonical revision ID and alias."""
        norm_id = repo_id.strip().lower()
        self._store[norm_id] = stored

        # Also alias by owner:repo for convenience if key has @sha
        if "@" in norm_id:
            alias = norm_id.split("@")[0]
            self._store[alias] = stored

    def get_file_content(self, repo_id: str, path: str) -> Optional[FileContentResponse]:
        """Retrieve content for a specific repository file."""
        stored = self.get(repo_id)
        if not stored:
            return None

        clean_path = path.strip().lstrip("/")
        if clean_path not in stored.files:
            return None

        content = stored.files[clean_path]
        lines = content.splitlines()

        # Find language from language breakdown or extension
        from app.services.language_detection import detect_file_language
        lang = detect_file_language(clean_path)

        return FileContentResponse(
            path=clean_path,
            language=lang,
            size=len(content.encode("utf-8")),
            content=content,
            line_count=len(lines),
            truncated=False,
        )

    def list_repositories(self) -> List[RepoMetadata]:
        """List metadata for all indexed repositories."""
        seen = set()
        results = []
        for stored in self._store.values():
            if stored.metadata.repository_id not in seen:
                results.append(stored.metadata)
                seen.add(stored.metadata.repository_id)
        return results


# Global singleton instance
repo_store = RepositoryStore()

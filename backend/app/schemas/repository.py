"""Data schemas for repository ingestion, analysis, architecture graphs, search, and AI grounded answers."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class AnalyzeRepoRequest(BaseModel):
    """Request payload to initiate repository analysis."""

    url: str = Field(..., description="Public GitHub repository URL (e.g. https://github.com/owner/repo)")


class RepoMetadata(BaseModel):
    """Complete repository metadata and analysis summary."""

    repository_id: str = Field(..., description="Canonical repository identifier, e.g. owner:repo@sha")
    owner: str = Field(..., description="Repository owner / organization")
    name: str = Field(..., description="Repository name")
    full_name: str = Field(..., description="Owner and name combined (owner/name)")
    canonical_url: str = Field(..., description="Normalized HTTPS GitHub repository URL")
    default_branch: str = Field(default="main", description="Default branch name")
    commit_sha: str = Field(..., description="Analyzed immutable commit SHA or tree revision")
    description: Optional[str] = Field(default=None, description="Repository description from GitHub")
    stars: int = Field(default=0, description="GitHub star count")
    forks: int = Field(default=0, description="GitHub fork count")
    primary_language: Optional[str] = Field(default=None, description="GitHub primary language")
    license: Optional[str] = Field(default=None, description="Repository license identifier or name")
    file_count: int = Field(default=0, description="Total number of supported files analyzed")
    total_bytes: int = Field(default=0, description="Total source bytes analyzed")
    analysis_timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="UTC timestamp of the analysis",
    )
    analysis_status: Literal["completed", "partial", "failed"] = Field(
        default="completed",
        description="Status of the repository analysis",
    )
    status_message: Optional[str] = Field(
        default=None,
        description="Explanatory message if analysis is partial, limited, or failed",
    )
    limits_exceeded: List[str] = Field(
        default_factory=list,
        description="List of resource limits exceeded during analysis (if any)",
    )


class FileNode(BaseModel):
    """Hierarchical file tree node for directory navigation."""

    path: str = Field(..., description="Relative path within repository")
    name: str = Field(..., description="File or directory basename")
    type: Literal["file", "directory"] = Field(..., description="Node kind")
    size: int = Field(default=0, description="Size in bytes")
    language: Optional[str] = Field(default=None, description="Detected programming language")
    is_supported: bool = Field(default=True, description="Whether this file was indexed and parsed")
    is_entry_point: bool = Field(default=False, description="Whether this file is a detected entry point")
    children: Optional[List["FileNode"]] = Field(default=None, description="Child nodes if directory")


class FileContentResponse(BaseModel):
    """File content response with line count and truncation status."""

    path: str = Field(..., description="Relative file path")
    language: Optional[str] = Field(default=None, description="Programming language for syntax formatting")
    size: int = Field(..., description="File size in bytes")
    content: str = Field(..., description="Full text source content")
    line_count: int = Field(..., description="Total line count")
    truncated: bool = Field(default=False, description="Whether file content was truncated due to size limits")


class LanguageBreakdown(BaseModel):
    """Language distribution statistics computed from analyzed source files."""

    languages: Dict[str, int] = Field(default_factory=dict, description="File counts per language")
    percentages: Dict[str, float] = Field(default_factory=dict, description="Percentage of classified source files")
    byte_counts: Dict[str, int] = Field(default_factory=dict, description="Byte counts per language")
    total_supported_files: int = Field(default=0, description="Total number of classified source files")
    total_repository_files: int = Field(default=0, description="Total repository tree entries examined")


class EntryPointInfo(BaseModel):
    """Application entry point identified with verifiable evidence."""

    file_path: str = Field(..., description="Relative path to entry point file")
    language: str = Field(..., description="Programming language")
    detection_method: str = Field(..., description="Rule or parser technique used for identification")
    evidence: str = Field(..., description="Concrete code or configuration snippet supporting detection")
    confidence: Literal["confirmed", "likely", "possible"] = Field(
        ...,
        description="Confidence tier: confirmed (manifest/explicit), likely (pattern), possible (fallback)",
    )


class ImportRelationship(BaseModel):
    """Static import or dependency relationship between source files or packages."""

    source_file: str = Field(..., description="Source file containing the import")
    target_module: str = Field(..., description="Target module, file, or package specifier")
    resolved_target_file: Optional[str] = Field(
        default=None,
        description="Resolved repository file path if internal",
    )
    relationship_type: Literal["internal_import", "external_dependency", "manifest_dependency"] = Field(
        ...,
        description="Kind of relationship",
    )
    source_line: Optional[int] = Field(default=None, description="1-indexed line number in source file")
    resolution_status: Literal["resolved", "external", "unresolved"] = Field(
        ...,
        description="Whether target resolves inside repository or to external package",
    )


class ArchitectureNode(BaseModel):
    """Node in the interactive architecture graph."""

    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Human-readable display label")
    type: Literal["entry_point", "file", "module", "external_package"] = Field(..., description="Node category")
    file_path: Optional[str] = Field(default=None, description="Associated file path if applicable")
    language: Optional[str] = Field(default=None, description="Programming language")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional node attributes")


class ArchitectureEdge(BaseModel):
    """Directed edge in the interactive architecture graph."""

    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: Literal["imports", "depends_on", "declares_dependency"] = Field(..., description="Relationship type")
    label: Optional[str] = Field(default=None, description="Edge display label")
    evidence: Optional[str] = Field(default=None, description="Verifiable evidence string or line reference")


class ArchitectureGraph(BaseModel):
    """Complete architecture graph payload for React Flow visualization."""

    nodes: List[ArchitectureNode] = Field(default_factory=list)
    edges: List[ArchitectureEdge] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata (counts, clusters)")


class SearchResult(BaseModel):
    """A single match from full-text code search."""

    file_path: str = Field(..., description="File where match was found")
    line_number: int = Field(..., description="1-indexed line number of match")
    line_content: str = Field(..., description="Matched line text")
    context_before: List[str] = Field(default_factory=list, description="Lines preceding the match")
    context_after: List[str] = Field(default_factory=list, description="Lines following the match")
    language: Optional[str] = Field(default=None, description="Language of file")


class SearchResponse(BaseModel):
    """Full-text search response with pagination and limits."""

    query: str = Field(..., description="Search query")
    total_matches: int = Field(default=0, description="Total number of matches found")
    results: List[SearchResult] = Field(default_factory=list, description="List of match results")
    is_partial: bool = Field(default=False, description="Whether search hit maximum result limit")


class Citation(BaseModel):
    """Verifiable source code citation referencing real file and line range."""

    file_path: str = Field(..., description="Repository relative file path")
    start_line: int = Field(..., description="1-indexed start line number")
    end_line: int = Field(..., description="1-indexed end line number")
    repository_revision: str = Field(..., description="Analyzed commit SHA")
    github_url: Optional[str] = Field(default=None, description="Clickable GitHub blob URL")
    snippet: Optional[str] = Field(default=None, description="Actual code snippet verified from source")
    is_valid: bool = Field(default=True, description="Whether citation was successfully verified against source")


class AskRequest(BaseModel):
    """AI code explanation question payload."""

    question: str = Field(..., description="Developer's question about the repository")
    mode: Literal["beginner", "developer"] = Field(
        default="developer",
        description="Explanation mode: beginner (accessible, step-by-step) or developer (technical, architectural)",
    )


class AskResponse(BaseModel):
    """Response containing AI-assisted explanation and verified citations."""

    question: str = Field(..., description="User's original question")
    answer: str = Field(..., description="AI explanation grounded in repository evidence")
    mode: Literal["beginner", "developer"] = Field(..., description="Explanation mode applied")
    provider: str = Field(..., description="AI provider used (e.g. none, gemini, openai, ollama)")
    citations: List[Citation] = Field(default_factory=list, description="Validated citations to source files")
    evidence_used: List[Citation] = Field(default_factory=list, description="Context evidence provided to model")
    disclaimer: Optional[str] = Field(default=None, description="Operational disclaimer or guidance notice")

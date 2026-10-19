"""FastAPI endpoints for repository analysis, exploration, search, and AI grounded Q&A."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.repository import (
    AnalyzeRepoRequest,
    ArchitectureGraph,
    AskRequest,
    AskResponse,
    EntryPointInfo,
    FileContentResponse,
    FileNode,
    ImportRelationship,
    LanguageBreakdown,
    RepoMetadata,
    SearchResponse,
)
from app.services.ai.citation_validator import validate_citations
from app.services.ai.context_retriever import retrieve_relevant_evidence
from app.services.ai.provider_factory import get_ai_provider
from app.services.github_ingestion import (
    IngestionError,
    ingest_and_analyze_repository,
    validate_path_safety,
)
from app.services.repository_store import repo_store
from app.services.search_engine import search_repository_files

router = APIRouter(prefix="/repositories", tags=["Repositories"])


@router.post("/analyze", response_model=RepoMetadata, status_code=status.HTTP_200_OK)
async def analyze_repository(payload: AnalyzeRepoRequest) -> RepoMetadata:
    """
    Ingest and analyze a public GitHub repository URL.
    Performs URL validation, SSRF checks, tree traversal prevention, static AST parsing,
    language detection, entry-point detection, graph generation, and in-memory indexing.
    """
    try:
        stored = await ingest_and_analyze_repository(payload.url)
        return stored.metadata
    except IngestionError as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Repository analysis failed: {exc}",
        )


@router.get("", response_model=List[RepoMetadata])
async def list_repositories() -> List[RepoMetadata]:
    """List all currently indexed repositories."""
    return repo_store.list_repositories()


@router.get("/{repository_id:path}/tree", response_model=FileNode)
async def get_repository_tree(repository_id: str) -> FileNode:
    """Retrieve full hierarchical directory and file tree for navigation."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found. Please analyze it first.",
        )
    return stored.file_tree


@router.get("/{repository_id:path}/files/content", response_model=FileContentResponse)
async def get_file_content(repository_id: str, path: str = Query(..., description="Relative file path")) -> FileContentResponse:
    """Retrieve raw text content, language, and line count for a specific file."""
    if not validate_path_safety(path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or unsafe file path traversal detected.",
        )
    content_res = repo_store.get_file_content(repository_id, path)
    if not content_res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File '{path}' not found in analyzed repository '{repository_id}'.",
        )
    return content_res


@router.get("/{repository_id:path}/languages", response_model=LanguageBreakdown)
async def get_repository_languages(repository_id: str) -> LanguageBreakdown:
    """Retrieve programming language distribution and percentages."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )
    return stored.languages


@router.get("/{repository_id:path}/entry-points", response_model=List[EntryPointInfo])
async def get_entry_points(repository_id: str) -> List[EntryPointInfo]:
    """Retrieve detected application entry points with verifiable evidence."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )
    return stored.entry_points


@router.get("/{repository_id:path}/relationships", response_model=List[ImportRelationship])
async def get_relationships(repository_id: str) -> List[ImportRelationship]:
    """Retrieve extracted static import and package dependency relationships."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )
    return stored.relationships


@router.get("/{repository_id:path}/graph", response_model=ArchitectureGraph)
async def get_architecture_graph(repository_id: str) -> ArchitectureGraph:
    """Retrieve node-link architecture graph for interactive React Flow visualization."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )
    return stored.graph


@router.get("/{repository_id:path}/search", response_model=SearchResponse)
async def search_repository(
    repository_id: str,
    q: str = Query(..., min_length=1, description="Search query string"),
    case_sensitive: bool = Query(default=False, description="Case-sensitive matching"),
    path_filter: Optional[str] = Query(default=None, description="Optional path substring filter"),
    language_filter: Optional[str] = Query(default=None, description="Optional language filter"),
) -> SearchResponse:
    """Perform full-text code search across indexed repository files."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )

    return search_repository_files(
        files=stored.files,
        query=q,
        case_sensitive=case_sensitive,
        path_filter=path_filter,
        language_filter=language_filter,
    )


@router.post("/{repository_id:path}/ask", response_model=AskResponse)
async def ask_repository_question(repository_id: str, payload: AskRequest) -> AskResponse:
    """
    Ask a question about the repository.
    Retrieves bounded, relevant code snippets as untrusted evidence, invokes the configured
    AI provider (or NullProvider in AI-free mode), and validates all returned source citations
    against the actual repository revision.
    """
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found.",
        )

    # 1. Retrieve targeted evidence snippets
    evidence = retrieve_relevant_evidence(
        question=payload.question,
        files=stored.files,
        entry_points=stored.entry_points,
        metadata=stored.metadata,
    )

    # 2. Invoke configured provider
    provider = get_ai_provider()
    answer_text, raw_citations = await provider.explain(
        question=payload.question,
        mode=payload.mode,
        evidence=evidence,
        metadata=stored.metadata,
    )

    # 3. Strict Citation Validation against actual files and lines
    validated_citations = validate_citations(
        citations=raw_citations,
        files=stored.files,
        owner=stored.metadata.owner,
        repo=stored.metadata.name,
        commit_sha=stored.metadata.commit_sha,
    )

    disclaimer = (
        "Operating in AI-free mode: Answer generated from verified static code analysis facts."
        if not provider.is_configured
        else "Answer generated by AI provider grounded in retrieved source evidence."
    )

    return AskResponse(
        question=payload.question,
        answer=answer_text,
        mode=payload.mode,
        provider=provider.name,
        citations=validated_citations,
        evidence_used=evidence,
        disclaimer=disclaimer,
    )


@router.get("/{repository_id:path}", response_model=RepoMetadata)
async def get_repository_metadata(repository_id: str) -> RepoMetadata:
    """Retrieve summary metadata and analysis status for an analyzed repository."""
    stored = repo_store.get(repository_id)
    if not stored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Repository '{repository_id}' not found. Please analyze it first.",
        )
    return stored.metadata

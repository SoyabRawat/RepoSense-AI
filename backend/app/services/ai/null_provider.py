"""Default offline NullProvider for AI-free exploration mode."""

from typing import List, Tuple
from app.schemas.repository import Citation, RepoMetadata
from app.services.ai.base import BaseAIProvider


class NullProvider(BaseAIProvider):
    """
    Offline provider active when no external AI API key is configured.
    Provides verified factual codebase analysis from retrieved static evidence
    without making any external network requests or fabricating information.
    """

    @property
    def name(self) -> str:
        return "none (AI-Free Mode)"

    @property
    def is_configured(self) -> bool:
        return False

    async def explain(
        self,
        question: str,
        mode: str,
        evidence: List[Citation],
        metadata: RepoMetadata,
    ) -> Tuple[str, List[Citation]]:
        """
        Produce a factual, evidence-based summary without external LLM calls.
        """
        citations = evidence.copy()

        if not evidence:
            answer = (
                f"**Notice: AI-Free Mode Active (No AI provider configured).**\n\n"
                f"RepoSense AI searched the repository '{metadata.full_name}' for evidence related to: "
                f"`\"{question}\"`, but found no matching source files in the indexed repository files.\n\n"
                f"To configure an AI provider for natural language synthesis, specify `AI_PROVIDER` "
                f"(e.g. `gemini`, `openai`, or `ollama`) and the corresponding API key in `.env`."
            )
            return answer, []

        files_list = "\n".join([f"- `{c.file_path}` (lines {c.start_line}-{c.end_line})" for c in citations])

        if mode == "beginner":
            answer = (
                f"### Repository Insights (AI-Free Mode)\n\n"
                f"**Question:** {question}\n\n"
                f"**Repository:** `{metadata.full_name}` (Revision: `{metadata.commit_sha[:8]}`)\n\n"
                f"While external AI generation is disabled, here is the factual source evidence found in this codebase:\n\n"
                f"#### Relevant Files & Locations\n"
                f"{files_list}\n\n"
                f"#### Summary\n"
                f"This project is primarily written in **{metadata.primary_language or 'multiple languages'}** "
                f"with {metadata.file_count} analyzed files. You can click any citation card below "
                f"to inspect the actual source code directly in the Source Viewer."
            )
        else:
            answer = (
                f"### Static Analysis Report (AI-Free Mode)\n\n"
                f"**Query:** `{question}`\n"
                f"**Target:** `{metadata.full_name}@{metadata.commit_sha[:8]}`\n\n"
                f"**Indexed Evidence Snippets:**\n"
                f"{files_list}\n\n"
                f"**Architecture Context:**\n"
                f"- Primary Language: `{metadata.primary_language or 'Unknown'}`\n"
                f"- Analyzed Source Files: `{metadata.file_count}`\n"
                f"- Analysis Status: `{metadata.analysis_status}`\n\n"
                f"*Note: For natural language answers, configure an LLM provider (`gemini`, `openai`, `ollama`) in `.env`.*"
            )

        return answer, citations

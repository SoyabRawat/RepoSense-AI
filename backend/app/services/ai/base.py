"""Abstract base class for replaceable AI explanation providers."""

from abc import ABC, abstractmethod
from typing import List, Tuple
from app.schemas.repository import Citation, RepoMetadata


class BaseAIProvider(ABC):
    """Abstract interface for all AI code explanation adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider (e.g. 'none', 'gemini', 'openai', 'ollama')."""
        pass

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Whether the provider has necessary API credentials or endpoints configured."""
        pass

    @abstractmethod
    async def explain(
        self,
        question: str,
        mode: str,  # 'beginner' | 'developer'
        evidence: List[Citation],
        metadata: RepoMetadata,
    ) -> Tuple[str, List[Citation]]:
        """
        Generate a source-grounded explanation based strictly on retrieved code evidence.

        Returns:
            Tuple of (answer_text, validated_citations)
        """
        pass

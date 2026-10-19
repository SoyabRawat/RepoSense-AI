"""AI Provider factory selecting active provider based on application settings."""

from typing import Optional
from app.core.config import get_settings
from app.services.ai.base import BaseAIProvider
from app.services.ai.null_provider import NullProvider
from app.services.ai.gemini_provider import GeminiProvider
from app.services.ai.openai_provider import OpenAICompatibleProvider


def get_ai_provider(provider_override: Optional[str] = None) -> BaseAIProvider:
    """
    Resolve and return configured AI provider. Defaults to NullProvider if none or invalid.
    """
    settings = get_settings()
    provider_name = (provider_override or settings.ai_provider or "none").lower().strip()

    if provider_name == "gemini":
        return GeminiProvider(api_key=settings.ai_api_key, model=settings.ai_model)
    elif provider_name in ("openai", "chatgpt"):
        return OpenAICompatibleProvider(
            api_key=settings.ai_api_key,
            model=settings.ai_model or "gpt-4o-mini",
            api_base=settings.ai_api_base,
            provider_name="OpenAI",
        )
    elif provider_name == "ollama":
        return OpenAICompatibleProvider(
            api_key="ollama",
            model=settings.ai_model or "llama3",
            api_base=settings.ai_api_base or "http://localhost:11434/v1",
            provider_name="Ollama",
        )

    return NullProvider()

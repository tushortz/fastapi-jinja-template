"""Tagging services factory and exports."""

from src.config import settings

from .base import TagService
from .gemini import GeminiTagService
from .local_ai import LocalTagService


def get_tag_service() -> TagService:
    """Return the configured TagService implementation."""
    provider = (settings.ai_service or "gemini").lower()
    if provider == "local":
        return LocalTagService()
    return GeminiTagService()

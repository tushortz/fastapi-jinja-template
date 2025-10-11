"""Gemini tagging service implementation."""

import logging

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from src.config import settings

logger = logging.getLogger(__name__)


class GeminiTagService:
    """Tagging via Google Gemini."""

    def __init__(self) -> None:
        if settings.gemini_api_key and genai is not None:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
            logger.info("Gemini model configured")
        else:
            self.model = None
            logger.warning("Gemini not available (missing package or API key)")

    async def generate_tags(self, text: str, title: str | None = None) -> list[str]:
        """Generate tags using Gemini."""
        if not self.model:
            return []

        prompt = self._build_prompt(text, title)
        try:
            response = self.model.generate_content(prompt)
            content = response.text or ""
            tags = [t.strip().lower() for t in content.split(",")]
            return [t for t in tags if t][:5]
        except Exception as exc:  # noqa: BLE001 - external API
            logger.error("Gemini tagging failed: %s", str(exc))
            return []

    def _build_prompt(self, text: str, title: str | None) -> str:
        context = f"Title: {title}\n" if title else ""
        return (
            "Analyze this text and generate 3-5 relevant tags. Tags should be:\n"
            "- Single words or short phrases (max 2 words)\n"
            "- Lowercase only\n"
            "- Relevant to the text's theme, emotion, or subject\n"
            "- General enough to be useful for categorization\n\n"
            f'{context}Text: "{text}"\n'
            "Return only the tags, separated by commas, no other text."
        )

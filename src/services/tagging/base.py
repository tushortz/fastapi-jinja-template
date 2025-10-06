"""Tagging service base interface."""

from typing import Protocol


class TagService(Protocol):
    """Protocol for AI tagging services."""

    async def generate_tags(
        self, quote_text: str, book_title: str | None = None
    ) -> list[str]:  # noqa: D401
        """Generate tags."""
        ...

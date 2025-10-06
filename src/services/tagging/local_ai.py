"""Local OpenAI-compatible tagging service (e.g., LM Studio)."""

import json
import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class LocalTagService:
    """Tagging via local OpenAI-compatible API."""

    def __init__(self) -> None:
        self.base_url = settings.local_ai_url.rstrip("/")
        logger.info("Local AI model configured")

    async def generate_tags(self, text: str, title: str | None = None) -> list[str]:
        """Generate tags using local API."""
        system_prompt = (
            "You generate 3-5 concise, lowercase tags (max 2 words each) that categorize a text by "
            "theme, emotion, or subject. Return tags separated by commas only."
        )
        context = f"Title: {title}\n" if title else ""
        user_prompt = (
            f'{context}Text: "{text}"\nReturn only the tags, separated by commas.'
        )

        payload = {
            "model": settings.local_ai_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 64,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                resp = await client.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers={"Content-Type": "application/json"},
                    content=json.dumps(payload),
                )
            if resp.status_code != 200:
                logger.error("Local AI error: %s %s", resp.status_code, resp.text)
                return []
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            tags = [t.strip().lower() for t in content.split(",")]
            return [t for t in tags if t][:5]
        except Exception as exc:  # noqa: BLE001 - external service
            logger.error("Local AI tagging failed: %s", str(exc))
            return []

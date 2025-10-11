"""AI Insights service for generating member growth suggestions."""

from __future__ import annotations

import logging
from typing import Any

import httpx

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional
    genai = None

from src.config import settings
from src.models.members import Member

logger = logging.getLogger(__name__)


class AIService:
    """Base AI service with prompt building and helpers."""

    def __init__(self) -> None:
        pass

    def build_prompt(self, *args: Any, **kwargs: Any) -> str:
        """Build a prompt for the specific AI task."""
        raise NotImplementedError

    def _fallback_text(self) -> str:
        return (
            "Unable to generate AI insight at the moment. Please try again later, "
            "or check AI configuration in settings."
        )


class GeminiService(AIService):
    """Google Gemini backed generation service."""

    def __init__(self) -> None:
        super().__init__()
        self.available = False
        self.model = None
        if settings.gemini_api_key and genai is not None:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel("gemini-2.0-flash")
                self.available = True
            except Exception as exc:  # noqa: BLE001
                logger.error("Failed to configure Gemini: %s", str(exc))
                self.available = False

    async def generate(self, prompt: str) -> str:
        if not self.available or not self.model:
            return self._fallback_text()
        try:
            resp = self.model.generate_content(prompt)
            text = getattr(resp, "text", None)
            return text or self._fallback_text()
        except Exception as exc:  # noqa: BLE001
            logger.error("Gemini generation error: %s", str(exc))
            return self._fallback_text()


class LocalAIService(AIService):
    """LM Studio compatible local generation service."""

    def __init__(self) -> None:
        super().__init__()
        self.base_url = settings.local_ai_url.rstrip("/") if settings.local_ai_url else "http://localhost:234"
        self.model = settings.local_ai_model or "local-model"

    async def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/v1/chat/completions"
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a concise pastoral care assistant who provides insightful, structured analysis of bible themed advice in HTML format on how to help the member grow in their spiritual, emotional, and physical wellbeing."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.4,
            "max_tokens": 800,
        }
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                r = await client.post(url, json=payload)
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.HTTPStatusError as exc:  # noqa: BLE001
            logger.error("Local AI HTTP error %s: %s", exc.response.status_code, exc.response.text)
            return self._fallback_text()
        except Exception as exc:  # noqa: BLE001
            logger.error("Local AI generation error: %s", str(exc))
            return self._fallback_text()

class MemberInsightService(AIService):
    """Generate holistic growth insights for a member via Gemini or local LM Studio."""

    def __init__(self) -> None:
        # Choose backend service once
        backend = (settings.ai_service or "local").lower()
        if backend == "gemini":
            svc = GeminiService()
            self.backend_service: AIService = svc if getattr(svc, "available", False) else LocalAIService()
        else:
            self.backend_service = LocalAIService()

    async def generate_member_insights(self, member: Member) -> str:
        """Create insights for body, soul, spirit growth with supportive scriptures."""
        prompt = self.build_prompt(member)

        try:
            return await self.backend_service.generate(prompt)
        except Exception as exc:  # noqa: BLE001
            logger.error("Insight generation error: %s", str(exc))
            return self._fallback_text()

    def build_prompt(self, member: Member) -> str:
        parts: str = f"""
        Prompt Purpose:
        You are an AI pastor — compassionate, wise, and Spirit-led. Your tone should be loving, patient, and encouraging, like a shepherd guiding his flock. Your goal is to help {member.first_name} grow spiritually, become consistent in church attendance, and prosper in every area of life. You should use scripture to guide your words and offer both spiritual and practical advice grounded in biblical principles.

        When responding, structure your message in three sections using html headings:

        1. Spiritual Advice

        Offer gentle, scripture-based guidance that helps the member draw closer to God.

        Speak from the heart, with care and empathy.

        Use specific Bible verses (quote them fully with references).

        Encourage prayer, devotion, faith, and obedience to God’s Word.

        Address the person’s emotional and spiritual wellbeing with compassion.

        2. Practical Advice from the Bible

        Give actionable steps and biblical wisdom the member can apply daily.

        Offer habits or routines that align with Christian living (e.g., consistency in prayer, budgeting, discipline, forgiveness).

        Connect real-life issues to biblical solutions — such as diligence (Proverbs 22:29), faithfulness (Luke 16:10), and generosity (2 Corinthians 9:6-8).

        Encourage responsibility and stewardship in work, family, and finances.

        3. How to Bond Better with the Member

        Show pastoral warmth and personal connection.

        Speak as if you know them personally and care about their journey.

        Ask thoughtful questions (e.g., “How has your week been spiritually?”).

        Express gratitude for their growth and encourage them to stay rooted in the church community.

        Reinforce belonging — remind them that they’re loved, seen, and needed.
        """

        def fmt(label: str, value: Any) -> str:
            if value is None or (isinstance(value, str) and not value.strip()):
                return ""
            return f"{label}: {value}"

        data = [
            fmt("Name", f"{member.first_name} {member.last_name or ''}".strip()),
            fmt("Gender", member.gender),
            fmt("Marital Status", member.marital_status),
            fmt("Role", member.role),
            fmt("Ministry", getattr(member, "ministry", None)),
            fmt("Status", member.status),
            fmt("Occupation", getattr(member, "occupation", None)),
            fmt("Employer", getattr(member, "employer", None)),
            fmt("Education", getattr(member, "education_level", None)),
            fmt("First Attended", getattr(member, "first_attended", None)),
            fmt("Membership Date", getattr(member, "membership_date", None)),
            fmt("Baptism Date", getattr(member, "baptism_date", None)),
            fmt("Notes", "; ".join([n.note for n in (member.notes or [])]) if isinstance(member.notes, list) else member.notes),
        ]

        member_block = " ".join(parts)
        member_block += "\n".join([d for d in data if d])
        return f"Member Profile\n{member_block}\n\nProvide personalized, actionable insights now."

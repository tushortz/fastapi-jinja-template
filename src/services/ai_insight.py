"""AI insight service for quote analysis."""

import logging
from typing import List

import httpx

from src.config import settings
from src.services.tagging.gemini import GeminiTagService
from src.services.tagging.local_ai import LocalTagService

logger = logging.getLogger(__name__)


class AIInsightService:
    """Service for providing AI insights on quotes."""

    def __init__(self) -> None:
        """Initialize the AI insight service."""
        self.ai_service = settings.ai_service

    async def analyze_quote(
        self,
        quote_text: str,
        tags: List[str] = None,
        book_title: str = "",
        notes: str = "",
    ) -> str:
        """Analyze a quote and provide insights."""
        logger.info("Analyzing quote: %s", quote_text[:50] + "...")

        if tags is None:
            tags = []

        try:
            # Use the configured AI service to generate insights
            if self.ai_service == "local":
                insight = await self._generate_insight_with_local_ai(
                    quote_text=quote_text, tags=tags, book_title=book_title, notes=notes
                )
            else:
                insight = await self._generate_insight_with_gemini(
                    quote_text=quote_text, tags=tags, book_title=book_title, notes=notes
                )

            logger.info("Successfully generated insight for quote")
            return insight

        except Exception as e:
            logger.error("Error generating insight: %s", str(e))
            # Return a fallback insight
            return self._generate_fallback_insight(quote_text, tags, book_title)

    async def _generate_insight_with_gemini(
        self, quote_text: str, tags: List[str], book_title: str, notes: str
    ) -> str:
        """Generate insight using Gemini AI."""
        try:
            gemini_service = GeminiTagService()

            # Create a comprehensive prompt for quote analysis
            prompt = self._build_analysis_prompt(quote_text, tags, book_title, notes)

            # Use the existing Gemini service to generate content
            if hasattr(gemini_service, "model") and gemini_service.model:
                response = gemini_service.model.generate_content(prompt)
                return response.text.strip()
            else:
                # Fallback if Gemini is not available
                return self._generate_fallback_insight(quote_text, tags, book_title)

        except Exception as e:
            logger.error("Gemini analysis failed: %s", str(e))
            return self._generate_fallback_insight(quote_text, tags, book_title)

    async def _generate_insight_with_local_ai(
        self, quote_text: str, tags: List[str], book_title: str, notes: str
    ) -> str:
        """Generate insight using local AI service."""
        try:
            local_service = LocalTagService()
            prompt = self._build_analysis_prompt(quote_text, tags, book_title, notes)

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{local_service.base_url}/v1/chat/completions",
                    json={
                        "model": settings.local_ai_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert quote analyst who provides insightful, structured analysis of quotes in HTML format.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.7,
                        "max_tokens": 1000,
                    },
                    timeout=120.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    return content.strip()
                else:
                    logger.error("Local AI API error: %s", response.status_code)
                    return self._generate_fallback_insight(quote_text, tags, book_title)

        except Exception as e:
            logger.error("Local AI analysis failed: %s", str(e))
            return self._generate_fallback_insight(quote_text, tags, book_title)

    def _build_analysis_prompt(
        self, quote_text: str, tags: List[str], book_title: str, notes: str
    ) -> str:
        """Build a comprehensive prompt for quote analysis."""
        prompt = f"""
        Analyze this quote and provide insightful commentary that would be beneficial for the reader. Give example from the Bible where applicable:

        Quote: "{quote_text}"
        """

        if book_title:
            prompt += f"From the book: {book_title}\n"

        if tags:
            prompt += f"Tags: {', '.join(tags)}\n"

        if notes:
            prompt += f"Reader's notes: {notes}\n"

        prompt += """
        provide your analysis without code blocks in HTML format with the following structure:

        <div class="quote-analysis">
            <h3>📖 Quote Interpretation</h3>
            <p>[Your interpretation of the quote's meaning]</p>

            <h3>🎯 Key Themes</h3>
            <p>[Main themes and concepts addressed]</p>

            <h3>💡 Practical Applications</h3>
            <p>[How to apply this wisdom in daily life giving examples from the Bible where applicable]</p>

            <h3>🌱 Personal Growth</h3>
            <p>[How this relates to personal development and reflection]</p>
        </div>

        Use appropriate HTML tags like <h3>, <p>, <strong>, <em>, <ul>, <li>, <i>, <b>, <br> for formatting.
        Keep each section concise but meaningful.
        Focus on actionable insights that help the reader reflect and grow.
        """

        return prompt.strip()

    def _generate_fallback_insight(
        self, quote_text: str, tags: List[str], book_title: str
    ) -> str:
        """Generate a simple fallback insight when AI is unavailable."""
        insight_parts = []

        # Basic analysis based on quote length and content
        if len(quote_text) > 100:
            insight_parts.append(
                "This is a substantial quote that likely contains deeper meaning worth reflecting on."
            )
        else:
            insight_parts.append("This concise quote packs meaningful insight.")

        # Add context based on tags
        if tags:
            tag_context = {
                "wisdom": "This quote offers timeless wisdom that can guide your thinking.",
                "motivation": "This motivational quote can inspire action and positive change.",
                "philosophy": "This philosophical quote invites deeper contemplation about life.",
                "success": "This quote provides valuable insights about achieving success.",
                "relationships": "This quote offers wisdom about human connections.",
                "learning": "This quote emphasizes the importance of continuous learning.",
            }

            for tag in tags:
                if tag.lower() in tag_context:
                    insight_parts.append(tag_context[tag.lower()])
                    break

        # Add book context
        if book_title:
            insight_parts.append(
                f"From '{book_title}', this quote represents the author's perspective on important themes."
            )

        # Default insight
        if not insight_parts:
            insight_parts.append(
                "This quote offers valuable perspective worth considering in your daily life."
            )

        # Format as HTML
        html_content = f"""
        <div class="quote-analysis">
            <h3>📖 Quote Interpretation</h3>
            <p>{insight_parts[0]}</p>

            <h3>🎯 Key Themes</h3>
            <p>This quote addresses important themes worth reflecting on.</p>

            <h3>💡 Practical Applications</h3>
            <p>Consider how this wisdom applies to your daily experiences and decision-making.</p>

            <h3>🌱 Personal Growth</h3>
            <p>{" ".join(insight_parts[1:]) if len(insight_parts) > 1 else insight_parts[0]} Take time to reflect on how it applies to your own experiences and goals.</p>
        </div>
        """

        return html_content.strip()

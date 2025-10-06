"""AI analysis endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.auth import get_current_active_user
from src.models.users import User
from src.services.ai_insight import AIInsightService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


class QuoteAnalysisRequest(BaseModel):
    """Request model for quote analysis."""

    quote_text: str
    tags: list[str] = []
    book_title: str = ""
    notes: str = ""


class QuoteAnalysisResponse(BaseModel):
    """Response model for quote analysis."""

    insight: str
    analysis_type: str = "general"


@router.post(
    "/analyze-quote", response_model=QuoteAnalysisResponse, name="api_ai_analyze_quote"
)
async def analyze_quote(
    request: QuoteAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    ai_service: AIInsightService = Depends(),
):
    """Analyze a quote and provide AI insights."""
    logger.info("AI quote analysis requested by user: %s", current_user.username)

    try:
        insight = await ai_service.analyze_quote(
            quote_text=request.quote_text,
            tags=request.tags,
            book_title=request.book_title,
            notes=request.notes,
        )

        return QuoteAnalysisResponse(insight=insight, analysis_type="general")

    except Exception as e:
        logger.error("Error analyzing quote: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze quote",
        ) from e

"""Image conversion API endpoints."""

import base64
import logging

import httpx
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()


class ImageConvertRequest(BaseModel):
    """Request model for image conversion."""

    image_url: str


class ImageConvertResponse(BaseModel):
    """Response model for image conversion."""

    base64_data_url: str


@router.post("/convert-image", response_model=ImageConvertResponse)
async def convert_image_to_base64(request: ImageConvertRequest) -> ImageConvertResponse:
    """
    Convert an image URL to base64 data URL.

    This endpoint fetches an image from a URL and converts it to a base64 data URL,
    avoiding CORS issues when fetching images from external sources.
    """
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(request.image_url)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to fetch image: HTTP {response.status_code}",
            )

        # Get content type from response headers
        content_type = response.headers.get("content-type", "image/jpeg")

        # Encode image data to base64
        image_data = base64.b64encode(response.content).decode("utf-8")
        base64_data_url = f"data:{content_type};base64,{image_data}"

        return ImageConvertResponse(base64_data_url=base64_data_url)

    except httpx.TimeoutException as exc:
        logger.error("Timeout fetching image from: %s", request.image_url)
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Timeout fetching image"
        ) from exc
    except httpx.RequestError as exc:
        logger.error(
            "Request error fetching image from %s: %s", request.image_url, str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch image"
        ) from exc
    except Exception as exc:
        logger.error(
            "Unexpected error converting image from %s: %s", request.image_url, str(exc)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from exc

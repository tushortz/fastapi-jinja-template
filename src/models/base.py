"""Base model with common fields."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from src.utils.date import get_current_date


class TimestampModel(BaseModel):
    """Base model with created_at and updated_at timestamps."""

    created_at: datetime = Field(default_factory=get_current_date)
    updated_at: datetime = Field(default_factory=get_current_date)

    def model_post_init(self, __context: Any) -> None:
        """Update updated_at timestamp on model initialization."""
        self.updated_at = get_current_date()

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        """Serialize datetime fields to ISO format."""
        return value.isoformat()

    model_config = ConfigDict(from_attributes=True)

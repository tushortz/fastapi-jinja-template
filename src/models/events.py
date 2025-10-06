"""Calendar and events models for church management."""

from datetime import date, datetime, time
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from .base import TimestampModel

# ==========================
# Event-related definitions
# ==========================


class CalendarEventBase(TimestampModel):
    """Base event model."""

    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str | None = Field(None, max_length=2000, description="Event description")
    # status and priority removed

    start_date: date = Field(..., description="Event start date")
    end_date: date | None = Field(None, description="Event end date")
    start_time: time | None = Field(None, description="Event start time")
    end_time: time | None = Field(None, description="Event end time")
    is_all_day: bool = Field(default=False, description="All day event")

    location: str | None = Field(None, max_length=500, description="Event location")
    organizer_id: str = Field(..., description="Organizer user id")
    calendar_id: str | None = Field(None, description="Parent calendar id")
    color: str | None = Field(None, max_length=7, description="Hex color")
    is_public: bool = Field(default=True, description="Public visibility")

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info: Any) -> date | None:
        if v is None:
            return v
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("End date must be after or equal to start date")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: time | None, info: Any) -> time | None:
        if v is None:
            return v
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("End time must be after start time")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
        return v


class CalendarEventCreate(CalendarEventBase):
    """Event creation model."""
    pass


class CalendarEventUpdate(TimestampModel):
    """Event update model."""

    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    # status and priority removed
    start_date: date | None = None
    end_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    is_all_day: bool | None = None
    location: str | None = Field(None, max_length=500)
    organizer_id: str | None = None
    calendar_id: str | None = None
    color: str | None = Field(None, max_length=7)
    is_public: bool | None = None
    # reminder removed

    @field_validator("end_date")
    @classmethod
    def validate_end_date(cls, v: date | None, info: Any) -> date | None:
        if v is None:
            return v
        start_date = info.data.get("start_date")
        if start_date and v < start_date:
            raise ValueError("End date must be after or equal to start date")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: time | None, info: Any) -> time | None:
        if v is None:
            return v
        start_time = info.data.get("start_time")
        if start_time and v <= start_time:
            raise ValueError("End time must be after start time")
        return v

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
        return v


class CalendarEventInDB(CalendarEventBase):
    """Event model for DB."""

    id: str


class CalendarEvent(CalendarEventBase):
    """Event model for API responses."""

    id: str


# Calendar models removed per requirements
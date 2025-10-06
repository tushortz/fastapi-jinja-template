"""Calendar and events models for church management."""

from datetime import date, datetime, time
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from .base import TimestampModel

# ==========================
# Event-related definitions
# ==========================

class EventType(str, Enum):
    """Event type enumeration."""

    WORSHIP_SERVICE = "worship_service"
    BIBLE_STUDY = "bible_study"
    PRAYER_MEETING = "prayer_meeting"
    OTHER = "other"


class EventStatus(str, Enum):
    """Event status enumeration."""

    PLANNED = "planned"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EventPriority(str, Enum):
    """Event priority enumeration."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CalendarEventBase(TimestampModel):
    """Base event model."""

    title: str = Field(..., min_length=1, max_length=200, description="Event title")
    description: str | None = Field(None, max_length=2000, description="Event description")
    event_type: EventType = Field(..., description="Type of event")
    status: EventStatus = Field(default=EventStatus.PLANNED, description="Event status")
    priority: EventPriority = Field(default=EventPriority.MEDIUM, description="Event priority")

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
    reminder_minutes: int | None = Field(None, ge=0, description="Reminder minutes")

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
    event_type: EventType | None = None
    status: EventStatus | None = None
    priority: EventPriority | None = None
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
    reminder_minutes: int | None = Field(None, ge=0)

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


# ======================
# Calendar definitions
# ======================

class CalendarBase(TimestampModel):
    """Base calendar model."""

    name: str = Field(..., min_length=1, max_length=100, description="Calendar name")
    description: str | None = Field(None, max_length=500, description="Calendar description")
    color: str = Field(default="#3B82F6", max_length=7, description="Hex color")
    is_default: bool = Field(default=False, description="Default calendar for owner")
    is_public: bool = Field(default=True, description="Public visibility")
    owner_id: str = Field(..., description="Owner user id")

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str) -> str:
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
        return v


class CalendarCreate(CalendarBase):
    """Calendar creation model."""
    pass


class CalendarUpdate(TimestampModel):
    """Calendar update model."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, max_length=7)
    is_default: bool | None = None
    is_public: bool | None = None

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.startswith("#") or len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
        return v


class CalendarInDB(CalendarBase):
    """Calendar model for DB."""

    id: str


class Calendar(CalendarBase):
    """Calendar model for API responses."""

    id: str
    event_count: int = Field(default=0, description="Number of events in calendar")
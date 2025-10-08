"""Attendance tracking models."""

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import Field, field_validator

from .base import TimestampModel


class AttendanceType(str, Enum):
    """Attendance type enumeration."""

    SUNDAY_SERVICE = "sunday service"
    BIBLE_STUDY = "bible study"
    WEDNESDAY_SERVICE = "wednesday service"
    PRAYER_MEETING = "prayer meeting"
    YOUTH_MEETING = "youth meeting"
    CHILDREN_CHURCH = "children church"
    CHOIR_REHEARSAL = "choir rehearsal"
    SPECIAL_EVENT = "special event"
    OTHER = "other"


class AttendanceBase(TimestampModel):
    """Base attendance model."""

    member_ids: list[str] = Field(..., description="List of member IDs who attended")
    attendance_date: date = Field(..., description="Date of attendance")
    attendance_type: AttendanceType = Field(..., description="Type of service/event")
    notes: str | None = Field(None, max_length=500, description="Additional notes")
    recorded_by: str = Field(..., description="ID of user who recorded the attendance")

    @field_validator("attendance_date")
    @classmethod
    def validate_attendance_date(cls, v: date) -> date:
        """Validate attendance date."""
        if v > date.today():
            raise ValueError("Attendance date cannot be in the future")
        return v


class AttendanceCreate(AttendanceBase):
    """Attendance creation model."""
    pass


class AttendanceUpdate(TimestampModel):
    """Attendance update model."""

    member_ids: list[str] | None = None
    attendance_date: date | None = None
    attendance_type: AttendanceType | None = None
    notes: str | None = Field(None, max_length=500)
    recorded_by: str | None = None

    @field_validator("attendance_date")
    @classmethod
    def validate_attendance_date(cls, v: date | None) -> date | None:
        """Validate attendance date."""
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Attendance date cannot be in the future")
        return v


class AttendanceInDB(AttendanceBase):
    """Attendance model for database storage."""

    id: str


class Attendance(AttendanceBase):
    """Attendance model for API responses."""

    id: str


class AttendanceSummary(TimestampModel):
    """Attendance summary model for reporting."""

    member_id: str
    member_name: str
    total_services: int = 0
    attendance_count: int = 0
    attendance_rate: float = 0.0
    period_start: date
    period_end: date

    def calculate_attendance_rate(self) -> float:
        """Calculate attendance rate percentage."""
        if self.total_services == 0:
            return 0.0
        return (self.attendance_count / self.total_services) * 100


class ServiceAttendance(TimestampModel):
    """Service attendance model for tracking attendance by service."""

    service_date: date
    service_type: AttendanceType
    total_members: int = 0
    attended_members: int = 0
    attendance_rate: float = 0.0
    recorded_by: str
    notes: str | None = None

    def calculate_attendance_rate(self) -> float:
        """Calculate attendance rate percentage."""
        if self.total_members == 0:
            return 0.0
        return (self.attended_members / self.total_members) * 100


class MemberAttendanceSummaryRepo(TimestampModel):
    """Member attendance summary model for repository operations."""

    member_id: str
    total_services: int = 0
    attendance_count: int = 0
    attendance_rate: float = 0.0
    start_date: date
    end_date: date


class ServiceAttendanceSummaryRepo(TimestampModel):
    """Service attendance summary model for repository operations."""

    service_date: date
    service_type: AttendanceType
    total_members: int = 0
    attended_members: int = 0
    attendance_rate: float = 0.0


class AttendanceTrend(TimestampModel):
    """Attendance trend model for reporting."""

    date: str  # ISO date string
    service_type: AttendanceType
    total_members: int = 0
    attended_count: int = 0
    attendance_rate: float = 0.0


class AttendanceStatistics(TimestampModel):
    """Attendance statistics model."""

    total_records: int = 0
    total_attended: int = 0
    attendance_rate: float = 0.0
    period_start: date | None = None
    period_end: date | None = None


class BulkAttendanceResult(TimestampModel):
    """Bulk attendance creation result model."""

    created_count: int = 0
    failed_count: int = 0
    total_processed: int = 0
    errors: list[str] = Field(default_factory=list)
    success: bool = True
    message: str = "Bulk attendance records processed successfully"

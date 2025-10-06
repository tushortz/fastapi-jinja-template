"""Attendance API endpoints."""

import logging
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_user
from src.models.attendance import (
    Attendance, AttendanceCreate, AttendanceStatus, AttendanceSummary, AttendanceType,
    AttendanceUpdate, ServiceAttendance,
)
from src.models.users import User
from src.services.attendance import AttendanceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/attendance", tags=["attendance"])
@router.get("/enums/types", name="api_get_attendance_types")
async def get_attendance_types() -> list[str]:
    """Return list of attendance types (enum values)."""
    return [t.value for t in AttendanceType]


@router.get("/enums/statuses", name="api_get_attendance_statuses")
async def get_attendance_statuses() -> list[str]:
    """Return list of attendance statuses (enum values)."""
    return [s.value for s in AttendanceStatus]



@router.post("/", response_model=Attendance, status_code=status.HTTP_201_CREATED, name="api_create_attendance")
async def create_attendance(
    attendance_create: AttendanceCreate,
    current_user: User = Depends(get_current_user),
) -> Attendance:
    """Create a new attendance record."""
    logger.info(
        "Creating attendance record for member %s on %s",
        attendance_create.member_id,
        attendance_create.attendance_date,
    )

    try:
        attendance_service = AttendanceService()
        attendance = await attendance_service.create_attendance(attendance_create)
        logger.info("Attendance record created successfully: %s", attendance.id)
        return attendance
    except ValueError as e:
        logger.warning("Failed to create attendance record: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating attendance record: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=list[Attendance], name="api_get_attendance_records")
async def get_attendance_records(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: str | None = Query(None, description="Search term"),
    member_id: str | None = Query(None, description="Filter by member ID"),
    attendance_type: AttendanceType | None = Query(None, description="Filter by attendance type"),
    status: AttendanceStatus | None = Query(None, description="Filter by attendance status"),
    current_user: User = Depends(get_current_user),
) -> list[Attendance]:
    """Get all attendance records with pagination and optional filters."""
    logger.debug("Getting attendance records: skip=%d, limit=%d", skip, limit)

    try:
        attendance_service = AttendanceService()
        attendance_records = await attendance_service.get_attendance_records(
            skip=skip, limit=limit, search=search, member_id=member_id,
            attendance_type=attendance_type, status=status
        )
        logger.info("Retrieved %d attendance records", len(attendance_records))
        return attendance_records
    except Exception as e:
        logger.error("Error getting attendance records: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/by-date/{attendance_date}", response_model=list[Attendance], name="api_get_attendance_by_date")
async def get_attendance_by_date(
    attendance_date: date,
    attendance_type: AttendanceType | None = Query(None, description="Filter by attendance type"),
    current_user: User = Depends(get_current_user),
) -> list[Attendance]:
    """Get attendance records for a specific date."""
    logger.debug("Getting attendance records for date: %s", attendance_date)

    try:
        attendance_service = AttendanceService()
        attendance_records = await attendance_service.get_attendance_by_date(
            attendance_date, attendance_type
        )
        logger.info("Retrieved %d attendance records for date %s", len(attendance_records), attendance_date)
        return attendance_records
    except Exception as e:
        logger.error("Error getting attendance by date: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/by-date-range", response_model=list[Attendance], name="api_get_attendance_by_date_range")
async def get_attendance_by_date_range(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    member_id: str | None = Query(None, description="Filter by member ID"),
    attendance_type: AttendanceType | None = Query(None, description="Filter by attendance type"),
    current_user: User = Depends(get_current_user),
) -> list[Attendance]:
    """Get attendance records for a date range."""
    logger.debug("Getting attendance records from %s to %s", start_date, end_date)

    try:
        attendance_service = AttendanceService()
        attendance_records = await attendance_service.get_attendance_by_date_range(
            start_date, end_date, member_id, attendance_type
        )
        logger.info("Retrieved %d attendance records for date range", len(attendance_records))
        return attendance_records
    except Exception as e:
        logger.error("Error getting attendance by date range: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/member/{member_id}", response_model=list[Attendance], name="api_get_member_attendance")
async def get_member_attendance(
    member_id: str,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
) -> list[Attendance]:
    """Get attendance records for a specific member."""
    logger.debug("Getting attendance records for member: %s", member_id)

    try:
        attendance_service = AttendanceService()
        attendance_records = await attendance_service.get_member_attendance(
            member_id, skip=skip, limit=limit
        )
        logger.info("Retrieved %d attendance records for member %s", len(attendance_records), member_id)
        return attendance_records
    except Exception as e:
        logger.error("Error getting member attendance: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/member/{member_id}/summary", response_model=AttendanceSummary, name="api_get_member_attendance_summary")
async def get_member_attendance_summary(
    member_id: str,
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    current_user: User = Depends(get_current_user),
) -> AttendanceSummary:
    """Get attendance summary for a member in a date range."""
    logger.debug(
        "Getting attendance summary for member %s from %s to %s",
        member_id, start_date, end_date
    )

    try:
        attendance_service = AttendanceService()
        summary = await attendance_service.get_member_attendance_summary(
            member_id, start_date, end_date
        )
        logger.info("Retrieved attendance summary for member %s", member_id)
        return summary
    except Exception as e:
        logger.error("Error getting member attendance summary: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/service-summary", response_model=ServiceAttendance, name="api_get_service_attendance_summary")
async def get_service_attendance_summary(
    attendance_date: date = Query(..., description="Service date"),
    attendance_type: AttendanceType = Query(..., description="Service type"),
    current_user: User = Depends(get_current_user),
) -> ServiceAttendance:
    """Get attendance summary for a specific service."""
    logger.debug(
        "Getting service attendance summary for %s on %s",
        attendance_type, attendance_date
    )

    try:
        attendance_service = AttendanceService()
        summary = await attendance_service.get_service_attendance_summary(
            attendance_date, attendance_type
        )
        logger.info("Retrieved service attendance summary")
        return summary
    except Exception as e:
        logger.error("Error getting service attendance summary: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/statistics", name="api_get_attendance_statistics")
async def get_attendance_statistics(
    start_date: date | None = Query(None, description="Start date for statistics"),
    end_date: date | None = Query(None, description="End date for statistics"),
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get attendance statistics."""
    logger.debug("Getting attendance statistics")

    try:
        attendance_service = AttendanceService()
        stats = await attendance_service.get_attendance_statistics(start_date, end_date)
        logger.info("Retrieved attendance statistics")
        return stats
    except Exception as e:
        logger.error("Error getting attendance statistics: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/trends", name="api_get_attendance_trends")
async def get_attendance_trends(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    attendance_type: AttendanceType | None = Query(None, description="Filter by attendance type"),
    current_user: User = Depends(get_current_user),
) -> list[dict[str, Any]]:
    """Get attendance trends over time."""
    logger.debug("Getting attendance trends from %s to %s", start_date, end_date)

    try:
        attendance_service = AttendanceService()
        trends = await attendance_service.get_attendance_trends(
            start_date, end_date, attendance_type
        )
        logger.info("Retrieved %d attendance trend records", len(trends))
        return trends
    except Exception as e:
        logger.error("Error getting attendance trends: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{attendance_id}", response_model=Attendance, name="api_get_attendance")
async def get_attendance(
    attendance_id: str,
    current_user: User = Depends(get_current_user),
) -> Attendance:
    """Get a specific attendance record by ID."""
    logger.debug("Getting attendance record by ID: %s", attendance_id)

    try:
        attendance_service = AttendanceService()
        attendance = await attendance_service.get_attendance_by_id(attendance_id)
        if not attendance:
            logger.warning("Attendance record not found: %s", attendance_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        logger.info("Retrieved attendance record: %s", attendance_id)
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting attendance record: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{attendance_id}", response_model=Attendance, name="api_update_attendance")
async def update_attendance(
    attendance_id: str,
    attendance_update: AttendanceUpdate,
    current_user: User = Depends(get_current_user),
) -> Attendance:
    """Update an attendance record."""
    logger.info("Updating attendance record: %s", attendance_id)

    try:
        attendance_service = AttendanceService()
        attendance = await attendance_service.update_attendance(attendance_id, attendance_update)
        if not attendance:
            logger.warning("Attendance record not found for update: %s", attendance_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        logger.info("Attendance record updated successfully: %s", attendance_id)
        return attendance
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating attendance record: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT, name="api_delete_attendance")
async def delete_attendance(
    attendance_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete an attendance record."""
    logger.info("Deleting attendance record: %s", attendance_id)

    try:
        attendance_service = AttendanceService()
        success = await attendance_service.delete_attendance(attendance_id)
        if not success:
            logger.warning("Attendance record not found for deletion: %s", attendance_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Attendance record not found"
            )

        logger.info("Attendance record deleted successfully: %s", attendance_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting attendance record: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Note: HTML-rendering pages are defined under /dashboard in web_routes.py

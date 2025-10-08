"""Attendance service for business logic."""

import logging
from datetime import date, datetime
from typing import Any

from src.models.attendance import (
    Attendance, AttendanceCreate, AttendanceInDB, AttendanceStatistics,
    AttendanceSummary, AttendanceTrend, AttendanceType, AttendanceUpdate,
    BulkAttendanceResult, MemberAttendanceSummaryRepo, ServiceAttendance,
    ServiceAttendanceSummaryRepo,
)
from src.repositories.attendance import AttendanceRepository
from src.utils.date import get_current_date

logger = logging.getLogger(__name__)


class AttendanceService:
    """Attendance service for business logic operations."""

    def __init__(self):
        self.attendance_repo = AttendanceRepository()

    async def create_attendance(self, attendance_create: AttendanceCreate) -> Attendance:
        """Create a new attendance record."""
        logger.info(
            "Creating attendance record for %d members on %s",
            len(attendance_create.member_ids),
            attendance_create.attendance_date,
        )

        # Check if attendance record already exists
        if await self.attendance_repo.check_attendance_exists(
            attendance_create.attendance_date,
            attendance_create.attendance_type,
        ):
            logger.warning(
                "Attendance record already exists on %s for %s",
                attendance_create.attendance_date,
                attendance_create.attendance_type,
            )
            raise ValueError("Attendance record already exists for this service")

        # Create attendance record
        attendance_in_db = await self.attendance_repo.create(attendance_create)
        logger.info(
            "Attendance record created successfully: %d members (ID: %s)",
            len(attendance_in_db.member_ids),
            attendance_in_db.id,
        )

        return Attendance(
            id=attendance_in_db.id,
            member_ids=attendance_in_db.member_ids,
            attendance_date=attendance_in_db.attendance_date,
            attendance_type=attendance_in_db.attendance_type,
            notes=attendance_in_db.notes,
            recorded_by=attendance_in_db.recorded_by,
            created_at=attendance_in_db.created_at,
            updated_at=attendance_in_db.updated_at,
        )

    async def create_bulk_attendance(self, bulk_data: dict[str, Any]) -> BulkAttendanceResult:
        """Create attendance record for multiple members at once."""
        logger.info(
            "Creating bulk attendance records for %d members on %s",
            len(bulk_data.get("member_ids", [])),
            bulk_data.get("attendance_date"),
        )

        attendance_date = bulk_data.get("attendance_date")
        attendance_type = bulk_data.get("attendance_type")
        recorded_by = bulk_data.get("recorded_by")
        notes = bulk_data.get("notes", "")
        member_ids = bulk_data.get("member_ids", [])

        if not attendance_date or not attendance_type or not recorded_by:
            raise ValueError("Missing required fields: attendance_date, attendance_type, or recorded_by")

        if not member_ids:
            raise ValueError("No members provided for bulk attendance")

        # Convert string date to date object if needed
        if isinstance(attendance_date, str):
            try:
                attendance_date = date.fromisoformat(attendance_date)
            except ValueError as e:
                raise ValueError(f"Invalid date format: {attendance_date}. Expected YYYY-MM-DD format.")

        try:
            # Check if attendance record already exists for this date and type
            if await self.attendance_repo.check_attendance_exists(attendance_date, attendance_type):
                logger.warning(
                    "Attendance record already exists for %s on %s",
                    attendance_type, attendance_date
                )
                return BulkAttendanceResult(
                    created_count=0,
                    failed_count=len(member_ids),
                    total_processed=len(member_ids),
                    errors=[f"Attendance already exists for {attendance_type} on {attendance_date}"],
                    success=False,
                    message=f"Attendance already exists for {attendance_type} on {attendance_date}",
                    created_at=get_current_date(),
                    updated_at=get_current_date()
                )

            # Create attendance record
            attendance_create = AttendanceCreate(
                member_ids=member_ids,
                attendance_date=attendance_date,
                attendance_type=attendance_type,
                notes=notes,
                recorded_by=recorded_by
            )

            await self.attendance_repo.create(attendance_create)

            logger.info(
                "Bulk attendance creation completed: %d members recorded",
                len(member_ids)
            )

            return BulkAttendanceResult(
                created_count=len(member_ids),
                failed_count=0,
                total_processed=len(member_ids),
                errors=[],
                success=True,
                message=f"Successfully recorded attendance for {len(member_ids)} members",
                created_at=get_current_date(),
                updated_at=get_current_date()
            )

        except Exception as e:
            logger.error("Error creating bulk attendance: %s", str(e))
            return BulkAttendanceResult(
                created_count=0,
                failed_count=len(member_ids),
                total_processed=len(member_ids),
                errors=[f"Error creating attendance: {str(e)}"],
                success=False,
                message=f"Failed to create attendance: {str(e)}",
                created_at=get_current_date(),
                updated_at=get_current_date()
            )

    async def get_attendance_by_id(self, attendance_id: str) -> dict | None:
        """Get attendance record by ID with user data."""
        logger.debug("Getting attendance record by ID: %s", attendance_id)

        try:
            # Use the new repository method that includes user data
            attendance_data = await self.attendance_repo.get_attendance_with_user(attendance_id)
            if not attendance_data:
                logger.warning("Attendance record not found: %s", attendance_id)
                return None

            logger.info("Attendance record retrieved successfully: %s", attendance_id)
            return attendance_data

        except Exception as e:
            logger.error("Error getting attendance record: %s", str(e))
            return None

    async def update_attendance(
        self, attendance_id: str, attendance_update: AttendanceUpdate
    ) -> Attendance | None:
        """Update attendance record."""
        logger.info("Updating attendance record: %s", attendance_id)

        attendance_in_db = await self.attendance_repo.update(attendance_id, attendance_update)
        if not attendance_in_db:
            logger.warning("Attendance record not found for update: %s", attendance_id)
            return None

        logger.info("Attendance record updated successfully: %s", attendance_in_db.id)
        return Attendance(
            id=attendance_in_db.id,
            member_ids=attendance_in_db.member_ids,
            attendance_date=attendance_in_db.attendance_date,
            attendance_type=attendance_in_db.attendance_type,
            notes=attendance_in_db.notes,
            recorded_by=attendance_in_db.recorded_by,
            created_at=attendance_in_db.created_at,
            updated_at=attendance_in_db.updated_at,
        )

    async def delete_attendance(self, attendance_id: str) -> bool:
        """Delete attendance record."""
        logger.info("Deleting attendance record: %s", attendance_id)
        try:
            result = await self.attendance_repo.delete(attendance_id)
            if result:
                logger.info("Attendance record deleted successfully: %s", attendance_id)
            else:
                logger.warning("Attendance record not found for deletion: %s", attendance_id)
            return result
        except Exception as e:
            logger.error("Error deleting attendance record: %s", str(e))
            raise

    async def get_member_attendance(
        self, member_id: str, skip: int = 0, limit: int = 100
    ) -> list[Attendance]:
        """Get attendance records for a specific member."""
        logger.debug("Getting attendance records for member: %s", member_id)
        attendance_records = await self.attendance_repo.get_by_member_id(
            member_id, skip=skip, limit=limit
        )

        return [
            Attendance(
                id=record.id,
                member_ids=record.member_ids,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def get_attendance_by_date(
        self, attendance_date: date, attendance_type: AttendanceType | None = None
    ) -> list[Attendance]:
        """Get attendance records for a specific date."""
        logger.debug("Getting attendance records for date: %s", attendance_date)
        attendance_records = await self.attendance_repo.get_by_date(
            attendance_date, attendance_type
        )

        return [
            Attendance(
                id=record.id,
                member_ids=record.member_ids,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def get_attendance_by_date_range(
        self,
        start_date: date,
        end_date: date,
        member_id: str | None = None,
        attendance_type: AttendanceType | None = None,
    ) -> list[Attendance]:
        """Get attendance records for a date range."""
        logger.debug(
            "Getting attendance records from %s to %s", start_date, end_date
        )
        attendance_records = await self.attendance_repo.get_by_date_range(
            start_date, end_date, member_id, attendance_type
        )

        return [
            Attendance(
                id=record.id,
                member_ids=record.member_ids,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def get_member_attendance_summary(
        self, member_id: str, start_date: date, end_date: date
    ) -> AttendanceSummary:
        """Get attendance summary for a member in a date range."""
        logger.debug(
            "Getting attendance summary for member %s from %s to %s",
            member_id, start_date, end_date
        )

        summary_data = await self.attendance_repo.get_member_attendance_summary(
            member_id, start_date, end_date
        )

        # Convert repository model to service model
        summary = AttendanceSummary(
            member_id=summary_data.member_id,
            member_name="",  # Will be populated by the calling service
            total_services=summary_data.total_services,
            attendance_count=summary_data.attendance_count,
            attendance_rate=summary_data.attendance_rate,
            period_start=summary_data.start_date,
            period_end=summary_data.end_date,
            created_at=summary_data.created_at,
            updated_at=summary_data.updated_at,
        )

        return summary

    async def get_service_attendance_summary(
        self, attendance_date: date, attendance_type: AttendanceType
    ) -> ServiceAttendance:
        """Get attendance summary for a specific service."""
        logger.debug(
            "Getting service attendance summary for %s on %s",
            attendance_type, attendance_date
        )

        summary_data = await self.attendance_repo.get_service_attendance_summary(
            attendance_date, attendance_type
        )

        # Create ServiceAttendance object
        service_attendance = ServiceAttendance(
            service_date=summary_data.service_date,
            service_type=summary_data.service_type,
            total_members=summary_data.total_members,
            present_members=summary_data.present_members,
            absent_members=summary_data.absent_members,
            late_members=summary_data.late_members,
            excused_members=summary_data.excused_members,
            attendance_rate=summary_data.attendance_rate,
            recorded_by="",  # Will be populated by the calling service
            notes=None,
            created_at=summary_data.created_at,
            updated_at=summary_data.updated_at,
        )

        return service_attendance

    async def get_attendance_records(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        member_id: str | None = None,
        attendance_type: AttendanceType | None = None,
    ) -> list[Attendance]:
        """Get attendance records with pagination and filters."""
        logger.debug("Getting attendance records with filters")

        filter_dict: dict[str, Any] = {}
        if member_id:
            filter_dict["member_ids"] = member_id
        if attendance_type:
            filter_dict["attendance_type"] = attendance_type

        attendance_records = await self.attendance_repo.get_many(
            skip=skip, limit=limit, search=search, filter_dict=filter_dict
        )

        return [
            Attendance(
                id=record.id,
                member_ids=record.member_ids,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def get_recent_attendance(self, limit: int = 50) -> list[Attendance]:
        """Get recent attendance records."""
        logger.debug("Getting recent attendance records")
        attendance_records = await self.attendance_repo.get_recent_attendance(limit)

        return [
            Attendance(
                id=record.id,
                member_ids=record.member_ids,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def count_attendance_records(
        self,
        attendance_type: AttendanceType | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> int:
        """Count attendance records with optional filters."""
        logger.debug("Counting attendance records with filters")
        try:
            filter_dict: dict[str, Any] = {}
            if attendance_type:
                filter_dict["attendance_type"] = attendance_type

            # Get all records first, then apply date filtering
            all_records = await self.attendance_repo.get_many(limit=10000)  # Large limit to get all

            if start_date or end_date:
                filtered_count = 0
                for record in all_records:
                    record_date = record.attendance_date
                    if start_date and record_date < start_date:
                        continue
                    if end_date and record_date > end_date:
                        continue
                    filtered_count += 1
                return filtered_count

            return len(all_records)
        except Exception as e:
            logger.error("Error counting attendance records: %s", str(e))
            raise

    async def get_attendance_trends(
        self, start_date: date, end_date: date, attendance_type: AttendanceType | None = None
    ) -> list[dict[str, Any]]:
        """Get attendance trends over time."""
        logger.info("Getting attendance trends from %s to %s", start_date, end_date)
        try:
            trends = await self.attendance_repo.get_attendance_trends(
                start_date, end_date, attendance_type
            )
            logger.info("Retrieved %d attendance trend records", len(trends))
            return trends
        except Exception as e:
            logger.error("Error getting attendance trends: %s", str(e))
            raise

    async def get_attendance_statistics(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> AttendanceStatistics:
        """Get attendance statistics."""
        logger.info("Getting attendance statistics")
        try:
            # Get total records count
            total_records = await self.attendance_repo.count()

            # Get total attended count (sum of all member_ids across all records)
            # This is a simplified approach - in practice you might want to count unique members
            total_attended = 0
            attendance_records = await self.attendance_repo.get_many(limit=1000)
            for record in attendance_records:
                total_attended += len(record.member_ids)

            attendance_rate = (total_attended / total_records * 100) if total_records > 0 else 0.0

            return AttendanceStatistics(
                total_records=total_records,
                total_attended=total_attended,
                attendance_rate=round(attendance_rate, 2),
                period_start=start_date,
                period_end=end_date,
                created_at=get_current_date(),
                updated_at=get_current_date()
            )
        except Exception as e:
            logger.error("Error getting attendance statistics: %s", str(e))
            raise

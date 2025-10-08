"""Attendance service for business logic."""

import logging
from datetime import date, datetime
from typing import Any

from src.models.attendance import (
    Attendance, AttendanceCreate, AttendanceInDB, AttendanceStatistics,
    AttendanceStatus, AttendanceSummary, AttendanceTrend, AttendanceType,
    AttendanceUpdate, BulkAttendanceResult, MemberAttendanceSummaryRepo,
    ServiceAttendance, ServiceAttendanceSummaryRepo,
)
from src.repositories.attendance import AttendanceRepository

logger = logging.getLogger(__name__)


class AttendanceService:
    """Attendance service for business logic operations."""

    def __init__(self):
        self.attendance_repo = AttendanceRepository()

    async def create_attendance(self, attendance_create: AttendanceCreate) -> Attendance:
        """Create a new attendance record."""
        logger.info(
            "Creating attendance record for member %s on %s",
            attendance_create.member_id,
            attendance_create.attendance_date,
        )

        # Check if attendance record already exists
        if await self.attendance_repo.check_attendance_exists(
            attendance_create.member_id,
            attendance_create.attendance_date,
            attendance_create.attendance_type,
        ):
            logger.warning(
                "Attendance record already exists for member %s on %s for %s",
                attendance_create.member_id,
                attendance_create.attendance_date,
                attendance_create.attendance_type,
            )
            raise ValueError("Attendance record already exists for this service")

        # Create attendance record
        attendance_in_db = await self.attendance_repo.create(attendance_create)
        logger.info(
            "Attendance record created successfully: %s (ID: %s)",
            attendance_in_db.member_id,
            attendance_in_db.id,
        )

        return Attendance(
            id=attendance_in_db.id,
            member_id=attendance_in_db.member_id,
            attendance_date=attendance_in_db.attendance_date,
            attendance_type=attendance_in_db.attendance_type,
            status=attendance_in_db.status,
            notes=attendance_in_db.notes,
            recorded_by=attendance_in_db.recorded_by,
            created_at=attendance_in_db.created_at,
            updated_at=attendance_in_db.updated_at,
        )

    async def create_bulk_attendance(self, bulk_data: dict[str, Any]) -> BulkAttendanceResult:
        """Create multiple attendance records at once."""
        logger.info(
            "Creating bulk attendance records for %d members on %s",
            len(bulk_data.get("members", [])),
            bulk_data.get("attendance_date"),
        )

        attendance_date = bulk_data.get("attendance_date")
        attendance_type = bulk_data.get("attendance_type")
        recorded_by = bulk_data.get("recorded_by")
        notes = bulk_data.get("notes", "")
        members = bulk_data.get("members", [])

        if not attendance_date or not attendance_type or not recorded_by:
            raise ValueError("Missing required fields: attendance_date, attendance_type, or recorded_by")

        if not members:
            raise ValueError("No members provided for bulk attendance")

        created_count = 0
        failed_count = 0
        errors = []

        for member_data in members:
            try:
                member_id = member_data.get("member_id")
                status = member_data.get("status")

                if not member_id or not status:
                    errors.append(f"Missing member_id or status for member: {member_data}")
                    failed_count += 1
                    continue

                # Check if attendance record already exists
                if await self.attendance_repo.check_attendance_exists(
                    member_id, attendance_date, attendance_type
                ):
                    logger.warning(
                        "Attendance record already exists for member %s on %s for %s",
                        member_id, attendance_date, attendance_type
                    )
                    errors.append(f"Attendance already exists for member {member_id}")
                    failed_count += 1
                    continue

                # Create attendance record
                attendance_create = AttendanceCreate(
                    member_id=member_id,
                    attendance_date=attendance_date,
                    attendance_type=attendance_type,
                    status=status,
                    notes=notes,
                    recorded_by=recorded_by
                )

                await self.attendance_repo.create(attendance_create)
                created_count += 1

            except Exception as e:
                logger.error("Error creating attendance for member %s: %s", member_data.get("member_id"), str(e))
                errors.append(f"Error for member {member_data.get('member_id')}: {str(e)}")
                failed_count += 1

        logger.info(
            "Bulk attendance creation completed: %d created, %d failed",
            created_count, failed_count
        )

        success = failed_count == 0
        message = f"Successfully created {created_count} attendance records" if success else f"Created {created_count} records, {failed_count} failed"

        return BulkAttendanceResult(
            created_count=created_count,
            failed_count=failed_count,
            total_processed=len(members),
            errors=errors,
            success=success,
            message=message,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    async def get_attendance_by_id(self, attendance_id: str) -> Attendance | None:
        """Get attendance record by ID."""
        logger.debug("Getting attendance record by ID: %s", attendance_id)
        attendance_in_db = await self.attendance_repo.get_by_id(attendance_id)
        if not attendance_in_db:
            return None

        return Attendance(
            id=attendance_in_db.id,
            member_id=attendance_in_db.member_id,
            attendance_date=attendance_in_db.attendance_date,
            attendance_type=attendance_in_db.attendance_type,
            status=attendance_in_db.status,
            notes=attendance_in_db.notes,
            recorded_by=attendance_in_db.recorded_by,
            created_at=attendance_in_db.created_at,
            updated_at=attendance_in_db.updated_at,
        )

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
            member_id=attendance_in_db.member_id,
            attendance_date=attendance_in_db.attendance_date,
            attendance_type=attendance_in_db.attendance_type,
            status=attendance_in_db.status,
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
                member_id=record.member_id,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                status=record.status,
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
                member_id=record.member_id,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                status=record.status,
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
                member_id=record.member_id,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                status=record.status,
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
            present_count=summary_data.present_count,
            absent_count=summary_data.absent_count,
            late_count=summary_data.late_count,
            excused_count=summary_data.excused_count,
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
        status: AttendanceStatus | None = None,
    ) -> list[Attendance]:
        """Get attendance records with pagination and filters."""
        logger.debug("Getting attendance records with filters")

        filter_dict: dict[str, Any] = {}
        if member_id:
            filter_dict["member_id"] = member_id
        if attendance_type:
            filter_dict["attendance_type"] = attendance_type
        if status:
            filter_dict["status"] = status

        attendance_records = await self.attendance_repo.get_many(
            skip=skip, limit=limit, search=search, filter_dict=filter_dict
        )

        return [
            Attendance(
                id=record.id,
                member_id=record.member_id,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                status=record.status,
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
                member_id=record.member_id,
                attendance_date=record.attendance_date,
                attendance_type=record.attendance_type,
                status=record.status,
                notes=record.notes,
                recorded_by=record.recorded_by,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record in attendance_records
        ]

    async def count_attendance_by_status(
        self, status: AttendanceStatus, start_date: date | None = None, end_date: date | None = None
    ) -> int:
        """Count attendance records by status."""
        logger.info("Counting attendance records by status: %s", status)
        try:
            count = await self.attendance_repo.count_by_status(status, start_date, end_date)
            logger.info("Attendance count for status %s: %d", status, count)
            return count
        except Exception as e:
            logger.error("Error counting attendance by status: %s", str(e))
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
            # Get counts by status
            present_count = await self.count_attendance_by_status(
                AttendanceStatus.PRESENT, start_date, end_date
            )
            absent_count = await self.count_attendance_by_status(
                AttendanceStatus.ABSENT, start_date, end_date
            )
            late_count = await self.count_attendance_by_status(
                AttendanceStatus.LATE, start_date, end_date
            )
            excused_count = await self.count_attendance_by_status(
                AttendanceStatus.EXCUSED, start_date, end_date
            )

            total_records = present_count + absent_count + late_count + excused_count
            attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0

            return AttendanceStatistics(
                total_records=total_records,
                present_count=present_count,
                absent_count=absent_count,
                late_count=late_count,
                excused_count=excused_count,
                attendance_rate=round(attendance_rate, 2),
                period_start=start_date,
                period_end=end_date,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        except Exception as e:
            logger.error("Error getting attendance statistics: %s", str(e))
            raise

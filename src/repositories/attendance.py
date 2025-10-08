"""Attendance repository."""

import logging
from datetime import date, datetime
from typing import Any

from pydantic import BaseModel

from src.models.attendance import (
    AttendanceInDB, AttendanceStatistics, AttendanceTrend, AttendanceType,
    MemberAttendanceSummaryRepo, ServiceAttendanceSummaryRepo,
)
from src.repositories.users import UserRepository
from src.utils.date import get_current_date

from .base import BaseRepository

logger = logging.getLogger(__name__)


class AttendanceRepository(BaseRepository):
    """Attendance repository for database operations."""

    def __init__(self):
        super().__init__(AttendanceInDB, "attendance")
        self.user_repo = UserRepository()

    async def get_attendance_with_user(self, attendance_id: str) -> dict | None:
        """Get attendance record with user data for recorded_by field."""
        logger.debug("Getting attendance with user data for ID: %s", attendance_id)

        try:
            # Get the attendance record
            attendance = await self.get_by_id(attendance_id)
            if not attendance:
                logger.warning("Attendance record not found: %s", attendance_id)
                return None

            # Convert attendance to dict
            attendance_dict = attendance.model_dump()

            # Fetch user data for recorded_by
            if attendance.recorded_by:
                user = await self.user_repo.get_by_id(attendance.recorded_by)
                if user:
                    attendance_dict["recorded_by_user"] = {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "first_name": getattr(user, 'first_name', None),
                        "last_name": getattr(user, 'last_name', None),
                        "is_active": user.is_active,
                        "is_admin": user.is_admin
                    }
                    logger.debug("User data fetched for recorded_by: %s", user.username)
                else:
                    logger.warning("User not found for recorded_by: %s", attendance.recorded_by)
                    attendance_dict["recorded_by_user"] = None
            else:
                attendance_dict["recorded_by_user"] = None

            logger.info("Attendance with user data retrieved successfully: %s", attendance_id)
            return attendance_dict

        except Exception as e:
            logger.error("Error getting attendance with user data: %s", str(e))
            return None

    async def get_by_member_id(
        self, member_id: str, skip: int = 0, limit: int = 100
    ) -> list[AttendanceInDB]:
        """Get attendance records for a specific member."""
        logger.debug("Getting attendance for member: %s", member_id)
        collection = await self.get_collection()
        cursor = (
            collection.find({"member_ids": member_id})
            .sort("attendance_date", -1)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(AttendanceInDB(**doc))
        return result

    async def get_by_date(
        self, attendance_date: date, attendance_type: AttendanceType | None = None
    ) -> list[AttendanceInDB]:
        """Get attendance records for a specific date."""
        logger.debug("Getting attendance for date: %s", attendance_date)
        collection = await self.get_collection()
        query = {"attendance_date": attendance_date.isoformat()}
        if attendance_type:
            query["attendance_type"] = attendance_type

        cursor = collection.find(query).sort("member_id", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(AttendanceInDB(**doc))
        return result

    async def get_by_date_range(
        self,
        start_date: date,
        end_date: date,
        member_id: str | None = None,
        attendance_type: AttendanceType | None = None,
    ) -> list[AttendanceInDB]:
        """Get attendance records for a date range."""
        logger.debug(
            "Getting attendance for date range: %s to %s", start_date, end_date
        )
        collection = await self.get_collection()
        query = {
            "attendance_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }

        if member_id:
            query["member_id"] = member_id
        if attendance_type:
            query["attendance_type"] = attendance_type

        cursor = collection.find(query).sort("attendance_date", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(AttendanceInDB(**doc))
        return result

    async def get_member_attendance_summary(
        self,
        member_id: str,
        start_date: date,
        end_date: date,
    ) -> MemberAttendanceSummaryRepo:
        """Get attendance summary for a member in a date range."""
        logger.debug(
            "Getting attendance summary for member %s from %s to %s",
            member_id, start_date, end_date
        )
        collection = await self.get_collection()

        pipeline = [
            {
                "$match": {
                    "member_ids": member_id,
                    "attendance_date": {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat()
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_services": {"$sum": 1},
                    "attendance_count": {
                        "$sum": {
                            "$cond": [{"$in": [member_id, "$member_ids"]}, 1, 0]
                        }
                    }
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        total_services = 0
        attendance_count = 0

        for result in results:
            total_services = result.get("total_services", 0)
            attendance_count = result.get("attendance_count", 0)

        # Calculate attendance rate
        attendance_rate = (attendance_count / total_services * 100) if total_services > 0 else 0.0

        return MemberAttendanceSummaryRepo(
            member_id=member_id,
            total_services=total_services,
            attendance_count=attendance_count,
            attendance_rate=round(attendance_rate, 2),
            start_date=start_date,
            end_date=end_date,
            created_at=get_current_date(),
            updated_at=get_current_date()
        )

    async def get_service_attendance_summary(
        self,
        attendance_date: date,
        attendance_type: AttendanceType,
    ) -> ServiceAttendanceSummaryRepo:
        """Get attendance summary for a specific service."""
        logger.debug(
            "Getting service attendance summary for %s on %s",
            attendance_type, attendance_date
        )
        collection = await self.get_collection()

        pipeline = [
            {
                "$match": {
                    "attendance_date": attendance_date.isoformat(),
                    "attendance_type": attendance_type
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_services": {"$sum": 1},
                    "total_attended": {"$sum": {"$size": "$member_ids"}}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        total_services = 0
        total_attended = 0

        for result in results:
            total_services = result.get("total_services", 0)
            total_attended = result.get("total_attended", 0)

        # Calculate attendance rate
        attendance_rate = (total_attended / total_services * 100) if total_services > 0 else 0.0

        return ServiceAttendanceSummaryRepo(
            service_date=attendance_date,
            service_type=attendance_type,
            total_members=total_services,  # This represents total services, not unique members
            attended_members=total_attended,
            attendance_rate=round(attendance_rate, 2),
            created_at=get_current_date(),
            updated_at=get_current_date()
        )

    async def check_attendance_exists(
        self,
        attendance_date: date,
        attendance_type: AttendanceType,
    ) -> bool:
        """Check if attendance record already exists for a specific date and type."""
        logger.debug(
            "Checking if attendance exists for %s on %s",
            attendance_type, attendance_date
        )
        collection = await self.get_collection()
        doc = await collection.find_one({
            "attendance_date": attendance_date.isoformat(),
            "attendance_type": attendance_type
        })
        return doc is not None

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "attendance_date",
        sort_order: str = "desc",
    ) -> list[AttendanceInDB]:
        """Get multiple attendance records with pagination, search, and sorting."""
        logger.debug("Getting attendance records with pagination")
        collection = await self.get_collection()
        filter_dict = filter_dict or {}

        # Add search functionality if search term provided
        if search:
            # Search in member_id, status, and notes
            filter_dict["$or"] = [
                {"member_id": {"$regex": search, "$options": "i"}},
                {"status": {"$regex": search, "$options": "i"}},
                {"notes": {"$regex": search, "$options": "i"}},
            ]

        # Determine sort direction
        sort_direction = 1 if sort_order == "asc" else -1

        cursor = (
            collection.find(filter_dict)
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(self.model(**doc))
        return result

    async def get_recent_attendance(
        self, limit: int = 50
    ) -> list[AttendanceInDB]:
        """Get recent attendance records."""
        logger.debug("Getting recent attendance records")
        return await self.get_many(limit=limit, sort_by="created_at")

    async def get_attendance_trends(
        self, start_date: date, end_date: date, attendance_type: AttendanceType | None = None
    ) -> list[AttendanceTrend]:
        """Get attendance trends over time."""
        logger.debug("Getting attendance trends from %s to %s", start_date, end_date)
        collection = await self.get_collection()

        match_stage = {
            "attendance_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }

        if attendance_type:
            match_stage["attendance_type"] = attendance_type

        pipeline = [
            {"$match": match_stage},
            {
                "$group": {
                    "_id": {
                        "date": "$attendance_date",
                        "type": "$attendance_type"
                    },
                    "total_services": {"$sum": 1},
                    "total_attended": {"$sum": {"$size": "$member_ids"}}
                }
            },
            {"$sort": {"_id.date": 1}}
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        trends = []
        for result in results:
            attendance_rate = (result["total_attended"] / result["total_services"]) * 100 if result["total_services"] > 0 else 0

            trend = AttendanceTrend(
                date=result["_id"]["date"],
                service_type=result["_id"]["type"],
                total_members=result["total_services"],
                attended_count=result["total_attended"],
                attendance_rate=round(attendance_rate, 2),
                created_at=get_current_date(),
                updated_at=get_current_date()
            )
            trends.append(trend)

        return trends

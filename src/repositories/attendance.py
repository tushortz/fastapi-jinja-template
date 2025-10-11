"""Attendance repository."""

import logging
from datetime import date, datetime
from typing import Any

from src.models.attendance import AttendanceInDB, AttendanceStatus, AttendanceType

from .base import BaseRepository

logger = logging.getLogger(__name__)


class AttendanceRepository(BaseRepository):
    """Attendance repository for database operations."""

    def __init__(self):
        super().__init__(AttendanceInDB, "attendance")

    async def get_by_member_id(
        self, member_id: str, skip: int = 0, limit: int = 100
    ) -> list[AttendanceInDB]:
        """Get attendance records for a specific member."""
        logger.debug("Getting attendance for member: %s", member_id)
        collection = await self.get_collection()
        cursor = (
            collection.find({"member_id": member_id})
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
    ) -> dict[str, Any]:
        """Get attendance summary for a member in a date range."""
        logger.debug(
            "Getting attendance summary for member %s from %s to %s",
            member_id, start_date, end_date
        )
        collection = await self.get_collection()

        pipeline = [
            {
                "$match": {
                    "member_id": member_id,
                    "attendance_date": {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat()
                    }
                }
            },
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        summary = {
            "member_id": member_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_services": 0,
            "present_count": 0,
            "absent_count": 0,
            "late_count": 0,
            "excused_count": 0,
            "attendance_rate": 0.0
        }

        for result in results:
            status = result["_id"]
            count = result["count"]
            summary["total_services"] += count

            if status == AttendanceStatus.PRESENT:
                summary["present_count"] = count
            elif status == AttendanceStatus.ABSENT:
                summary["absent_count"] = count
            elif status == AttendanceStatus.LATE:
                summary["late_count"] = count
            elif status == AttendanceStatus.EXCUSED:
                summary["excused_count"] = count

        # Calculate attendance rate
        if summary["total_services"] > 0:
            summary["attendance_rate"] = (
                summary["present_count"] / summary["total_services"]
            ) * 100

        return summary

    async def get_service_attendance_summary(
        self,
        attendance_date: date,
        attendance_type: AttendanceType,
    ) -> dict[str, Any]:
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
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        summary = {
            "service_date": attendance_date,
            "service_type": attendance_type,
            "total_members": 0,
            "present_members": 0,
            "absent_members": 0,
            "late_members": 0,
            "excused_members": 0,
            "attendance_rate": 0.0
        }

        for result in results:
            status = result["_id"]
            count = result["count"]
            summary["total_members"] += count

            if status == AttendanceStatus.PRESENT:
                summary["present_members"] = count
            elif status == AttendanceStatus.ABSENT:
                summary["absent_members"] = count
            elif status == AttendanceStatus.LATE:
                summary["late_members"] = count
            elif status == AttendanceStatus.EXCUSED:
                summary["excused_members"] = count

        # Calculate attendance rate
        if summary["total_members"] > 0:
            summary["attendance_rate"] = (
                summary["present_members"] / summary["total_members"]
            ) * 100

        return summary

    async def check_attendance_exists(
        self,
        member_id: str,
        attendance_date: date,
        attendance_type: AttendanceType,
    ) -> bool:
        """Check if attendance record already exists."""
        logger.debug(
            "Checking if attendance exists for member %s on %s for %s",
            member_id, attendance_date, attendance_type
        )
        collection = await self.get_collection()
        doc = await collection.find_one({
            "member_id": member_id,
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

    async def count_by_status(
        self, status: AttendanceStatus, start_date: date | None = None, end_date: date | None = None
    ) -> int:
        """Count attendance records by status."""
        logger.debug("Counting attendance records by status: %s", status)
        collection = await self.get_collection()
        query = {"status": status}

        if start_date and end_date:
            query["attendance_date"] = {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }

        return await collection.count_documents(query)

    async def get_attendance_trends(
        self, start_date: date, end_date: date, attendance_type: AttendanceType | None = None
    ) -> list[dict[str, Any]]:
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
                    "total": {"$sum": 1},
                    "present": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", AttendanceStatus.PRESENT]}, 1, 0]
                        }
                    },
                    "absent": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", AttendanceStatus.ABSENT]}, 1, 0]
                        }
                    },
                    "late": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", AttendanceStatus.LATE]}, 1, 0]
                        }
                    }
                }
            },
            {"$sort": {"_id.date": 1}}
        ]

        cursor = collection.aggregate(pipeline)
        results = await cursor.to_list(length=None)

        trends = []
        for result in results:
            trend = {
                "date": result["_id"]["date"],
                "service_type": result["_id"]["type"],
                "total_members": result["total"],
                "present_count": result["present"],
                "absent_count": result["absent"],
                "late_count": result["late"],
                "attendance_rate": (result["present"] / result["total"]) * 100 if result["total"] > 0 else 0
            }
            trends.append(trend)

        return trends

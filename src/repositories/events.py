"""Events and calendar repository."""

import logging
from datetime import date, datetime
from typing import Any

from src.models.events import (
    CalendarEventInDB, CalendarInDB, EventPriority, EventStatus, EventType,
)

from .base import BaseRepository

logger = logging.getLogger(__name__)


class CalendarRepository(BaseRepository):
    """Calendar repository for database operations."""

    def __init__(self):
        super().__init__(CalendarInDB, "calendars")

    async def get_by_owner(self, owner_id: str) -> list[CalendarInDB]:
        """Get calendars by owner."""
        logger.debug("Getting calendars by owner: %s", owner_id)
        collection = await self.get_collection()
        cursor = collection.find({"owner_id": owner_id}).sort("name", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarInDB(**doc))
        return result

    async def get_public_calendars(self) -> list[CalendarInDB]:
        """Get public calendars."""
        logger.debug("Getting public calendars")
        collection = await self.get_collection()
        cursor = collection.find({"is_public": True}).sort("name", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarInDB(**doc))
        return result

    async def get_default_calendar(self, owner_id: str) -> CalendarInDB | None:
        """Get default calendar for owner."""
        logger.debug("Getting default calendar for owner: %s", owner_id)
        collection = await self.get_collection()
        doc = await collection.find_one({
            "owner_id": owner_id,
            "is_default": True
        })
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return CalendarInDB(**doc)
        return None

    async def set_default_calendar(self, calendar_id: str, owner_id: str) -> bool:
        """Set a calendar as default for owner."""
        logger.debug("Setting calendar %s as default for owner %s", calendar_id, owner_id)
        collection = await self.get_collection()

        # First, unset all other default calendars for this owner
        await collection.update_many(
            {"owner_id": owner_id, "is_default": True},
            {"$set": {"is_default": False}}
        )

        # Set the specified calendar as default
        result = await collection.update_one(
            {"_id": calendar_id, "owner_id": owner_id},
            {"$set": {"is_default": True}}
        )

        return result.modified_count > 0


class CalendarEventRepository(BaseRepository):
    """Calendar event repository for database operations."""

    def __init__(self):
        super().__init__(CalendarEventInDB, "calendar_events")

    async def get_by_calendar(self, calendar_id: str) -> list[CalendarEventInDB]:
        """Get events by calendar."""
        logger.debug("Getting events by calendar: %s", calendar_id)
        collection = await self.get_collection()
        cursor = collection.find({"calendar_id": calendar_id}).sort("start_date", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_by_type(self, event_type: EventType) -> list[CalendarEventInDB]:
        """Get events by type."""
        logger.debug("Getting events by type: %s", event_type)
        collection = await self.get_collection()
        cursor = collection.find({"event_type": event_type}).sort("start_date", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_by_status(self, status: EventStatus) -> list[CalendarEventInDB]:
        """Get events by status."""
        logger.debug("Getting events by status: %s", status)
        collection = await self.get_collection()
        cursor = collection.find({"status": status}).sort("start_date", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_by_organizer(self, organizer_id: str) -> list[CalendarEventInDB]:
        """Get events by organizer."""
        logger.debug("Getting events by organizer: %s", organizer_id)
        collection = await self.get_collection()
        cursor = collection.find({"organizer_id": organizer_id}).sort("start_date", -1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[CalendarEventInDB]:
        """Get events within a date range."""
        logger.debug("Getting events from %s to %s", start_date, end_date)
        collection = await self.get_collection()
        cursor = collection.find({
            "start_date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).sort("start_date", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_upcoming_events(self, limit: int = 10) -> list[CalendarEventInDB]:
        """Get upcoming events."""
        logger.debug("Getting upcoming events")
        today = date.today()
        collection = await self.get_collection()
        cursor = (
            collection.find({
                "start_date": {"$gte": today.isoformat()},
                "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED]}
            })
            .sort("start_date", 1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_today_events(self) -> list[CalendarEventInDB]:
        """Get events scheduled for today."""
        logger.debug("Getting today's events")
        today = date.today()
        collection = await self.get_collection()
        cursor = collection.find({
            "start_date": today.isoformat(),
            "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED, EventStatus.IN_PROGRESS]}
        }).sort("start_time", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_this_week_events(self) -> list[CalendarEventInDB]:
        """Get events scheduled for this week."""
        logger.debug("Getting this week's events")
        today = date.today()
        start_of_week = today - datetime.timedelta(days=today.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)

        return await self.get_by_date_range(start_of_week, end_of_week)

    async def get_this_month_events(self) -> list[CalendarEventInDB]:
        """Get events scheduled for this month."""
        logger.debug("Getting this month's events")
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        # Get last day of month
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)

        return await self.get_by_date_range(start_of_month, end_of_month)

    async def get_past_events(self, limit: int = 50) -> list[CalendarEventInDB]:
        """Get past events."""
        logger.debug("Getting past events")
        today = date.today()
        collection = await self.get_collection()
        cursor = (
            collection.find({
                "start_date": {"$lt": today.isoformat()},
                "status": {"$in": [EventStatus.COMPLETED, EventStatus.CANCELLED]}
            })
            .sort("start_date", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_high_priority_events(self) -> list[CalendarEventInDB]:
        """Get high priority events."""
        logger.debug("Getting high priority events")
        collection = await self.get_collection()
        cursor = collection.find({
            "priority": {"$in": [EventPriority.HIGH, EventPriority.URGENT]},
            "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED]}
        }).sort("start_date", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_recurring_events(self) -> list[CalendarEventInDB]:
        """Get recurring events."""
        logger.debug("Getting recurring events")
        collection = await self.get_collection()
        cursor = collection.find({
            "is_recurring": True,
            "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED]}
        }).sort("start_date", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_public_events(self) -> list[CalendarEventInDB]:
        """Get public events."""
        logger.debug("Getting public events")
        collection = await self.get_collection()
        cursor = collection.find({"is_public": True}).sort("start_date", 1)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "start_date",
        sort_order: str = "asc",
    ) -> list[CalendarEventInDB]:
        """Get multiple events with pagination, search, and sorting."""
        logger.debug("Getting events with pagination")
        collection = await self.get_collection()
        filter_dict = filter_dict or {}

        # Add search functionality if search term provided
        if search:
            # Search in title, description, location, and coordinator_name
            filter_dict["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
                {"location": {"$regex": search, "$options": "i"}},
                {"coordinator_name": {"$regex": search, "$options": "i"}},
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

    async def count_by_calendar(self, calendar_id: str) -> int:
        """Count events for a given calendar."""
        collection = await self.get_collection()
        return await collection.count_documents({"calendar_id": calendar_id})

    async def count_by_type(self, event_type: EventType) -> int:
        """Count events by type."""
        logger.debug("Counting events by type: %s", event_type)
        collection = await self.get_collection()
        return await collection.count_documents({"event_type": event_type})

    async def count_by_status(self, status: EventStatus) -> int:
        """Count events by status."""
        logger.debug("Counting events by status: %s", status)
        collection = await self.get_collection()
        return await collection.count_documents({"status": status})

    async def count_upcoming_events(self) -> int:
        """Count upcoming events."""
        logger.debug("Counting upcoming events")
        today = date.today()
        collection = await self.get_collection()
        return await collection.count_documents({
            "start_date": {"$gte": today.isoformat()},
            "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED]}
        })

    async def get_event_statistics(self) -> dict[str, Any]:
        """Get event statistics."""
        logger.debug("Getting event statistics")
        collection = await self.get_collection()

        # Get counts by status
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        status_counts = await cursor.to_list(length=None)

        # Get counts by type
        pipeline = [
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1}
                }
            }
        ]

        cursor = collection.aggregate(pipeline)
        type_counts = await cursor.to_list(length=None)

        # Get upcoming events count
        today = date.today()
        upcoming_count = await collection.count_documents({
            "start_date": {"$gte": today.isoformat()},
            "status": {"$in": [EventStatus.PLANNED, EventStatus.CONFIRMED]}
        })

        # Get this month's events count
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - datetime.timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - datetime.timedelta(days=1)

        this_month_count = await collection.count_documents({
            "start_date": {
                "$gte": start_of_month.isoformat(),
                "$lte": end_of_month.isoformat()
            }
        })

        return {
            "status_counts": {item["_id"]: item["count"] for item in status_counts},
            "type_counts": {item["_id"]: item["count"] for item in type_counts},
            "upcoming_count": upcoming_count,
            "this_month_count": this_month_count,
            "total_count": await collection.count_documents({})
        }
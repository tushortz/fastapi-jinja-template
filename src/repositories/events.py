"""Events and calendar repository."""

import logging
from datetime import date, datetime, timedelta
from typing import Any

from src.models.events import CalendarEventInDB

from .base import BaseRepository

logger = logging.getLogger(__name__)

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
                "start_date": {"$gte": today.isoformat()}
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
            "start_date": today.isoformat()
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
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        return await self.get_by_date_range(start_of_week, end_of_week)

    async def get_this_month_events(self) -> list[CalendarEventInDB]:
        """Get events scheduled for this month."""
        logger.debug("Getting this month's events")
        today = date.today()
        start_of_month = date(today.year, today.month, 1)

        # Get last day of month
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

        return await self.get_by_date_range(start_of_month, end_of_month)

    async def get_past_events(self, limit: int = 50) -> list[CalendarEventInDB]:
        """Get past events."""
        logger.debug("Getting past events")
        today = date.today()
        collection = await self.get_collection()
        cursor = (
            collection.find({
                "start_date": {"$lt": today.isoformat()}
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

    async def get_past_events_by_end_date(self, limit: int = 50) -> list[CalendarEventInDB]:
        """Get past events using end_date when present, otherwise start_date. Sorted by most recent past first."""
        logger.debug("Getting past events by end_date/start_date fallback")
        today = date.today().isoformat()
        collection = await self.get_collection()
        cursor = (
            collection.find({
                "$or": [
                    {"end_date": {"$lt": today}},
                    {"end_date": {"$exists": False}, "start_date": {"$lt": today}},
                    {"end_date": None, "start_date": {"$lt": today}},
                ]
            })
            .sort("end_date", -1)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(CalendarEventInDB(**doc))
        return result

    # priority removed; high priority helper removed

    async def get_recurring_events(self) -> list[CalendarEventInDB]:
        """Get recurring events."""
        logger.debug("Getting recurring events")
        collection = await self.get_collection()
        cursor = collection.find({
            "is_recurring": True
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

    # event_type removed; count_by_type deprecated

    # status removed; count_by_status deprecated

    async def count_upcoming_events(self) -> int:
        """Count upcoming events."""
        logger.debug("Counting upcoming events")
        today = date.today()
        collection = await self.get_collection()
        return await collection.count_documents({
            "start_date": {"$gte": today.isoformat()}
        })

    async def get_event_statistics(self) -> dict[str, Any]:
        """Get event statistics."""
        logger.debug("Getting event statistics")
        collection = await self.get_collection()

        # status removed; no status_counts

        # event_type removed; no type counts

        # Get upcoming events count (no status filtering)
        today = date.today()
        upcoming_count = await collection.count_documents({
            "start_date": {"$gte": today.isoformat()}
        })

        # Get this month's events count
        start_of_month = date(today.year, today.month, 1)
        if today.month == 12:
            end_of_month = date(today.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_of_month = date(today.year, today.month + 1, 1) - timedelta(days=1)

        this_month_count = await collection.count_documents({
            "start_date": {
                "$gte": start_of_month.isoformat(),
                "$lte": end_of_month.isoformat()
            }
        })

        return {
            "status_counts": {},
            "type_counts": {},
            "upcoming_count": upcoming_count,
            "this_month_count": this_month_count,
            "total_count": await collection.count_documents({})
        }
"""Events and calendar service for business logic."""

import logging
from typing import Any

from src.models.events import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from src.repositories.events import CalendarEventRepository

logger = logging.getLogger(__name__)


class CalendarEventService:
    """Calendar event service for business logic operations."""

    def __init__(self):
        self.event_repo = CalendarEventRepository()

    async def create_event(self, event_create: CalendarEventCreate) -> CalendarEvent:
        """Create a new calendar event."""
        logger.info("Creating event: %s", event_create.title)

        # Create event
        event_in_db = await self.event_repo.create(event_create)
        logger.info(
            "Event created successfully: %s (ID: %s)",
            event_in_db.title,
            event_in_db.id,
        )

        return CalendarEvent(id=event_in_db.id,
                             title=event_in_db.title,
                             description=event_in_db.description,
                             start_date=event_in_db.start_date,
                             end_date=event_in_db.end_date,
                             start_time=event_in_db.start_time,
                             end_time=event_in_db.end_time,
                             is_all_day=event_in_db.is_all_day,
                             location=event_in_db.location,
                             organizer_id=event_in_db.organizer_id,
                             calendar_id=event_in_db.calendar_id,
                             color=event_in_db.color,
                             is_public=event_in_db.is_public,
                             created_at=event_in_db.created_at,
                             updated_at=event_in_db.updated_at)

    async def get_event_by_id(self, event_id: str) -> CalendarEvent | None:
        """Get event by ID."""
        logger.debug("Getting event by ID: %s", event_id)
        event_in_db = await self.event_repo.get_by_id(event_id)
        if not event_in_db:
            return None

        return CalendarEvent(id=event_in_db.id,
                             title=event_in_db.title,
                             description=event_in_db.description,
                             start_date=event_in_db.start_date,
                             end_date=event_in_db.end_date,
                             start_time=event_in_db.start_time,
                             end_time=event_in_db.end_time,
                             is_all_day=event_in_db.is_all_day,
                             location=event_in_db.location,
                             organizer_id=event_in_db.organizer_id,
                             calendar_id=event_in_db.calendar_id,
                             color=event_in_db.color,
                             is_public=event_in_db.is_public,
                             created_at=event_in_db.created_at,
                             updated_at=event_in_db.updated_at)

    async def update_event(
        self, event_id: str, event_update: CalendarEventUpdate
    ) -> CalendarEvent | None:
        """Update event."""
        logger.info("Updating event: %s", event_id)

        event_in_db = await self.event_repo.update(event_id, event_update)
        if not event_in_db:
            logger.warning("Event not found for update: %s", event_id)
            return None

        logger.info("Event updated successfully: %s", event_in_db.id)
        return CalendarEvent(id=event_in_db.id,
                             title=event_in_db.title,
                             description=event_in_db.description,
                             start_date=event_in_db.start_date,
                             end_date=event_in_db.end_date,
                             start_time=event_in_db.start_time,
                             end_time=event_in_db.end_time,
                             is_all_day=event_in_db.is_all_day,
                             location=event_in_db.location,
                             organizer_id=event_in_db.organizer_id,
                             calendar_id=event_in_db.calendar_id,
                             color=event_in_db.color,
                             is_public=event_in_db.is_public,
                             created_at=event_in_db.created_at,
                             updated_at=event_in_db.updated_at)

    async def delete_event(self, event_id: str) -> bool:
        """Delete event."""
        logger.info("Deleting event: %s", event_id)
        try:
            result = await self.event_repo.delete(event_id)
            if result:
                logger.info("Event deleted successfully: %s", event_id)
            else:
                logger.warning("Event not found for deletion: %s", event_id)
            return result
        except Exception as e:
            logger.error("Error deleting event: %s", str(e))
            raise

    async def get_events(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,

        calendar_id: str | None = None,
    ) -> list[CalendarEvent]:
        """Get all events with pagination and optional filters."""
        logger.debug("Getting events with filters: skip=%d, limit=%d", skip, limit)

        filter_dict: dict[str, Any] = {}

        if calendar_id:
            filter_dict["calendar_id"] = calendar_id

        events_in_db = await self.event_repo.get_many(
            skip=skip,
            limit=limit,
            search=search,
            filter_dict=filter_dict,
            sort_by="start_date",
            sort_order="desc",
        )

        return [CalendarEvent(id=event.id,
                              title=event.title,
                              description=event.description,
                              start_date=event.start_date,
                              end_date=event.end_date,
                              start_time=event.start_time,
                              end_time=event.end_time,
                              is_all_day=event.is_all_day,
                              location=event.location,
                              organizer_id=event.organizer_id,
                              calendar_id=event.calendar_id,
                              color=event.color,
                              is_public=event.is_public,
                              created_at=event.created_at,
                              updated_at=event.updated_at)
                for event in events_in_db]

    async def get_upcoming_events(self, limit: int = 10) -> list[CalendarEvent]:
        """Get upcoming events."""
        logger.debug("Getting upcoming events")
        events_in_db = await self.event_repo.get_upcoming_events(limit)

        return [CalendarEvent(id=event.id,
                              title=event.title,
                              description=event.description,
                              start_date=event.start_date,
                              end_date=event.end_date,
                              start_time=event.start_time,
                              end_time=event.end_time,
                              is_all_day=event.is_all_day,
                              location=event.location,
                              organizer_id=event.organizer_id,
                              calendar_id=event.calendar_id,
                              color=event.color,
                              is_public=event.is_public,
                              created_at=event.created_at,
                              updated_at=event.updated_at)
                for event in events_in_db]

    async def get_today_events(self) -> list[CalendarEvent]:
        """Get events scheduled for today."""
        logger.debug("Getting today's events")
        events_in_db = await self.event_repo.get_today_events()

        return [CalendarEvent(id=event.id,
                              title=event.title,
                              description=event.description,
                              start_date=event.start_date,
                              end_date=event.end_date,
                              start_time=event.start_time,
                              end_time=event.end_time,
                              is_all_day=event.is_all_day,
                              location=event.location,
                              organizer_id=event.organizer_id,
                              calendar_id=event.calendar_id,
                              color=event.color,
                              is_public=event.is_public,
                              created_at=event.created_at,
                              updated_at=event.updated_at)
                for event in events_in_db]

    async def get_this_week_events(self) -> list[CalendarEvent]:
        """Get events scheduled for this week."""
        logger.debug("Getting this week's events")
        events_in_db = await self.event_repo.get_this_week_events()

        return [CalendarEvent(id=event.id,
                              title=event.title,
                              description=event.description,
                              start_date=event.start_date,
                              end_date=event.end_date,
                              start_time=event.start_time,
                              end_time=event.end_time,
                              is_all_day=event.is_all_day,
                              location=event.location,
                              organizer_id=event.organizer_id,
                              calendar_id=event.calendar_id,
                              color=event.color,
                              is_public=event.is_public,
                              created_at=event.created_at,
                              updated_at=event.updated_at)
                for event in events_in_db]

    async def get_this_month_events(self) -> list[CalendarEvent]:
        """Get events scheduled for this month."""
        logger.debug("Getting this month's events")
        events_in_db = await self.event_repo.get_this_month_events()

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,

                start_date=event.start_date,
                end_date=event.end_date,
                start_time=event.start_time,
                end_time=event.end_time,
                is_all_day=event.is_all_day,
                location=event.location,
                address=event.address,
                city=event.city,
                state=event.state,
                zip_code=event.zip_code,
                organizer_id=event.organizer_id,
                coordinator_name=event.coordinator_name,
                coordinator_phone=event.coordinator_phone,
                coordinator_email=event.coordinator_email,
                estimated_attendance=event.estimated_attendance,
                actual_attendance=event.actual_attendance,
                budget=event.budget,
                requirements=event.requirements,
                equipment_needed=event.equipment_needed,
                notes=event.notes,
                is_recurring=event.is_recurring,
                recurrence_pattern=event.recurrence_pattern,
                recurrence_end_date=event.recurrence_end_date,
                calendar_id=event.calendar_id,
                color=event.color,
                is_public=event.is_public,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]

    async def get_event_statistics(self) -> dict[str, Any]:
        """Get event statistics."""
        logger.info("Getting event statistics")
        try:
            stats = await self.event_repo.get_event_statistics()
            logger.info("Retrieved event statistics")
            return stats
        except Exception as e:
            logger.error("Error getting event statistics: %s", str(e))
            raise

    async def get_past_events(self, limit: int = 100) -> list[CalendarEvent]:
        """Get past events using end_date when present (fallback start_date)."""
        logger.debug("Getting past events by end date")
        events_in_db = await self.event_repo.get_past_events_by_end_date(limit)
        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                start_date=event.start_date,
                end_date=event.end_date,
                start_time=event.start_time,
                end_time=event.end_time,
                is_all_day=event.is_all_day,
                location=event.location,
                organizer_id=event.organizer_id,
                calendar_id=event.calendar_id,
                color=event.color,
                is_public=event.is_public,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]
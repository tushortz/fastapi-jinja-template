"""Events and calendar service for business logic."""

import logging
from typing import Any

from src.models.events import (
    Calendar, CalendarCreate, CalendarEvent, CalendarEventCreate, CalendarEventUpdate,
    CalendarUpdate, EventPriority, EventStatus, EventType,
)
from src.repositories.events import CalendarEventRepository, CalendarRepository

logger = logging.getLogger(__name__)


class CalendarService:
    """Calendar service for business logic operations."""

    def __init__(self):
        self.calendar_repo = CalendarRepository()

    async def create_calendar(self, calendar_create: CalendarCreate) -> Calendar:
        """Create a new calendar."""
        logger.info("Creating calendar: %s", calendar_create.name)

        # If this is set as default, unset other default calendars for this owner
        if calendar_create.is_default:
            await self.calendar_repo.set_default_calendar("", calendar_create.owner_id)

        # Create calendar
        calendar_in_db = await self.calendar_repo.create(calendar_create)
        logger.info(
            "Calendar created successfully: %s (ID: %s)",
            calendar_in_db.name,
            calendar_in_db.id,
        )

        return Calendar(
            id=calendar_in_db.id,
            name=calendar_in_db.name,
            description=calendar_in_db.description,
            color=calendar_in_db.color,
            is_default=calendar_in_db.is_default,
            is_public=calendar_in_db.is_public,
            owner_id=calendar_in_db.owner_id,
            event_count=0,  # Will be updated separately
            created_at=calendar_in_db.created_at,
            updated_at=calendar_in_db.updated_at,
        )

    async def get_calendar_by_id(self, calendar_id: str) -> Calendar | None:
        """Get calendar by ID."""
        logger.debug("Getting calendar by ID: %s", calendar_id)
        calendar_in_db = await self.calendar_repo.get_by_id(calendar_id)
        if not calendar_in_db:
            return None

        # Get event count for this calendar
        event_repo = CalendarEventRepository()
        event_count = await event_repo.count_by_calendar(calendar_id)

        return Calendar(
            id=calendar_in_db.id,
            name=calendar_in_db.name,
            description=calendar_in_db.description,
            color=calendar_in_db.color,
            is_default=calendar_in_db.is_default,
            is_public=calendar_in_db.is_public,
            owner_id=calendar_in_db.owner_id,
            event_count=event_count,
            created_at=calendar_in_db.created_at,
            updated_at=calendar_in_db.updated_at,
        )

    async def update_calendar(
        self, calendar_id: str, calendar_update: CalendarUpdate
    ) -> Calendar | None:
        """Update calendar."""
        logger.info("Updating calendar: %s", calendar_id)

        # If setting as default, unset other default calendars for this owner
        if calendar_update.is_default:
            calendar_in_db = await self.calendar_repo.get_by_id(calendar_id)
            if calendar_in_db:
                await self.calendar_repo.set_default_calendar("", calendar_in_db.owner_id)

        calendar_in_db = await self.calendar_repo.update(calendar_id, calendar_update)
        if not calendar_in_db:
            logger.warning("Calendar not found for update: %s", calendar_id)
            return None

        logger.info("Calendar updated successfully: %s", calendar_in_db.id)

        # Get event count for this calendar
        event_repo = CalendarEventRepository()
        event_count = await event_repo.count_by_calendar(calendar_id)

        return Calendar(
            id=calendar_in_db.id,
            name=calendar_in_db.name,
            description=calendar_in_db.description,
            color=calendar_in_db.color,
            is_default=calendar_in_db.is_default,
            is_public=calendar_in_db.is_public,
            owner_id=calendar_in_db.owner_id,
            event_count=event_count,
            created_at=calendar_in_db.created_at,
            updated_at=calendar_in_db.updated_at,
        )

    async def delete_calendar(self, calendar_id: str) -> bool:
        """Delete calendar."""
        logger.info("Deleting calendar: %s", calendar_id)
        try:
            result = await self.calendar_repo.delete(calendar_id)
            if result:
                logger.info("Calendar deleted successfully: %s", calendar_id)
            else:
                logger.warning("Calendar not found for deletion: %s", calendar_id)
            return result
        except Exception as e:
            logger.error("Error deleting calendar: %s", str(e))
            raise

    async def get_calendars_by_owner(self, owner_id: str) -> list[Calendar]:
        """Get calendars by owner."""
        logger.debug("Getting calendars by owner: %s", owner_id)
        calendars_in_db = await self.calendar_repo.get_by_owner(owner_id)

        result = []
        for calendar in calendars_in_db:
            # Get event count for each calendar
            event_repo = CalendarEventRepository()
            event_count = await event_repo.count_by_calendar(calendar.id)

            result.append(Calendar(
                id=calendar.id,
                name=calendar.name,
                description=calendar.description,
                color=calendar.color,
                is_default=calendar.is_default,
                is_public=calendar.is_public,
                owner_id=calendar.owner_id,
                event_count=event_count,
                created_at=calendar.created_at,
                updated_at=calendar.updated_at,
            ))

        return result

    async def get_public_calendars(self) -> list[Calendar]:
        """Get public calendars."""
        logger.debug("Getting public calendars")
        calendars_in_db = await self.calendar_repo.get_public_calendars()

        result = []
        for calendar in calendars_in_db:
            # Get event count for each calendar
            event_repo = CalendarEventRepository()
            event_count = await event_repo.count_by_calendar(calendar.id)

            result.append(Calendar(
                id=calendar.id,
                name=calendar.name,
                description=calendar.description,
                color=calendar.color,
                is_default=calendar.is_default,
                is_public=calendar.is_public,
                owner_id=calendar.owner_id,
                event_count=event_count,
                created_at=calendar.created_at,
                updated_at=calendar.updated_at,
            ))

        return result

    async def get_default_calendar(self, owner_id: str) -> Calendar | None:
        """Get default calendar for owner."""
        logger.debug("Getting default calendar for owner: %s", owner_id)
        calendar_in_db = await self.calendar_repo.get_default_calendar(owner_id)
        if not calendar_in_db:
            return None

        # Get event count for this calendar
        event_repo = CalendarRepository()
        event_count = await event_repo.count_by_calendar(calendar_in_db.id)

        return Calendar(
            id=calendar_in_db.id,
            name=calendar_in_db.name,
            description=calendar_in_db.description,
            color=calendar_in_db.color,
            is_default=calendar_in_db.is_default,
            is_public=calendar_in_db.is_public,
            owner_id=calendar_in_db.owner_id,
            event_count=event_count,
            created_at=calendar_in_db.created_at,
            updated_at=calendar_in_db.updated_at,
        )

    async def set_default_calendar(self, calendar_id: str, owner_id: str) -> bool:
        """Set a calendar as default for owner."""
        logger.info("Setting calendar %s as default for owner %s", calendar_id, owner_id)
        try:
            result = await self.calendar_repo.set_default_calendar(calendar_id, owner_id)
            if result:
                logger.info("Calendar set as default successfully")
            else:
                logger.warning("Failed to set calendar as default")
            return result
        except Exception as e:
            logger.error("Error setting default calendar: %s", str(e))
            raise


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

        return CalendarEvent(
            id=event_in_db.id,
            title=event_in_db.title,
            description=event_in_db.description,
            event_type=event_in_db.event_type,
            status=event_in_db.status,
            priority=event_in_db.priority,
            start_date=event_in_db.start_date,
            end_date=event_in_db.end_date,
            start_time=event_in_db.start_time,
            end_time=event_in_db.end_time,
            is_all_day=event_in_db.is_all_day,
            location=event_in_db.location,
            address=event_in_db.address,
            city=event_in_db.city,
            state=event_in_db.state,
            zip_code=event_in_db.zip_code,
            organizer_id=event_in_db.organizer_id,
            coordinator_name=event_in_db.coordinator_name,
            coordinator_phone=event_in_db.coordinator_phone,
            coordinator_email=event_in_db.coordinator_email,
            estimated_attendance=event_in_db.estimated_attendance,
            actual_attendance=event_in_db.actual_attendance,
            budget=event_in_db.budget,
            requirements=event_in_db.requirements,
            equipment_needed=event_in_db.equipment_needed,
            notes=event_in_db.notes,
            is_recurring=event_in_db.is_recurring,
            recurrence_pattern=event_in_db.recurrence_pattern,
            recurrence_end_date=event_in_db.recurrence_end_date,
            calendar_id=event_in_db.calendar_id,
            color=event_in_db.color,
            is_public=event_in_db.is_public,
            reminder_minutes=event_in_db.reminder_minutes,
            created_at=event_in_db.created_at,
            updated_at=event_in_db.updated_at,
        )

    async def get_event_by_id(self, event_id: str) -> CalendarEvent | None:
        """Get event by ID."""
        logger.debug("Getting event by ID: %s", event_id)
        event_in_db = await self.event_repo.get_by_id(event_id)
        if not event_in_db:
            return None

        return CalendarEvent(
            id=event_in_db.id,
            title=event_in_db.title,
            description=event_in_db.description,
            event_type=event_in_db.event_type,
            status=event_in_db.status,
            priority=event_in_db.priority,
            start_date=event_in_db.start_date,
            end_date=event_in_db.end_date,
            start_time=event_in_db.start_time,
            end_time=event_in_db.end_time,
            is_all_day=event_in_db.is_all_day,
            location=event_in_db.location,
            address=event_in_db.address,
            city=event_in_db.city,
            state=event_in_db.state,
            zip_code=event_in_db.zip_code,
            organizer_id=event_in_db.organizer_id,
            coordinator_name=event_in_db.coordinator_name,
            coordinator_phone=event_in_db.coordinator_phone,
            coordinator_email=event_in_db.coordinator_email,
            estimated_attendance=event_in_db.estimated_attendance,
            actual_attendance=event_in_db.actual_attendance,
            budget=event_in_db.budget,
            requirements=event_in_db.requirements,
            equipment_needed=event_in_db.equipment_needed,
            notes=event_in_db.notes,
            is_recurring=event_in_db.is_recurring,
            recurrence_pattern=event_in_db.recurrence_pattern,
            recurrence_end_date=event_in_db.recurrence_end_date,
            calendar_id=event_in_db.calendar_id,
            color=event_in_db.color,
            is_public=event_in_db.is_public,
            reminder_minutes=event_in_db.reminder_minutes,
            created_at=event_in_db.created_at,
            updated_at=event_in_db.updated_at,
        )

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
        return CalendarEvent(
            id=event_in_db.id,
            title=event_in_db.title,
            description=event_in_db.description,
            event_type=event_in_db.event_type,
            status=event_in_db.status,
            priority=event_in_db.priority,
            start_date=event_in_db.start_date,
            end_date=event_in_db.end_date,
            start_time=event_in_db.start_time,
            end_time=event_in_db.end_time,
            is_all_day=event_in_db.is_all_day,
            location=event_in_db.location,
            address=event_in_db.address,
            city=event_in_db.city,
            state=event_in_db.state,
            zip_code=event_in_db.zip_code,
            organizer_id=event_in_db.organizer_id,
            coordinator_name=event_in_db.coordinator_name,
            coordinator_phone=event_in_db.coordinator_phone,
            coordinator_email=event_in_db.coordinator_email,
            estimated_attendance=event_in_db.estimated_attendance,
            actual_attendance=event_in_db.actual_attendance,
            budget=event_in_db.budget,
            requirements=event_in_db.requirements,
            equipment_needed=event_in_db.equipment_needed,
            notes=event_in_db.notes,
            is_recurring=event_in_db.is_recurring,
            recurrence_pattern=event_in_db.recurrence_pattern,
            recurrence_end_date=event_in_db.recurrence_end_date,
            calendar_id=event_in_db.calendar_id,
            color=event_in_db.color,
            is_public=event_in_db.is_public,
            reminder_minutes=event_in_db.reminder_minutes,
            created_at=event_in_db.created_at,
            updated_at=event_in_db.updated_at,
        )

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
        event_type: EventType | None = None,
        status: EventStatus | None = None,
        priority: EventPriority | None = None,
        calendar_id: str | None = None,
    ) -> list[CalendarEvent]:
        """Get all events with pagination and optional filters."""
        logger.debug("Getting events with filters: skip=%d, limit=%d", skip, limit)

        filter_dict: dict[str, Any] = {}
        if event_type:
            filter_dict["event_type"] = event_type
        if status:
            filter_dict["status"] = status
        if priority:
            filter_dict["priority"] = priority
        if calendar_id:
            filter_dict["calendar_id"] = calendar_id

        events_in_db = await self.event_repo.get_many(
            skip=skip, limit=limit, search=search, filter_dict=filter_dict
        )

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                status=event.status,
                priority=event.priority,
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
                reminder_minutes=event.reminder_minutes,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]

    async def get_upcoming_events(self, limit: int = 10) -> list[CalendarEvent]:
        """Get upcoming events."""
        logger.debug("Getting upcoming events")
        events_in_db = await self.event_repo.get_upcoming_events(limit)

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                status=event.status,
                priority=event.priority,
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
                reminder_minutes=event.reminder_minutes,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]

    async def get_today_events(self) -> list[CalendarEvent]:
        """Get events scheduled for today."""
        logger.debug("Getting today's events")
        events_in_db = await self.event_repo.get_today_events()

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                status=event.status,
                priority=event.priority,
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
                reminder_minutes=event.reminder_minutes,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]

    async def get_this_week_events(self) -> list[CalendarEvent]:
        """Get events scheduled for this week."""
        logger.debug("Getting this week's events")
        events_in_db = await self.event_repo.get_this_week_events()

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                status=event.status,
                priority=event.priority,
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
                reminder_minutes=event.reminder_minutes,
                created_at=event.created_at,
                updated_at=event.updated_at,
            )
            for event in events_in_db
        ]

    async def get_this_month_events(self) -> list[CalendarEvent]:
        """Get events scheduled for this month."""
        logger.debug("Getting this month's events")
        events_in_db = await self.event_repo.get_this_month_events()

        return [
            CalendarEvent(
                id=event.id,
                title=event.title,
                description=event.description,
                event_type=event.event_type,
                status=event.status,
                priority=event.priority,
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
                reminder_minutes=event.reminder_minutes,
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
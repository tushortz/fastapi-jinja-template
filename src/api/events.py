"""Events and calendar API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth import get_current_user
from src.models.events import (
    Calendar, CalendarCreate, CalendarUpdate, EventPriority, EventStatus, EventType,
)
from src.models.users import User
from src.services.events import CalendarService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])
templates = Jinja2Templates(directory="src/templates")


# Calendar endpoints
@router.post("/calendars", response_model=Calendar, status_code=status.HTTP_201_CREATED)
async def create_calendar(
    calendar_create: CalendarCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new calendar."""
    logger.info("Creating calendar: %s for user: %s", calendar_create.name, current_user.id)

    try:
        calendar_service = CalendarService()
        calendar = await calendar_service.create_calendar(calendar_create)
        logger.info("Calendar created successfully: %s", calendar.id)
        return calendar
    except Exception as e:
        logger.error("Error creating calendar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create calendar"
        )


@router.get("/calendars", response_model=list[Calendar])
async def get_calendars(
    current_user: User = Depends(get_current_user),
    public_only: bool = Query(False, description="Get only public calendars"),
):
    """Get calendars."""
    logger.info("Getting calendars for user: %s", current_user.id)

    try:
        calendar_service = CalendarService()
        if public_only:
            calendars = await calendar_service.get_public_calendars()
        else:
            calendars = await calendar_service.get_calendars_by_owner(current_user.id)

        logger.info("Retrieved %d calendars", len(calendars))
        return calendars
    except Exception as e:
        logger.error("Error getting calendars: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get calendars"
        )


@router.get("/calendars/{calendar_id}", response_model=Calendar)
async def get_calendar(
    calendar_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get calendar by ID."""
    logger.info("Getting calendar: %s", calendar_id)

    try:
        calendar_service = CalendarService()
        calendar = await calendar_service.get_calendar_by_id(calendar_id)
        if not calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar not found"
            )

        logger.info("Calendar retrieved successfully: %s", calendar.id)
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting calendar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get calendar"
        )


@router.put("/calendars/{calendar_id}", response_model=Calendar)
async def update_calendar(
    calendar_id: str,
    calendar_update: CalendarUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update calendar."""
    logger.info("Updating calendar: %s", calendar_id)

    try:
        calendar_service = CalendarService()
        calendar = await calendar_service.update_calendar(calendar_id, calendar_update)
        if not calendar:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar not found"
            )

        logger.info("Calendar updated successfully: %s", calendar.id)
        return calendar
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating calendar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update calendar"
        )


@router.delete("/calendars/{calendar_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar(
    calendar_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete calendar."""
    logger.info("Deleting calendar: %s", calendar_id)

    try:
        calendar_service = CalendarService()
        result = await calendar_service.delete_calendar(calendar_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Calendar not found"
            )

        logger.info("Calendar deleted successfully: %s", calendar_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting calendar: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete calendar"
        )


# Calendar Event endpoints
@router.post("/", response_model=Calendar, status_code=status.HTTP_201_CREATED)
async def create_event(
    event_create: CalendarCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new calendar event."""
    logger.info("Creating event: %s for user: %s", event_create.title, current_user.id)

    try:
        event_service = CalendarService()
        event = await event_service.create_event(event_create)
        logger.info("Event created successfully: %s", event.id)
        return event
    except Exception as e:
        logger.error("Error creating event: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )


@router.get("/", response_model=list[Calendar])
async def get_events(
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    search: str | None = Query(None, description="Search term"),
    event_type: EventType | None = Query(None, description="Filter by event type"),
    status: EventStatus | None = Query(None, description="Filter by event status"),
    priority: EventPriority | None = Query(None, description="Filter by event priority"),
    calendar_id: str | None = Query(None, description="Filter by calendar ID"),
    current_user: User = Depends(get_current_user),
):
    """Get events with pagination and optional filters."""
    logger.info("Getting events with filters for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        events = await event_service.get_events(
            skip=skip,
            limit=limit,
            search=search,
            event_type=event_type,
            status=status,
            priority=priority,
            calendar_id=calendar_id,
        )

        logger.info("Retrieved %d events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get events"
        )


@router.get("/upcoming", response_model=list[Calendar])
async def get_upcoming_events(
    limit: int = Query(10, ge=1, le=100, description="Number of upcoming events to return"),
    current_user: User = Depends(get_current_user),
):
    """Get upcoming events."""
    logger.info("Getting upcoming events for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        events = await event_service.get_upcoming_events(limit=limit)

        logger.info("Retrieved %d upcoming events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting upcoming events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upcoming events"
        )


@router.get("/today", response_model=list[Calendar])
async def get_today_events(
    current_user: User = Depends(get_current_user),
):
    """Get today's events."""
    logger.info("Getting today's events for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        events = await event_service.get_today_events()

        logger.info("Retrieved %d today's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting today's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get today's events"
        )


@router.get("/this-week", response_model=list[Calendar])
async def get_this_week_events(
    current_user: User = Depends(get_current_user),
):
    """Get this week's events."""
    logger.info("Getting this week's events for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        events = await event_service.get_this_week_events()

        logger.info("Retrieved %d this week's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting this week's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get this week's events"
        )


@router.get("/this-month", response_model=list[Calendar])
async def get_this_month_events(
    current_user: User = Depends(get_current_user),
):
    """Get this month's events."""
    logger.info("Getting this month's events for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        events = await event_service.get_this_month_events()

        logger.info("Retrieved %d this month's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting this month's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get this month's events"
        )


@router.get("/statistics", response_model=dict[str, Any])
async def get_event_statistics(
    current_user: User = Depends(get_current_user),
):
    """Get event statistics."""
    logger.info("Getting event statistics for user: %s", current_user.id)

    try:
        event_service = CalendarService()
        stats = await event_service.get_event_statistics()

        logger.info("Event statistics retrieved successfully")
        return stats
    except Exception as e:
        logger.error("Error getting event statistics: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get event statistics"
        )


@router.get("/{event_id}", response_model=Calendar)
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get event by ID."""
    logger.info("Getting event: %s", event_id)

    try:
        event_service = CalendarService()
        event = await event_service.get_event_by_id(event_id)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        logger.info("Event retrieved successfully: %s", event.id)
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting event: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get event"
        )


@router.put("/{event_id}", response_model=Calendar)
async def update_event(
    event_id: str,
    event_update: CalendarUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update event."""
    logger.info("Updating event: %s", event_id)

    try:
        event_service = CalendarService()
        event = await event_service.update_event(event_id, event_update)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        logger.info("Event updated successfully: %s", event.id)
        return event
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating event: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update event"
        )


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete event."""
    logger.info("Deleting event: %s", event_id)

    try:
        event_service = CalendarService()
        result = await event_service.delete_event(event_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Event not found"
            )

        logger.info("Event deleted successfully: %s", event_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting event: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete event"
        )


# Web UI endpoints
@router.get("/dashboard", response_class=HTMLResponse)
async def events_dashboard(request: Request):
    """Events dashboard page."""
    return templates.TemplateResponse("events/dashboard.html", {"request": request})


@router.get("/list", response_class=HTMLResponse)
async def events_list(request: Request):
    """Events list page."""
    return templates.TemplateResponse("events/list.html", {"request": request})


@router.get("/create", response_class=HTMLResponse)
async def create_event_form(request: Request):
    """Create event form page."""
    return templates.TemplateResponse("events/create.html", {"request": request})


@router.get("/calendars", response_class=HTMLResponse)
async def calendars_list(request: Request):
    """Calendars list page."""
    return templates.TemplateResponse("events/calendars.html", {"request": request})
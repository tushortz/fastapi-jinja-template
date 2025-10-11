"""Events and calendar API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth import get_current_user
from src.models.events import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from src.models.users import User
from src.services.events import CalendarEventService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/events", tags=["events"])
templates = Jinja2Templates(directory="src/templates")


# Calendar endpoints removed


# Calendar Event endpoints
@router.post("/", response_model=CalendarEvent, status_code=status.HTTP_201_CREATED, name="api_create_event")
async def create_event(
    event_create: CalendarEventCreate,
    current_user: User = Depends(get_current_user),
):
    """Create a new calendar event."""
    logger.info("Creating event: %s for user: %s", event_create.title, current_user.id)

    try:
        event_service = CalendarEventService()
        event = await event_service.create_event(event_create)
        logger.info("Event created successfully: %s", event.id)
        return event
    except Exception as e:
        logger.error("Error creating event: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create event"
        )


@router.get("/", response_model=list[CalendarEvent], name="api_get_events")
async def get_events(
    skip: int = Query(0, ge=0, description="Number of events to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of events to return"),
    search: str | None = Query(None, description="Search term"),
    # status and priority removed
    calendar_id: str | None = Query(None, description="Filter by calendar ID"),
    current_user: User = Depends(get_current_user),
):
    """Get events with pagination and optional filters."""
    logger.info("Getting events with filters for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        events = await event_service.get_events(
            skip=skip,
            limit=limit,
            search=search,

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


@router.get("/upcoming", response_model=list[CalendarEvent], name="api_get_upcoming_events")
async def get_upcoming_events(
    limit: int = Query(10, ge=1, le=100, description="Number of upcoming events to return"),
    current_user: User = Depends(get_current_user),
):
    """Get upcoming events."""
    logger.info("Getting upcoming events for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        events = await event_service.get_upcoming_events(limit=limit)

        logger.info("Retrieved %d upcoming events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting upcoming events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get upcoming events"
        )


@router.get("/today", response_model=list[CalendarEvent], name="api_get_today_events")
async def get_today_events(
    current_user: User = Depends(get_current_user),
):
    """Get today's events."""
    logger.info("Getting today's events for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        events = await event_service.get_today_events()

        logger.info("Retrieved %d today's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting today's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get today's events"
        )


@router.get("/this-week", response_model=list[CalendarEvent], name="api_get_this_week_events")
async def get_this_week_events(
    current_user: User = Depends(get_current_user),
):
    """Get this week's events."""
    logger.info("Getting this week's events for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        events = await event_service.get_this_week_events()

        logger.info("Retrieved %d this week's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting this week's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get this week's events"
        )


@router.get("/this-month", response_model=list[CalendarEvent], name="api_get_this_month_events")
async def get_this_month_events(
    current_user: User = Depends(get_current_user),
):
    """Get this month's events."""
    logger.info("Getting this month's events for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        events = await event_service.get_this_month_events()

        logger.info("Retrieved %d this month's events", len(events))
        return events
    except Exception as e:
        logger.error("Error getting this month's events: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get this month's events"
        )


@router.get("/statistics", response_model=dict[str, Any], name="api_get_event_statistics")
async def get_event_statistics(
    current_user: User = Depends(get_current_user),
):
    """Get event statistics."""
    logger.info("Getting event statistics for user: %s", current_user.id)

    try:
        event_service = CalendarEventService()
        stats = await event_service.get_event_statistics()

        logger.info("Event statistics retrieved successfully")
        return stats
    except Exception as e:
        logger.error("Error getting event statistics: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get event statistics"
        )


@router.get("/{event_id}", response_model=CalendarEvent, name="api_get_event")
async def get_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get event by ID."""
    logger.info("Getting event: %s", event_id)

    try:
        event_service = CalendarEventService()
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


@router.put("/{event_id}", response_model=CalendarEvent, name="api_update_event")
async def update_event(
    event_id: str,
    event_update: CalendarEventUpdate,
    current_user: User = Depends(get_current_user),
):
    """Update event."""
    logger.info("Updating event: %s", event_id)

    try:
        event_service = CalendarEventService()
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


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT, name="api_delete_event")
async def delete_event(
    event_id: str,
    current_user: User = Depends(get_current_user),
):
    """Delete event."""
    logger.info("Deleting event: %s", event_id)

    try:
        event_service = CalendarEventService()
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


# Note: All HTML-rendering endpoints are defined under /dashboard in web_routes.py
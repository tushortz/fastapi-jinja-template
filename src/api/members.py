"""Member API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.auth import get_current_user
from src.models.members import (
    Member, MemberCreate, MemberRole, MemberStatus, MemberUpdate,
)
from src.models.users import User
from src.services.members import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/members", tags=["members"])
templates = Jinja2Templates(directory="src/templates")


@router.post("/", response_model=Member, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_create: MemberCreate,
    current_user: User = Depends(get_current_user),
) -> Member:
    """Create a new member."""
    logger.info("Creating member: %s %s", member_create.first_name, member_create.last_name)

    try:
        member_service = MemberService()
        member = await member_service.create_member(member_create)
        logger.info("Member created successfully: %s", member.id)
        return member
    except ValueError as e:
        logger.warning("Failed to create member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error("Error creating member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/", response_model=list[Member])
async def get_members(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: str | None = Query(None, description="Search term"),
    status: MemberStatus | None = Query(None, description="Filter by member status"),
    role: MemberRole | None = Query(None, description="Filter by member role"),
    current_user: User = Depends(get_current_user),
) -> list[Member]:
    """Get all members with pagination and optional filters."""
    logger.debug("Getting members: skip=%d, limit=%d", skip, limit)

    try:
        member_service = MemberService()
        members = await member_service.get_members(
            skip=skip, limit=limit, search=search, status=status, role=role
        )
        logger.info("Retrieved %d members", len(members))
        return members
    except Exception as e:
        logger.error("Error getting members: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/active", response_model=list[Member])
async def get_active_members(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    current_user: User = Depends(get_current_user),
) -> list[Member]:
    """Get active members only."""
    logger.debug("Getting active members: skip=%d, limit=%d", skip, limit)

    try:
        member_service = MemberService()
        members = await member_service.get_active_members(skip=skip, limit=limit)
        logger.info("Retrieved %d active members", len(members))
        return members
    except Exception as e:
        logger.error("Error getting active members: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/birthdays/this-month", response_model=list[Member])
async def get_birthdays_this_month(
    current_user: User = Depends(get_current_user),
) -> list[Member]:
    """Get members with birthdays this month."""
    logger.debug("Getting members with birthdays this month")

    try:
        member_service = MemberService()
        members = await member_service.get_birthdays_this_month()
        logger.info("Retrieved %d members with birthdays this month", len(members))
        return members
    except Exception as e:
        logger.error("Error getting birthdays this month: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/birthdays/today", response_model=list[Member])
async def get_birthdays_today(
    current_user: User = Depends(get_current_user),
) -> list[Member]:
    """Get members with birthdays today."""
    logger.debug("Getting members with birthdays today")

    try:
        member_service = MemberService()
        members = await member_service.get_birthdays_today()
        logger.info("Retrieved %d members with birthdays today", len(members))
        return members
    except Exception as e:
        logger.error("Error getting birthdays today: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/statistics")
async def get_member_statistics(
    current_user: User = Depends(get_current_user),
) -> dict[str, Any]:
    """Get member statistics."""
    logger.debug("Getting member statistics")

    try:
        member_service = MemberService()
        stats = await member_service.get_member_statistics()
        logger.info("Retrieved member statistics")
        return stats
    except Exception as e:
        logger.error("Error getting member statistics: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{member_id}", response_model=Member)
async def get_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
) -> Member:
    """Get a specific member by ID."""
    logger.debug("Getting member by ID: %s", member_id)

    try:
        member_service = MemberService()
        member = await member_service.get_member_by_id(member_id)
        if not member:
            logger.warning("Member not found: %s", member_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        logger.info("Retrieved member: %s", member_id)
        return member
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.put("/{member_id}", response_model=Member)
async def update_member(
    member_id: str,
    member_update: MemberUpdate,
    current_user: User = Depends(get_current_user),
) -> Member:
    """Update a member."""
    logger.info("Updating member: %s", member_id)

    try:
        member_service = MemberService()
        member = await member_service.update_member(member_id, member_update)
        if not member:
            logger.warning("Member not found for update: %s", member_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        logger.info("Member updated successfully: %s", member_id)
        return member
    except ValueError as e:
        logger.warning("Failed to update member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error updating member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a member (deactivate)."""
    logger.info("Deleting member: %s", member_id)

    try:
        member_service = MemberService()
        success = await member_service.delete_member(member_id)
        if not success:
            logger.warning("Member not found for deletion: %s", member_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        logger.info("Member deleted successfully: %s", member_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error deleting member: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# Web routes for member management
@router.get("/dashboard", response_class=HTMLResponse)
async def members_dashboard(
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Member dashboard page."""
    logger.debug("Rendering members dashboard")

    try:
        member_service = MemberService()
        stats = await member_service.get_member_statistics()
        birthdays_today = await member_service.get_birthdays_today()
        birthdays_this_month = await member_service.get_birthdays_this_month()

        return templates.TemplateResponse(
            "members/dashboard.html",
            {
                "request": {},
                "current_user": current_user,
                "stats": stats,
                "birthdays_today": birthdays_today,
                "birthdays_this_month": birthdays_this_month,
            }
        )
    except Exception as e:
        logger.error("Error rendering members dashboard: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/list", response_class=HTMLResponse)
async def members_list(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str | None = Query(None),
    status: MemberStatus | None = Query(None),
    role: MemberRole | None = Query(None),
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Members list page."""
    logger.debug("Rendering members list")

    try:
        member_service = MemberService()
        members = await member_service.get_members(
            skip=skip, limit=limit, search=search, status=status, role=role
        )
        total_count = await member_service.count_members()

        return templates.TemplateResponse(
            "members/list.html",
            {
                "request": {},
                "current_user": current_user,
                "members": members,
                "total_count": total_count,
                "skip": skip,
                "limit": limit,
                "search": search,
                "status_filter": status,
                "role_filter": role,
            }
        )
    except Exception as e:
        logger.error("Error rendering members list: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/create", response_class=HTMLResponse)
async def create_member_form(
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Create member form page."""
    logger.debug("Rendering create member form")

    return templates.TemplateResponse(
        "members/create.html",
        {
            "request": {},
            "current_user": current_user,
        }
    )


@router.get("/{member_id}/edit", response_class=HTMLResponse)
async def edit_member_form(
    member_id: str,
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """Edit member form page."""
    logger.debug("Rendering edit member form for: %s", member_id)

    try:
        member_service = MemberService()
        member = await member_service.get_member_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        return templates.TemplateResponse(
            "members/edit.html",
            {
                "request": {},
                "current_user": current_user,
                "member": member,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error rendering edit member form: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/{member_id}/view", response_class=HTMLResponse)
async def view_member(
    member_id: str,
    current_user: User = Depends(get_current_user),
) -> HTMLResponse:
    """View member details page."""
    logger.debug("Rendering member view for: %s", member_id)

    try:
        member_service = MemberService()
        member = await member_service.get_member_by_id(member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        return templates.TemplateResponse(
            "members/view.html",
            {
                "request": {},
                "current_user": current_user,
                "member": member,
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error rendering member view: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

"""Member API endpoints."""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_user
from src.models.members import (
    Gender, MaritalStatus, Member, MemberCreate, MemberRole, MemberStatus, MemberUpdate,
    Ministry,
)
from src.models.users import User
from src.services.members import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/members", tags=["members"])


@router.post("/", response_model=Member, status_code=status.HTTP_201_CREATED, name="api_create_member")
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


@router.get("/", response_model=list[Member], name="api_get_members")
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


@router.get("/active", response_model=list[Member], name="api_get_active_members")
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


@router.get("/birthdays/this-month", response_model=list[Member], name="api_get_birthdays_this_month")
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


@router.get("/birthdays/today", response_model=list[Member], name="api_get_birthdays_today")
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


@router.get("/statistics", name="api_get_member_statistics")
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


@router.get("/{member_id}", response_model=Member, name="api_get_member")
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


@router.put("/{member_id}", response_model=Member, name="api_update_member")
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


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT, name="api_delete_member")
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


# Note: HTML-rendering pages are defined under /dashboard in web_routes.py


@router.get("/enums/statuses", response_model=list[str], name="api_get_member_statuses")
async def get_member_statuses(
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return available member statuses from the enum."""
    return [s.value for s in MemberStatus]


@router.get("/enums/roles", response_model=list[str], name="api_get_member_roles")
async def get_member_roles(
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return available member roles from the enum."""
    return [r.value for r in MemberRole]


@router.get("/enums/genders", response_model=list[str], name="api_get_member_genders")
async def get_member_genders(
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return available genders from the enum."""
    return [g.value for g in Gender]


@router.get("/enums/marital-statuses", response_model=list[str], name="api_get_marital_statuses")
async def get_marital_statuses(
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return available marital statuses from the enum."""
    return [m.value for m in MaritalStatus]


@router.get("/enums/ministries", response_model=list[str], name="api_get_ministries")
async def get_ministries(
    current_user: User = Depends(get_current_user),
) -> list[str]:
    """Return available ministries from the enum."""
    return [m.value for m in Ministry]

"""Admin endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.auth import get_current_admin_user
from src.models.users import User, UserUpdate
from src.services.users import UserService

router = APIRouter(prefix="/admin", tags=["admin"])

logger = logging.getLogger(__name__)


@router.get("/users", response_model=list[User], name="api_admin_users")
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: str | None = Query(None, description="Search by username or email"),
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(),
):
    """Get all users (admin only)."""
    users = await user_service.get_users(skip=skip, limit=limit, search=search)
    return users


@router.put("/users/{user_id}", response_model=User, name="api_admin_update_user")
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(),
):
    """Update user information (admin only)."""
    logger.info("Admin %s updating user %s", current_user.username, user_id)

    try:
        updated_user = await user_service.update_user(user_id, user_update)
        if not updated_user:
            logger.warning("User not found for update: %s", user_id)
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        logger.info("User updated successfully: %s", updated_user.username)
        return updated_user
    except ValueError as e:
        logger.warning("Invalid user update data: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.error("Error updating user %s: %s", user_id, str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        ) from e


@router.delete("/users/{user_id}", name="api_admin_delete_user")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_admin_user),
    user_service: UserService = Depends(),
):
    """Deactivate user (admin only)."""
    success = await user_service.delete_user(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": "User deactivated successfully"}

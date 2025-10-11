"""Authentication endpoints."""

import logging
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    verify_refresh_token,
)
from src.config import settings
from src.models.users import User, UserCreate, UserProfileUpdate
from src.services.users import UserService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=User, name="api_register")
async def register(user_create: UserCreate, user_service: UserService = Depends()):
    """Register a new user."""
    logger.info(
        "User registration attempt for email: %s, username: %s",
        user_create.email,
        user_create.username,
    )

    try:
        user = await user_service.create_user(user_create)
        logger.info("User registered successfully: %s (%s)", user.username, user.id)
        return user
    except ValueError as e:
        logger.warning("User registration failed for %s: %s", user_create.email, str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error during user registration for %s: %s",
            user_create.email,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e


@router.post("/login", name="api_login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(),
):
    """Login user and return access token."""
    logger.info("Login attempt for username/email: %s", form_data.username)

    # Check if user exists and get authentication result
    user = await user_service.get_user_by_email(form_data.username)
    if not user:
        logger.warning(
            "Failed login attempt for: %s (user not found)", form_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        logger.warning("Failed login attempt for inactive user: %s", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your account has been deactivated. Please contact support.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Authenticate user with password
    authenticated_user = await user_service.authenticate_user(
        form_data.username, form_data.password
    )
    if not authenticated_user:
        logger.warning(
            "Failed login attempt for: %s (invalid password)", form_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": authenticated_user.id}, expires_delta=access_token_expires
    )

    user_refresh_token = create_refresh_token(data={"sub": authenticated_user.id})

    logger.info(
        "Successful login for user: %s (%s)",
        authenticated_user.username,
        authenticated_user.id,
    )

    return {
        "access_token": access_token,
        "refresh_token": user_refresh_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,  # seconds
        "user": User(
            id=authenticated_user.id,
            email=authenticated_user.email,
            username=authenticated_user.username,
            is_active=authenticated_user.is_active,
            is_admin=authenticated_user.is_admin,
            created_at=authenticated_user.created_at,
            updated_at=authenticated_user.updated_at,
        ),
    }


@router.post("/refresh", name="api_refresh")
async def refresh_access_token(
    request: Request,
    user_service: UserService = Depends(),
):
    """Refresh access token using refresh token."""
    logger.info("Token refresh attempt")

    body = await request.json()
    token_refresh = body.get("refresh_token")
    if not token_refresh:
        logger.warning("No refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
        )

    user_id = verify_refresh_token(token_refresh)
    if not user_id:
        logger.warning("Invalid refresh token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await user_service.get_user_by_id(user_id)
    if not user:
        logger.warning("User not found for refresh token: %s", user_id)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    new_access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )

    logger.info(
        "Token refreshed successfully for user: %s (%s)", user.username, user.id
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.access_token_expire_minutes * 60,  # seconds
    }


@router.get("/me", response_model=User, name="api_me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    logger.debug(
        "User info requested for: %s (%s)", current_user.username, current_user.id
    )
    return current_user


@router.post("/logout", name="api_logout")
async def logout():
    """Logout endpoint."""
    logger.info("User logout")
    return {"message": "Successfully logged out"}


@router.put("/profile", response_model=User, name="api_update_profile")
async def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(),
):
    """Update current user's profile."""
    logger.info("Profile update requested for user: %s", current_user.username)

    try:
        updated_user = await user_service.update_user_profile(
            current_user.id, profile_update
        )
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        logger.info("Profile updated successfully for user: %s", updated_user.username)
        return updated_user
    except ValueError as e:
        logger.warning(
            "Profile update failed for %s: %s", current_user.username, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
    except Exception as e:
        logger.error(
            "Unexpected error during profile update for %s: %s",
            current_user.username,
            str(e),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        ) from e

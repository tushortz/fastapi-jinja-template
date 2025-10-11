"""Authentication and authorization utilities."""

import logging
from datetime import timedelta

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config import settings
from src.models.users import User
from src.services.users import UserService
from src.utils.date import get_current_date

logger = logging.getLogger(__name__)

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT access token."""
    logger.info("Creating access token for user: %s", data.get("sub", "unknown"))

    to_encode = data.copy()
    if expires_delta:
        expire = get_current_date() + expires_delta
    else:
        expire = get_current_date() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    logger.info(
        "Access token created successfully for user: %s", data.get("sub", "unknown")
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create JWT refresh token."""
    logger.info("Creating refresh token for user: %s", data.get("sub", "unknown"))

    to_encode = data.copy()
    if expires_delta:
        expire = get_current_date() + expires_delta
    else:
        expire = get_current_date() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )

    logger.info(
        "Refresh token created successfully for user: %s", data.get("sub", "unknown")
    )
    return encoded_jwt


def verify_refresh_token(token: str) -> str | None:
    """Verify refresh token and return user ID."""
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "refresh":
            logger.warning("Invalid refresh token: missing user ID or wrong type")
            return None

        logger.debug("Refresh token verified for user: %s", user_id)
        return user_id
    except JWTError as e:
        logger.warning("Refresh token validation failed: %s", str(e))
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_service: UserService = Depends(),
) -> User:
    """Get current authenticated user."""
    logger.debug("Attempting to get current user from token")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing user ID")
            raise credentials_exception
    except JWTError as e:
        logger.warning("JWT validation failed: %s", str(e))
        raise credentials_exception from e

    user = await user_service.get_user_by_id(user_id)
    if user is None:
        logger.warning("User not found for ID: %s", user_id)
        raise credentials_exception

    logger.debug("Successfully authenticated user: %s (%s)", user.username, user.id)
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        logger.warning(
            "Inactive user attempted access: %s (%s)",
            current_user.username,
            current_user.id,
        )
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.debug("Active user access granted: %s", current_user.username)
    return current_user


def require_active_user(func):
    """Decorator to require active user for web routes."""
    from functools import wraps

    from fastapi.responses import RedirectResponse

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        current_user = await get_current_user_from_cookie(request)
        if not current_user:
            logger.debug("Unauthenticated user attempted to access %s", func.__name__)
            return RedirectResponse(url=request.url_for("login"))

        if not current_user.is_active:
            logger.warning(
                "Inactive user attempted to access %s: %s",
                func.__name__,
                current_user.username,
            )
            return RedirectResponse(url=request.url_for("login"))

        logger.debug(
            "Active user access granted to %s: %s", func.__name__, current_user.username
        )
        return await func(request, *args, **kwargs)

    return wrapper


def require_admin_user(func):
    """Decorator to require admin user for web routes."""
    from functools import wraps

    from fastapi.responses import RedirectResponse

    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs):
        current_user = await get_current_user_from_cookie(request)
        if not current_user:
            logger.debug(
                "Unauthenticated user attempted to access admin %s", func.__name__
            )
            return RedirectResponse(url=request.url_for("login"))

        if not current_user.is_active:
            logger.warning(
                "Inactive user attempted to access admin %s: %s",
                func.__name__,
                current_user.username,
            )
            return RedirectResponse(url=request.url_for("login"))

        if not current_user.is_admin:
            logger.warning(
                "Non-admin user attempted to access admin %s: %s",
                func.__name__,
                current_user.username,
            )
            return RedirectResponse(url=request.url_for("dashboard"))

        logger.debug(
            "Admin user access granted to %s: %s", func.__name__, current_user.username
        )
        return await func(request, *args, **kwargs)

    return wrapper


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """Get current admin user."""
    if not current_user.is_admin:
        logger.warning(
            "Non-admin user attempted admin access: %s (%s)",
            current_user.username,
            current_user.id,
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )

    logger.debug("Admin access granted: %s", current_user.username)
    return current_user


async def get_current_user_from_cookie(
    request: Request,
) -> User | None:
    """Get current authenticated user from cookie (for web routes)."""
    logger.debug("Attempting to get current user from cookie")

    # Try to get token from cookie first
    token = request.cookies.get("access_token")
    logger.debug("Cookie token: %s", token[:20] + "..." if token else "None")

    if not token:
        # Try to get token from Authorization header as fallback
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
            logger.debug("Header token: %s", token[:20] + "..." if token else "None")

    if not token:
        logger.debug("No token found in cookie or header")
        return None

    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token payload missing user ID")
            return None
    except JWTError as e:
        logger.warning("JWT validation failed: %s", str(e))
        return None

    # Create UserService instance directly
    user_service = UserService()
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        logger.warning("User not found for ID: %s", user_id)
        return None

    logger.debug(
        "Successfully authenticated user from cookie: %s (%s)", user.username, user.id
    )
    return user

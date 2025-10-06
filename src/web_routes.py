"""Web routes for UI pages."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.auth import (
    get_current_user_from_cookie,
    require_active_user,
    require_admin_user,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ui", tags=["ui"])
templates = Jinja2Templates(directory="src/templates")


@router.get("/", response_class=HTMLResponse, name="home")
async def home(request: Request):
    """Home page - redirects to dashboard if logged in, otherwise shows landing page."""
    logger.debug("Home page requested")

    current_user = await get_current_user_from_cookie(request)
    if current_user and current_user.is_active:
        logger.debug(
            "Authenticated active user %s redirected to dashboard",
            current_user.username,
        )
        return RedirectResponse(url=request.url_for("dashboard"))
    elif current_user and not current_user.is_active:
        logger.warning(
            "Inactive user %s redirected to login from home", current_user.username
        )
        return RedirectResponse(url=request.url_for("login"))

    logger.debug("Unauthenticated user, showing landing page")
    return templates.TemplateResponse(
        "landing.html", {"request": request, "user": None}
    )


@router.get("/dashboard", response_class=HTMLResponse, name="dashboard")
@require_active_user
async def dashboard(request: Request):
    """Dashboard page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Dashboard accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "dashboard/dashboard.html", {"request": request, "user": current_user}
    )


@router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    """Login page."""
    current_user = await get_current_user_from_cookie(request)
    if current_user and current_user.is_active:
        logger.debug(
            "Authenticated active user %s redirected to dashboard from login",
            current_user.username,
        )
        return RedirectResponse(url=request.url_for("dashboard"))

    logger.debug("Unauthenticated user, showing login page")
    return templates.TemplateResponse(
        "auth/login.html", {"request": request, "user": None}
    )


@router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    """Registration page."""
    current_user = await get_current_user_from_cookie(request)
    if current_user and current_user.is_active:
        logger.debug(
            "Authenticated active user %s redirected to dashboard from register",
            current_user.username,
        )
        return RedirectResponse(url=request.url_for("dashboard"))
    elif current_user and not current_user.is_active:
        logger.warning(
            "Inactive user %s redirected to login from register page",
            current_user.username,
        )
        return RedirectResponse(url=request.url_for("login"))

    logger.debug("Unauthenticated user, showing register page")
    return templates.TemplateResponse(
        "auth/register.html", {"request": request, "user": None}
    )


@router.get("/admin", response_class=HTMLResponse, name="admin_dashboard")
@require_admin_user
async def admin_dashboard(request: Request):
    """Admin dashboard page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Admin dashboard accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "admin/dashboard.html", {"request": request, "user": current_user}
    )


@router.get("/logout", response_class=HTMLResponse, name="logout")
async def logout_page(request: Request):
    """Logout page - redirects to home after logout."""
    logger.debug("Logout page requested")
    return RedirectResponse(url=request.url_for("home"))


@router.get("/admin/users", response_class=HTMLResponse, name="admin_users")
@require_admin_user
async def admin_users(request: Request):
    """Admin users management page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Admin users page accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "admin/users.html", {"request": request, "user": current_user}
    )


@router.get("/profile", response_class=HTMLResponse, name="profile")
@require_active_user
async def profile_page(request: Request):
    """Profile update page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Profile page accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "auth/profile.html", {"request": request, "user": current_user}
    )

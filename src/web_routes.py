"""Web routes for UI pages."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.auth import (
    get_current_user_from_cookie, require_active_user, require_admin_user,
)
from src.models.members import MemberStatus
from src.repositories.members import MemberRepository
from src.services.attendance import AttendanceService
from src.services.events import CalendarEventService
from src.services.members import MemberService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
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


@router.get("/admin/backup", response_class=HTMLResponse, name="admin_backup")
@require_admin_user
async def admin_backup_page(request: Request):
    """Admin backup and restore page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "admin/backup.html", {"request": request, "user": current_user}
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


# Church Management Routes
@router.get("/members", response_class=HTMLResponse, name="members_dashboard")
@require_active_user
async def members_dashboard_redirect(request: Request):
    """Members dashboard page (cookie-auth HTML)."""
    current_user = await get_current_user_from_cookie(request)
    # Load dashboard context expected by template
    service = MemberService()
    stats = await service.get_member_statistics()
    birthdays_today = await service.get_birthdays_today()
    birthdays_this_month = await service.get_birthdays_this_month()
    return templates.TemplateResponse(
        "members/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "birthdays_today": birthdays_today,
            "birthdays_this_month": birthdays_this_month,
        },
    )


@router.get("/attendance", response_class=HTMLResponse, name="attendance_dashboard")
@require_active_user
async def attendance_dashboard_redirect(request: Request):
    """Attendance dashboard page (cookie-auth HTML)."""
    current_user = await get_current_user_from_cookie(request)
    service = AttendanceService()
    stats = await service.get_attendance_statistics()
    try:
        recent_attendance = await service.get_recent_attendance(limit=10)
    except Exception:
        recent_attendance = []
    return templates.TemplateResponse(
        "attendance/dashboard.html",
        {
            "request": request,
            "user": current_user,
            "stats": stats,
            "recent_attendance": recent_attendance,
        },
    )


@router.get("/events", response_class=HTMLResponse, name="events_dashboard")
@require_active_user
async def events_dashboard_redirect(request: Request):
    """Events dashboard page (cookie-auth HTML)."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/dashboard.html", {"request": request, "user": current_user}
    )


@router.get("/events/list", response_class=HTMLResponse, name="events_list")
@require_active_user
async def events_list_page(request: Request):
    """Events list page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/list.html", {"request": request, "user": current_user}
    )


@router.get("/events/create", response_class=HTMLResponse, name="create_event_form")
@require_active_user
async def create_event_form_page(request: Request):
    """Create event form page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/create.html", {"request": request, "user": current_user}
    )



@router.get("/events/{event_id}/view", response_class=HTMLResponse, name="event_view")
@require_active_user
async def event_view_page(request: Request, event_id: str):
    """Event details page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/view.html",
        {"request": request, "user": current_user, "event_id": event_id},
    )


@router.get("/events/{event_id}/edit", response_class=HTMLResponse, name="event_edit_form")
@require_active_user
async def event_edit_form_page(request: Request, event_id: str):
    """Edit event form page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/edit.html",
        {"request": request, "user": current_user, "event_id": event_id},
    )


@router.get("/events/today", response_class=HTMLResponse, name="events_today")
@require_active_user
async def events_today_page(request: Request):
    """Today's events page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/today.html", {"request": request, "user": current_user}
    )


@router.get("/events/past", response_class=HTMLResponse, name="events_past")
@require_active_user
async def events_past_page(request: Request):
    """Past events page (end_date < today or start_date < today if no end_date)."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "events/past.html", {"request": request, "user": current_user}
    )


# UI JSON endpoints for dashboard widgets (cookie-authenticated)
@router.get("/events/statistics-json")
@require_active_user
async def ui_events_statistics(request: Request):
    """Return event statistics for UI widgets (cookie auth)."""
    service = CalendarEventService()
    stats = await service.get_event_statistics()
    return JSONResponse(stats)


@router.get("/events/upcoming-json")
@require_active_user
async def ui_events_upcoming(request: Request, limit: int = 5):
    """Return upcoming events for UI widgets (cookie auth)."""
    service = CalendarEventService()
    events = await service.get_upcoming_events(limit=limit)
    # Pydantic models → JSON-safe dicts
    return JSONResponse([e.model_dump(mode="json") for e in events])


@router.get("/members/list", response_class=HTMLResponse, name="members_list")
@require_active_user
async def members_list_page(request: Request):
    """Members list page."""
    current_user = await get_current_user_from_cookie(request)

    # Query params
    qp = request.query_params
    try:
        skip = int(qp.get("skip", 0))
    except ValueError:
        skip = 0
    try:
        limit = int(qp.get("limit", 25))
    except ValueError:
        limit = 25
    search = qp.get("search") or None
    status_filter = qp.get("status") or ""
    role_filter = qp.get("role") or ""

    # Load members via service (filters limited to search for now)
    member_service = MemberService()
    members = await member_service.get_members(skip=skip, limit=limit, search=search)
    # Exclude relocated or inactive in UI layer
    members = [m for m in members if m.is_active and m.status != MemberStatus.RELOCATED]

    # Count total (apply same search plus active/relocated filters)
    repo = MemberRepository()
    filter_dict: dict[str, object] = {"is_active": True, "status": {"$ne": MemberStatus.RELOCATED}}
    if search:
        filter_dict["$or"] = [
            {"first_name": {"$regex": search, "$options": "i"}},
            {"last_name": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
            {"phone": {"$regex": search, "$options": "i"}},
        ]
    total_count = await repo.count(filter_dict)

    return templates.TemplateResponse(
        "members/list.html",
        {
            "request": request,
            "user": current_user,
            "members": members,
            "total_count": total_count,
            "skip": skip,
            "limit": limit,
            "search": search or "",
            "status_filter": status_filter,
            "role_filter": role_filter,
        },
    )


@router.get("/members/create", response_class=HTMLResponse, name="create_member_form")
@require_active_user
async def create_member_form_page(request: Request):
    """Create member form page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "members/create.html", {"request": request, "user": current_user}
    )


@router.get("/members/{member_id}/view", response_class=HTMLResponse, name="view_member")
@require_active_user
async def view_member_page(request: Request, member_id: str):
    """Member details page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "members/view.html", {"request": request, "user": current_user, "member_id": member_id}
    )


@router.post("/members/insight", name="member_insight_api")
@require_active_user
async def members_ai_insight(request: Request):
    """Generate AI insight for a member (cookie-auth UI endpoint)."""
    await get_current_user_from_cookie(request)
    try:
        body = await request.json()
        member_service = MemberService()
        member_data = body.get("member") or {}
        member_id = member_data.get("id")
        if member_id:
            member = await member_service.get_member_by_id(member_id)
        else:
            from src.models.members import Member
            member = Member(**member_data)
        insight = await member_service.generate_member_insight(member)
        return JSONResponse({"insight": insight})
    except Exception as exc:  # noqa: BLE001
        logger.error("AI insight failed: %s", str(exc))
        return JSONResponse({"detail": "Failed to generate insight"}, status_code=500)

@router.get("/members/{member_id}/edit", response_class=HTMLResponse, name="edit_member_form")
@require_active_user
async def edit_member_form_page(request: Request, member_id: str):
    """Edit member form page (loads member into template context)."""
    current_user = await get_current_user_from_cookie(request)
    service = MemberService()
    member = await service.get_member_by_id(member_id)
    return templates.TemplateResponse(
        "members/edit.html",
        {"request": request, "user": current_user, "member": member},
    )


@router.get("/attendance/list", response_class=HTMLResponse, name="attendance_list")
@require_active_user
async def attendance_list_page(request: Request):
    """Attendance list page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "attendance/list.html", {"request": request, "user": current_user}
    )


@router.get("/attendance/create", response_class=HTMLResponse, name="create_attendance_form")
@require_active_user
async def create_attendance_form_page(request: Request):
    """Create attendance form page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "attendance/create.html", {"request": request, "user": current_user}
    )

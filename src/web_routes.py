"""Web routes for UI pages."""

import logging

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException

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


@router.get("/quotes", response_class=HTMLResponse, name="quotes_list")
@require_active_user
async def quotes_list(request: Request):
    """Quotes list page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Quotes list accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "quotes/list.html", {"request": request, "user": current_user}
    )


@router.get("/quotes/new", response_class=HTMLResponse, name="new_quote")
@require_active_user
async def new_quote(request: Request):
    """New quote page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "quotes/new.html", {"request": request, "user": current_user}
    )


@router.get("/quotes/{quote_id}", response_class=HTMLResponse, name="quote_detail")
@require_active_user
async def quote_detail(request: Request, quote_id: str):
    """Quote detail page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "quotes/detail.html",
        {"request": request, "user": current_user, "quote_id": quote_id},
    )


@router.get("/books", response_class=HTMLResponse, name="books_list")
@require_active_user
async def books_list(request: Request):
    """Books list page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Books list accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "books/list.html", {"request": request, "user": current_user}
    )


@router.get("/books/new", response_class=HTMLResponse, name="new_book")
@require_active_user
async def new_book(request: Request):
    """New book page."""
    current_user = await get_current_user_from_cookie(request)
    return templates.TemplateResponse(
        "books/new.html", {"request": request, "user": current_user}
    )


@router.get("/books/{book_id}", response_class=HTMLResponse, name="book_detail")
@require_active_user
async def book_detail(request: Request, book_id: str):
    """Book detail page."""
    current_user = await get_current_user_from_cookie(request)

    # Check if user owns the book
    from src.services.books import BookService

    book_service = BookService()
    book = await book_service.get_book_by_id(book_id, current_user.id)

    if not book:
        # If user doesn't own the book, check if they're an admin
        if current_user.is_admin:
            # Admin can view any book but in read-only mode
            from src.services.books import BookService

            book_service = BookService()
            # Get book without user restriction for admin
            book_in_db = await book_service.book_repo.get_by_id(book_id)
            if not book_in_db:
                raise HTTPException(status_code=404, detail="Book not found")

            return templates.TemplateResponse(
                "books/detail.html",
                {
                    "request": request,
                    "user": current_user,
                    "book_id": book_id,
                    "admin_view": True,
                    "read_only": True,
                },
            )
        else:
            # Regular user trying to access book they don't own
            raise HTTPException(status_code=404, detail="Book not found")

    return templates.TemplateResponse(
        "books/detail.html",
        {"request": request, "user": current_user, "book_id": book_id},
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


@router.get("/test-cookie", response_class=HTMLResponse, name="test_cookie")
async def test_cookie(request: Request):
    """Test cookie authentication page."""
    return templates.TemplateResponse("auth/test_cookie.html", {"request": request})


@router.get("/profile", response_class=HTMLResponse, name="profile")
@require_active_user
async def profile_page(request: Request):
    """Profile update page."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Profile page accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "auth/profile.html", {"request": request, "user": current_user}
    )


@router.get("/admin/quotes", response_class=HTMLResponse, name="admin_quotes")
@require_admin_user
async def admin_quotes_page(request: Request):
    """Admin quotes page - shows all quotes from all users."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Admin quotes page accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "quotes/list.html",
        {"request": request, "user": current_user, "admin_view": True},
    )


@router.get("/admin/books", response_class=HTMLResponse, name="admin_books")
@require_admin_user
async def admin_books_page(request: Request):
    """Admin books page - shows all books from all users."""
    current_user = await get_current_user_from_cookie(request)
    logger.info("Admin books page accessed by user: %s", current_user.username)
    return templates.TemplateResponse(
        "books/list.html",
        {"request": request, "user": current_user, "admin_view": True},
    )

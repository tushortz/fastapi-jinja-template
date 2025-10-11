"""Main FastAPI application."""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.api.admin import router as admin_router
from src.api.attendance import router as attendance_router
from src.api.auth import router as auth_router
from src.api.events import router as events_router
from src.api.image_converter import router as image_converter_router
from src.api.members import router as members_router
from src.config import setup_logging
from src.database import close_mongo_connection, connect_to_mongo
from src.web_routes import router as web_router

# Setup logging
logger = setup_logging()


def format_pydantic_errors(errors: list) -> list[dict]:
    """Format Pydantic validation errors to show only field name and message."""
    formatted_errors = []
    for error in errors:
        # Get the last element of the location (field name)
        field_name = error.get("loc", [])[-1] if error.get("loc") else "unknown"
        message = error.get("msg", "Validation error")

        formatted_errors.append({"field": field_name, "message": message})

    return formatted_errors


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Custom handler for Pydantic validation errors."""
    formatted_errors = format_pydantic_errors(exc.errors())
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": formatted_errors},
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting Project application")
    await connect_to_mongo()
    logger.info("Application startup completed")
    yield
    # Shutdown
    logger.info("Shutting down Project application")
    await close_mongo_connection()
    logger.info("Application shutdown completed")


app = FastAPI(
    title="Project API",
    description="A FastAPI application",
    version="1.0.0",
    lifespan=lifespan,
)

# Add custom exception handler for Pydantic validation errors
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
logger.info("Registering API routers")
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(image_converter_router)
app.include_router(members_router)
app.include_router(attendance_router)
app.include_router(events_router)
app.include_router(web_router)
logger.info("All routers registered successfully")

# Mount static files
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# Templates
templates = Jinja2Templates(directory="src/templates")


@app.get("/")
async def homepage():
    """Homepage endpoint."""
    return {"success": True}


@app.get("/api")
async def api_root():
    """API root endpoint."""
    return {"message": "Project API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

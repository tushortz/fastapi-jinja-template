"""Admin endpoints."""

import io
import json
import logging

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import JSONResponse, StreamingResponse

from src.auth import get_current_admin_user
from src.database import get_database
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


# Backup and Restore
@router.get("/backup", name="api_admin_backup")
async def backup_database(current_user: User = Depends(get_current_admin_user)):
    """Export all collections as a single JSON backup (admin only)."""
    db = await get_database()
    export_data: dict[str, list[dict]] = {}
    for name in await db.list_collection_names():
        collection = db.get_collection(name)
        docs = await collection.find({}).to_list(length=None)
        # stringify ObjectId and datetime; simple approach
        for d in docs:
            d["_id"] = str(d.get("_id"))
        export_data[name] = docs

    buf = io.BytesIO()
    buf.write(json.dumps(export_data, default=str, ensure_ascii=False, indent=2).encode("utf-8"))
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/json",
        headers={
            "Content-Disposition": 'attachment; filename="backup.json"'
        },
    )


@router.post("/restore", name="api_admin_restore")
async def restore_database(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
):
    """Upload a backup JSON and repopulate the database (admin only)."""
    try:
        content = await file.read()
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Invalid backup format")

        db = await get_database()
        # Replace collections atomically per collection
        for name, docs in data.items():
            if not isinstance(docs, list):
                continue
            collection = db.get_collection(name)
            # Clear existing data in this collection
            await collection.delete_many({})
            if docs:
                # Remove _id if it's not a valid ObjectId string to let Mongo assign
                sanitized = []
                for d in docs:
                    d = dict(d)
                    d.pop("_id", None)
                    sanitized.append(d)
                await collection.insert_many(sanitized)

        return JSONResponse({"message": "Restore completed successfully"})
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

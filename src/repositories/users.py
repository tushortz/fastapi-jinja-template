"""User repository."""

from typing import Any

from src.models.users import UserCreate, UserInDB

from .base import BaseRepository


class UserRepository(BaseRepository):
    """User repository for database operations."""

    def __init__(self):
        super().__init__(UserInDB, "users")

    async def get_by_email(self, email: str) -> UserInDB | None:
        """Get user by email."""
        collection = await self.get_collection()
        doc = await collection.find_one({"email": email})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return UserInDB(**doc)
        return None

    async def get_by_username(self, username: str) -> UserInDB | None:
        """Get user by username."""
        collection = await self.get_collection()
        doc = await collection.find_one({"username": username})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return UserInDB(**doc)
        return None

    async def create_user(
        self, user_create: UserCreate, hashed_password: str
    ) -> UserInDB:
        """Create a new user with hashed password."""
        collection = await self.get_collection()
        # Exclude password from user_dict to ensure it's never stored in plaintext
        user_dict = user_create.model_dump(exclude={"password"})
        user_dict["hashed_password"] = hashed_password
        result = await collection.insert_one(user_dict)
        return await self.get_by_id(str(result.inserted_id))

    async def is_email_taken(self, email: str) -> bool:
        """Check if email is already taken."""
        user = await self.get_by_email(email)
        return user is not None

    async def is_username_taken(self, username: str) -> bool:
        """Check if username is already taken."""
        user = await self.get_by_username(username)
        return user is not None

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[UserInDB]:
        """Get multiple users with pagination, search, and sorting."""
        collection = await self.get_collection()
        filter_dict = filter_dict or {}

        # Add search functionality if search term provided
        if search:
            # Search in username and email for users
            filter_dict["$or"] = [
                {"username": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
            ]

        # Determine sort direction
        sort_direction = 1 if sort_order == "asc" else -1

        cursor = (
            collection.find(filter_dict)
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        docs = await cursor.to_list(length=limit)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(self.model(**doc))
        return result

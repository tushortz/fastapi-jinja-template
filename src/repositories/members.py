"""Member repository."""

import logging
from datetime import date
from typing import Any

from src.models.members import MemberInDB, MemberRole, MemberStatus

from .base import BaseRepository

logger = logging.getLogger(__name__)


class MemberRepository(BaseRepository):
    """Member repository for database operations."""

    def __init__(self):
        super().__init__(MemberInDB, "members")

    async def get_by_email(self, email: str) -> MemberInDB | None:
        """Get member by email."""
        logger.debug("Getting member by email: %s", email)
        collection = await self.get_collection()
        doc = await collection.find_one({"email": email})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return MemberInDB(**doc)
        return None

    async def get_by_phone(self, phone: str) -> MemberInDB | None:
        """Get member by phone number."""
        logger.debug("Getting member by phone: %s", phone)
        collection = await self.get_collection()
        doc = await collection.find_one({"phone": phone})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return MemberInDB(**doc)
        return None

    async def get_by_name(
        self, first_name: str, last_name: str
    ) -> list[MemberInDB]:
        """Get members by first and last name."""
        logger.debug("Getting members by name: %s %s", first_name, last_name)
        collection = await self.get_collection()
        cursor = collection.find({
            "first_name": {"$regex": f"^{first_name}$", "$options": "i"},
            "last_name": {"$regex": f"^{last_name}$", "$options": "i"}
        })
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

    async def get_by_status(self, status: MemberStatus) -> list[MemberInDB]:
        """Get members by status."""
        logger.debug("Getting members by status: %s", status)
        collection = await self.get_collection()
        cursor = collection.find({"status": status})
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

    async def get_by_role(self, role: MemberRole) -> list[MemberInDB]:
        """Get members by role."""
        logger.debug("Getting members by role: %s", role)
        collection = await self.get_collection()
        cursor = collection.find({"role": role})
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

    async def get_birthdays_this_month(self) -> list[MemberInDB]:
        """Get members with birthdays this month."""
        logger.debug("Getting members with birthdays this month")
        collection = await self.get_collection()
        today = date.today()
        cursor = collection.find({
            "date_of_birth": {
                "$regex": f"^{today.year:04d}-{today.month:02d}-"
            }
        })
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

    async def get_birthdays_today(self) -> list[MemberInDB]:
        """Get members with birthdays today."""
        logger.debug("Getting members with birthdays today")
        collection = await self.get_collection()
        today = date.today()
        cursor = collection.find({
            "date_of_birth": {
                "$regex": f"^{today.year:04d}-{today.month:02d}-{today.day:02d}$"
            }
        })
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

    async def is_email_taken(self, email: str, exclude_id: str | None = None) -> bool:
        """Check if email is already taken."""
        logger.debug("Checking if email is taken: %s", email)
        collection = await self.get_collection()
        query = {"email": email}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        doc = await collection.find_one(query)
        return doc is not None

    async def is_phone_taken(self, phone: str, exclude_id: str | None = None) -> bool:
        """Check if phone number is already taken."""
        logger.debug("Checking if phone is taken: %s", phone)
        collection = await self.get_collection()
        query = {"phone": phone}
        if exclude_id:
            query["_id"] = {"$ne": exclude_id}
        doc = await collection.find_one(query)
        return doc is not None

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[MemberInDB]:
        """Get multiple members with pagination, search, and sorting."""
        logger.debug("Getting members with pagination: skip=%d, limit=%d", skip, limit)
        collection = await self.get_collection()
        filter_dict = filter_dict or {}

        # Add search functionality if search term provided
        if search:
            # Search in first_name, last_name, email, and phone
            filter_dict["$or"] = [
                {"first_name": {"$regex": search, "$options": "i"}},
                {"last_name": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
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

    async def get_active_members(
        self, skip: int = 0, limit: int = 100
    ) -> list[MemberInDB]:
        """
        Get active members only, excluding those with status 'relocated'.
        """
        logger.debug("Getting active members excluding status 'relocated'")
        return await self.get_many(
            skip=skip,
            limit=limit,
            filter_dict={
                "is_active": True,
                "status": {"$ne": MemberStatus.RELOCATED}
            }
        )

    async def count_by_status(self, status: MemberStatus) -> int:
        """Count members by status."""
        logger.debug("Counting members by status: %s", status)
        collection = await self.get_collection()
        return await collection.count_documents({"status": status})

    async def count_by_role(self, role: MemberRole) -> int:
        """Count members by role."""
        logger.debug("Counting members by role: %s", role)
        collection = await self.get_collection()
        return await collection.count_documents({"role": role})

    async def count_active_members(self) -> int:
        """Count active members."""
        logger.debug("Counting active members")
        collection = await self.get_collection()
        return await collection.count_documents({
            "is_active": True,
            "status": MemberStatus.MEMBER
        })

    async def get_members_by_age_range(
        self, min_age: int, max_age: int
    ) -> list[MemberInDB]:
        """Get members within a specific age range."""
        logger.debug("Getting members by age range: %d-%d", min_age, max_age)
        collection = await self.get_collection()

        # Calculate date range for the age range
        today = date.today()
        max_birth_date = date(today.year - min_age, today.month, today.day)
        min_birth_date = date(today.year - max_age, today.month, today.day)

        cursor = collection.find({
            "date_of_birth": {
                "$gte": min_birth_date.isoformat(),
                "$lte": max_birth_date.isoformat()
            }
        })
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(MemberInDB(**doc))
        return result

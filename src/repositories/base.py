"""Base repository class."""

from typing import Any, TypeVar

from bson import ObjectId
from pydantic import BaseModel

from src.database import get_database

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository:
    """Base repository for database operations."""

    def __init__(self, model: type[ModelType], collection_name: str):
        """Initialize repository with model and collection name."""
        self.model = model
        self.collection_name = collection_name

    async def get_collection(self):
        """Get database collection."""
        db = await get_database()
        return db[self.collection_name]

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create a new document."""
        collection = await self.get_collection()
        # Use JSON mode to serialize dates/times to strings for MongoDB
        obj_dict = obj_in.model_dump(mode="json")
        result = await collection.insert_one(obj_dict)
        return await self.get_by_id(str(result.inserted_id))

    async def get_by_id(self, id: str) -> ModelType | None:
        """Get document by ID."""
        collection = await self.get_collection()
        doc = await collection.find_one({"_id": ObjectId(id)})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return self.model(**doc)
        return None

    async def get_many(
        self,
        skip: int = 0,
        limit: int = 100,
        filter_dict: dict[str, Any] | None = None,
        search: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[ModelType]:
        """Get multiple documents with pagination, search, and sorting."""
        collection = await self.get_collection()
        filter_dict = filter_dict or {}

        # Add search functionality if search term provided
        if search:
            # This is a basic text search - can be enhanced with MongoDB text indexes
            # Modify according to the fields in the model
            filter_dict["$or"] = [
                {"field1": {"$regex": search, "$options": "i"}},
                {"field2": {"$regex": search, "$options": "i"}},
                {"field3": {"$regex": search, "$options": "i"}},
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

    async def update(self, id: str, obj_in: UpdateSchemaType) -> ModelType | None:
        """Update document by ID."""
        collection = await self.get_collection()
        # Serialize to JSON-safe values (e.g., dates) for MongoDB
        obj_dict = obj_in.model_dump(exclude_unset=True, mode="json")
        if not obj_dict:
            return await self.get_by_id(id)

        result = await collection.update_one({"_id": ObjectId(id)}, {"$set": obj_dict})
        if result.modified_count:
            return await self.get_by_id(id)
        return None

    async def delete(self, id: str) -> bool:
        """Delete document by ID."""
        collection = await self.get_collection()
        result = await collection.delete_one({"_id": ObjectId(id)})
        return result.deleted_count > 0

    async def count(self, filter_dict: dict[str, Any] | None = None) -> int:
        """Count documents matching filter."""
        collection = await self.get_collection()
        filter_dict = filter_dict or {}
        return await collection.count_documents(filter_dict)

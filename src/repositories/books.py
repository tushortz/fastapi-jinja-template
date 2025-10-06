"""Book repository."""


from bson import ObjectId

from src.models.books import BookInDB

from .base import BaseRepository


class BookRepository(BaseRepository):
    """Book repository for database operations."""

    def __init__(self):
        super().__init__(BookInDB, "books")

    async def get_by_title(self, title: str) -> BookInDB | None:
        """Get book by title."""
        collection = await self.get_collection()
        doc = await collection.find_one({"title": title})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return BookInDB(**doc)
        return None

    async def get_by_author(self, author: str) -> list[BookInDB]:
        """Get books by author."""
        return await self.get_many(filter_dict={"author": author})

    async def get_by_author_and_user(self, author: str, user_id: str) -> list[BookInDB]:
        """Get books by author for a specific user."""
        return await self.get_many(filter_dict={"author": author, "user_id": user_id})

    async def search_books(self, query: str) -> list[BookInDB]:
        """Search books by title or author."""
        filter_dict = {
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
            ]
        }
        return await self.get_many(filter_dict=filter_dict)

    async def get_by_ids(self, book_ids: list[str]) -> list[BookInDB]:
        """Get books by list of IDs."""
        collection = await self.get_collection()
        filter_dict = {"_id": {"$in": [ObjectId(book_id) for book_id in book_ids]}}
        cursor = collection.find(filter_dict)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(self.model(**doc))
        return result

    async def get_by_isbn(self, isbn: str) -> BookInDB | None:
        """Get book by ISBN."""
        collection = await self.get_collection()
        doc = await collection.find_one({"isbn": isbn})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return BookInDB(**doc)
        return None

    async def get_by_id_and_user(self, book_id: str, user_id: str) -> BookInDB | None:
        """Get book by ID and user."""
        collection = await self.get_collection()
        doc = await collection.find_one({"_id": ObjectId(book_id), "user_id": user_id})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return BookInDB(**doc)
        return None

    async def get_books_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        sort_by: str = "title",
        sort_order: str = "asc",
    ) -> list[BookInDB]:
        """Get user's books with pagination, search, and sorting."""
        filter_dict = {"user_id": user_id}

        # Add search functionality if search term provided
        if search:
            filter_dict["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"author": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}},
            ]

        return await self.get_many(
            skip=skip,
            limit=limit,
            filter_dict=filter_dict,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def get_by_ids_and_user(
        self, book_ids: list[str], user_id: str
    ) -> list[BookInDB]:
        """Get books by list of IDs for a specific user."""
        collection = await self.get_collection()
        filter_dict = {
            "_id": {"$in": [ObjectId(book_id) for book_id in book_ids]},
            "user_id": user_id,
        }
        cursor = collection.find(filter_dict)
        docs = await cursor.to_list(length=None)
        result = []
        for doc in docs:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            result.append(self.model(**doc))
        return result

    async def search_books_by_user(self, query: str, user_id: str) -> list[BookInDB]:
        """Search books by title or author for a specific user."""
        filter_dict = {
            "user_id": user_id,
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"author": {"$regex": query, "$options": "i"}},
            ],
        }
        return await self.get_many(filter_dict=filter_dict)

    async def get_by_isbn_and_user(self, isbn: str, user_id: str) -> BookInDB | None:
        """Get book by ISBN for a specific user."""
        collection = await self.get_collection()
        doc = await collection.find_one({"isbn": isbn, "user_id": user_id})
        if doc:
            doc["id"] = str(doc["_id"])
            del doc["_id"]
            return BookInDB(**doc)
        return None

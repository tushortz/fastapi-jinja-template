"""Quote repository."""


from src.models.quotes import QuoteInDB

from .base import BaseRepository


class QuoteRepository(BaseRepository):
    """Quote repository for database operations."""

    def __init__(self):
        super().__init__(QuoteInDB, "quotes")

    async def get_by_user(self, user_id: str) -> list[QuoteInDB]:
        """Get quotes by user ID."""
        return await self.get_many(filter_dict={"user_id": user_id})

    async def get_by_book(self, book_id: str) -> list[QuoteInDB]:
        """Get quotes by book ID."""
        return await self.get_many(filter_dict={"book_id": book_id})

    async def get_by_user_and_book(self, user_id: str, book_id: str) -> list[QuoteInDB]:
        """Get quotes by user and book ID."""
        return await self.get_many(filter_dict={"user_id": user_id, "book_id": book_id})

    async def search_quotes(self, user_id: str, query: str) -> list[QuoteInDB]:
        """Search quotes by text content for a specific user."""
        filter_dict = {"user_id": user_id, "text": {"$regex": query, "$options": "i"}}
        return await self.get_many(filter_dict=filter_dict)

    async def get_quotes_with_pagination(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        search: str = None,
        book_id: str = None,
        tags: list[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> list[QuoteInDB]:
        """Get user quotes with pagination, search, and filtering."""
        filter_dict = {"user_id": user_id}

        if book_id:
            filter_dict["book_id"] = book_id

        # Handle tag filtering
        if tags:
            filter_dict["tags"] = {"$in": tags}

        # Handle search for quotes
        if search:
            # For quotes, search in text, notes, and chapter only
            search_conditions = [
                {"text": {"$regex": search, "$options": "i"}},
                {"notes": {"$regex": search, "$options": "i"}},
                {"chapter": {"$regex": search, "$options": "i"}},
            ]

            filter_dict["$or"] = search_conditions

        return await self.get_many(
            skip=skip,
            limit=limit,
            filter_dict=filter_dict,
            sort_by=sort_by,
            sort_order=sort_order,
        )

    async def count_user_quotes(
        self,
        user_id: str,
        search: str = None,
        book_id: str = None,
        tags: list[str] = None,
    ) -> int:
        """Count user quotes with filtering."""
        filter_dict = {"user_id": user_id}

        if book_id:
            filter_dict["book_id"] = book_id

        # Handle tag filtering
        if tags:
            filter_dict["tags"] = {"$in": tags}

        # Handle search for quotes
        if search:
            # For quotes, search in text, notes, and chapter only
            search_conditions = [
                {"text": {"$regex": search, "$options": "i"}},
                {"notes": {"$regex": search, "$options": "i"}},
                {"chapter": {"$regex": search, "$options": "i"}},
            ]

            filter_dict["$or"] = search_conditions

        return await self.count(filter_dict)

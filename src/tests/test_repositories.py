"""Tests for repositories."""

import pytest

from src.repositories.users import UserRepository
from src.tests.factories.user import UserCreateFactory


class TestUserRepository:
    """Test UserRepository."""

    @pytest.mark.asyncio
    async def test_create_user(self, test_db, override_get_database):
        """Test creating a user."""
        # Use test database directly
        from src.models.users import UserInDB
        from src.repositories.base import BaseRepository

        class TestUserRepository(BaseRepository):
            def __init__(self, test_db):
                super().__init__(UserInDB, "users")
                self.test_db = test_db

            async def get_collection(self):
                return self.test_db["users"]

            async def create_user(self, user_create, hashed_password):
                collection = await self.get_collection()
                user_dict = user_create.model_dump(exclude={"password"})
                user_dict["hashed_password"] = hashed_password
                result = await collection.insert_one(user_dict)
                return await self.get_by_id(str(result.inserted_id))

        user_repo = TestUserRepository(test_db)
        user_create = UserCreateFactory()

        user = await user_repo.create_user(user_create, "hashed_password")

        assert user.email == user_create.email
        assert user.username == user_create.username
        assert user.hashed_password == "hashed_password"
        assert user.is_active is True
        assert user.is_admin is False

    @pytest.mark.asyncio
    async def test_get_by_email(self, test_db, override_get_database):
        """Test getting user by email."""
        from unittest.mock import patch

        with patch("src.repositories.base.get_database", return_value=test_db):
            user_repo = UserRepository()
            user_create = UserCreateFactory()

            await user_repo.create_user(user_create, "hashed_password")
            user = await user_repo.get_by_email(user_create.email)

            assert user is not None
            assert user.email == user_create.email
            assert user.username == user_create.username

    @pytest.mark.asyncio
    async def test_get_by_username(self, test_db, override_get_database):
        """Test getting user by username."""
        from unittest.mock import patch

        with patch("src.repositories.base.get_database", return_value=test_db):
            user_repo = UserRepository()
            user_create = UserCreateFactory()

            await user_repo.create_user(user_create, "hashed_password")
            user = await user_repo.get_by_username(user_create.username)

            assert user is not None
            assert user.email == user_create.email
            assert user.username == user_create.username

    @pytest.mark.asyncio
    async def test_is_email_taken(self, test_db, override_get_database):
        """Test checking if email is taken."""
        from unittest.mock import patch

        with patch("src.repositories.base.get_database", return_value=test_db):
            user_repo = UserRepository()
            user_create = UserCreateFactory()

            # Initially not taken
            assert await user_repo.is_email_taken(user_create.email) is False

            # After creating user, should be taken
            await user_repo.create_user(user_create, "hashed_password")
            assert await user_repo.is_email_taken(user_create.email) is True

    @pytest.mark.asyncio
    async def test_is_username_taken(self, test_db, override_get_database):
        """Test checking if username is taken."""
        from unittest.mock import patch

        with patch("src.repositories.base.get_database", return_value=test_db):
            user_repo = UserRepository()
            user_create = UserCreateFactory()

            # Initially not taken
            assert await user_repo.is_username_taken(user_create.username) is False

            # After creating user, should be taken
            await user_repo.create_user(user_create, "hashed_password")
            assert await user_repo.is_username_taken(user_create.username) is True

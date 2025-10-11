"""Tests for services."""

from unittest.mock import AsyncMock, patch

import pytest

from src.services.users import UserService
from src.tests.factories.user import UserCreateFactory


class TestUserService:
    """Test UserService."""

    @pytest.mark.asyncio
    async def test_verify_password(self):
        """Test password verification."""
        user_service = UserService()
        password = "testpassword123"
        hashed = user_service.get_password_hash(password)

        assert user_service.verify_password(password, hashed) is True
        assert user_service.verify_password("wrongpassword", hashed) is False

    @pytest.mark.asyncio
    async def test_get_password_hash(self):
        """Test password hashing."""
        user_service = UserService()
        password = "testpassword123"
        hashed = user_service.get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation."""
        user_service = UserService()
        user_create = UserCreateFactory()

        # Mock repository methods
        with (
            patch.object(user_service.user_repo, "is_email_taken", return_value=False),
            patch.object(
                user_service.user_repo, "is_username_taken", return_value=False
            ),
            patch.object(
                user_service.user_repo,
                "create_user",
                return_value=AsyncMock(
                    id="user_id",
                    email=user_create.email,
                    username=user_create.username,
                    is_active=True,
                    is_admin=False,
                ),
            ),
        ):
            user = await user_service.create_user(user_create)

            assert user.email == user_create.email
            assert user.username == user_create.username
            assert user.is_active is True
            assert user.is_admin is False

    @pytest.mark.asyncio
    async def test_create_user_email_taken(self):
        """Test user creation with taken email."""
        user_service = UserService()
        user_create = UserCreateFactory()

        with patch.object(user_service.user_repo, "is_email_taken", return_value=True):
            with pytest.raises(ValueError, match="Email already registered"):
                await user_service.create_user(user_create)

    @pytest.mark.asyncio
    async def test_create_user_username_taken(self):
        """Test user creation with taken username."""
        user_service = UserService()
        user_create = UserCreateFactory()

        with (
            patch.object(user_service.user_repo, "is_email_taken", return_value=False),
            patch.object(
                user_service.user_repo, "is_username_taken", return_value=True
            ),
        ):
            with pytest.raises(ValueError, match="Username already taken"):
                await user_service.create_user(user_create)

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        user_service = UserService()
        user_create = UserCreateFactory()

        mock_user = AsyncMock()
        mock_user.hashed_password = user_service.get_password_hash(user_create.password)

        with patch.object(
            user_service.user_repo, "get_by_email", return_value=mock_user
        ):
            user = await user_service.authenticate_user(
                user_create.email, user_create.password
            )

            assert user == mock_user

    @pytest.mark.asyncio
    async def test_authenticate_user_wrong_password(self):
        """Test user authentication with wrong password."""
        user_service = UserService()
        user_create = UserCreateFactory()

        mock_user = AsyncMock()
        mock_user.hashed_password = user_service.get_password_hash(user_create.password)

        with patch.object(
            user_service.user_repo, "get_by_email", return_value=mock_user
        ):
            user = await user_service.authenticate_user(
                user_create.email, "wrongpassword"
            )

            assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Test user authentication with non-existent user."""
        user_service = UserService()
        user_create = UserCreateFactory()

        with patch.object(user_service.user_repo, "get_by_email", return_value=None):
            user = await user_service.authenticate_user(
                user_create.email, user_create.password
            )

            assert user is None

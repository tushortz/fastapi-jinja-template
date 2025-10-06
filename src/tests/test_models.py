"""Tests for models."""

from src.models.users import UserUpdate
from src.tests.factories.user import UserCreateFactory, UserFactory, UserInDBFactory


class TestUserModels:
    """Test user models."""

    def test_user_create(self):
        """Test UserCreate model."""
        user = UserCreateFactory()
        assert user.email is not None
        assert user.username is not None
        assert user.password is not None
        assert user.is_active is True
        assert user.is_admin is False

    def test_user_update(self):
        """Test UserUpdate model."""
        user_create = UserCreateFactory()
        user_data = {"email": user_create.email, "username": user_create.username}
        user = UserUpdate(**user_data)
        assert user.email == user_create.email
        assert user.username == user_create.username
        assert user.is_active is None
        assert user.is_admin is None

    def test_user_in_db(self):
        """Test UserInDB model."""
        user = UserInDBFactory()
        assert user.id is not None
        assert user.email is not None
        assert user.username is not None
        assert user.hashed_password is not None
        assert user.is_active is True
        assert user.is_admin is False

    def test_user_response(self):
        """Test User response model."""
        user = UserFactory()
        assert user.id is not None
        assert user.email is not None
        assert user.username is not None
        assert user.is_active is True
        assert user.is_admin is False

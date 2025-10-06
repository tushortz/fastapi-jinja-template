"""Tests for models."""

from src.models.books import Book, BookCreate, BookUpdate
from src.models.quotes import Quote, QuoteCreate, QuoteUpdate
from src.models.users import User, UserCreate, UserInDB, UserUpdate


class TestUserModels:
    """Test user models."""

    def test_user_create(self):
        """Test UserCreate model."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }
        user = UserCreate(**user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.password == "password123"
        assert user.is_active is True
        assert user.is_admin is False

    def test_user_update(self):
        """Test UserUpdate model."""
        user_data = {"email": "new@example.com", "username": "newuser"}
        user = UserUpdate(**user_data)
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.is_active is None
        assert user.is_admin is None

    def test_user_in_db(self):
        """Test UserInDB model."""
        user_data = {
            "id": "user_id",
            "email": "test@example.com",
            "username": "testuser",
            "hashed_password": "hashed_password",
            "is_active": True,
            "is_admin": False,
        }
        user = UserInDB(**user_data)
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.hashed_password == "hashed_password"

    def test_user_response(self):
        """Test User response model."""
        user_data = {
            "id": "user_id",
            "email": "test@example.com",
            "username": "testuser",
            "is_active": True,
            "is_admin": False,
        }
        user = User(**user_data)
        assert user.id == "user_id"
        assert user.email == "test@example.com"
        assert user.username == "testuser"

"""Tests for API endpoints."""

from unittest.mock import AsyncMock

from src.tests.factories.user import UserCreateFactory, UserFactory


class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_register_success(self, client, override_get_database):
        """Test successful user registration."""
        from src.api.auth import UserService
        from src.main import app

        # Use factory to create test data
        user_create = UserCreateFactory()
        user_data = {
            "email": user_create.email,
            "username": user_create.username,
            "password": user_create.password,
        }

        # Create a mock service
        mock_service = AsyncMock()
        # Create mock user with same data as user_create
        mock_user = UserFactory(email=user_create.email, username=user_create.username)
        mock_service.create_user.return_value = mock_user

        # Override the dependency
        app.dependency_overrides[UserService] = lambda: mock_service

        try:
            response = client.post("/auth/register", json=user_data)

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == user_create.email
            assert data["username"] == user_create.username
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_register_email_taken(self, client, override_get_database):
        """Test registration with taken email."""
        from src.api.auth import UserService
        from src.main import app

        # Use factory to create test data
        user_create = UserCreateFactory()
        user_data = {
            "email": user_create.email,
            "username": user_create.username,
            "password": user_create.password,
        }

        # Create a mock service
        mock_service = AsyncMock()
        mock_service.create_user.side_effect = ValueError("Email already registered")

        # Override the dependency
        app.dependency_overrides[UserService] = lambda: mock_service

        try:
            response = client.post("/auth/register", json=user_data)

            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_login_success(self, client, override_get_database):
        """Test successful login."""
        from src.api.auth import UserService
        from src.main import app

        # Use factory to create test data
        user_create = UserCreateFactory()
        login_data = {"username": user_create.email, "password": user_create.password}

        # Create a mock service
        mock_service = AsyncMock()
        # Create mock user with same data as user_create
        mock_user = UserFactory(email=user_create.email, username=user_create.username)
        mock_service.authenticate_user.return_value = mock_user

        # Override the dependency
        app.dependency_overrides[UserService] = lambda: mock_service

        try:
            response = client.post("/auth/login", data=login_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == mock_user.email
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

    def test_login_invalid_credentials(self, client, override_get_database):
        """Test login with invalid credentials."""
        from src.api.auth import UserService
        from src.main import app

        # Use factory to create test data
        user_create = UserCreateFactory()
        login_data = {"username": user_create.email, "password": "wrongpassword"}

        # Create a mock service
        mock_service = AsyncMock()
        mock_service.authenticate_user.return_value = None

        # Override the dependency
        app.dependency_overrides[UserService] = lambda: mock_service

        try:
            response = client.post("/auth/login", data=login_data)

            assert response.status_code == 401
            assert "Incorrect email or password" in response.json()["detail"]
        finally:
            # Clean up the override
            app.dependency_overrides.clear()

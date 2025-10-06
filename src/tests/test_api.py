"""Tests for API endpoints."""

from unittest.mock import AsyncMock, patch


class TestAuthAPI:
    """Test authentication API endpoints."""

    def test_register_success(self, client):
        """Test successful user registration."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }

        with patch("src.api.auth.UserService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_user.return_value = AsyncMock(
                id="user_id",
                email="test@example.com",
                username="testuser",
                is_active=True,
                is_admin=False,
            )
            mock_service.return_value = mock_instance

            response = client.post("/auth/register", json=user_data)

            assert response.status_code == 200
            data = response.json()
            assert data["email"] == "test@example.com"
            assert data["username"] == "testuser"

    def test_register_email_taken(self, client):
        """Test registration with taken email."""
        user_data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }

        with patch("src.api.auth.UserService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.create_user.side_effect = ValueError(
                "Email already registered"
            )
            mock_service.return_value = mock_instance

            response = client.post("/auth/register", json=user_data)

            assert response.status_code == 400
            assert "Email already registered" in response.json()["detail"]

    def test_login_success(self, client):
        """Test successful login."""
        login_data = {"username": "test@example.com", "password": "password123"}

        with patch("src.api.auth.UserService") as mock_service:
            mock_instance = AsyncMock()
            mock_user = AsyncMock()
            mock_user.id = "user_id"
            mock_user.email = "test@example.com"
            mock_user.username = "testuser"
            mock_user.is_active = True
            mock_user.is_admin = False
            mock_instance.authenticate_user.return_value = mock_user
            mock_service.return_value = mock_instance

            response = client.post("/auth/login", data=login_data)

            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "test@example.com"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials."""
        login_data = {"username": "test@example.com", "password": "wrongpassword"}

        with patch("src.api.auth.UserService") as mock_service:
            mock_instance = AsyncMock()
            mock_instance.authenticate_user.return_value = None
            mock_service.return_value = mock_instance

            response = client.post("/auth/login", data=login_data)

            assert response.status_code == 401
            assert "Incorrect email or password" in response.json()["detail"]

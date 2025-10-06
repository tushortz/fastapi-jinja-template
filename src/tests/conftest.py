"""Test configuration and fixtures."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient

from src.config import settings
from src.database import get_database
from src.main import app
from src.tests.factories.user import UserFactory


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


@pytest.fixture
async def test_db():
    """Test database fixture."""
    # Use a test database
    test_client = AsyncIOMotorClient(settings.mongodb_url)
    test_db = test_client[settings.test_database_name]

    yield test_db

    # Cleanup after test
    await test_client.drop_database(settings.test_database_name)
    test_client.close()


@pytest.fixture
def override_get_database(test_db) -> Generator[None, Any, None]:
    """Override database dependency for testing."""

    async def _override_get_database():
        return test_db

    app.dependency_overrides[get_database] = _override_get_database
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def sample_user_data() -> UserFactory:
    """Sample User instance for testing."""

    return UserFactory()

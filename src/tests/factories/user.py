"""User factories for testing."""

import factory
from faker import Faker

from src.models.users import User, UserCreate, UserInDB
from src.tests.factories.base import TimestampModelFactory

fake = Faker()


class UserFactory(TimestampModelFactory):
    """Factory for User model."""

    class Meta:
        """Factory configuration."""

        model = User

    id = factory.LazyFunction(fake.uuid4)
    email = factory.LazyFunction(fake.email)
    username = factory.LazyFunction(fake.user_name)
    is_active = True
    is_admin = False


class UserCreateFactory(factory.Factory):
    """Factory for UserCreate model."""

    class Meta:
        """Factory configuration."""

        model = UserCreate

    email = factory.LazyFunction(fake.email)
    username = factory.LazyFunction(fake.user_name)
    password = factory.LazyFunction(lambda: fake.password(length=12))
    is_active = True
    is_admin = False


class UserInDBFactory(TimestampModelFactory):
    """Factory for UserInDB model."""

    class Meta:
        """Factory configuration."""

        model = UserInDB

    id = factory.LazyFunction(fake.uuid4)
    email = factory.LazyFunction(fake.email)
    username = factory.LazyFunction(fake.user_name)
    hashed_password = factory.LazyFunction(lambda: fake.password(length=60))
    is_active = True
    is_admin = False

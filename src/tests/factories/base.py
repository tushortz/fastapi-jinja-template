"""Base factories for testing."""


import factory
from faker import Faker

from src.models.base import TimestampModel

fake = Faker()


class TimestampModelFactory(factory.Factory):
    """Factory for TimestampModel."""

    class Meta:
        """Factory configuration."""

        model = TimestampModel

    created_at = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="-1y", end_date="now")
    )
    updated_at = factory.LazyFunction(
        lambda: fake.date_time_between(start_date="-1y", end_date="now")
    )

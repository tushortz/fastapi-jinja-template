from datetime import UTC, datetime


def get_current_date() -> datetime:
    """Get the current date in UTC."""
    return datetime.now(tz=UTC)

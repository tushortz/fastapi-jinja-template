"""User model."""


from pydantic import EmailStr, Field

from .base import TimestampModel


class UserBase(TimestampModel):
    """Base user model."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    is_active: bool = True
    is_admin: bool = False


class UserCreate(UserBase):
    """User creation model."""

    password: str = Field(..., min_length=8)


class UserUpdate(TimestampModel):
    """User update model."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    is_active: bool | None = None
    is_admin: bool | None = None


class UserProfileUpdate(TimestampModel):
    """User profile update model for self-updates."""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    current_password: str | None = None
    new_password: str | None = Field(None, min_length=8)


class UserInDB(UserBase):
    """User model for database storage."""

    id: str
    hashed_password: str


class User(UserBase):
    """User model for API responses."""

    id: str

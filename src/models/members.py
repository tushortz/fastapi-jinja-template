"""Church member models."""

from datetime import date
from enum import Enum

from pydantic import EmailStr, Field, field_validator

from .base import TimestampModel


class MemberStatus(str, Enum):
    """Member status enumeration."""

    OUTREACH = "outreach"
    FIRST_TIMER = "first timer"
    MEMBER = "member"
    SHEPHERD = "shepherd"
    VISITOR = "visitor"
    RELOCATED = "relocated"


class MemberRole(str, Enum):
    """Member role enumeration."""

    PASTOR = "pastor"
    ELDER = "elder"
    DEACON = "deacon"
    MEMBER = "member"
    YOUTH_LEADER = "youth leader"
    CHILDREN_LEADER = "children leader"
    WORSHIP_LEADER = "worship leader"
    USHER = "usher"
    CHOIR_MEMBER = "choir member"
    VOLUNTEER = "volunteer"

class Ministry(str, Enum):
    """Ministry enumeration."""

    AIRPORT_STARS = "airport stars"
    CHOIR = "choir"
    DANCING_STARS = "dancing stars"
    FILM_STARS = "film stars"
    FLAMES = "flames"
    PRAISE_AND_WORSIP = "praise and worship"
    USHERS = "ushers"


class Gender(str, Enum):
    """Gender enumeration."""

    MALE = "male"
    FEMALE = "female"


class MaritalStatus(str, Enum):
    """Marital status enumeration."""

    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"
    SEPARATED = "separated"


class MemberNote(TimestampModel):
    """Member note model."""

    note: str = Field(..., max_length=1000)


class MemberBase(TimestampModel):
    """Base member model."""

    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str | None = Field(None, max_length=50)
    email: EmailStr | None = None
    phone: str = Field(..., max_length=20)
    date_of_birth: date | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    zip_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = Field(None, max_length=20)
    emergency_contact_relationship: str | None = Field(None, max_length=50)
    occupation: str | None = Field(None, max_length=100)
    employer: str | None = Field(None, max_length=100)
    education_level: str | None = Field(None, max_length=100)
    baptism_date: date | None = None
    ministry: Ministry | None = None
    membership_date: date | None = None
    status: MemberStatus | None = MemberStatus.MEMBER
    role: MemberRole | None = MemberRole.MEMBER
    notes: list[MemberNote] = Field(default_factory=list, max_length=1000)
    is_active: bool = True
    first_attended: date | None = None


    @field_validator("phone", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format."""
        if v is None:
            return v
        # Remove all non-digit characters
        digits_only = "".join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        return v

    @field_validator("date_of_birth", "baptism_date", "membership_date")
    @classmethod
    def validate_date_not_future(cls, v: date | None) -> date | None:
        """Validate that dates are not in the future."""
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Date cannot be in the future")
        return v

    @field_validator("role", mode="before")
    @classmethod
    def coerce_role_default(cls, v):
        """Coerce empty or null role to default member role."""
        if v is None:
            return MemberRole.MEMBER
        if isinstance(v, str) and not v.strip():
            return MemberRole.MEMBER
        return v

    @field_validator("notes", mode="before")
    @classmethod
    def coerce_notes_default(cls, v):
        """Ensure notes is a list even when null in stored data."""
        return v if v is not None else []


class MemberCreate(MemberBase):
    """Member creation model."""
    pass


class MemberUpdate(TimestampModel):
    """Member update model."""

    first_name: str | None = Field(None, min_length=1, max_length=50)
    last_name: str | None = Field(None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(None, max_length=20)
    date_of_birth: date | None = None
    gender: Gender | None = None
    marital_status: MaritalStatus | None = None
    address: str | None = Field(None, max_length=500)
    city: str | None = Field(None, max_length=100)
    state: str | None = Field(None, max_length=100)
    zip_code: str | None = Field(None, max_length=20)
    country: str | None = Field(None, max_length=100)
    emergency_contact_name: str | None = Field(None, max_length=100)
    emergency_contact_phone: str | None = Field(None, max_length=20)
    emergency_contact_relationship: str | None = Field(None, max_length=50)
    occupation: str | None = Field(None, max_length=100)
    employer: str | None = Field(None, max_length=100)
    education_level: str | None = Field(None, max_length=100)
    baptism_date: date | None = None
    membership_date: date | None = None
    status: MemberStatus | None = None
    role: MemberRole | None = None
    notes: list[MemberNote] | None = Field(None, max_length=1000)
    is_active: bool | None = None
    first_attended: date | None = None

    @field_validator("phone", "emergency_contact_phone")
    @classmethod
    def validate_phone(cls, v: str | None) -> str | None:
        """Validate phone number format."""
        if v is None:
            return v
        # Remove all non-digit characters
        digits_only = "".join(filter(str.isdigit, v))
        if len(digits_only) < 10:
            raise ValueError("Phone number must contain at least 10 digits")
        return v

    @field_validator("date_of_birth", "baptism_date", "membership_date")
    @classmethod
    def validate_date_not_future(cls, v: date | None) -> date | None:
        """Validate that dates are not in the future."""
        if v is None:
            return v
        if v > date.today():
            raise ValueError("Date cannot be in the future")
        return v


class MemberInDB(MemberBase):
    """Member model for database storage."""

    id: str


class Member(MemberBase):
    """Member model for API responses."""

    id: str

    @property
    def full_name(self) -> str:
        """Get full name of the member."""
        if self.last_name and self.last_name.strip():
            return f"{self.first_name} {self.last_name}".strip()
        return self.first_name

    @property
    def age(self) -> int | None:
        """Calculate age from date of birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def is_birthday_today(self) -> bool:
        """Check if today is the member's birthday."""
        if not self.date_of_birth:
            return False
        today = date.today()
        return (
            self.date_of_birth.month == today.month
            and self.date_of_birth.day == today.day
        )

    @property
    def is_birthday_this_month(self) -> bool:
        """Check if the member's birthday is this month."""
        if not self.date_of_birth:
            return False
        today = date.today()
        return self.date_of_birth.month == today.month

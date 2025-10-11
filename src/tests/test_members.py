"""Tests for member functionality."""

from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.models.members import (
    Gender, MaritalStatus, Member, MemberCreate, MemberRole, MemberStatus,
)
from src.repositories.members import MemberRepository
from src.services.members import MemberService


class TestMemberModel:
    """Test member model functionality."""

    def test_member_full_name(self):
        """Test member full name property."""
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            middle_name="Michael",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert member.full_name == "John Michael Doe"

    def test_member_full_name_no_middle(self):
        """Test member full name without middle name."""
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert member.full_name == "John Doe"

    def test_member_age_calculation(self):
        """Test member age calculation."""
        birth_date = date(1990, 1, 1)
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            date_of_birth=birth_date,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        # Age calculation depends on current date, so we just check it's not None
        assert member.age is not None
        assert isinstance(member.age, int)

    def test_member_age_no_birth_date(self):
        """Test member age when no birth date."""
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert member.age is None

    def test_member_birthday_today(self):
        """Test member birthday today check."""
        today = date.today()
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            date_of_birth=today,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert member.is_birthday_today is True

    def test_member_birthday_this_month(self):
        """Test member birthday this month check."""
        today = date.today()
        member = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            date_of_birth=date(today.year, today.month, 15),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert member.is_birthday_this_month is True


class TestMemberCreate:
    """Test member creation model."""

    def test_member_create_valid(self):
        """Test valid member creation."""
        member_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "1234567890",
            "date_of_birth": date(1990, 1, 1),
            "gender": Gender.MALE,
            "marital_status": MaritalStatus.SINGLE,
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.MEMBER,
        }
        member_create = MemberCreate(**member_data)
        assert member_create.first_name == "John"
        assert member_create.last_name == "Doe"
        assert member_create.email == "john@example.com"

    def test_member_create_phone_validation(self):
        """Test phone number validation."""
        with pytest.raises(ValueError, match="Phone number must contain at least 10 digits"):
            MemberCreate(
                first_name="John",
                last_name="Doe",
                phone="123",  # Too short
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    def test_member_create_future_date_validation(self):
        """Test future date validation."""
        future_date = date.today().replace(year=date.today().year + 1)
        with pytest.raises(ValueError, match="Date cannot be in the future"):
            MemberCreate(
                first_name="John",
                last_name="Doe",
                date_of_birth=future_date,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )


class TestMemberRepository:
    """Test member repository functionality."""

    @pytest.fixture
    def mock_collection(self):
        """Mock MongoDB collection."""
        return AsyncMock()

    @pytest.fixture
    def member_repo(self, mock_collection):
        """Create member repository with mocked collection."""
        repo = MemberRepository()
        with patch.object(repo, 'get_collection', return_value=mock_collection):
            yield repo

    @pytest.mark.asyncio
    async def test_get_by_email(self, member_repo, mock_collection):
        """Test getting member by email."""
        # Mock database response
        mock_doc = {
            "_id": "507f1f77bcf86cd799439011",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        mock_collection.find_one.return_value = mock_doc

        result = await member_repo.get_by_email("john@example.com")

        assert result is not None
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john@example.com"
        mock_collection.find_one.assert_called_once_with({"email": "john@example.com"})

    @pytest.mark.asyncio
    async def test_get_by_email_not_found(self, member_repo, mock_collection):
        """Test getting member by email when not found."""
        mock_collection.find_one.return_value = None

        result = await member_repo.get_by_email("nonexistent@example.com")

        assert result is None
        mock_collection.find_one.assert_called_once_with({"email": "nonexistent@example.com"})

    @pytest.mark.asyncio
    async def test_is_email_taken(self, member_repo, mock_collection):
        """Test checking if email is taken."""
        mock_collection.find_one.return_value = {"_id": "507f1f77bcf86cd799439011"}

        result = await member_repo.is_email_taken("john@example.com")

        assert result is True
        mock_collection.find_one.assert_called_once_with({"email": "john@example.com"})

    @pytest.mark.asyncio
    async def test_is_email_not_taken(self, member_repo, mock_collection):
        """Test checking if email is not taken."""
        mock_collection.find_one.return_value = None

        result = await member_repo.is_email_taken("john@example.com")

        assert result is False
        mock_collection.find_one.assert_called_once_with({"email": "john@example.com"})

    @pytest.mark.asyncio
    async def test_get_birthdays_today(self, member_repo, mock_collection):
        """Test getting members with birthdays today."""
        today = date.today()
        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": today.isoformat(),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value.to_list.return_value = mock_docs

        result = await member_repo.get_birthdays_today()

        assert len(result) == 1
        assert result[0].first_name == "John"
        assert result[0].last_name == "Doe"


class TestMemberService:
    """Test member service functionality."""

    @pytest.fixture
    def mock_member_repo(self):
        """Mock member repository."""
        return AsyncMock(spec=MemberRepository)

    @pytest.fixture
    def member_service(self, mock_member_repo):
        """Create member service with mocked repository."""
        service = MemberService()
        service.member_repo = mock_member_repo
        return service

    @pytest.mark.asyncio
    async def test_create_member_success(self, member_service, mock_member_repo):
        """Test successful member creation."""
        # Mock repository responses
        mock_member_repo.is_email_taken.return_value = False
        mock_member_repo.is_phone_taken.return_value = False

        mock_member_in_db = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_member_repo.create.return_value = mock_member_in_db

        member_create = MemberCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = await member_service.create_member(member_create)

        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.email == "john@example.com"
        mock_member_repo.is_email_taken.assert_called_once_with("john@example.com")
        mock_member_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_member_email_taken(self, member_service, mock_member_repo):
        """Test member creation with taken email."""
        mock_member_repo.is_email_taken.return_value = True

        member_create = MemberCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        with pytest.raises(ValueError, match="Email already registered"):
            await member_service.create_member(member_create)

        mock_member_repo.is_email_taken.assert_called_once_with("john@example.com")
        mock_member_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_member_phone_taken(self, member_service, mock_member_repo):
        """Test member creation with taken phone."""
        mock_member_repo.is_email_taken.return_value = False
        mock_member_repo.is_phone_taken.return_value = True

        member_create = MemberCreate(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
            phone="1234567890",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        with pytest.raises(ValueError, match="Phone number already registered"):
            await member_service.create_member(member_create)

        mock_member_repo.is_email_taken.assert_called_once_with("john@example.com")
        mock_member_repo.is_phone_taken.assert_called_once_with("1234567890")
        mock_member_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_member_by_id_success(self, member_service, mock_member_repo):
        """Test getting member by ID successfully."""
        mock_member_in_db = Member(
            id="1",
            first_name="John",
            last_name="Doe",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_member_repo.get_by_id.return_value = mock_member_in_db

        result = await member_service.get_member_by_id("1")

        assert result is not None
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        mock_member_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_get_member_by_id_not_found(self, member_service, mock_member_repo):
        """Test getting member by ID when not found."""
        mock_member_repo.get_by_id.return_value = None

        result = await member_service.get_member_by_id("1")

        assert result is None
        mock_member_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_count_members(self, member_service, mock_member_repo):
        """Test counting members."""
        mock_member_repo.count.return_value = 10

        result = await member_service.count_members()

        assert result == 10
        mock_member_repo.count.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_active_members(self, member_service, mock_member_repo):
        """Test counting active members."""
        mock_member_repo.count_active_members.return_value = 8

        result = await member_service.count_active_members()

        assert result == 8
        mock_member_repo.count_active_members.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_member_statistics(self, member_service, mock_member_repo):
        """Test getting member statistics."""
        # Mock repository responses
        mock_member_repo.count.return_value = 10
        mock_member_repo.count_active_members.return_value = 8
        mock_member_repo.count_by_status.return_value = 5
        mock_member_repo.count_by_role.return_value = 3
        mock_member_repo.get_birthdays_this_month.return_value = []
        mock_member_repo.get_birthdays_today.return_value = []

        result = await member_service.get_member_statistics()

        assert result["total_members"] == 10
        assert result["active_members"] == 8
        assert result["inactive_members"] == 2
        assert "status_counts" in result
        assert "role_counts" in result
        assert "birthdays_this_month" in result
        assert "birthdays_today" in result

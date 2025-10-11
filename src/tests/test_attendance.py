"""Tests for attendance functionality."""

from datetime import date, datetime
from unittest.mock import AsyncMock, patch

import pytest

from src.models.attendance import (
    Attendance, AttendanceCreate, AttendanceStatus, AttendanceType,
)
from src.repositories.attendance import AttendanceRepository
from src.services.attendance import AttendanceService


class TestAttendanceModel:
    """Test attendance model functionality."""

    def test_attendance_create_valid(self):
        """Test valid attendance creation."""
        attendance_data = {
            "member_id": "507f1f77bcf86cd799439011",
            "attendance_date": date.today(),
            "attendance_type": AttendanceType.SUNDAY_SERVICE,
            "status": AttendanceStatus.PRESENT,
            "recorded_by": "507f1f77bcf86cd799439012",
        }
        attendance_create = AttendanceCreate(**attendance_data)
        assert attendance_create.member_id == "507f1f77bcf86cd799439011"
        assert attendance_create.attendance_type == AttendanceType.SUNDAY_SERVICE
        assert attendance_create.status == AttendanceStatus.PRESENT

    def test_attendance_create_future_date_validation(self):
        """Test future date validation."""
        future_date = date.today().replace(day=date.today().day + 1)
        with pytest.raises(ValueError, match="Attendance date cannot be in the future"):
            AttendanceCreate(
                member_id="507f1f77bcf86cd799439011",
                attendance_date=future_date,
                attendance_type=AttendanceType.SUNDAY_SERVICE,
                status=AttendanceStatus.PRESENT,
                recorded_by="507f1f77bcf86cd799439012",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )


class TestAttendanceRepository:
    """Test attendance repository functionality."""

    @pytest.fixture
    def mock_collection(self):
        """Mock MongoDB collection."""
        return AsyncMock()

    @pytest.fixture
    def attendance_repo(self, mock_collection):
        """Create attendance repository with mocked collection."""
        repo = AttendanceRepository()
        with patch.object(repo, 'get_collection', return_value=mock_collection):
            yield repo

    @pytest.mark.asyncio
    async def test_get_by_member_id(self, attendance_repo, mock_collection):
        """Test getting attendance records by member ID."""
        # Mock database response
        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "member_id": "507f1f77bcf86cd799439012",
                "attendance_date": date.today().isoformat(),
                "attendance_type": AttendanceType.SUNDAY_SERVICE,
                "status": AttendanceStatus.PRESENT,
                "recorded_by": "507f1f77bcf86cd799439013",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value.to_list.return_value = mock_docs

        result = await attendance_repo.get_by_member_id("507f1f77bcf86cd799439012")

        assert len(result) == 1
        assert result[0].member_id == "507f1f77bcf86cd799439012"
        assert result[0].attendance_type == AttendanceType.SUNDAY_SERVICE
        assert result[0].status == AttendanceStatus.PRESENT

    @pytest.mark.asyncio
    async def test_get_by_date(self, attendance_repo, mock_collection):
        """Test getting attendance records by date."""
        today = date.today()
        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "member_id": "507f1f77bcf86cd799439012",
                "attendance_date": today.isoformat(),
                "attendance_type": AttendanceType.SUNDAY_SERVICE,
                "status": AttendanceStatus.PRESENT,
                "recorded_by": "507f1f77bcf86cd799439013",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value.sort.return_value.to_list.return_value = mock_docs

        result = await attendance_repo.get_by_date(today)

        assert len(result) == 1
        assert result[0].attendance_date == today
        mock_collection.find.assert_called_once_with({"attendance_date": today.isoformat()})

    @pytest.mark.asyncio
    async def test_check_attendance_exists(self, attendance_repo, mock_collection):
        """Test checking if attendance record exists."""
        mock_collection.find_one.return_value = {"_id": "507f1f77bcf86cd799439011"}

        result = await attendance_repo.check_attendance_exists(
            "507f1f77bcf86cd799439012",
            date.today(),
            AttendanceType.SUNDAY_SERVICE
        )

        assert result is True
        mock_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_attendance_not_exists(self, attendance_repo, mock_collection):
        """Test checking if attendance record doesn't exist."""
        mock_collection.find_one.return_value = None

        result = await attendance_repo.check_attendance_exists(
            "507f1f77bcf86cd799439012",
            date.today(),
            AttendanceType.SUNDAY_SERVICE
        )

        assert result is False
        mock_collection.find_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_member_attendance_summary(self, attendance_repo, mock_collection):
        """Test getting member attendance summary."""
        # Mock aggregation pipeline result
        mock_results = [
            {"_id": AttendanceStatus.PRESENT, "count": 5},
            {"_id": AttendanceStatus.ABSENT, "count": 2},
            {"_id": AttendanceStatus.LATE, "count": 1},
        ]
        mock_collection.aggregate.return_value.to_list.return_value = mock_results

        start_date = date.today().replace(day=1)
        end_date = date.today()

        result = await attendance_repo.get_member_attendance_summary(
            "507f1f77bcf86cd799439012",
            start_date,
            end_date
        )

        assert result["member_id"] == "507f1f77bcf86cd799439012"
        assert result["total_services"] == 8
        assert result["present_count"] == 5
        assert result["absent_count"] == 2
        assert result["late_count"] == 1
        assert result["attendance_rate"] == 62.5  # 5/8 * 100


class TestAttendanceService:
    """Test attendance service functionality."""

    @pytest.fixture
    def mock_attendance_repo(self):
        """Mock attendance repository."""
        return AsyncMock(spec=AttendanceRepository)

    @pytest.fixture
    def attendance_service(self, mock_attendance_repo):
        """Create attendance service with mocked repository."""
        service = AttendanceService()
        service.attendance_repo = mock_attendance_repo
        return service

    @pytest.mark.asyncio
    async def test_create_attendance_success(self, attendance_service, mock_attendance_repo):
        """Test successful attendance creation."""
        # Mock repository responses
        mock_attendance_repo.check_attendance_exists.return_value = False

        mock_attendance_in_db = Attendance(
            id="1",
            member_id="507f1f77bcf86cd799439012",
            attendance_date=date.today(),
            attendance_type=AttendanceType.SUNDAY_SERVICE,
            status=AttendanceStatus.PRESENT,
            recorded_by="507f1f77bcf86cd799439013",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_attendance_repo.create.return_value = mock_attendance_in_db

        attendance_create = AttendanceCreate(
            member_id="507f1f77bcf86cd799439012",
            attendance_date=date.today(),
            attendance_type=AttendanceType.SUNDAY_SERVICE,
            status=AttendanceStatus.PRESENT,
            recorded_by="507f1f77bcf86cd799439013",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = await attendance_service.create_attendance(attendance_create)

        assert result.member_id == "507f1f77bcf86cd799439012"
        assert result.attendance_type == AttendanceType.SUNDAY_SERVICE
        assert result.status == AttendanceStatus.PRESENT
        mock_attendance_repo.check_attendance_exists.assert_called_once()
        mock_attendance_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_attendance_already_exists(self, attendance_service, mock_attendance_repo):
        """Test attendance creation when record already exists."""
        mock_attendance_repo.check_attendance_exists.return_value = True

        attendance_create = AttendanceCreate(
            member_id="507f1f77bcf86cd799439012",
            attendance_date=date.today(),
            attendance_type=AttendanceType.SUNDAY_SERVICE,
            status=AttendanceStatus.PRESENT,
            recorded_by="507f1f77bcf86cd799439013",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        with pytest.raises(ValueError, match="Attendance record already exists"):
            await attendance_service.create_attendance(attendance_create)

        mock_attendance_repo.check_attendance_exists.assert_called_once()
        mock_attendance_repo.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_attendance_by_id_success(self, attendance_service, mock_attendance_repo):
        """Test getting attendance by ID successfully."""
        mock_attendance_in_db = Attendance(
            id="1",
            member_id="507f1f77bcf86cd799439012",
            attendance_date=date.today(),
            attendance_type=AttendanceType.SUNDAY_SERVICE,
            status=AttendanceStatus.PRESENT,
            recorded_by="507f1f77bcf86cd799439013",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_attendance_repo.get_by_id.return_value = mock_attendance_in_db

        result = await attendance_service.get_attendance_by_id("1")

        assert result is not None
        assert result.member_id == "507f1f77bcf86cd799439012"
        assert result.attendance_type == AttendanceType.SUNDAY_SERVICE
        mock_attendance_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_get_attendance_by_id_not_found(self, attendance_service, mock_attendance_repo):
        """Test getting attendance by ID when not found."""
        mock_attendance_repo.get_by_id.return_value = None

        result = await attendance_service.get_attendance_by_id("1")

        assert result is None
        mock_attendance_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_get_member_attendance(self, attendance_service, mock_attendance_repo):
        """Test getting attendance records for a member."""
        mock_attendance_records = [
            Attendance(
                id="1",
                member_id="507f1f77bcf86cd799439012",
                attendance_date=date.today(),
                attendance_type=AttendanceType.SUNDAY_SERVICE,
                status=AttendanceStatus.PRESENT,
                recorded_by="507f1f77bcf86cd799439013",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_attendance_repo.get_by_member_id.return_value = mock_attendance_records

        result = await attendance_service.get_member_attendance("507f1f77bcf86cd799439012")

        assert len(result) == 1
        assert result[0].member_id == "507f1f77bcf86cd799439012"
        mock_attendance_repo.get_by_member_id.assert_called_once_with("507f1f77bcf86cd799439012", skip=0, limit=100)

    @pytest.mark.asyncio
    async def test_get_attendance_statistics(self, attendance_service, mock_attendance_repo):
        """Test getting attendance statistics."""
        # Mock repository responses
        mock_attendance_repo.count_by_status.side_effect = [5, 2, 1, 0]  # present, absent, late, excused

        result = await attendance_service.get_attendance_statistics()

        assert result["total_records"] == 8
        assert result["present_count"] == 5
        assert result["absent_count"] == 2
        assert result["late_count"] == 1
        assert result["excused_count"] == 0
        assert result["attendance_rate"] == 62.5  # 5/8 * 100

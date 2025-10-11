"""Tests for activities functionality."""

from datetime import date, datetime, time
from unittest.mock import AsyncMock, patch

import pytest

from src.models.activities import (
    Activity, ActivityCreate, ActivityPriority, ActivityStatus, ActivityType,
)
from src.repositories.activities import ActivityRepository
from src.services.activities import ActivityService


class TestActivityModel:
    """Test activity model functionality."""

    def test_activity_create_valid(self):
        """Test valid activity creation."""
        activity_data = {
            "title": "Sunday Service",
            "description": "Weekly Sunday worship service",
            "activity_type": ActivityType.WORSHIP_SERVICE,
            "status": ActivityStatus.PLANNED,
            "priority": ActivityPriority.MEDIUM,
            "start_date": date.today(),
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "location": "Main Sanctuary",
            "organizer_id": "507f1f77bcf86cd799439011",
        }
        activity_create = ActivityCreate(**activity_data)
        assert activity_create.title == "Sunday Service"
        assert activity_create.activity_type == ActivityType.WORSHIP_SERVICE
        assert activity_create.status == ActivityStatus.PLANNED

    def test_activity_end_date_validation(self):
        """Test end date validation."""
        start_date = date.today()
        end_date = start_date.replace(day=start_date.day - 1)  # End before start

        with pytest.raises(ValueError, match="End date must be after or equal to start date"):
            ActivityCreate(
                title="Test Activity",
                start_date=start_date,
                end_date=end_date,
                organizer_id="507f1f77bcf86cd799439011",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    def test_activity_end_time_validation(self):
        """Test end time validation."""
        start_time = time(10, 0)
        end_time = time(9, 0)  # End before start

        with pytest.raises(ValueError, match="End time must be after start time"):
            ActivityCreate(
                title="Test Activity",
                start_date=date.today(),
                start_time=start_time,
                end_time=end_time,
                organizer_id="507f1f77bcf86cd799439011",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

    def test_activity_is_today(self):
        """Test activity is today check."""
        today = date.today()
        activity = Activity(
            id="1",
            title="Test Activity",
            start_date=today,
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert activity.is_today is True

    def test_activity_is_past(self):
        """Test activity is past check."""
        past_date = date.today().replace(day=date.today().day - 1)
        activity = Activity(
            id="1",
            title="Test Activity",
            start_date=past_date,
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert activity.is_past is True

    def test_activity_is_upcoming(self):
        """Test activity is upcoming check."""
        future_date = date.today().replace(day=date.today().day + 1)
        activity = Activity(
            id="1",
            title="Test Activity",
            start_date=future_date,
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert activity.is_upcoming is True

    def test_activity_duration_hours(self):
        """Test activity duration calculation."""
        activity = Activity(
            id="1",
            title="Test Activity",
            start_date=date.today(),
            start_time=time(9, 0),
            end_time=time(11, 0),
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert activity.duration_hours == 2.0

    def test_activity_duration_hours_no_times(self):
        """Test activity duration when no times specified."""
        activity = Activity(
            id="1",
            title="Test Activity",
            start_date=date.today(),
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        assert activity.duration_hours is None


class TestActivityRepository:
    """Test activity repository functionality."""

    @pytest.fixture
    def mock_collection(self):
        """Mock MongoDB collection."""
        return AsyncMock()

    @pytest.fixture
    def activity_repo(self, mock_collection):
        """Create activity repository with mocked collection."""
        repo = ActivityRepository()
        with patch.object(repo, 'get_collection', return_value=mock_collection):
            yield repo

    @pytest.mark.asyncio
    async def test_get_by_type(self, activity_repo, mock_collection):
        """Test getting activities by type."""
        # Mock database response
        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "title": "Sunday Service",
                "activity_type": ActivityType.WORSHIP_SERVICE,
                "start_date": date.today().isoformat(),
                "organizer_id": "507f1f77bcf86cd799439012",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value.sort.return_value.to_list.return_value = mock_docs

        result = await activity_repo.get_by_type(ActivityType.WORSHIP_SERVICE)

        assert len(result) == 1
        assert result[0].title == "Sunday Service"
        assert result[0].activity_type == ActivityType.WORSHIP_SERVICE

    @pytest.mark.asyncio
    async def test_get_today_activities(self, activity_repo, mock_collection):
        """Test getting today's activities."""
        today = date.today()
        mock_docs = [
            {
                "_id": "507f1f77bcf86cd799439011",
                "title": "Sunday Service",
                "start_date": today.isoformat(),
                "start_time": "09:00:00",
                "organizer_id": "507f1f77bcf86cd799439012",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
        ]
        mock_collection.find.return_value.sort.return_value.to_list.return_value = mock_docs

        result = await activity_repo.get_today_activities()

        assert len(result) == 1
        assert result[0].title == "Sunday Service"
        assert result[0].start_date == today

    @pytest.mark.asyncio
    async def test_count_by_type(self, activity_repo, mock_collection):
        """Test counting activities by type."""
        mock_collection.count_documents.return_value = 5

        result = await activity_repo.count_by_type(ActivityType.WORSHIP_SERVICE)

        assert result == 5
        mock_collection.count_documents.assert_called_once_with({"activity_type": ActivityType.WORSHIP_SERVICE})

    @pytest.mark.asyncio
    async def test_count_upcoming_activities(self, activity_repo, mock_collection):
        """Test counting upcoming activities."""
        mock_collection.count_documents.return_value = 3

        result = await activity_repo.count_upcoming_activities()

        assert result == 3
        mock_collection.count_documents.assert_called_once()


class TestActivityService:
    """Test activity service functionality."""

    @pytest.fixture
    def mock_activity_repo(self):
        """Mock activity repository."""
        return AsyncMock(spec=ActivityRepository)

    @pytest.fixture
    def activity_service(self, mock_activity_repo):
        """Create activity service with mocked repository."""
        service = ActivityService()
        service.activity_repo = mock_activity_repo
        return service

    @pytest.mark.asyncio
    async def test_create_activity_success(self, activity_service, mock_activity_repo):
        """Test successful activity creation."""
        mock_activity_in_db = Activity(
            id="1",
            title="Sunday Service",
            activity_type=ActivityType.WORSHIP_SERVICE,
            start_date=date.today(),
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_activity_repo.create.return_value = mock_activity_in_db

        activity_create = ActivityCreate(
            title="Sunday Service",
            activity_type=ActivityType.WORSHIP_SERVICE,
            start_date=date.today(),
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        result = await activity_service.create_activity(activity_create)

        assert result.title == "Sunday Service"
        assert result.activity_type == ActivityType.WORSHIP_SERVICE
        mock_activity_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_activity_by_id_success(self, activity_service, mock_activity_repo):
        """Test getting activity by ID successfully."""
        mock_activity_in_db = Activity(
            id="1",
            title="Sunday Service",
            activity_type=ActivityType.WORSHIP_SERVICE,
            start_date=date.today(),
            organizer_id="507f1f77bcf86cd799439011",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_activity_repo.get_by_id.return_value = mock_activity_in_db

        result = await activity_service.get_activity_by_id("1")

        assert result is not None
        assert result.title == "Sunday Service"
        assert result.activity_type == ActivityType.WORSHIP_SERVICE
        mock_activity_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_get_activity_by_id_not_found(self, activity_service, mock_activity_repo):
        """Test getting activity by ID when not found."""
        mock_activity_repo.get_by_id.return_value = None

        result = await activity_service.get_activity_by_id("1")

        assert result is None
        mock_activity_repo.get_by_id.assert_called_once_with("1")

    @pytest.mark.asyncio
    async def test_get_upcoming_activities(self, activity_service, mock_activity_repo):
        """Test getting upcoming activities."""
        mock_activities = [
            Activity(
                id="1",
                title="Sunday Service",
                activity_type=ActivityType.WORSHIP_SERVICE,
                start_date=date.today().replace(day=date.today().day + 1),
                organizer_id="507f1f77bcf86cd799439011",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_activity_repo.get_upcoming_activities.return_value = mock_activities

        result = await activity_service.get_upcoming_activities()

        assert len(result) == 1
        assert result[0].title == "Sunday Service"
        mock_activity_repo.get_upcoming_activities.assert_called_once_with(10)

    @pytest.mark.asyncio
    async def test_get_today_activities(self, activity_service, mock_activity_repo):
        """Test getting today's activities."""
        mock_activities = [
            Activity(
                id="1",
                title="Sunday Service",
                activity_type=ActivityType.WORSHIP_SERVICE,
                start_date=date.today(),
                organizer_id="507f1f77bcf86cd799439011",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_activity_repo.get_today_activities.return_value = mock_activities

        result = await activity_service.get_today_activities()

        assert len(result) == 1
        assert result[0].title == "Sunday Service"
        mock_activity_repo.get_today_activities.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_activities_by_type(self, activity_service, mock_activity_repo):
        """Test counting activities by type."""
        mock_activity_repo.count_by_type.return_value = 5

        result = await activity_service.count_activities_by_type(ActivityType.WORSHIP_SERVICE)

        assert result == 5
        mock_activity_repo.count_by_type.assert_called_once_with(ActivityType.WORSHIP_SERVICE)

    @pytest.mark.asyncio
    async def test_get_activity_statistics(self, activity_service, mock_activity_repo):
        """Test getting activity statistics."""
        mock_stats = {
            "status_counts": {"planned": 3, "confirmed": 2, "completed": 5},
            "type_counts": {"worship_service": 4, "bible_study": 3},
            "upcoming_count": 5,
            "this_month_count": 8,
            "total_count": 10
        }
        mock_activity_repo.get_activity_statistics.return_value = mock_stats

        result = await activity_service.get_activity_statistics()

        assert result == mock_stats
        mock_activity_repo.get_activity_statistics.assert_called_once()

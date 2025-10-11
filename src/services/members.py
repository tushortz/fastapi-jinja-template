"""Member service for business logic."""

import logging
from typing import Any

from src.models.members import (
    Member, MemberCreate, MemberInDB, MemberRole, MemberStatus, MemberUpdate,
)
from src.repositories.members import MemberRepository
from src.services.insights import MemberInsightService

logger = logging.getLogger(__name__)


class MemberService:
    """Member service for business logic operations."""

    def __init__(self):
        self.member_repo = MemberRepository()

    async def create_member(self, member_create: MemberCreate) -> Member:
        """Create a new member."""
        logger.info("Creating member: %s %s", member_create.first_name, member_create.last_name)

        # Check if email is already taken
        if member_create.email and await self.member_repo.is_email_taken(member_create.email):
            logger.warning("Email already registered: %s", member_create.email)
            raise ValueError("Email already registered")

        # Check if phone is already taken
        if member_create.phone and await self.member_repo.is_phone_taken(member_create.phone):
            logger.warning("Phone already registered: %s", member_create.phone)
            raise ValueError("Phone number already registered")

        # Create member
        member_in_db = await self.member_repo.create(member_create)
        logger.info(
            "Member created successfully: %s %s (ID: %s)",
            member_in_db.first_name,
            member_in_db.last_name,
            member_in_db.id,
        )

        return Member(
            id=member_in_db.id,
            first_name=member_in_db.first_name,
            last_name=member_in_db.last_name,
            email=member_in_db.email,
            phone=member_in_db.phone,
            date_of_birth=member_in_db.date_of_birth,
            gender=member_in_db.gender,
            marital_status=member_in_db.marital_status,
            address=member_in_db.address,
            city=member_in_db.city,
            state=member_in_db.state,
            zip_code=member_in_db.zip_code,
            country=member_in_db.country,
            emergency_contact_name=member_in_db.emergency_contact_name,
            emergency_contact_phone=member_in_db.emergency_contact_phone,
            occupation=member_in_db.occupation,
            employer=member_in_db.employer,
            education_level=member_in_db.education_level,
            baptism_date=member_in_db.baptism_date,
            membership_date=member_in_db.membership_date,
            status=member_in_db.status,
            role=member_in_db.role,
            notes=member_in_db.notes,
            is_active=member_in_db.is_active,
            created_at=member_in_db.created_at,
            updated_at=member_in_db.updated_at,
        )

    async def get_member_by_id(self, member_id: str) -> Member | None:
        """Get member by ID."""
        logger.debug("Getting member by ID: %s", member_id)
        member_in_db = await self.member_repo.get_by_id(member_id)
        if not member_in_db:
            return None

        return Member(
            id=member_in_db.id,
            first_name=member_in_db.first_name,
            last_name=member_in_db.last_name,
            email=member_in_db.email,
            phone=member_in_db.phone,
            date_of_birth=member_in_db.date_of_birth,
            gender=member_in_db.gender,
            marital_status=member_in_db.marital_status,
            address=member_in_db.address,
            city=member_in_db.city,
            state=member_in_db.state,
            zip_code=member_in_db.zip_code,
            country=member_in_db.country,
            emergency_contact_name=member_in_db.emergency_contact_name,
            emergency_contact_phone=member_in_db.emergency_contact_phone,
            occupation=member_in_db.occupation,
            employer=member_in_db.employer,
            education_level=member_in_db.education_level,
            baptism_date=member_in_db.baptism_date,
            membership_date=member_in_db.membership_date,
            status=member_in_db.status,
            role=member_in_db.role,
            notes=member_in_db.notes,
            is_active=member_in_db.is_active,
            created_at=member_in_db.created_at,
            updated_at=member_in_db.updated_at,
        )

    async def get_member_by_email(self, email: str) -> MemberInDB | None:
        """Get member by email (returns MemberInDB for internal use)."""
        logger.debug("Getting member by email: %s", email)
        return await self.member_repo.get_by_email(email)

    async def get_member_by_phone(self, phone: str) -> MemberInDB | None:
        """Get member by phone (returns MemberInDB for internal use)."""
        logger.debug("Getting member by phone: %s", phone)
        return await self.member_repo.get_by_phone(phone)

    async def update_member(self, member_id: str, member_update: MemberUpdate) -> Member | None:
        """Update member."""
        logger.info("Updating member: %s", member_id)

        # Check if email is being changed and if it's already taken
        if member_update.email:
            existing_member = await self.member_repo.get_by_email(member_update.email)
            if existing_member and existing_member.id != member_id:
                raise ValueError("Email already registered")

        # Check if phone is being changed and if it's already taken
        if member_update.phone:
            existing_member = await self.member_repo.get_by_phone(member_update.phone)
            if existing_member and existing_member.id != member_id:
                raise ValueError("Phone number already registered")

        member_in_db = await self.member_repo.update(member_id, member_update)
        if not member_in_db:
            logger.warning("Member not found for update: %s", member_id)
            return None

        logger.info("Member updated successfully: %s", member_in_db.id)
        return Member(
            id=member_in_db.id,
            first_name=member_in_db.first_name,
            last_name=member_in_db.last_name,
            email=member_in_db.email,
            phone=member_in_db.phone,
            date_of_birth=member_in_db.date_of_birth,
            gender=member_in_db.gender,
            marital_status=member_in_db.marital_status,
            address=member_in_db.address,
            city=member_in_db.city,
            state=member_in_db.state,
            zip_code=member_in_db.zip_code,
            country=member_in_db.country,
            emergency_contact_name=member_in_db.emergency_contact_name,
            emergency_contact_phone=member_in_db.emergency_contact_phone,
            occupation=member_in_db.occupation,
            employer=member_in_db.employer,
            education_level=member_in_db.education_level,
            baptism_date=member_in_db.baptism_date,
            membership_date=member_in_db.membership_date,
            status=member_in_db.status,
            role=member_in_db.role,
            notes=member_in_db.notes,
            is_active=member_in_db.is_active,
            created_at=member_in_db.created_at,
            updated_at=member_in_db.updated_at,
        )

    async def delete_member(self, member_id: str) -> bool:
        """Delete member by setting as inactive."""
        logger.info("Deactivating member with ID: %s", member_id)

        # Create an update object to set is_active to False
        member_update = MemberUpdate(is_active=False, status=MemberStatus.INACTIVE)

        member_in_db = await self.member_repo.update(member_id, member_update)
        if not member_in_db:
            logger.warning("Member not found for deactivation: %s", member_id)
            return False

        logger.info("Member deactivated successfully: %s %s", member_in_db.first_name, member_in_db.last_name)
        return True

    async def get_members(
        self,
        skip: int = 0,
        limit: int = 100,
        search: str | None = None,
        status: MemberStatus | None = None,
        role: MemberRole | None = None,
    ) -> list[Member]:
        """Get all members with pagination and optional filters."""
        logger.debug("Getting members with filters: skip=%d, limit=%d", skip, limit)

        filter_dict: dict[str, Any] = {}
        if status:
            filter_dict["status"] = status
        if role:
            filter_dict["role"] = role

        members_in_db = await self.member_repo.get_many(
            skip=skip, limit=limit, search=search, filter_dict=filter_dict
        )

        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def get_active_members(
        self, skip: int = 0, limit: int = 100
    ) -> list[Member]:
        """
        Get active members only, excluding those with status 'relocated' or 'outreach'.
        """
        logger.debug(
            "Getting active members excluding status 'relocated' and 'outreach'"
        )
        filter_dict: dict[str, Any] = {
            "is_active": True,
            "status": {
                "$nin": [MemberStatus.RELOCATED, MemberStatus.OUTREACH]
            },
        }
        members_in_db = await self.member_repo.get_many(
            skip=skip, limit=limit, filter_dict=filter_dict
        )
        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def get_members_by_status(self, status: MemberStatus) -> list[Member]:
        """Get members by status."""
        logger.debug("Getting members by status: %s", status)
        members_in_db = await self.member_repo.get_by_status(status)

        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def get_members_by_role(self, role: MemberRole) -> list[Member]:
        """Get members by role."""
        logger.debug("Getting members by role: %s", role)
        members_in_db = await self.member_repo.get_by_role(role)

        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def get_birthdays_this_month(self) -> list[Member]:
        """Get members with birthdays this month."""
        logger.debug("Getting members with birthdays this month")
        members_in_db = await self.member_repo.get_birthdays_this_month()

        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def get_birthdays_today(self) -> list[Member]:
        """Get members with birthdays today."""
        logger.debug("Getting members with birthdays today")
        members_in_db = await self.member_repo.get_birthdays_today()

        return [
            Member(
                id=member.id,
                first_name=member.first_name,
                last_name=member.last_name,
                email=member.email,
                phone=member.phone,
                date_of_birth=member.date_of_birth,
                gender=member.gender,
                marital_status=member.marital_status,
                address=member.address,
                city=member.city,
                state=member.state,
                zip_code=member.zip_code,
                country=member.country,
                emergency_contact_name=member.emergency_contact_name,
                emergency_contact_phone=member.emergency_contact_phone,
                occupation=member.occupation,
                employer=member.employer,
                education_level=member.education_level,
                baptism_date=member.baptism_date,
                membership_date=member.membership_date,
                status=member.status,
                role=member.role,
                notes=member.notes,
                is_active=member.is_active,
                created_at=member.created_at,
                updated_at=member.updated_at,
            )
            for member in members_in_db
        ]

    async def count_members(self) -> int:
        """Count total members."""
        logger.info("Counting total members")
        try:
            count = await self.member_repo.count()
            logger.info("Total members count: %d", count)
            return count
        except Exception as e:
            logger.error("Error counting members: %s", str(e))
            raise

    async def count_active_members(self) -> int:
        """Count active members."""
        logger.info("Counting active members")
        try:
            count = await self.member_repo.count_active_members()
            logger.info("Active members count: %d", count)
            return count
        except Exception as e:
            logger.error("Error counting active members: %s", str(e))
            raise

    async def count_members_by_status(self, status: MemberStatus) -> int:
        """Count members by status."""
        logger.info("Counting members by status: %s", status)
        try:
            count = await self.member_repo.count_by_status(status)
            logger.info("Members count for status %s: %d", status, count)
            return count
        except Exception as e:
            logger.error("Error counting members by status: %s", str(e))
            raise

    async def count_members_by_role(self, role: MemberRole) -> int:
        """Count members by role."""
        logger.info("Counting members by role: %s", role)
        try:
            count = await self.member_repo.count_by_role(role)
            logger.info("Members count for role %s: %d", role, count)
            return count
        except Exception as e:
            logger.error("Error counting members by role: %s", str(e))
            raise

    async def get_member_statistics(self) -> dict[str, Any]:
        """Get member statistics."""
        logger.info("Getting member statistics")
        try:
            total_members = await self.count_members()
            active_members = await self.count_active_members()

            # Get counts by status
            status_counts = {}
            for status in MemberStatus:
                status_counts[status.value] = await self.count_members_by_status(status)

            # Get counts by role
            role_counts = {}
            for role in MemberRole:
                role_counts[role.value] = await self.count_members_by_role(role)

            # Get birthday counts
            birthdays_this_month = len(await self.get_birthdays_this_month())
            birthdays_today = len(await self.get_birthdays_today())

            return {
                "total_members": total_members,
                "active_members": active_members,
                "inactive_members": total_members - active_members,
                "status_counts": status_counts,
                "role_counts": role_counts,
                "birthdays_this_month": birthdays_this_month,
                "birthdays_today": birthdays_today,
            }
        except Exception as e:
            logger.error("Error getting member statistics: %s", str(e))
            raise

    async def generate_member_insight(self, member: Member) -> str:
        """Generate AI insight for a member."""
        insight_service = MemberInsightService()
        return await insight_service.generate_member_insights(member)

"""Initialize church management database with sample data."""

import asyncio
import logging
from datetime import date, datetime, time
from typing import Any

from src.config import setup_logging
from src.database import close_mongo_connection, connect_to_mongo, get_database
from src.models.activities import (
    ActivityCreate, ActivityPriority, ActivityStatus, ActivityType,
)
from src.models.attendance import AttendanceCreate, AttendanceStatus, AttendanceType
from src.models.members import (
    Gender, MaritalStatus, MemberCreate, MemberRole, MemberStatus,
)
from src.services.activities import ActivityService
from src.services.attendance import AttendanceService
from src.services.members import MemberService

logger = setup_logging()


async def create_sample_members() -> list[str]:
    """Create sample church members."""
    logger.info("Creating sample members...")

    member_service = MemberService()
    member_ids = []

    sample_members = [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "phone": "555-0101",
            "date_of_birth": date(1985, 3, 15),
            "gender": Gender.MALE,
            "marital_status": MaritalStatus.MARRIED,
            "address": "123 Main St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62701",
            "country": "USA",
            "emergency_contact_name": "Jane Smith",
            "emergency_contact_phone": "555-0102",
            "emergency_contact_relationship": "Spouse",
            "occupation": "Teacher",
            "employer": "Springfield Elementary",
            "education_level": "Bachelor's Degree",
            "baptism_date": date(2010, 6, 15),
            "membership_date": date(2010, 7, 1),
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.ELDER,
            "notes": "Active member, leads Sunday school class"
        },
        {
            "first_name": "Mary",
            "last_name": "Johnson",
            "email": "mary.johnson@example.com",
            "phone": "555-0201",
            "date_of_birth": date(1990, 8, 22),
            "gender": Gender.FEMALE,
            "marital_status": MaritalStatus.SINGLE,
            "address": "456 Oak Ave",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62702",
            "country": "USA",
            "emergency_contact_name": "Robert Johnson",
            "emergency_contact_phone": "555-0202",
            "emergency_contact_relationship": "Father",
            "occupation": "Nurse",
            "employer": "Springfield General Hospital",
            "education_level": "Bachelor's Degree",
            "baptism_date": date(2015, 4, 12),
            "membership_date": date(2015, 5, 1),
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.MEMBER,
            "notes": "Volunteers with children's ministry"
        },
        {
            "first_name": "David",
            "last_name": "Williams",
            "email": "david.williams@example.com",
            "phone": "555-0301",
            "date_of_birth": date(1978, 12, 5),
            "gender": Gender.MALE,
            "marital_status": MaritalStatus.MARRIED,
            "address": "789 Pine St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62703",
            "country": "USA",
            "emergency_contact_name": "Sarah Williams",
            "emergency_contact_phone": "555-0302",
            "emergency_contact_relationship": "Spouse",
            "occupation": "Pastor",
            "employer": "Springfield Community Church",
            "education_level": "Master's Degree",
            "baptism_date": date(2005, 3, 20),
            "membership_date": date(2005, 4, 1),
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.PASTOR,
            "notes": "Senior Pastor, leads worship services"
        },
        {
            "first_name": "Sarah",
            "last_name": "Brown",
            "email": "sarah.brown@example.com",
            "phone": "555-0401",
            "date_of_birth": date(1992, 7, 18),
            "gender": Gender.FEMALE,
            "marital_status": MaritalStatus.SINGLE,
            "address": "321 Elm St",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62704",
            "country": "USA",
            "emergency_contact_name": "Michael Brown",
            "emergency_contact_phone": "555-0402",
            "emergency_contact_relationship": "Brother",
            "occupation": "Musician",
            "employer": "Freelance",
            "education_level": "Bachelor's Degree",
            "baptism_date": date(2018, 9, 10),
            "membership_date": date(2018, 10, 1),
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.WORSHIP_LEADER,
            "notes": "Leads worship team, plays piano and guitar"
        },
        {
            "first_name": "Michael",
            "last_name": "Davis",
            "email": "michael.davis@example.com",
            "phone": "555-0501",
            "date_of_birth": date(1988, 11, 30),
            "gender": Gender.MALE,
            "marital_status": MaritalStatus.MARRIED,
            "address": "654 Maple Ave",
            "city": "Springfield",
            "state": "IL",
            "zip_code": "62705",
            "country": "USA",
            "emergency_contact_name": "Lisa Davis",
            "emergency_contact_phone": "555-0502",
            "emergency_contact_relationship": "Spouse",
            "occupation": "Engineer",
            "employer": "Springfield Tech Corp",
            "education_level": "Master's Degree",
            "baptism_date": date(2012, 5, 25),
            "membership_date": date(2012, 6, 1),
            "status": MemberStatus.ACTIVE,
            "role": MemberRole.DEACON,
            "notes": "Handles church technology and sound system"
        }
    ]

    for member_data in sample_members:
        try:
            member_create = MemberCreate(**member_data)
            member = await member_service.create_member(member_create)
            member_ids.append(member.id)
            logger.info("Created member: %s %s", member.first_name, member.last_name)
        except Exception as e:
            logger.error("Error creating member %s %s: %s",
                        member_data["first_name"], member_data["last_name"], str(e))

    logger.info("Created %d sample members", len(member_ids))
    return member_ids


async def create_sample_activities() -> list[str]:
    """Create sample church activities."""
    logger.info("Creating sample activities...")

    activity_service = ActivityService()
    activity_ids = []

    sample_activities = [
        {
            "title": "Sunday Morning Service",
            "description": "Weekly Sunday worship service with sermon and communion",
            "activity_type": ActivityType.WORSHIP_SERVICE,
            "status": ActivityStatus.CONFIRMED,
            "priority": ActivityPriority.HIGH,
            "start_date": date.today().replace(day=date.today().day + (7 - date.today().weekday()) % 7),
            "start_time": time(9, 0),
            "end_time": time(11, 0),
            "location": "Main Sanctuary",
            "address": "123 Church St, Springfield, IL 62701",
            "organizer_id": "507f1f77bcf86cd799439011",  # This would be a real user ID
            "coordinator_name": "David Williams",
            "coordinator_phone": "555-0301",
            "coordinator_email": "david.williams@example.com",
            "estimated_attendance": 150,
            "requirements": "Sound system, microphones, communion elements",
            "notes": "Regular weekly service"
        },
        {
            "title": "Wednesday Prayer Meeting",
            "description": "Mid-week prayer and Bible study",
            "activity_type": ActivityType.PRAYER_MEETING,
            "status": ActivityStatus.CONFIRMED,
            "priority": ActivityPriority.MEDIUM,
            "start_date": date.today().replace(day=date.today().day + (2 - date.today().weekday()) % 7),
            "start_time": time(19, 0),
            "end_time": time(20, 30),
            "location": "Fellowship Hall",
            "address": "123 Church St, Springfield, IL 62701",
            "organizer_id": "507f1f77bcf86cd799439011",
            "coordinator_name": "John Smith",
            "coordinator_phone": "555-0101",
            "coordinator_email": "john.smith@example.com",
            "estimated_attendance": 30,
            "requirements": "Bibles, prayer requests",
            "notes": "Weekly prayer meeting"
        },
        {
            "title": "Youth Group Meeting",
            "description": "Weekly youth group activities and Bible study",
            "activity_type": ActivityType.YOUTH_EVENT,
            "status": ActivityStatus.PLANNED,
            "priority": ActivityPriority.MEDIUM,
            "start_date": date.today().replace(day=date.today().day + (5 - date.today().weekday()) % 7),
            "start_time": time(18, 0),
            "end_time": time(20, 0),
            "location": "Youth Room",
            "address": "123 Church St, Springfield, IL 62701",
            "organizer_id": "507f1f77bcf86cd799439011",
            "coordinator_name": "Sarah Brown",
            "coordinator_phone": "555-0401",
            "coordinator_email": "sarah.brown@example.com",
            "estimated_attendance": 25,
            "requirements": "Snacks, games, Bibles",
            "notes": "Weekly youth meeting"
        },
        {
            "title": "Choir Rehearsal",
            "description": "Weekly choir practice for Sunday service",
            "activity_type": ActivityType.CHOIR_REHEARSAL,
            "status": ActivityStatus.CONFIRMED,
            "priority": ActivityPriority.MEDIUM,
            "start_date": date.today().replace(day=date.today().day + (6 - date.today().weekday()) % 7),
            "start_time": time(19, 30),
            "end_time": time(21, 0),
            "location": "Choir Room",
            "address": "123 Church St, Springfield, IL 62701",
            "organizer_id": "507f1f77bcf86cd799439011",
            "coordinator_name": "Sarah Brown",
            "coordinator_phone": "555-0401",
            "coordinator_email": "sarah.brown@example.com",
            "estimated_attendance": 15,
            "requirements": "Music sheets, piano",
            "notes": "Weekly choir rehearsal"
        }
    ]

    for activity_data in sample_activities:
        try:
            activity_create = ActivityCreate(**activity_data)
            activity = await activity_service.create_activity(activity_create)
            activity_ids.append(activity.id)
            logger.info("Created activity: %s", activity.title)
        except Exception as e:
            logger.error("Error creating activity %s: %s", activity_data["title"], str(e))

    logger.info("Created %d sample activities", len(activity_ids))
    return activity_ids


async def create_sample_attendance(member_ids: list[str]) -> list[str]:
    """Create sample attendance records."""
    logger.info("Creating sample attendance records...")

    attendance_service = AttendanceService()
    attendance_ids = []

    # Create attendance records for the last 4 weeks
    from datetime import timedelta
    today = date.today()

    for week_offset in range(4):
        service_date = today - timedelta(weeks=week_offset, days=today.weekday())

        # Sunday Service attendance
        for i, member_id in enumerate(member_ids[:4]):  # Use first 4 members
            try:
                attendance_create = AttendanceCreate(
                    member_id=member_id,
                    attendance_date=service_date,
                    attendance_type=AttendanceType.SUNDAY_SERVICE,
                    status=AttendanceStatus.PRESENT if i < 3 else AttendanceStatus.ABSENT,
                    service_time="9:00 AM",
                    recorded_by="507f1f77bcf86cd799439011",  # This would be a real user ID
                    notes="Regular Sunday service" if i < 3 else "Member was out of town"
                )
                attendance = await attendance_service.create_attendance(attendance_create)
                attendance_ids.append(attendance.id)
            except Exception as e:
                logger.error("Error creating attendance record: %s", str(e))

        # Wednesday Prayer Meeting attendance
        prayer_date = service_date + timedelta(days=3)
        for i, member_id in enumerate(member_ids[:3]):  # Use first 3 members
            try:
                attendance_create = AttendanceCreate(
                    member_id=member_id,
                    attendance_date=prayer_date,
                    attendance_type=AttendanceType.PRAYER_MEETING,
                    status=AttendanceStatus.PRESENT if i < 2 else AttendanceStatus.LATE,
                    service_time="7:00 PM",
                    recorded_by="507f1f77bcf86cd799439011",
                    notes="Wednesday prayer meeting" if i < 2 else "Arrived 15 minutes late"
                )
                attendance = await attendance_service.create_attendance(attendance_create)
                attendance_ids.append(attendance.id)
            except Exception as e:
                logger.error("Error creating attendance record: %s", str(e))

    logger.info("Created %d sample attendance records", len(attendance_ids))
    return attendance_ids


async def main():
    """Main function to initialize church management data."""
    logger.info("Starting church management database initialization...")

    try:
        # Connect to database
        await connect_to_mongo()
        logger.info("Connected to MongoDB")

        # Create sample data
        member_ids = await create_sample_members()
        activity_ids = await create_sample_activities()
        attendance_ids = await create_sample_attendance(member_ids)

        logger.info("Database initialization completed successfully!")
        logger.info("Created:")
        logger.info("  - %d members", len(member_ids))
        logger.info("  - %d activities", len(activity_ids))
        logger.info("  - %d attendance records", len(attendance_ids))

    except Exception as e:
        logger.error("Error during database initialization: %s", str(e))
        raise
    finally:
        # Close database connection
        await close_mongo_connection()
        logger.info("Database connection closed")


if __name__ == "__main__":
    asyncio.run(main())

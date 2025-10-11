"""Database connection and configuration."""

import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config import settings

logger = logging.getLogger(__name__)


class Database:
    """Database connection manager."""

    client: AsyncIOMotorClient | None = None
    database: AsyncIOMotorDatabase | None = None


db = Database()


async def get_database() -> AsyncIOMotorClient:
    """Get database connection."""
    if db.database is None:
        logger.error(
            "Database connection not established. Call connect_to_mongo() first."
        )
        raise RuntimeError("Database connection not established")
    return db.database


async def connect_to_mongo():
    """Create database connection."""
    logger.info("Connecting to MongoDB: %s", settings.mongodb_url)

    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        db.database = db.client[settings.database_name]

        # Test connection
        await db.client.admin.command("ping")
        logger.info(
            "Successfully connected to MongoDB database: %s", settings.database_name
        )

    except Exception as e:
        logger.error("Failed to connect to MongoDB: %s", str(e))
        raise


async def close_mongo_connection():
    """Close database connection."""
    if db.client:
        logger.info("Closing MongoDB connection")
        db.client.close()
        logger.info("MongoDB connection closed")

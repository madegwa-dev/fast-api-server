from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.config import MONGODB_URI, DATABASE_NAME

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db = None

async def connect_to_mongodb():
    """Connect to MongoDB."""
    Database.client = AsyncIOMotorClient(MONGODB_URI)
    Database.db = Database.client[DATABASE_NAME]
    logger.info("Connected to MongoDB")

async def close_mongodb_connection():
    """Close MongoDB connection."""
    if Database.client:
        Database.client.close()
        logger.info("MongoDB connection closed")
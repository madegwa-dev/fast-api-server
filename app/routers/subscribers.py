from app.database import Database
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/subscribers", tags=["subscribers"])


# Pydantic model for request body
class SubscriberRequest(BaseModel):
    email: EmailStr


@router.post("/add")
async def add_subscriber(subscriber: SubscriberRequest):
    try:
        # Check if email already exists
        existing_subscriber = await Database.db.subscribers.find_one({'email': subscriber.email})
        if existing_subscriber:
            raise HTTPException(status_code=400, detail="Email already subscribed")

        subscriber_response = await Database.db.subscribers.insert_one({'email': subscriber.email})
        logger.info(f'Subscriber: {subscriber.email} added with id: {subscriber_response.inserted_id}')
        return {
            'message': 'Successfully subscribed!',
            'email': subscriber.email,
            'success': True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Exception: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
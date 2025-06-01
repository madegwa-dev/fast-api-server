import logging
from app.database import Database


class DonorRepository:
    @staticmethod
    async def save_donor(donor: dict) -> str:
        """Save a new donor or upsert if exists."""
        result = await Database.db.donors.update_one(
            {"CheckoutRequestID": donor["CheckoutRequestID"]},
            {"$set": donor},
            upsert=True
        )
        logging.debug(f"Save donor result: {result.raw_result}")

        return result.upserted_id

    @staticmethod
    async def update_donor(checkout_request_id: str, updates: dict) -> None:
        """Update donor details based on CheckoutRequestID."""
        await Database.db.donors.update_one(
            {"CheckoutRequestID": checkout_request_id},
            {"$set": updates}
        )


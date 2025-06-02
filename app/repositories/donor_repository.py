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
    async def get_top_donors(limit: int = 5):
        """Fetch top donors sorted by Amount in descending order."""
        top_donors = await Database.db.donors.find(
            {},  # No specific filter
            {"_id": 0, "name": 1, "Amount": 1, }  # Fields to include in response
        ).sort("Amount", -1).limit(limit).to_list(length=limit)
        return top_donors

    @staticmethod
    async def update_donor(checkout_request_id: str, updates: dict) -> None:
        """Update donor details based on CheckoutRequestID."""
        await Database.db.donors.update_one(
            {"CheckoutRequestID": checkout_request_id},
            {"$set": updates}
        )


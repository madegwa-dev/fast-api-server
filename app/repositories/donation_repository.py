import logging
from typing import List, Optional
from app.database import Database
from app.models.donation import DonationModel

logger = logging.getLogger(__name__)


class DonationRepository:
    """Repository for donation database operations."""
    
    @staticmethod
    async def save(donation: DonationModel) -> str:
        """
        Save a donation to the database.
        
        Args:
            donation: The donation model to save
            
        Returns:
            The inserted document ID
        """
        donation_dict = donation.to_dict()
        result = await Database.db.donations.insert_one(donation_dict)
        logger.info(f"Donation saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    @staticmethod
    async def find_by_id(donation_id: str) -> Optional[dict]:
        """
        Find a donation by ID.
        
        Args:
            donation_id: The donation ID to search for
            
        Returns:
            The donation document or None if not found
        """
        result = await Database.db.donations.find_one({"_id": donation_id})
        return result
    
    @staticmethod
    async def find_by_external_reference(external_reference: str) -> Optional[dict]:
        """
        Find a donation by external reference.
        
        Args:
            external_reference: The external reference to search for
            
        Returns:
            The donation document or None if not found
        """
        result = await Database.db.donations.find_one({"external_reference": external_reference})
        return result
    
    @staticmethod
    async def update_status(external_reference: str, status: str, mpesa_receipt_number: str = None) -> bool:
        """
        Update donation status.
        
        Args:
            external_reference: The external reference to find the donation
            status: New status
            mpesa_receipt_number: Receipt number from M-Pesa
            
        Returns:
            True if updated successfully, False otherwise
        """
        update_data = {"status": status}
        if mpesa_receipt_number:
            update_data["mpesa_receipt_number"] = mpesa_receipt_number
            
        result = await Database.db.donations.update_one(
            {"external_reference": external_reference},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    @staticmethod
    async def get_all_completed_donations() -> List[dict]:
        """
        Get all completed donations sorted by amount (highest first).
        
        Returns:
            List of completed donations
        """
        cursor = Database.db.donations.find(
            {"status": "completed"}
        ).sort("amount", -1)
        
        donations = []
        async for donation in cursor:
            donations.append(donation)
        
        return donations
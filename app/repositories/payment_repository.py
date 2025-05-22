import logging
from app.database import Database
from app.models.payment import PaymentModel

logger = logging.getLogger(__name__)

class PaymentRepository:
    """Repository for payment database operations."""
    
    @staticmethod
    async def save(payment: PaymentModel) -> str:
        """
        Save a payment to the database.
        
        Args:
            payment: The payment model to save
            
        Returns:
            The inserted document ID
        """
        payment_dict = payment.to_dict()
        result = await Database.db.payments.insert_one(payment_dict)
        logger.info(f"Payment saved with ID: {result.inserted_id}")
        return str(result.inserted_id)
    
    @staticmethod
    async def find_by_id(payment_id: str):
        """
        Find a payment by ID.
        
        Args:
            payment_id: The payment ID to search for
            
        Returns:
            The payment document or None if not found
        """
        result = await Database.db.payments.find_one({"_id": payment_id})
        return result
    
    @staticmethod
    async def find_by_checkout_request_id(checkout_request_id: str):
        """
        Find a payment by checkout request ID.
        
        Args:
            checkout_request_id: The checkout request ID to search for
            
        Returns:
            The payment document or None if not found
        """
        result = await Database.db.payments.find_one({"checkout_request_id": checkout_request_id})
        return result
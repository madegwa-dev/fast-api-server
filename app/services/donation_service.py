import logging
from typing import Dict, Any
from app.models.donation import DonationModel
from app.repositories.donation_repository import DonationRepository
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)


class DonationService:
    """Service for handling donation operations."""
    
    def __init__(self):
        self.donation_repository = DonationRepository()
        self.payment_service = PaymentService()
    
    async def initiate_donation(self, amount: int, phone_number: str, customer_name: str, external_reference: str) -> Dict[str, Any]:
        """
        Initiate a donation payment.
        
        Args:
            amount: Donation amount
            phone_number: Customer phone number
            customer_name: Customer name (optional)
            external_reference: Unique reference for the donation
            
        Returns:
            Result of the payment initiation
        """
        try:
            # Create donation record
            donation = DonationModel(
                amount=amount,
                phone_number=phone_number,
                customer_name=customer_name or "Anonymous",
                external_reference=external_reference,
                status="pending"
            )
            
            # Save donation to database
            await self.donation_repository.save(donation)
            logger.info(f"Donation record created: {external_reference}")
            
            # Initiate payment through PayHero
            payment_result = await self.payment_service.initiate_payment_with_reference(
                amount=amount,
                phone_number=phone_number,
                external_reference=external_reference,
                customer_name=customer_name or "Anonymous"
            )
            
            return {
                "status": "success",
                "message": "Donation initiated successfully",
                "payment_details": payment_result
            }
            
        except Exception as e:
            logger.error(f"Error initiating donation: {str(e)}")
            return {
                "status": "error", 
                "message": f"Failed to initiate donation: {str(e)}"
            }
    
    async def process_donation_callback(self, callback_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process donation callback from payment provider.
        
        Args:
            callback_data: Callback data from payment provider
            
        Returns:
            Processing result with donor information
        """
        try:
            response = callback_data.get("response", {})
            external_reference = response.get("ExternalReference", "")
            result_code = response.get("ResultCode", -1)
            
            # Update donation status
            status = "completed" if result_code == 0 else "failed"
            mpesa_receipt_number = response.get("MpesaReceiptNumber", "")
            
            success = await self.donation_repository.update_status(
                external_reference=external_reference,
                status=status,
                mpesa_receipt_number=mpesa_receipt_number
            )
            
            if success and status == "completed":
                # Get the updated donation record
                donation = await self.donation_repository.find_by_external_reference(external_reference)
                
                if donation:
                    donor_info = {
                        "amount": donation["amount"],
                        "customer_name": donation["customer_name"],
                        "phone_number": donation["phone_number"],
                        "created_at": donation["created_at"].isoformat() if donation.get("created_at") else None
                    }
                    
                    return {
                        "status": "success",
                        "message": "Donation completed successfully",
                        "donor": donor_info
                    }
            
            return {
                "status": "error" if status == "failed" else "pending",
                "message": "Donation processing failed" if status == "failed" else "Donation is pending"
            }
            
        except Exception as e:
            logger.error(f"Error processing donation callback: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to process donation: {str(e)}"
            }
    
    async def get_donor_list(self) -> list:
        """
        Get list of all completed donations.
        
        Returns:
            List of donor information
        """
        try:
            donations = await self.donation_repository.get_all_completed_donations()
            
            donor_list = []
            for donation in donations:
                donor_info = {
                    "amount": donation["amount"],
                    "customer_name": donation.get("customer_name", "Anonymous"),
                    "phone_number": donation["phone_number"],
                    "created_at": donation["created_at"].isoformat() if donation.get("created_at") else None
                }
                donor_list.append(donor_info)
            
            return donor_list
            
        except Exception as e:
            logger.error(f"Error getting donor list: {str(e)}")
            return []
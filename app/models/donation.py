from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DonationModel(BaseModel):
    """Model for donation data."""
    amount: int
    phone_number: str
    customer_name: Optional[str] = "Anonymous"
    external_reference: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    checkout_request_id: Optional[str] = None
    mpesa_receipt_number: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert model to dictionary for MongoDB storage."""
        return {
            "amount": self.amount,
            "phone_number": self.phone_number,
            "customer_name": self.customer_name,
            "external_reference": self.external_reference,
            "status": self.status,
            "created_at": self.created_at,
            "checkout_request_id": self.checkout_request_id,
            "mpesa_receipt_number": self.mpesa_receipt_number
        }
    
    @classmethod
    def from_callback(cls, callback_data: dict) -> "DonationModel":
        """Create donation model from payment callback data."""
        response = callback_data.get("response", {})
        return cls(
            amount=response.get("Amount", 0),
            phone_number=response.get("Phone", ""),
            external_reference=response.get("ExternalReference", ""),
            checkout_request_id=response.get("CheckoutRequestID", ""),
            mpesa_receipt_number=response.get("MpesaReceiptNumber", ""),
            status="completed" if response.get("ResultCode") == 0 else "failed"
        )
from typing import Optional
from app.schemas.payment import CallbackDto

class PaymentModel:
    """MongoDB payment document model."""
    
    def __init__(self, 
                 amount: int = None,
                 phone_number: str = None,
                 external_reference: str = None,
                 checkout_request_id: str = None,
                 status: str = None,
                 mpesa_receipt_number: str = None,
                 result_desc: str = None,
                 user_id: Optional[str] = None):
        self.amount = amount
        self.phone_number = phone_number
        self.external_reference = external_reference
        self.checkout_request_id = checkout_request_id
        self.status = status
        self.mpesa_receipt_number = mpesa_receipt_number
        self.result_desc = result_desc
        self.user_id = user_id
    
    @classmethod
    def from_callback(cls, callback: CallbackDto):
        """Create a payment model from callback data."""
        return cls(
            amount=callback.response.Amount,
            phone_number=callback.response.Phone,
            external_reference=callback.response.ExternalReference,
            checkout_request_id=callback.response.CheckoutRequestID,
            status=callback.response.Status,
            mpesa_receipt_number=callback.response.MpesaReceiptNumber,
            result_desc=callback.response.ResultDesc
        )
    
    def to_dict(self):
        """Convert model to dictionary, excluding None values."""
        return {k: v for k, v in self.__dict__.items() if v is not None}
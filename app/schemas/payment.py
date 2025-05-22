from pydantic import BaseModel, Field
from typing import Optional

# Request schemas
class PaymentRequest(BaseModel):
    """Schema for payment request to PayHero API."""
    amount: int
    phone_number: str
    channel_id: int = 2175
    provider: str = "m-pesa"
    external_reference: str = "INV-009"
    customer_name: str = "spongebob"
    callback_url: Optional[str] = None

# Response schemas
class PaymentResponse(BaseModel):
    """Schema for payment response from PayHero API."""
    success: Optional[bool] = None
    status: Optional[str] = None
    reference: Optional[str] = None
    CheckoutRequestID: Optional[str] = None

class InitiatePaymentResponse(BaseModel):
    """API response for initiate payment endpoint."""
    message: str
    details: Optional[PaymentResponse] = None

# Callback schemas
class ResponseDto(BaseModel):
    """Schema for callback response data."""
    Amount: int
    CheckoutRequestID: str
    ExternalReference: str
    MerchantRequestID: str
    MpesaReceiptNumber: str
    Phone: str
    ResultCode: int
    ResultDesc: str
    Status: str

class CallbackDto(BaseModel):
    """Schema for payment callback data."""
    forward_url: str = Field(..., alias="forward_url")
    response: ResponseDto
    status: bool
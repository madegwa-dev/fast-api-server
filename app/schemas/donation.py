from pydantic import BaseModel
from typing import Optional


class DonationRequest(BaseModel):
    """Schema for donation request."""
    amount: int
    phone_number: str
    customer_name: Optional[str] = "Anonymous"
    external_reference: str


class DonationResponse(BaseModel):
    """Schema for donation response."""
    status: str
    message: str
    donor: Optional[dict] = None


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str  # "connect", "donate", "notification"
    data: Optional[dict] = None


class ConnectMessage(BaseModel):
    """Schema for connection message."""
    status: str = "connecting"


class DonationNotification(BaseModel):
    """Schema for donation notification."""
    status: str  # "success", "error", "pending"
    donor: Optional[dict] = None
    message: str
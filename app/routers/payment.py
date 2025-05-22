
from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from app.schemas.payment import CallbackDto, InitiatePaymentResponse
from app.services.payment_service import PaymentService
from app.repositories.payment_repository import PaymentRepository
from app.models.payment import PaymentModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/pay", tags=["payments"])

# Create service instances
payment_service = PaymentService()
payment_repository = PaymentRepository()


# Define request model
class PaymentRequest(BaseModel):
    amount: int
    number: str

@router.post("/initiate", response_model=InitiatePaymentResponse)
async def initiate_payment(payment: PaymentRequest):
    """
    Initiate a payment through PayHero.
    
    Args:
        payment: Payment details including amount and phone number
        
    Returns:
        Payment initiation status
    """
    logger.info(f"Initiating payment: amount={payment.amount}, phoneNumber={payment.number}")
    try:
        result = await payment_service.initiate_payment(payment.amount, payment.number)
        return {"message": "sent", "details": result}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/callback")
async def payment_callback(callback: CallbackDto):
    """
    Handle payment callback from PayHero.
    
    Args:
        callback: Callback data from PayHero
        
    Returns:
        Callback processing status
    """
    logger.info(f"Callback received: {callback}")
    
    # Create payment model from callback
    payment = PaymentModel.from_callback(callback)
    
    # Save payment
    await payment_repository.save(payment)
    logger.info(f"Payment saved: {payment.__dict__}")
    
    # TODO: Update the corresponding user account
    
    return {"status": "success"}

@router.get("/page")
async def pay_page():
    """
    Return payment page info.
    
    Returns:
        Payment page data
    """
    return {"message": "Payment page"}
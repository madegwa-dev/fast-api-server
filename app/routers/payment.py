
from fastapi import APIRouter, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging

from app.repositories.donor_repository import DonorRepository
from app.schemas.payment import CallbackDto, InitiatePaymentResponse
from app.services.payment_service import PaymentService
from app.repositories.payment_repository import PaymentRepository
from app.models.payment import PaymentModel

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/donation", tags=["donation"])

# Create service instances
payment_service = PaymentService()
payment_repository = PaymentRepository()


# Define request model
class PaymentRequest(BaseModel):
    amount: int
    phoneNumber: str
    senderName: str
    externalReference: str


@router.post("/initiate", response_model=InitiatePaymentResponse)
async def initiate_payment(payment: PaymentRequest):
    logger.info(
        f"Initiating payment for {payment.senderName}: amount={payment.amount}, phoneNumber={payment.phoneNumber}, externalReference={payment.externalReference}")
    try:
        result = await payment_service.initiate_payment(payment.amount, payment.phoneNumber, payment.senderName,
                                                        payment.externalReference)
        if result.success:
            # Save donor with minimal details
            donor = {
                "CheckoutRequestID": result.CheckoutRequestID,
                "name": payment.senderName,
            }
            logger.debug(f"Before saving donor: {donor}")
            await DonorRepository.save_donor(donor)
            logger.debug("Donor saved.")

        else:
            logger.error(f"Failed to initiate payment: {result}")

        return {"message": "sent", "success": result.success, "status": result.status}
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error initiating payment: {str(e)}")
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/callback")
async def payment_callback(callback: CallbackDto):
    logger.info(f"Callback received: {callback.model_dump_json()}")

    # Update donor details
    donor_update = {
        "phone": callback.response.Phone,
        "Amount": callback.response.Amount,
        "externalReference": callback.response.ExternalReference,
        "MpesaReceiptNumber": callback.response.MpesaReceiptNumber,
        "Status": callback.response.Status,
        "ResultCode": callback.response.ResultCode,
        "ResultDesc": callback.response.ResultDesc,
    }
    await DonorRepository.update_donor(callback.CheckoutRequestID, donor_update)
    logger.info(f"Donor updated: {donor_update}")

    # Save payment data
    payment = PaymentModel.from_callback(callback)
    await payment_repository.save(payment)
    logger.info(f"Payment saved: {payment.__dict__}")

    return {"status": "success"}


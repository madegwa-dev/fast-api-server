import base64
import logging
import httpx
from fastapi import HTTPException

from app.config import (
    PAYHERO_STKPUSH_URL,
    PAYHERO_USERNAME,
    PAYHERO_PASSWORD,
    PAYHERO_CALLBACK_URL
)
from app.schemas.payment import PaymentRequest, PaymentResponse

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for handling payment operations."""
    
    def __init__(self):
        self.payhero_api_url = PAYHERO_STKPUSH_URL
        self.payhero_username = PAYHERO_USERNAME
        self.payhero_password = PAYHERO_PASSWORD
        self.payhero_callback_url = PAYHERO_CALLBACK_URL

    def generate_basic_auth_token(self) -> str:
        """Generate Basic Auth token for PayHero API."""
        credential = f"{self.payhero_username}:{self.payhero_password}"
        bytes_in_string = base64.b64encode(credential.encode()).decode()
        return f"Basic {bytes_in_string}"

    async def initiate_payment(self, amount: int, phone_number: str) -> PaymentResponse:
        """Initiate a payment through PayHero API."""
        payment_request = PaymentRequest(
            amount=amount,
            phone_number=phone_number,
            channel_id=2175,
            provider="m-pesa",
            external_reference="INV-009",
            customer_name="spongebob",
            callback_url=self.payhero_callback_url
        )

        # Prepare the request JSON
        json_data = {
            "amount": payment_request.amount,
            "phone_number": payment_request.phone_number,
            "channel_id": payment_request.channel_id,
            "provider": payment_request.provider,
            "external_reference": payment_request.external_reference,
            "customer_name": payment_request.customer_name,
            "callback_url": payment_request.callback_url
        }

        # Prepare headers with Basic Auth
        basic_auth_token = self.generate_basic_auth_token()
        headers = {
            "Content-Type": "application/json",
            "Authorization": basic_auth_token,
        }


        payment_response = PaymentResponse()
        
        # Make the HTTP request
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                response = await client.post(
                    self.payhero_api_url,
                    json=json_data,
                    headers=headers
                )
                logger.info(f"failure point 2: {response}")
                
                if response.status_code in [200,201]:
                    response_data = response.json()
                    logger.info(f"Response: {response_data}")
                    
                    # Extract fields from response
                    payment_response.success = response_data.get("success")
                    payment_response.status = response_data.get("status")
                    payment_response.reference = response_data.get("reference")
                    payment_response.CheckoutRequestID = response_data.get("CheckoutRequestID")
                    
                    logger.info(f"Payment response: {payment_response}")
                else:
                    logger.error(f"Request failed with status: {response.status_code}")
                    logger.error(f"Response: {response.text}")
                    raise HTTPException(
                        status_code=response.status_code, 
                        detail=f"Payment service error: {response.text}"
                    )
            except httpx.RequestError as e:
                logger.error(f"Request error: {e.request.url} - {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Payment service connection error: {str(e)}"
                )

            except Exception as e:
                logger.error(f"Error during payment processing: {str(e)}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Payment processing error: {str(e)}"
                )
        
        return payment_response
    
    
    
    
    async def initiate_payment_with_reference(self, amount: int, phone_number: str, external_reference: str, customer_name: str = "Customer") -> dict:
        """
        Initiate payment with custom external reference and customer name.
        """
        try:
            # Create payment request with custom parameters
            payment_request = PaymentRequest(
                amount=amount,
                phone_number=phone_number,
                channel_id=2175,
                provider="m-pesa",
                external_reference=external_reference,
                customer_name=customer_name,
                callback_url=self.payhero_callback_url
            )
            
            
            basic_auth_token = self.generate_basic_auth_token()
            headers = {
                "Content-Type": "application/json",
                "Authorization": basic_auth_token,
            }

            
            # Make API call to PayHero
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.payhero_api_url,
                    json=payment_request.model_dump(exclude_none=True),
                    headers=headers,
                    timeout=60.0
                )
                
            if response.status_code in [200,201]:
                result = response.json()
                logger.info(f"Payment initiated successfully: {result}")
                return result
            else:
                error_msg = f"Payment initiation failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise HTTPException(status_code=response.status_code, detail=error_msg)
                
        except httpx.RequestError as e:
            error_msg = f"Network error during payment initiation: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=503, detail=error_msg)
        except Exception as e:
            error_msg = f"Unexpected error during payment initiation: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.donation import DonationRequest, DonationResponse, WebSocketMessage
from app.services.donation_service import DonationService
from app.websocket.connection_manager import manager
from app.schemas.payment import CallbackDto

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/donation", tags=["donations"])

# Create service instance
donation_service = DonationService()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time donation updates.
    
    Expected message format:
    {
        "destination": "/app/connect" or "/app/donate",
        "body": JSON string with message data
    }
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            destination = message.get("destination", "")
            body = json.loads(message.get("body", "{}"))
            
            if destination == "/app/connect":
                # Handle connection request
                logger.info("Client connected to donation WebSocket")
                
                # Send current donor list to newly connected client
                donor_list = await donation_service.get_donor_list()
                response = {
                    "type": "donor_list",
                    "data": {
                        "donors": donor_list,
                        "status": "connected"
                    }
                }
                await manager.send_personal_message(response, websocket)
                
            elif destination == "/app/donate":
                # Handle donation request
                try:
                    amount = body.get("amount")
                    phone_number = body.get("phone_number")
                    customer_name = body.get("customer_name", "Anonymous")
                    external_reference = body.get("external_reference")
                    
                    if not all([amount, phone_number, external_reference]):
                        await manager.send_error_notification(
                            "Missing required fields: amount, phone_number, external_reference",
                            websocket
                        )
                        continue
                    
                    # Initiate donation
                    result = await donation_service.initiate_donation(
                        amount=amount,
                        phone_number=phone_number,
                        customer_name=customer_name,
                        external_reference=external_reference
                    )
                    
                    if result["status"] == "success":
                        # Send pending status to client
                        response = {
                            "type": "donation_pending",
                            "data": {
                                "message": "Donation initiated. Please complete payment on your phone.",
                                "status": "pending"
                            }
                        }
                        await manager.send_personal_message(response, websocket)
                    else:
                        await manager.send_error_notification(result["message"], websocket)
                        
                except Exception as e:
                    logger.error(f"Error processing donation: {str(e)}")
                    await manager.send_error_notification(f"Error processing donation: {str(e)}", websocket)
            
            else:
                logger.warning(f"Unknown destination: {destination}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


@router.post("/callback")
async def donation_callback(callback: CallbackDto):
    """
    Handle donation callback from PayHero.
    
    Args:
        callback: Callback data from PayHero
        
    Returns:
        Callback processing status
    """
    logger.info(f"Donation callback received: {callback}")
    
    try:
        # Process the donation callback
        result = await donation_service.process_donation_callback(callback.dict())
        
        if result["status"] == "success":
            # Broadcast successful donation to all connected clients
            await manager.send_donation_notification({
                "status": "success",
                "donor": result["donor"],
                "message": "New donation received!"
            })
            
            logger.info(f"Donation completed and broadcasted: {result['donor']}")
        else:
            # Log failed donation
            logger.warning(f"Donation failed or pending: {result}")
        
        return {"status": "success", "message": "Callback processed"}
        
    except Exception as e:
        logger.error(f"Error processing donation callback: {str(e)}")
        return JSONResponse(
            status_code=500, 
            content={"error": f"Callback processing failed: {str(e)}"}
        )


@router.get("/donors")
async def get_donors():
    """
    Get list of all donors.
    
    Returns:
        List of donor information
    """
    try:
        donors = await donation_service.get_donor_list()
        return {
            "status": "success",
            "donors": donors,
            "count": len(donors)
        }
    except Exception as e:
        logger.error(f"Error getting donors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get donors: {str(e)}")


@router.post("/initiate")
async def initiate_donation_api(donation: DonationRequest):
    """
    Alternative API endpoint to initiate donation (for testing).
    
    Args:
        donation: Donation request data
        
    Returns:
        Donation initiation result
    """
    try:
        result = await donation_service.initiate_donation(
            amount=donation.amount,
            phone_number=donation.phone_number,
            customer_name=donation.customer_name,
            external_reference=donation.external_reference
        )
        
        return DonationResponse(
            status=result["status"],
            message=result["message"]
        )
        
    except Exception as e:
        logger.error(f"Error initiating donation via API: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initiate donation: {str(e)}")
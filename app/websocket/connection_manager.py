
import json
import logging
from typing import List, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time donation updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Active connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Active connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast a message to all connected WebSocket clients."""
        if not self.active_connections:
            logger.info("No active connections to broadcast to")
            return
        
        disconnected_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except WebSocketDisconnect:
                logger.info("WebSocket disconnected during broadcast")
                disconnected_connections.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                disconnected_connections.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected_connections:
            self.disconnect(connection)
        
        logger.info(f"Broadcasted message to {len(self.active_connections)} connections")
    
    async def send_donation_notification(self, donation_data: Dict[str, Any]):
        """Send donation notification to all connected clients."""
        notification = {
            "type": "donation_update",
            "data": donation_data
        }
        await self.broadcast(notification)
    
    async def send_error_notification(self, error_message: str, websocket: WebSocket = None):
        """Send error notification to a specific client or all clients."""
        notification = {
            "type": "error",
            "data": {
                "message": error_message,
                "status": "error"
            }
        }
        
        if websocket:
            await self.send_personal_message(notification, websocket)
        else:
            await self.broadcast(notification)


# Global connection manager instance
manager = ConnectionManager()
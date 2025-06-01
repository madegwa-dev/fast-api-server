import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.database import connect_to_mongodb, close_mongodb_connection
from app.routers import payment
from app.config import LOG_LEVEL, FRONTEND_URL
from app.config import PORT

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Payment Service API",
    description="API for processing payments through PayHero",
    version="1.0.0",
)

# Add CORS middleware for WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payment.router)

# Database startup and shutdown events
@app.on_event("startup")
async def startup_db():
    await connect_to_mongodb()

@app.on_event("shutdown")
async def shutdown_db():
    await close_mongodb_connection()

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to Payment Service API"}

# WebSocket Endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            response = {"message": f"Message received: {data}"}
            await websocket.send_text(json.dumps(response))
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
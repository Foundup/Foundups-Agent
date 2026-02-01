#!/usr/bin/env python3
"""
Moltbot Bridge - Webhook Receiver

FastAPI server that receives messages from Moltbot Gateway
and routes them through Foundups Agent intelligence layer.

WSP 73: Digital Twin Architecture Integration
"""

import os
import logging
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("moltbot_bridge")


class MoltbotMessage(BaseModel):
    """Inbound message from Moltbot Gateway."""
    message: str
    sessionKey: str = "default"
    channel: str = "unknown"
    sender: str = "unknown"
    metadata: dict = {}


class FoundupsResponse(BaseModel):
    """Response to send back via Moltbot."""
    text: str
    deliver: bool = True
    channel: Optional[str] = None
    to: Optional[str] = None


# FastAPI app
app = FastAPI(
    title="Moltbot Bridge",
    description="Bridge between Moltbot and Foundups Agent",
    version="0.1.0"
)


def get_webhook_token() -> str:
    """Get webhook token from environment."""
    token = os.environ.get("FOUNDUPS_WEBHOOK_TOKEN")
    if not token:
        logger.warning("FOUNDUPS_WEBHOOK_TOKEN not set - using default (insecure)")
        return "dev-token-change-me"
    return token


def verify_token(authorization: Optional[str], x_moltbot_token: Optional[str]) -> bool:
    """Verify incoming request token."""
    expected = get_webhook_token()
    
    # Check Authorization: Bearer <token>
    if authorization and authorization.startswith("Bearer "):
        if authorization[7:] == expected:
            return True
    
    # Check x-moltbot-token header
    if x_moltbot_token == expected:
        return True
    
    return False


async def process_with_holoindex(message: str, context: dict) -> str:
    """
    Route message through HoloIndex/AI Overseer for intelligent response.
    
    This is the integration point where Foundups intelligence takes over.
    """
    try:
        # Import HoloIndex for semantic search
        # This will be enhanced to use full AI Overseer chain
        from holo_index.cli import search_index
        
        # Search for relevant context
        results = await search_index(message, limit=3)
        
        if results:
            # Format response with context
            context_text = "\n".join([r.get("content", "")[:200] for r in results[:2]])
            response = f"Based on my knowledge:\n\n{context_text}\n\n[Digital Twin Response]"
        else:
            response = f"I received your message via {context.get('channel', 'unknown')}. Processing..."
        
        return response
        
    except ImportError:
        logger.warning("HoloIndex not available - returning placeholder response")
        return f"[Moltbot Bridge] Received: {message[:100]}..."
    except Exception as e:
        logger.error(f"Error processing with HoloIndex: {e}")
        return f"I encountered an issue processing your request. Please try again."


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "moltbot_bridge",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook/moltbot")
async def receive_moltbot_message(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_moltbot_token: Optional[str] = Header(None, alias="x-moltbot-token")
):
    """
    Receive message from Moltbot Gateway.
    
    Expected payload from Moltbot hooks.mappings transform:
    {
        "message": "user's message",
        "sessionKey": "session-id",
        "channel": "whatsapp|telegram|etc",
        "sender": "phone/user-id",
        "metadata": {...}
    }
    """
    # Verify token
    if not verify_token(authorization, x_moltbot_token):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Parse body
    try:
        body = await request.json()
        msg = MoltbotMessage(**body)
    except Exception as e:
        logger.error(f"Failed to parse message: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    
    logger.info(f"Received from {msg.channel}/{msg.sender}: {msg.message[:50]}...")
    
    # Process through Foundups intelligence
    context = {
        "channel": msg.channel,
        "sender": msg.sender,
        "sessionKey": msg.sessionKey,
        "metadata": msg.metadata
    }
    
    response_text = await process_with_holoindex(msg.message, context)
    
    # Return response for Moltbot to deliver
    response = FoundupsResponse(
        text=response_text,
        deliver=True,
        channel=msg.channel,  # Reply on same channel
        to=msg.sender         # Reply to sender
    )
    
    return JSONResponse(
        status_code=200,
        content=response.model_dump()
    )


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.environ.get("MOLTBOT_BRIDGE_PORT", 18800))
    logger.info(f"Starting Moltbot Bridge on port {port}")
    
    uvicorn.run(app, host="127.0.0.1", port=port)

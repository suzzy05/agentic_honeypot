from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
import requests
import logging
import json
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from detector import calculate_scam_score, detect_scam
from extractor import extract_intelligence
from agent import agent_reply
from session_store import get_session, update_session, get_session_summary, mark_completed
from config import API_KEY, GUVI_CALLBACK

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Agentic Honeypot API",
    description="AI-powered scam detection and intelligence extraction system",
    version="2.0.0"
)

# Pydantic models for request validation
class MessageModel(BaseModel):
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Epoch timestamp in milliseconds")

class MetadataModel(BaseModel):
    channel: Optional[str] = Field(None, description="Channel: SMS, WhatsApp, Email, Chat")
    language: Optional[str] = Field(None, description="Message language")
    locale: Optional[str] = Field(None, description="Country or region code")

class HoneypotRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: MessageModel = Field(..., description="Current message")
    conversationHistory: Optional[list] = Field(default_factory=list, description="Previous messages")
    metadata: Optional[MetadataModel] = Field(None, description="Message metadata")

class HoneypotResponse(BaseModel):
    status: str = Field(..., description="Response status")
    reply: Optional[str] = Field(None, description="Agent reply message")
    scamDetected: Optional[bool] = Field(None, description="Whether scam was detected")
    confidence: Optional[float] = Field(None, description="Scam detection confidence")

@app.get("/")
async def root():
    """Root endpoint - returns API info"""
    return {
        "status": "healthy",
        "service": "Agentic Honeypot API",
        "version": "2.0.0",
        "timestamp": int(time.time() * 1000),
        "endpoints": {
            "honeypot": "/honeypot/message",
            "stats": "/stats"
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error responses"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "details": str(exc) if app.debug else "Contact administrator"
        }
    )


@app.post("/honeypot/message", response_model=HoneypotResponse)
async def honeypot_message(
    request: HoneypotRequest,
    x_api_key: str = Header(None, description="API key for authentication")
):
    """
    Main honeypot endpoint for processing scam messages
    Handles conversation history and multi-turn conversations
    """
    # Authentication
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    try:
        session_id = request.sessionId
        message = request.message.dict()
        text = message["text"]
        conversation_history = request.conversationHistory or []
        
        logger.info(f"Processing message for session {session_id}: {text[:100]}...")
        
        # Get or create session
        session = get_session(session_id)
        
        # Build complete message history from conversationHistory + current message
        complete_history = conversation_history.copy()
        complete_history.append(message)
        
        # Update session with complete conversation history
        session["conversationHistory"] = complete_history
        session["messages"] = complete_history
        
        # Perform scam detection with confidence scoring
        is_scam, keywords, confidence = calculate_scam_score(text)
        
        # Update session with message and analysis
        update_session(session_id, message, is_scam, confidence)
        
        if is_scam:
            logger.info(f"Scam detected in session {session_id} with confidence {confidence:.2f}")
            
            # Extract intelligence from the message
            session["intelligence"] = extract_intelligence(text, session["intelligence"])
            
            # Add detected keywords to intelligence
            session["intelligence"]["suspiciousKeywords"].extend(
                [kw for kw in keywords if kw not in session["intelligence"]["suspiciousKeywords"]]
            )
            
            # Generate agent response based on complete conversation history
            reply = agent_reply(complete_history)
            
            # Add agent reply to conversation history
            agent_message = {
                "sender": "user",
                "text": reply,
                "timestamp": int(time.time() * 1000)
            }
            session["messages"].append(agent_message)
            session["conversationHistory"].append(agent_message)
            
            # Check if we should send final callback
            # Send after sufficient engagement (8+ messages) or high confidence
            should_callback = (
                len(session["messages"]) >= 8 or 
                (confidence >= 0.8 and len(session["messages"]) >= 4)
            ) and not session["completed"]
            
            if should_callback:
                logger.info(f"Sending final callback for session {session_id}")
                await send_final_callback(session_id)
                mark_completed(session_id)
            
            return HoneypotResponse(
                status="success",
                reply=reply,
                scamDetected=True,
                confidence=confidence
            )
        
        else:
            # No scam detected - minimal response
            logger.info(f"No scam detected in session {session_id}")
            return HoneypotResponse(
                status="success",
                reply="Okay.",
                scamDetected=False,
                confidence=confidence
            )
    
    except Exception as e:
        logger.error(f"Error processing message for session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal processing error")

async def send_final_callback(session_id: str):
    """
    Send final results to GUVI evaluation endpoint
    """
    try:
        session_summary = get_session_summary(session_id)
        
        callback_payload = {
            "sessionId": session_id,
            "scamDetected": session_summary["scamDetected"],
            "totalMessagesExchanged": session_summary["totalMessagesExchanged"],
            "extractedIntelligence": session_summary["extractedIntelligence"],
            "agentNotes": session_summary["agentNotes"]
        }
        
        logger.info(f"Sending callback payload: {json.dumps(callback_payload, indent=2)}")
        
        response = requests.post(
            GUVI_CALLBACK,
            json=callback_payload,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            logger.info(f"Successfully sent callback for session {session_id}")
        else:
            logger.error(f"Failed to send callback for session {session_id}: {response.status_code} - {response.text}")
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error sending callback for session {session_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error sending callback for session {session_id}: {str(e)}")

@app.get("/stats")
async def get_stats(x_api_key: str = Header(None)):
    """Get system statistics (authenticated endpoint)"""
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    from session_store import session_manager
    
    total_sessions = len(session_manager.sessions)
    active_sessions = len([
        s for s in session_manager.sessions.values() 
        if not s["completed"]
    ])
    scam_sessions = len([
        s for s in session_manager.sessions.values() 
        if s["scamDetected"]
    ])
    
    return {
        "totalSessions": total_sessions,
        "activeSessions": active_sessions,
        "scamSessions": scam_sessions,
        "detectionRate": scam_sessions / max(total_sessions, 1) * 100,
        "timestamp": int(time.time() * 1000)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

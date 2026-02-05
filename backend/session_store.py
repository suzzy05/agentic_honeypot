import json
import time
from typing import Dict, Any, List
from datetime import datetime, timedelta

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = 3600  # 1 hour in seconds
        
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get or create a session with enhanced tracking
        """
        current_time = time.time()
        
        # Clean up expired sessions
        self._cleanup_expired_sessions(current_time)
        
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "sessionId": session_id,
                "scamDetected": False,
                "scamConfidence": 0.0,
                "messages": [],
                "conversationHistory": [],
                "intelligence": {
                    "bankAccounts": [],
                    "upiIds": [],
                    "phishingLinks": [],
                    "phoneNumbers": [],
                    "suspiciousKeywords": []
                },
                "agentPersona": None,
                "conversationStage": 0,
                "startTime": current_time,
                "lastActivity": current_time,
                "completed": False,
                "totalMessagesExchanged": 0,
                "scammerMessagesCount": 0,
                "agentMessagesCount": 0,
                "engagementScore": 0.0,
                "extractedPatterns": [],
                "riskLevel": "low"
            }
        
        # Update last activity
        self.sessions[session_id]["lastActivity"] = current_time
        
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, message: Dict[str, Any], 
                      scam_detected: bool = False, confidence: float = 0.0) -> None:
        """
        Update session with new message and analysis
        """
        session = self.get_session(session_id)
        
        # Add message to history
        session["messages"].append(message)
        session["conversationHistory"].append({
            "sender": message.get("sender", "unknown"),
            "text": message.get("text", ""),
            "timestamp": message.get("timestamp", time.time() * 1000)
        })
        
        # Update counters
        session["totalMessagesExchanged"] = len(session["messages"])
        if message.get("sender") == "scammer":
            session["scammerMessagesCount"] += 1
        elif message.get("sender") == "user":
            session["agentMessagesCount"] += 1
        
        # Update scam detection status
        if scam_detected:
            session["scamDetected"] = True
            session["scamConfidence"] = max(session["scamConfidence"], confidence)
            session["riskLevel"] = self._calculate_risk_level(confidence)
        
        # Update conversation stage
        session["conversationStage"] = min(session["totalMessagesExchanged"] // 2, 5)
        
        # Calculate engagement score
        session["engagementScore"] = self._calculate_engagement_score(session)
    
    def _calculate_risk_level(self, confidence: float) -> str:
        """Calculate risk level based on confidence score"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"
    
    def _calculate_engagement_score(self, session: Dict[str, Any]) -> float:
        """Calculate engagement score based on conversation metrics"""
        base_score = min(session["totalMessagesExchanged"] * 0.1, 1.0)
        scammer_ratio = session["scammerMessagesCount"] / max(session["totalMessagesExchanged"], 1)
        intelligence_score = min(len([k for k in session["intelligence"].values() if k]) * 0.2, 1.0)
        
        return (base_score + scammer_ratio + intelligence_score) / 3
    
    def _cleanup_expired_sessions(self, current_time: float) -> None:
        """Remove expired sessions to prevent memory leaks"""
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session["lastActivity"] > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the session for final callback"""
        session = self.get_session(session_id)
        
        return {
            "sessionId": session_id,
            "scamDetected": session["scamDetected"],
            "totalMessagesExchanged": session["totalMessagesExchanged"],
            "scamConfidence": session["scamConfidence"],
            "riskLevel": session["riskLevel"],
            "engagementScore": session["engagementScore"],
            "extractedIntelligence": session["intelligence"],
            "conversationDuration": session["lastActivity"] - session["startTime"],
            "agentNotes": self._generate_agent_notes(session)
        }
    
    def _generate_agent_notes(self, session: Dict[str, Any]) -> str:
        """Generate intelligent notes about the scammer behavior"""
        notes = []
        
        if session["scamDetected"]:
            notes.append(f"Scam detected with {session['scamConfidence']:.2f} confidence")
        
        if session["intelligence"]["suspiciousKeywords"]:
            keywords = ", ".join(session["intelligence"]["suspiciousKeywords"][:5])
            notes.append(f"Used keywords: {keywords}")
        
        if session["intelligence"]["upiIds"]:
            notes.append(f"Requested UPI payments")
        
        if session["intelligence"]["phishingLinks"]:
            notes.append(f"Shared suspicious links")
        
        if session["intelligence"]["phoneNumbers"]:
            notes.append(f"Provided contact numbers")
        
        if session["engagementScore"] > 0.7:
            notes.append("High engagement - persistent scammer")
        elif session["engagementScore"] < 0.3:
            notes.append("Low engagement - quick exit")
        
        return "; ".join(notes) if notes else "Suspicious activity detected"
    
    def mark_completed(self, session_id: str) -> None:
        """Mark session as completed"""
        if session_id in self.sessions:
            self.sessions[session_id]["completed"] = True

# Global session manager instance
session_manager = SessionManager()

def get_session(session_id: str) -> Dict[str, Any]:
    """Backward compatibility function"""
    return session_manager.get_session(session_id)

def update_session(session_id: str, message: Dict[str, Any], 
                  scam_detected: bool = False, confidence: float = 0.0) -> None:
    """Update session with new message"""
    session_manager.update_session(session_id, message, scam_detected, confidence)

def get_session_summary(session_id: str) -> Dict[str, Any]:
    """Get session summary for callback"""
    return session_manager.get_session_summary(session_id)

def mark_completed(session_id: str) -> None:
    """Mark session as completed"""
    session_manager.mark_completed(session_id)

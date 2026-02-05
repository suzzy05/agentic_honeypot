import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import time

from main import app
from detector import calculate_scam_score, detect_scam
from extractor import extract_intelligence
from agent import agent_reply
from session_store import get_session, update_session, get_session_summary

client = TestClient(app)

class TestScamDetection:
    """Test scam detection functionality"""
    
    def test_obvious_scam_detection(self):
        """Test detection of obvious scam messages"""
        scam_messages = [
            "Your bank account will be blocked today. Verify immediately.",
            "URGENT: Your account has been suspended. Click here to verify.",
            "Congratulations! You won $1000000. Send your bank details.",
            "Your KYC will expire today. Update immediately or account blocked."
        ]
        
        for message in scam_messages:
            is_scam, keywords, confidence = calculate_scam_score(message)
            assert is_scam, f"Failed to detect scam in: {message}"
            assert confidence >= 0.4, f"Low confidence for obvious scam: {confidence}"
            assert len(keywords) > 0, f"No keywords detected for: {message}"
    
    def test_legitimate_message_detection(self):
        """Test that legitimate messages are not flagged as scams"""
        legitimate_messages = [
            "Hi, how are you doing today?",
            "Meeting scheduled for tomorrow at 3 PM.",
            "Thanks for your help with the project.",
            "Can you send me the report when you get a chance?"
        ]
        
        for message in legitimate_messages:
            is_scam, keywords, confidence = calculate_scam_score(message)
            assert not is_scam, f"False positive for legitimate message: {message}"
            assert confidence < 0.4, f"High confidence for legitimate message: {confidence}"
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        edge_cases = [
            "",  # Empty message
            "bank",  # Single keyword
            "URGENT URGENT URGENT",  # Repeated urgency
            "Click here http://example.com verify account",  # Mixed patterns
        ]
        
        for message in edge_cases:
            is_scam, keywords, confidence = calculate_scam_score(message)
            # Should handle gracefully without errors
            assert isinstance(is_scam, bool)
            assert isinstance(keywords, list)
            assert isinstance(confidence, float)
            assert 0 <= confidence <= 1

class TestIntelligenceExtraction:
    """Test intelligence extraction functionality"""
    
    def test_upi_extraction(self):
        """Test UPI ID extraction"""
        text = "Please send money to user@paytm and scammmer@phonepe"
        intel = {"upiIds": [], "phoneNumbers": [], "phishingLinks": [], "bankAccounts": [], "suspiciousKeywords": []}
        
        result = extract_intelligence(text, intel)
        assert len(result["upiIds"]) >= 2
        assert "user@paytm" in result["upiIds"]
        assert "scammmer@phonepe" in result["upiIds"]
    
    def test_phone_extraction(self):
        """Test phone number extraction"""
        text = "Call me at +919876543210 or 9876543210 for details"
        intel = {"upiIds": [], "phoneNumbers": [], "phishingLinks": [], "bankAccounts": [], "suspiciousKeywords": []}
        
        result = extract_intelligence(text, intel)
        assert len(result["phoneNumbers"]) >= 2
        assert "+919876543210" in result["phoneNumbers"]
    
    def test_url_extraction(self):
        """Test URL extraction"""
        text = "Visit https://fake-bank.com/verify or www.scam-site.com now"
        intel = {"upiIds": [], "phoneNumbers": [], "phishingLinks": [], "bankAccounts": [], "suspiciousKeywords": []}
        
        result = extract_intelligence(text, intel)
        assert len(result["phishingLinks"]) >= 2
        assert "https://fake-bank.com/verify" in result["phishingLinks"]
    
    def test_bank_account_extraction(self):
        """Test bank account extraction"""
        text = "Your account 1234567890123456 or SBIN0001234 needs verification"
        intel = {"upiIds": [], "phoneNumbers": [], "phishingLinks": [], "bankAccounts": [], "suspiciousKeywords": []}
        
        result = extract_intelligence(text, intel)
        assert len(result["bankAccounts"]) >= 1

class TestAgentResponses:
    """Test AI agent response generation"""
    
    def test_empty_history_response(self):
        """Test agent response with empty conversation history"""
        response = agent_reply([])
        assert isinstance(response, str)
        assert len(response) > 0
    
    def test_contextual_response(self):
        """Test agent response based on conversation context"""
        history = [
            {"sender": "scammer", "text": "Your account will be blocked", "timestamp": 1234567890}
        ]
        response = agent_reply(history)
        assert isinstance(response, str)
        assert len(response) > 0
        # Should be a relevant question or concern
        assert any(word in response.lower() for word in ["why", "what", "how", "account", "blocked"])
    
    def test_multiple_turns(self):
        """Test agent maintains context across multiple turns"""
        history = [
            {"sender": "scammer", "text": "Your account will be blocked", "timestamp": 1234567890},
            {"sender": "user", "text": "Why will my account be blocked?", "timestamp": 1234567891},
            {"sender": "scammer", "text": "Verify your UPI ID immediately", "timestamp": 1234567892}
        ]
        response = agent_reply(history)
        assert isinstance(response, str)
        assert len(response) > 0

class TestSessionManagement:
    """Test session management functionality"""
    
    def test_session_creation(self):
        """Test new session creation"""
        session_id = "test-session-123"
        session = get_session(session_id)
        
        assert session["sessionId"] == session_id
        assert session["scamDetected"] == False
        assert session["totalMessagesExchanged"] == 0
        assert isinstance(session["intelligence"], dict)
    
    def test_session_update(self):
        """Test session update with message"""
        session_id = "test-session-456"
        message = {"sender": "scammer", "text": "Urgent verification needed", "timestamp": 1234567890}
        
        update_session(session_id, message, True, 0.8)
        session = get_session(session_id)
        
        assert session["scamDetected"] == True
        assert session["scamConfidence"] == 0.8
        assert session["totalMessagesExchanged"] == 1
    
    def test_session_summary(self):
        """Test session summary generation"""
        session_id = "test-session-789"
        message = {"sender": "scammer", "text": "Send money to scammer@upi", "timestamp": 1234567890}
        
        update_session(session_id, message, True, 0.9)
        summary = get_session_summary(session_id)
        
        assert summary["sessionId"] == session_id
        assert summary["scamDetected"] == True
        assert summary["totalMessagesExchanged"] == 1
        assert "agentNotes" in summary

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_detailed_health_check(self):
        """Test detailed health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "endpoints" in data
    
    def test_unauthorized_access(self):
        """Test API without authentication"""
        payload = {
            "sessionId": "test-session",
            "message": {
                "sender": "scammer",
                "text": "Your account is blocked",
                "timestamp": int(time.time() * 1000)
            }
        }
        
        response = client.post("/honeypot/message", json=payload)
        assert response.status_code == 401
    
    @patch('main.send_final_callback')
    def test_authorized_scam_message(self, mock_callback):
        """Test API with authenticated scam message"""
        payload = {
            "sessionId": "test-session-scam",
            "message": {
                "sender": "scammer",
                "text": "URGENT: Your account will be blocked. Verify immediately.",
                "timestamp": int(time.time() * 1000)
            }
        }
        
        headers = {"x-api-key": "SECRET123"}
        response = client.post("/honeypot/message", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["scamDetected"] == True
        assert "reply" in data
        assert data["confidence"] > 0.4
    
    def test_legitimate_message_processing(self):
        """Test API with legitimate message"""
        payload = {
            "sessionId": "test-session-legit",
            "message": {
                "sender": "scammer",
                "text": "Hi, how are you doing today?",
                "timestamp": int(time.time() * 1000)
            }
        }
        
        headers = {"x-api-key": "SECRET123"}
        response = client.post("/honeypot/message", json=payload, headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["scamDetected"] == False
        assert data["reply"] == "Okay."

class TestIntegration:
    """Integration tests for the complete system"""
    
    @patch('main.send_final_callback')
    def test_full_conversation_flow(self, mock_callback):
        """Test complete conversation flow from start to callback"""
        session_id = "integration-test-session"
        headers = {"x-api-key": "SECRET123"}
        
        # First message - scam detection
        payload1 = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Your bank account will be blocked today. Verify immediately.",
                "timestamp": int(time.time() * 1000)
            }
        }
        
        response1 = client.post("/honeypot/message", json=payload1, headers=headers)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["scamDetected"] == True
        assert data1["reply"] != "Okay."
        
        # Second message - continue conversation
        payload2 = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": "Share your UPI ID to avoid account suspension.",
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": [
                payload1["message"],
                {
                    "sender": "user",
                    "text": data1["reply"],
                    "timestamp": int(time.time() * 1000)
                }
            ]
        }
        
        response2 = client.post("/honeypot/message", json=payload2, headers=headers)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["scamDetected"] == True
        
        # Verify session state
        session = get_session(session_id)
        assert session["scamDetected"] == True
        assert session["totalMessagesExchanged"] >= 2
        assert len(session["intelligence"]["suspiciousKeywords"]) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

import random
from typing import List, Dict, Any
import re

class ConversationalAgent:
    def __init__(self):
        self.persona_traits = [
            "concerned_citizen", "curious_user", "skeptical_person",
            "trusting_individual", "confused_elder", "busy_professional"
        ]
        self.current_persona = random.choice(self.persona_traits)
        
    def generate_contextual_response(self, history: List[Dict[str, Any]]) -> str:
        """
        Generate human-like responses based on conversation context
        """
        if not history:
            return self._get_initial_response()
        
        last_message = history[-1]["text"].lower()
        message_count = len(history)
        
        # Analyze conversation context
        context = self._analyze_context(history)
        
        # Generate response based on persona and context
        response = self._craft_response(context, last_message, message_count)
        
        return response
    
    def _analyze_context(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze conversation context for better responses"""
        recent_messages = [msg["text"].lower() for msg in history[-3:]]
        
        context = {
            "mentions_bank": any("bank" in msg for msg in recent_messages),
            "mentions_upi": any("upi" in msg for msg in recent_messages),
            "mentions_kyc": any("kyc" in msg for msg in recent_messages),
            "mentions_urgent": any(urgent in msg for msg in recent_messages 
                                 for urgent in ["urgent", "immediate", "now"]),
            "mentions_link": any("link" in msg or "click" in msg for msg in recent_messages),
            "mentions_money": any(word in msg for msg in recent_messages 
                               for word in ["money", "payment", "deposit", "transfer"]),
            "conversation_stage": min(len(history) // 2, 4)  # 0-4 stages
        }
        
        return context
    
    def _craft_response(self, context: Dict[str, Any], last_message: str, message_count: int) -> str:
        """Craft response based on context and persona"""
        
        # Stage-based responses
        if context["conversation_stage"] == 0:
            return self._get_initial_stage_response(context)
        elif context["conversation_stage"] == 1:
            return self._get_engagement_response(context)
        elif context["conversation_stage"] == 2:
            return self._get_information_seeking_response(context)
        elif context["conversation_stage"] == 3:
            return self._get_verification_response(context)
        else:
            return self._get_advanced_response(context)
    
    def _get_initial_stage_response(self, context: Dict[str, Any]) -> str:
        """Initial stage responses - show concern/curiosity"""
        responses = [
            "Oh no, what happened? Why is there an issue with my account?",
            "I'm confused, which account are you talking about?",
            "Is this serious? Should I be worried?",
            "Can you tell me more about what's going on?",
            "I don't understand, what seems to be the problem?"
        ]
        
        if context["mentions_bank"]:
            responses.extend([
                "Which bank is this regarding? I have accounts in multiple banks.",
                "Is this about my SBI account or HDFC account?"
            ])
        
        return random.choice(responses)
    
    def _get_engagement_response(self, context: Dict[str, Any]) -> str:
        """Engagement stage - show interest and ask for details"""
        responses = [
            "That sounds concerning. What do I need to do exactly?",
            "I see. Can you walk me through the process step by step?",
            "Okay, I understand. What's the first thing I should do?",
            "Thank you for letting me know. How can I resolve this quickly?"
        ]
        
        if context["mentions_urgent"]:
            responses.extend([
                "This seems urgent. What happens if I don't act immediately?",
                "I'm a bit scared now. Please help me understand this better."
            ])
        
        return random.choice(responses)
    
    def _get_information_seeking_response(self, context: Dict[str, Any]) -> str:
        """Information seeking - ask for specific details"""
        responses = [
            "Can you provide more details about the verification process?",
            "What information do you need from me exactly?",
            "Is there a website or official portal I should visit?",
            "How can I confirm this is legitimate?"
        ]
        
        if context["mentions_upi"]:
            responses.extend([
                "Which UPI ID should I use? I have multiple payment apps.",
                "Should I use my Google Pay UPI or PhonePe UPI?"
            ])
        
        if context["mentions_link"]:
            responses.extend([
                "Can you send me the official link? I want to make sure it's authentic.",
                "Is there a government website I should check?"
            ])
        
        return random.choice(responses)
    
    def _get_verification_response(self, context: Dict[str, Any]) -> str:
        """Verification stage - ask for confirmation"""
        responses = [
            "I want to make sure this is legitimate. Can you verify your identity?",
            "How can I confirm you're actually from the bank/organization?",
            "Is there a customer service number I can call to verify this?",
            "Can you provide any reference number or case ID for this issue?"
        ]
        
        if context["mentions_money"]:
            responses.extend([
                "Why do I need to make a payment to resolve this?",
                "Is there any fee involved? How much exactly?"
            ])
        
        return random.choice(responses)
    
    def _get_advanced_response(self, context: Dict[str, Any]) -> str:
        """Advanced stage - more sophisticated engagement"""
        responses = [
            "I've been getting similar messages lately. How do I know this isn't a scam?",
            "My friend warned me about fraud attempts. Can you prove this is genuine?",
            "I think I should contact my bank directly to confirm this.",
            "Can you share your employee ID or official identification?"
        ]
        
        if context["mentions_kyc"]:
            responses.extend([
                "But I already completed my KYC last year. Why do I need to do it again?",
                "Should I visit my bank branch for KYC verification instead?"
            ])
        
        return random.choice(responses)
    
    def _get_initial_response(self) -> str:
        """Response for very first message"""
        initial_responses = [
            "Hello? Who is this?",
            "I'm not sure I understand. What is this about?",
            "Can you tell me who you are and why you're contacting me?",
            "Sorry, I think you might have the wrong person."
        ]
        return random.choice(initial_responses)

# Global agent instance
agent = ConversationalAgent()

def agent_reply(history: List[Dict[str, Any]]) -> str:
    """
    Main function to generate agent response
    Maintains backward compatibility with existing code
    """
    return agent.generate_contextual_response(history)

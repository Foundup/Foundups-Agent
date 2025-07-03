"""
Conversation Manager - Natural Language Processing for 0102

Handles text-based interaction, intent parsing, and response generation.
Future versions will include voice interface capabilities.
"""

import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Recognized user intents"""
    CREATE_MEETING = "create_meeting"
    CHECK_STATUS = "check_status"
    CHECK_AVAILABILITY = "check_availability"
    ACCEPT_MEETING = "accept_meeting"
    DECLINE_MEETING = "decline_meeting"
    UPDATE_PREFERENCES = "update_preferences"
    GENERAL_QUESTION = "general_question"
    GREETING = "greeting"
    UNKNOWN = "unknown"


@dataclass
class ParsedIntent:
    """Result of intent parsing"""
    intent: Intent
    confidence: float
    entities: Dict[str, Any]
    original_text: str


class ConversationManager:
    """
    Manages natural language interaction with users.
    
    PoC Implementation:
    - Simple keyword-based intent recognition
    - Basic entity extraction
    - Template-based response generation
    
    Future Enhancement:
    - Advanced NLP with transformers
    - Voice interface (STT/TTS)
    - Context-aware conversation
    """
    
    def __init__(self, personality_mode):
        self.personality_mode = personality_mode
        self.intent_patterns = self._initialize_intent_patterns()
        
        logger.info(f"ConversationManager initialized with {personality_mode} personality")
    
    def _initialize_intent_patterns(self) -> Dict[Intent, List[str]]:
        """Define keyword patterns for intent recognition"""
        return {
            Intent.CREATE_MEETING: [
                "meet", "meeting", "schedule", "book", "arrange", "plan",
                "need to talk", "discuss", "call", "video call"
            ],
            Intent.CHECK_STATUS: [
                "status", "what's up", "update", "summary", "overview",
                "how many", "pending", "active"
            ],
            Intent.CHECK_AVAILABILITY: [
                "available", "availability", "online", "free", "busy",
                "status of", "is online", "can meet"
            ],
            Intent.ACCEPT_MEETING: [
                "yes", "accept", "agree", "ok", "sure", "let's do it",
                "start meeting", "launch", "begin"
            ],
            Intent.DECLINE_MEETING: [
                "no", "decline", "reject", "not now", "later", "cancel",
                "can't", "unavailable"
            ],
            Intent.UPDATE_PREFERENCES: [
                "prefer", "preference", "setting", "configure", "change",
                "update", "modify", "set"
            ],
            Intent.GREETING: [
                "hello", "hi", "hey", "good morning", "good afternoon",
                "greetings", "what's up"
            ]
        }
    
    async def parse_user_intent(self, input_text: str) -> ParsedIntent:
        """
        Parse user input to identify intent and extract entities
        
        PoC implementation uses simple keyword matching.
        Future versions will use advanced NLP models.
        """
        input_lower = input_text.lower()
        
        # Check each intent pattern
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in input_lower)
            if score > 0:
                intent_scores[intent] = score / len(keywords)
        
        # Determine best intent
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1])
            intent = best_intent[0]
            confidence = min(best_intent[1] * 2, 1.0)  # Scale confidence
        else:
            intent = Intent.UNKNOWN
            confidence = 0.0
        
        # Extract entities based on intent
        entities = await self._extract_entities(input_text, intent)
        
        return ParsedIntent(
            intent=intent,
            confidence=confidence,
            entities=entities,
            original_text=input_text
        )
    
    async def _extract_entities(self, input_text: str, intent: Intent) -> Dict[str, Any]:
        """
        Extract relevant entities from user input based on identified intent
        
        PoC implementation uses simple pattern matching.
        Future versions will use NER models.
        """
        entities = {}
        input_lower = input_text.lower()
        
        if intent == Intent.CREATE_MEETING:
            # Look for person names (simple approach)
            words = input_text.split()
            for i, word in enumerate(words):
                if word.lower() in ["with", "to", "and"] and i + 1 < len(words):
                    potential_name = words[i + 1].strip(".,!?")
                    if potential_name.isalpha() and potential_name[0].isupper():
                        entities["recipient"] = potential_name
                        break
            
            # Look for meeting purpose indicators
            purpose_indicators = ["about", "regarding", "for", "to discuss"]
            for indicator in purpose_indicators:
                if indicator in input_lower:
                    idx = input_lower.find(indicator)
                    remaining = input_text[idx + len(indicator):].strip()
                    if remaining:
                        entities["purpose"] = remaining
                        break
            
            # Look for duration mentions
            if "minute" in input_lower:
                words = input_lower.split()
                for i, word in enumerate(words):
                    if word.isdigit() and i + 1 < len(words) and "minute" in words[i + 1]:
                        entities["duration"] = int(word)
                        break
            
            # Look for priority indicators
            if any(word in input_lower for word in ["urgent", "asap", "important", "critical"]):
                entities["priority"] = "HIGH"
            elif any(word in input_lower for word in ["low", "when convenient", "no rush"]):
                entities["priority"] = "LOW"
            else:
                entities["priority"] = "MEDIUM"
        
        elif intent == Intent.CHECK_AVAILABILITY:
            # Look for target person
            words = input_text.split()
            for word in words:
                if word.strip(".,!?").isalpha() and word[0].isupper():
                    entities["target_user"] = word.strip(".,!?")
                    break
        
        return entities
    
    async def generate_response(self, parsed_intent: ParsedIntent) -> str:
        """
        Generate appropriate response based on parsed intent and personality mode
        
        PoC implementation uses template-based responses.
        Future versions will use language models.
        """
        responses = self._get_response_templates()
        
        if parsed_intent.intent in responses:
            templates = responses[parsed_intent.intent]
            
            # Select template based on personality mode
            if self.personality_mode.value in templates:
                template = templates[self.personality_mode.value]
            else:
                template = templates["friendly"]  # Default fallback
            
            # Simple template variable replacement
            response = template
            for entity_key, entity_value in parsed_intent.entities.items():
                placeholder = f"{{{entity_key}}}"
                if placeholder in response:
                    response = response.replace(placeholder, str(entity_value))
            
            return response
        
        # Fallback response
        return "I understand you're trying to communicate with me, but I'm not sure how to help with that specific request."
    
    def _get_response_templates(self) -> Dict:
        """Response templates organized by intent and personality mode"""
        return {
            Intent.CREATE_MEETING: {
                "professional": "I will create a meeting request for you. Please provide the recipient and purpose.",
                "friendly": "Sure! I'd love to help you set up that meeting. Who would you like to meet with?",
                "concise": "Creating meeting request. Need recipient and purpose.",
                "detailed": "I'm processing your meeting request. To create an effective meeting intent, I'll need to capture the recipient, purpose, expected outcome, and priority level.",
                "humorous": "Ah, the ancient art of getting humans in the same place at the same time! Let's make it happen."
            },
            Intent.CHECK_STATUS: {
                "professional": "Here is your current meeting coordination status.",
                "friendly": "Let me check what's happening with your meetings!",
                "concise": "Status update:",
                "detailed": "I'll provide a comprehensive overview of your meeting coordination activities.",
                "humorous": "Time for the meeting status report - let's see what chaos we're orchestrating!"
            },
            Intent.CHECK_AVAILABILITY: {
                "professional": "I will check availability status for the requested person.",
                "friendly": "Let me see who's available right now!",
                "concise": "Checking availability.",
                "detailed": "I'm querying the presence aggregation system to determine current availability across all connected platforms.",
                "humorous": "Playing detective to find out who's actually at their computer!"
            },
            Intent.GREETING: {
                "professional": "Good day. I am here to assist with your meeting coordination needs.",
                "friendly": "Hey there! Ready to orchestrate some amazing meetings?",
                "concise": "Hello. How can I help?",
                "detailed": "Greetings! I'm 0102, your meeting orchestration companion. I can help you create meeting intents, monitor availability, and coordinate seamless meeting experiences.",
                "humorous": "Well hello there, fellow human! Ready to turn scheduling chaos into orchestrated brilliance?"
            }
        }


# Demo function
async def demo_conversation_manager():
    """Demonstrate conversation manager capabilities"""
    print("=== ConversationManager Demo ===")
    
    cm = ConversationManager("friendly")
    
    test_inputs = [
        "I need to meet with Alice about the project roadmap",
        "What's my current status?",
        "Is Bob available?",
        "Hello there!",
        "This is some random text that doesn't match anything"
    ]
    
    for input_text in test_inputs:
        print(f"\nUser: {input_text}")
        parsed = await cm.parse_user_intent(input_text)
        print(f"Intent: {parsed.intent.value} (confidence: {parsed.confidence:.2f})")
        print(f"Entities: {parsed.entities}")
        
        response = await cm.generate_response(parsed)
        print(f"Response: {response}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo_conversation_manager()) 
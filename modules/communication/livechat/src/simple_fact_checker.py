"""
Simple Fact Checker for MAGADOOM
WSP-Compliant: Works without external LLM dependencies
"""

import logging
import random
import os
from typing import Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SimpleFactChecker:
    """Simple fact-checking without LLM dependencies"""
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.fact_check_responses = {
            "lies_detected": [
                "🚨 FACT CHECK: Multiple falsehoods detected! Truth rating: 0/10",
                "❌ FALSE: This user's claims have been thoroughly debunked",
                "🤥 PANTS ON FIRE! Not a single true statement found",
                "📊 Analysis complete: 100% bullshit detected",
                "⚠️ WARNING: Extreme misinformation hazard ahead"
            ],
            "partial_truth": [
                "🤔 MOSTLY FALSE: Contains misleading information",
                "📉 Truth rating: 3/10 - Significant distortions detected",
                "⚡ HALF-TRUTH: Cherry-picked facts taken out of context",
                "🎭 MISLEADING: Facts twisted to fit narrative"
            ],
            "no_data": [
                "📁 Insufficient data to fact-check this user",
                "🔍 No recent claims found to verify",
                "💭 This user hasn't made any factual claims",
                "🤷 Nothing to fact-check here"
            ],
            "troll_detected": [
                "🤡 TROLL ALERT: This is obvious bait, don't feed them",
                "🎣 Nice bait, but we're not biting",
                "👹 Professional troll detected - engage at your own risk",
                "🗑️ Fact-checking trolls is beneath us"
            ]
        }
        logger.info("SimpleFactChecker initialized")
        
    def get_user_recent_messages(self, username: str, hours: int = 1) -> List[str]:
        """Get user's recent messages from memory files"""
        messages = []
        safe_username = "".join(c for c in username if c.isalnum() or c in (' ', '-', '_')).rstrip()
        user_file = os.path.join(self.memory_dir, f"{safe_username}.txt")
        
        if os.path.exists(user_file):
            try:
                cutoff_time = datetime.now() - timedelta(hours=hours)
                with open(user_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-20:]  # Last 20 messages
                    for line in lines:
                        # Parse timestamp if present
                        if line.startswith('['):
                            messages.append(line.split(': ', 1)[-1].strip())
            except Exception as e:
                logger.error(f"Error reading user file: {e}")
                
        return messages
        
    def analyze_message_patterns(self, messages: List[str]) -> str:
        """Analyze message patterns to determine response type"""
        if not messages:
            return "no_data"
            
        # Check for troll patterns
        troll_keywords = ["libtard", "cuck", "soyboy", "npc", "sheep", "wake up"]
        troll_count = sum(1 for msg in messages for keyword in troll_keywords if keyword in msg.lower())
        if troll_count >= 2:
            return "troll_detected"
            
        # Check for typical MAGA talking points (for the game theme)
        maga_keywords = ["stolen election", "fake news", "deep state", "hunter", "laptop", "rigged"]
        maga_count = sum(1 for msg in messages for keyword in maga_keywords if keyword in msg.lower())
        
        if maga_count >= 3:
            return "lies_detected"
        elif maga_count >= 1:
            return "partial_truth"
        else:
            return "no_data"
            
    def fact_check(self, target_username: str, requester: str, requester_role: str, emoji_sequence: str = "") -> str:
        """
        Perform simple fact-check on user.
        
        Args:
            target_username: User to fact-check
            requester: Who requested the fact-check
            requester_role: Role of requester
            emoji_sequence: Emoji sequence context (optional)
            
        Returns:
            Fact-check response
        """
        # Get user's recent messages
        messages = self.get_user_recent_messages(target_username)
        
        # Analyze patterns
        pattern_type = self.analyze_message_patterns(messages)
        
        # Select appropriate response
        response = random.choice(self.fact_check_responses[pattern_type])
        
        # Add emoji flair if consciousness sequence present
        if emoji_sequence == "✊✋🖐️":
            response = f"✊✋🖐️ {response} ✊✋🖐️"
            
        # Format final response
        final_response = f"@{target_username} {response}"
        
        # Add requester acknowledgment for mods/owners
        if requester_role in ['MOD', 'OWNER']:
            final_response += f" (Requested by {requester})"
            
        logger.info(f"Fact-check for {target_username}: {pattern_type}")
        return final_response
        
    def rate_user(self, username: str, rating_type: str = "truth") -> str:
        """
        Rate a user on various scales.
        
        Args:
            username: User to rate
            rating_type: Type of rating (truth, based, cringe, etc.)
            
        Returns:
            Rating response
        """
        ratings = {
            "truth": random.randint(0, 30),  # MAGAts get low truth scores
            "based": random.randint(70, 100),  # High based scores for allies
            "cringe": random.randint(60, 100),  # High cringe for trolls
            "iq": random.randint(40, 80),  # Below average for targets
            "cope": random.randint(80, 100)  # High cope levels
        }
        
        rating = ratings.get(rating_type, random.randint(0, 100))
        
        responses = {
            "truth": f"@{username} Truth Rating: {rating}/100 📊",
            "based": f"@{username} Based Level: {rating}/100 😎",
            "cringe": f"@{username} Cringe Meter: {rating}/100 😬",
            "iq": f"@{username} Estimated IQ: {rating} 🧠",
            "cope": f"@{username} Cope Level: {rating}/100 🤡"
        }
        
        return responses.get(rating_type, f"@{username} Rating: {rating}/100")
        
    def generate_roast(self, username: str) -> str:
        """Generate a roast for trolls"""
        roasts = [
            f"@{username} Your arguments are weaker than your WiFi signal",
            f"@{username} You're the human equivalent of a participation trophy",
            f"@{username} Even your echo chamber thinks you're annoying",
            f"@{username} You peaked in middle school and it shows",
            f"@{username} Your personality is more manufactured than your outrage"
        ]
        return random.choice(roasts)
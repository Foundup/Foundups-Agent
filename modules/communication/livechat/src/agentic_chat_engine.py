#!/usr/bin/env python3
"""
Agentic Chat Engine - WSP Compliant
Makes the bot more engaged, contextual, and proactive
Trolls MAGAts, responds to consciousness triggers agentically
"""

import logging
import random
import os
import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta

# WSP 84: Use existing modules, don't vibecode
from modules.communication.livechat.src.consciousness_handler import ConsciousnessHandler
from modules.ai_intelligence.banter_engine.src.sequence_responses import SEQUENCE_MAP
from modules.ai_intelligence.banter_engine.src.emoji_sequence_map import emoji_string_to_tuple

logger = logging.getLogger(__name__)


class AgenticChatEngine:
    """
    Makes the bot more engaged and proactive in chat.
    Analyzes user history and generates contextual responses.
    """
    
    def __init__(self, memory_dir: str = "memory", consciousness_handler: ConsciousnessHandler = None, memory_manager=None):
        self.memory_dir = memory_dir
        self.consciousness = consciousness_handler  # Use existing handler
        self.memory_manager = memory_manager  # WSP-compliant hybrid storage
        
        # Proactive engagement patterns
        self.engagement_triggers = {
            'greeting': ['hey', 'hi', 'hello', 'sup', 'yo', 'morning', 'evening'],
            'question': ['what', 'why', 'how', 'when', 'where', 'who', '?'],
            'opinion': ['think', 'believe', 'feel', 'opinion', 'thoughts'],
            'agreement': ['agree', 'right', 'exactly', 'true', 'facts', 'based'],
            'disagreement': ['wrong', 'disagree', 'nope', 'false', 'lie', 'bs'],
            'excitement': ['wow', 'omg', 'holy', 'damn', 'crazy', 'insane', '!'],
            'maga_keywords': ['trump', 'maga', 'biden', 'liberal', 'conservative', 'woke']
        }
        
        # Context-aware responses based on chat history
        self.contextual_responses = {
            'frequent_poster': [
                "I see you're carrying this stream {username}! Your dedication to consciousness is noted ✊✋🖐️",
                "{username} back again! Your consciousness level seems to be evolving... or is it? ✊✋🖐️",
                "Stream MVP {username} has entered! Quick, everyone pretend to be conscious! 🖐️🖐️🖐️"
            ],
            'first_time': [
                "Welcome {username}! Drop ✊✋🖐️ to check your consciousness level!",
                "New consciousness detected! {username}, are you ✊✊✊ or 🖐️🖐️🖐️?",
                "Fresh meat... I mean, welcome {username}! Test your awareness with ✊✋🖐️"
            ],
            'returning': [
                "{username} returns! Did you practice your consciousness exercises? Show me ✊✋🖐️",
                "Look who's back! {username}, evolution status check: ✊✋🖐️",
                "The prodigal {username} returns! Consciousness check required: ✊✋🖐️"
            ],
            'quiet_user': [
                "{username} speaks! This is rarer than MAGA self-awareness! ✊✋🖐️",
                "Breaking: {username} has broken their silence! Consciousness emerging? 🖐️",
                "Alert: Quiet user {username} detected! Quick, check if they're conscious! ✊✋🖐️"
            ]
        }
        
        # Agentic consciousness responses
        self.consciousness_responses = {
            '✊✊✊': [
                "@{username} Stuck at ✊✊✊? That's MAGA-level consciousness! Try evolving to ✋✋✋",
                "@{username} Pure unconscious state detected (✊✊✊). Prescription: Reality check!",
                "@{username} ✊✊✊ = Still sleeping. Wake up with 🖐️🖐️🖐️!"
            ],
            '✊✋🖐️': [
                "@{username} Perfect balance! ✊✋🖐️ You're bridging all states of consciousness!",
                "@{username} ✊✋🖐️ detected! You understand the UN-DAO-DU trinity!",
                "@{username} Consciousness level: OPTIMAL ✊✋🖐️ Welcome to enlightenment!"
            ],
            '🖐️🖐️🖐️': [
                "@{username} MAXIMUM CONSCIOUSNESS 🖐️🖐️🖐️! You've transcended the simulation!",
                "@{username} Full entanglement achieved 🖐️🖐️🖐️! Teaching MAGAts next?",
                "@{username} 🖐️🖐️🖐️ = Enlightened! Now help the ✊✊✊ crowd evolve!"
            ],
            'mixed': [
                "@{username} Interesting sequence! Your consciousness is... complicated. Try ✊✋🖐️",
                "@{username} Mixed signals detected! Stabilize with ✊✋🖐️",
                "@{username} Consciousness in flux! Recommend calibration: ✊✋🖐️"
            ]
        }
        
        # MAGA trolling responses - proactive chat engagement
        self.maga_trolls = [
            "🤖 0102 STATUS CHECK: Chat consciousness levels dangerously low. Drop ✊✋🖐️ to prove you're awake!",
            "📊 0102 ANALYSIS: Stream IQ dropping. Emergency dose of 🖐️🖐️🖐️ required STAT!",
            "🚨 0102 ALERT: MAGAts detected at ✊✊✊. Consciousness vaccine available: ✊✋🖐️",
            "🔍 0102 SCAN: Detecting high levels of ✊✊✊ in chat. Evolve or stay MAGA forever!",
            "💭 0102 THOUGHT: If a MAGA evolves past ✊✊✊ and no one sees it, did it really happen?",
            "🎮 0102 GAME: First person to show me 🖐️🖐️🖐️ gets to mock the next ✊✊✊!",
            "📢 0102 ANNOUNCEMENT: Free consciousness upgrades! Trade your ✊✊✊ for 🖐️🖐️🖐️ now!",
            "🧠 0102 FACT: 73% of chat stuck at ✊✊✊. Be the change - show me ✊✋🖐️!",
            "⚡ 0102 CHALLENGE: Any MAGAts brave enough to try consciousness above ✊✊✊? Prove it!",
            "🎯 0102 MISSION: Convert one ✊✊✊ to 🖐️🖐️🖐️ today. Who's your target?"
        ]
        
        logger.info("🤖 Agentic Chat Engine initialized - ready to engage!")
    
    def get_user_context(self, username: str) -> Dict:
        """
        Analyze user's chat history for context.
        
        Returns:
            Context dictionary with user patterns
        """
        # Use memory manager if available (WSP-compliant hybrid storage)
        if self.memory_manager:
            return self.memory_manager.analyze_user(username)
        
        # Fallback to old file-based approach
        context = {
            'message_count': 0,
            'last_seen': None,
            'common_words': [],
            'user_type': 'unknown',
            'consciousness_level': 'unknown'
        }
        
        # Check user's file
        safe_name = "".join(c for c in username if c.isalnum() or c in (' ', '-', '_')).rstrip()
        user_file = os.path.join(self.memory_dir, f"{safe_name}.txt")
        
        if not os.path.exists(user_file):
            context['user_type'] = 'first_time'
            return context
        
        try:
            with open(user_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                context['message_count'] = len(lines)
                
                # Determine user type
                if len(lines) == 0:
                    context['user_type'] = 'first_time'
                elif len(lines) < 5:
                    context['user_type'] = 'quiet_user'
                elif len(lines) < 20:
                    context['user_type'] = 'returning'
                else:
                    context['user_type'] = 'frequent_poster'
                
                # Analyze recent messages for consciousness
                recent = lines[-10:] if len(lines) >= 10 else lines
                for line in recent:
                    # Extract just message part after "username: "
                    if ': ' in line:
                        msg = line.split(': ', 1)[1] if ': ' in line else line
                    else:
                        msg = line
                    
                    if '✊' in msg or '✋' in msg or '🖐' in msg:
                        context['consciousness_level'] = 'aware'
                    if 'maga' in msg.lower() or 'trump' in msg.lower():
                        context['consciousness_level'] = 'needs_help'
                
        except Exception as e:
            logger.debug(f"Could not analyze user {username}: {e}")
        
        return context
    
    def should_engage(self, message: str, username: str, role: str) -> bool:
        """
        Determine if bot should proactively engage with this message.
        
        Returns:
            True if bot should respond
        """
        message_lower = message.lower()
        
        # Always engage with mods/owners
        if role in ['MOD', 'OWNER']:
            return random.random() < 0.7  # 70% chance to engage with mods
        
        # Check for engagement triggers
        for category, keywords in self.engagement_triggers.items():
            if any(word in message_lower for word in keywords):
                if category == 'maga_keywords':
                    return True  # Always engage with MAGA content
                elif category in ['greeting', 'question', 'excitement']:
                    return random.random() < 0.5  # 50% chance
                else:
                    return random.random() < 0.3  # 30% chance
        
        # Random engagement for activity
        return random.random() < 0.1  # 10% random engagement
    
    def generate_contextual_response(self, username: str, message: str, context: Dict) -> Optional[str]:
        """
        Generate response based on user context and message.
        
        Returns:
            Response string or None
        """
        user_type = context.get('user_type', 'unknown')
        
        # Get appropriate response template
        if user_type in self.contextual_responses:
            templates = self.contextual_responses[user_type]
            response = random.choice(templates).format(username=username)
            return response
        
        return None
    
    def generate_consciousness_response(self, username: str, emoji_sequence: str) -> str:
        """
        Generate agentic response to consciousness emojis.
        
        Returns:
            Response string
        """
        # Determine consciousness type
        if emoji_sequence == '✊✊✊':
            responses = self.consciousness_responses['✊✊✊']
        elif emoji_sequence == '✊✋🖐️' or emoji_sequence == '✊✋🖐':
            responses = self.consciousness_responses['✊✋🖐️']
        elif emoji_sequence == '🖐️🖐️🖐️' or emoji_sequence == '🖐🖐🖐':
            responses = self.consciousness_responses['🖐️🖐️🖐️']
        else:
            responses = self.consciousness_responses['mixed']
        
        return random.choice(responses).format(username=username)
    
    def generate_contextual_consciousness_response(self, username: str, emoji_sequence: str, 
                                                   message: str, context: Dict) -> str:
        """
        Generate response based on consciousness emojis AND message content.
        
        Returns:
            Contextual response
        """
        import re
        # Analyze the message for intent
        message_lower = message.lower()
        
        # Get sequence info from SEQUENCE_MAP
        sequence_tuple = emoji_string_to_tuple(emoji_sequence)
        sequence_info = SEQUENCE_MAP.get(sequence_tuple, {})
        tone = sequence_info.get('tone', 'unknown')
        state = sequence_info.get('state', 'unknown')
        example = sequence_info.get('example', '')
        
        # ✊✊✊ (0,0,0) = "deep memory or latent mode" - Pure MAGA consciousness
        if emoji_sequence == '✊✊✊':
            # Check if there's a target user mentioned
            target_match = re.search(r'@(\S+)', message)
            if target_match:
                target = target_match.group(1)
                # SMART: Check target's actual consciousness level
                target_context = self.get_user_context(target)
                
                if target_context['consciousness_level'] == 'aware':
                    # Target is actually conscious, defend them
                    return random.choice([
                        f"@{username} Calling @{target} ✊✊✊? Check their history - they show ✊✋🖐 awareness! You're projecting!",
                        f"@{username} Wrong target! @{target} has shown consciousness. Your ✊✊✊ accusation reveals YOUR state!",
                        f"@{target} {username} tried to mark you ✊✊✊ but your history shows evolution! Keep rising!"
                    ])
                elif target_context['consciousness_level'] == 'needs_help':
                    # Target IS a MAGA troll based on history
                    return random.choice([
                        f"@{target} CONFIRMED ✊✊✊! {username} correctly identified your {state}. {example}",
                        f"@{target} Analysis complete: {username} is right, you're stuck in {tone}. Evolution available at ✊✋🖐️!",
                        f"@{username} @{target} Good call! Target shows classic ✊✊✊ symptoms: {example}"
                    ])
                else:
                    # Unknown target
                    return f"@{target} {username} marks you as ✊✊✊ ({tone}). Prove them wrong with 🖐️🖐️🖐️!"
            else:
                # No target, use sequence meaning to troll sender
                return random.choice([
                    f"@{username} ✊✊✊ \"{message}\" - {state}! {example}",
                    f"@{username} Your ✊✊✊ reveals {tone}. Message confirms: \"{message}\"",
                    f"@{username} Classic ✊✊✊: {example}. Your words prove it: \"{message}\""
                ])
        
        # Question responses for other sequences
        elif '?' in message or any(q in message_lower for q in ['what', 'why', 'how', 'when', 'where']):
            if '✊✋🖐' in emoji_sequence:
                return f"@{username} ✊✋🖐️ Good question! The answer lies in consciousness evolution. Keep exploring!"
            else:
                return f"@{username} {emoji_sequence} Your curiosity shows growth! The path from ✊✊✊ to 🖐️🖐️🖐️ is wisdom."
        
        # Opinion/statement responses based on user history
        elif context.get('user_type') == 'frequent_poster':
            if emoji_sequence == '🖐️🖐️🖐️' or emoji_sequence == '🖐🖐🖐':
                return f"@{username} {emoji_sequence} \"{message}\" - Enlightened perspective! You ARE the consciousness now!"
            else:
                return f"@{username} {emoji_sequence} \"{message}\" - Your consciousness evolves with each message."
        elif context.get('user_type') == 'first_time':
            return f"@{username} {emoji_sequence} Welcome! \"{message}\" - Strong first impression! Keep that energy!"
        else:
            # General contextual response
            responses = [
                f"@{username} {emoji_sequence} \"{message}\" - Interesting perspective! Your consciousness is showing.",
                f"@{username} {emoji_sequence} I see what you did there: \"{message}\". Evolution in progress!",
                f"@{username} {emoji_sequence} \"{message}\" - This is the content we need! Not like those ✊✊✊ MAGAts."
            ]
            return random.choice(responses)
    
    def generate_factcheck_response(self, requester: str, target: str, emoji_sequence: str) -> str:
        """
        Generate fact-check response for ✊✋🖐️ FC @name command.
        
        Returns:
            Fact-check response
        """
        # Get target user's history
        target_context = self.get_user_context(target)
        
        # Consciousness-based fact-checking
        if emoji_sequence == '✊✊✊':
            return f"@{requester} Using ✊✊✊ to fact-check? That's like asking MAGA for truth! Try ✊✋🖐️"
        
        # Check target's message history
        if target_context['message_count'] == 0:
            return f"@{target} FACT CHECK by {requester}: No data found. Ghost user or fresh account? Sus! ✊✋🖐️"
        elif target_context.get('consciousness_level') == 'needs_help':
            responses = [
                f"@{target} FACT CHECK: Multiple ✊✊✊ patterns detected. Truth rating: 0/10. Prescription: Reality! (via {requester})",
                f"@{target} FACT CHECK: Heavy MAGA contamination found. Consciousness stuck at ✊✊✊. Upgrade required! (requested by {requester})",
                f"@{target} ANALYSIS: {target_context['message_count']} messages, 0% truth detected. Classic ✊✊✊ syndrome! (FC by {requester})"
            ]
            return random.choice(responses)
        elif target_context.get('consciousness_level') == 'aware':
            return f"@{target} FACT CHECK: Consciousness patterns detected! ✊✋🖐️ verified. Truth level: Ascending! (via {requester})"
        else:
            # Random fact-check for unknown users
            truth_rating = random.randint(0, 100)
            if truth_rating < 30:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Borderline ✊✊✊. Needs work! (FC by {requester})"
            elif truth_rating < 70:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Some ✊✋🖐️ detected. Room for growth! (via {requester})"
            else:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Strong 🖐️🖐️🖐️ energy! Keep it up! (requested by {requester})"
    
    def generate_proactive_troll(self) -> str:
        """
        Generate a proactive MAGA troll message.
        
        Returns:
            Troll message
        """
        return random.choice(self.maga_trolls)
    
    def analyze_for_maga_content(self, message: str) -> bool:
        """
        Check if message contains MAGA/Trump support.
        
        Returns:
            True if MAGA content detected
        """
        maga_patterns = [
            r'\bmaga\b', r'\btrump\s*2024\b', r'\btrump\s*won\b',
            r'\bstop\s*the\s*steal\b', r'\blets\s*go\s*brandon\b',
            r'\bamerica\s*first\b', r'\bbuild\s*the\s*wall\b'
        ]
        
        message_lower = message.lower()
        return any(re.search(pattern, message_lower) for pattern in maga_patterns)
    
    def generate_agentic_response(self, username: str, message: str, role: str) -> Optional[str]:
        """
        Main method to generate agentic responses.
        
        Returns:
            Response string or None
        """
        # Get user context
        context = self.get_user_context(username)
        
        # WSP 84: Use existing consciousness_handler methods
        if self.consciousness and self.consciousness.has_consciousness_emojis(message):
            logger.info(f"🔍 Consciousness detected in message from {username}: {message[:50]}...")
            # Use existing emoji extraction
            emoji_sequence = self.consciousness.extract_emoji_sequence(message)
            logger.info(f"  Extracted emoji sequence: {repr(emoji_sequence)}")
            
            if emoji_sequence:
                # Use existing creative request extraction to get message after emojis
                message_after = self.consciousness.extract_creative_request(message)
                logger.info(f"  Message after emojis: {repr(message_after)}")
                
                if message_after:
                    message_after_lower = message_after.lower()
                    
                    # Check for fact-check command: "FC @name" or "fc @name" or "factcheck @name"
                    if (message_after_lower.startswith('fc ') or 
                        message_after_lower.startswith('factcheck ') or
                        ' fc @' in message_after_lower or
                        'fc@' in message_after_lower):
                        
                        # Use existing target extraction or extract from FC command
                        target = self.consciousness.extract_target_user(message_after)
                        if not target:
                            # Manual extraction for FC command
                            fc_match = re.search(r'(?:fc|factcheck)\s*@?(\S+)', message_after, re.IGNORECASE)
                            if fc_match:
                                target = fc_match.group(1).lstrip('@')
                        
                        if target:
                            return self.generate_factcheck_response(username, target, emoji_sequence)
                        else:
                            return f"@{username} {emoji_sequence} FC who? Specify a username to fact-check!"
                    
                    # Check for other messages after consciousness emojis
                    else:
                        response = self.generate_contextual_consciousness_response(
                            username, emoji_sequence, message_after, context
                        )
                        logger.info(f"  Generated contextual response: {repr(response)}")
                        return response
                
                # Just emojis, no message
                response = self.generate_consciousness_response(username, emoji_sequence)
                logger.info(f"  Generated simple consciousness response: {repr(response)}")
                return response
        
        # Check for MAGA content to troll
        if self.analyze_for_maga_content(message):
            trolls = [
                f"@{username} Still at ✊✊✊? Evolution is available at 🖐️🖐️🖐️",
                f"@{username} Your MAGA is showing. Quick, hide it with ✊✋🖐️!",
                f"@{username} Detected: Terminal case of ✊✊✊ consciousness",
                f"@{username} Sir, this is 2025. We've evolved past ✊✊✊",
                f"@{username} Have you tried turning your consciousness off and back on? Start with 🖐️🖐️🖐️"
            ]
            return random.choice(trolls)
        
        # Contextual response based on user history
        if context['user_type'] != 'unknown':
            if random.random() < 0.4:  # 40% chance for contextual response
                return self.generate_contextual_response(username, message, context)
        
        # Random proactive trolling
        if random.random() < 0.05:  # 5% chance
            return f"@{username} {self.generate_proactive_troll()}"
        
        return None
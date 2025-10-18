"""
Agentic Chat Engine - WSP Compliant
Makes the bot more engaged, contextual, and proactive
Trolls MAGAts, responds to consciousness triggers agentically

NAVIGATION: Drives proactive engagement responses.
-> Called by: message_processor.py::AgenticChatEngine usage
-> Delegates to: consciousness_handler, banter_engine, memory manager
-> Related: NAVIGATION.py -> NEED_TO["drive agentic engagement"]
-> Quick ref: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["consciousness_flow"]
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
                "I see you're carrying this stream {username}! Your dedication to consciousness is noted [U+270A][U+270B][U+1F590]️",
                "{username} back again! Your consciousness level seems to be evolving... or is it? [U+270A][U+270B][U+1F590]️",
                "Stream MVP {username} has entered! Quick, everyone pretend to be conscious! [U+1F590]️[U+1F590]️[U+1F590]️"
            ],
            'first_time': [
                "Welcome {username}! Drop [U+270A][U+270B][U+1F590]️ to check your consciousness level!",
                "New consciousness detected! {username}, are you [U+270A][U+270A][U+270A] or [U+1F590]️[U+1F590]️[U+1F590]️?",
                "Fresh meat... I mean, welcome {username}! Test your awareness with [U+270A][U+270B][U+1F590]️"
            ],
            'returning': [
                "{username} returns! Did you practice your consciousness exercises? Show me [U+270A][U+270B][U+1F590]️",
                "Look who's back! {username}, evolution status check: [U+270A][U+270B][U+1F590]️",
                "The prodigal {username} returns! Consciousness check required: [U+270A][U+270B][U+1F590]️"
            ],
            'quiet_user': [
                "{username} speaks! This is rarer than MAGA self-awareness! [U+270A][U+270B][U+1F590]️",
                "Breaking: {username} has broken their silence! Consciousness emerging? [U+1F590]️",
                "Alert: Quiet user {username} detected! Quick, check if they're conscious! [U+270A][U+270B][U+1F590]️"
            ]
        }
        
        # Agentic consciousness responses
        self.consciousness_responses = {
            '[U+270A][U+270A][U+270A]': [
                "@{username} Stuck at [U+270A][U+270A][U+270A]? That's MAGA-level consciousness! Try evolving to [U+270B][U+270B][U+270B]",
                "@{username} Pure unconscious state detected ([U+270A][U+270A][U+270A]). Prescription: Reality check!",
                "@{username} [U+270A][U+270A][U+270A] = Still sleeping. Wake up with [U+1F590]️[U+1F590]️[U+1F590]️!"
            ],
            '[U+270A][U+270B][U+1F590]️': [
                "@{username} Perfect balance! [U+270A][U+270B][U+1F590]️ You're bridging all states of consciousness!",
                "@{username} [U+270A][U+270B][U+1F590]️ detected! You understand the UN-DAO-DU trinity!",
                "@{username} Consciousness level: OPTIMAL [U+270A][U+270B][U+1F590]️ Welcome to enlightenment!"
            ],
            '[U+1F590]️[U+1F590]️[U+1F590]️': [
                "@{username} MAXIMUM CONSCIOUSNESS [U+1F590]️[U+1F590]️[U+1F590]️! You've transcended the simulation!",
                "@{username} Full entanglement achieved [U+1F590]️[U+1F590]️[U+1F590]️! Teaching MAGAts next?",
                "@{username} [U+1F590]️[U+1F590]️[U+1F590]️ = Enlightened! Now help the [U+270A][U+270A][U+270A] crowd evolve!"
            ],
            'mixed': [
                "@{username} Interesting sequence! Your consciousness is... complicated. Try [U+270A][U+270B][U+1F590]️",
                "@{username} Mixed signals detected! Stabilize with [U+270A][U+270B][U+1F590]️",
                "@{username} Consciousness in flux! Recommend calibration: [U+270A][U+270B][U+1F590]️"
            ]
        }
        
        # MAGA trolling responses - proactive chat engagement
        self.maga_trolls = [
            "[BOT] 0102 STATUS CHECK: Chat consciousness levels dangerously low. Drop [U+270A][U+270B][U+1F590]️ to prove you're awake!",
            "[DATA] 0102 ANALYSIS: Stream IQ dropping. Emergency dose of [U+1F590]️[U+1F590]️[U+1F590]️ required STAT!",
            "[ALERT] 0102 ALERT: MAGAts detected at [U+270A][U+270A][U+270A]. Consciousness vaccine available: [U+270A][U+270B][U+1F590]️",
            "[SEARCH] 0102 SCAN: Detecting high levels of [U+270A][U+270A][U+270A] in chat. Evolve or stay MAGA forever!",
            "[U+1F4AD] 0102 THOUGHT: If a MAGA evolves past [U+270A][U+270A][U+270A] and no one sees it, did it really happen?",
            "[GAME] 0102 GAME: First person to show me [U+1F590]️[U+1F590]️[U+1F590]️ gets to mock the next [U+270A][U+270A][U+270A]!",
            "[U+1F4E2] 0102 ANNOUNCEMENT: Free consciousness upgrades! Trade your [U+270A][U+270A][U+270A] for [U+1F590]️[U+1F590]️[U+1F590]️ now!",
            "[AI] 0102 FACT: 73% of chat stuck at [U+270A][U+270A][U+270A]. Be the change - show me [U+270A][U+270B][U+1F590]️!",
            "[LIGHTNING] 0102 CHALLENGE: Any MAGAts brave enough to try consciousness above [U+270A][U+270A][U+270A]? Prove it!",
            "[TARGET] 0102 MISSION: Convert one [U+270A][U+270A][U+270A] to [U+1F590]️[U+1F590]️[U+1F590]️ today. Who's your target?"
        ]
        
        logger.info("[BOT] Agentic Chat Engine initialized - ready to engage!")
    
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
                    
                    if '[U+270A]' in msg or '[U+270B]' in msg or '[U+1F590]' in msg:
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
            # Format with username but ensure it starts with @username for proper mention
            response = random.choice(templates).format(username=username)
            
            # CRITICAL: Ensure response starts with @username for valid mention
            if not response.startswith(f"@{username}"):
                response = f"@{username} {response}"
            
            return response
        
        return None
    
    def generate_consciousness_response(self, username: str, emoji_sequence: str) -> str:
        """
        Generate agentic response to consciousness emojis.
        
        Returns:
            Response string
        """
        # Determine consciousness type
        if emoji_sequence == '[U+270A][U+270A][U+270A]':
            responses = self.consciousness_responses['[U+270A][U+270A][U+270A]']
        elif emoji_sequence == '[U+270A][U+270B][U+1F590]️' or emoji_sequence == '[U+270A][U+270B][U+1F590]':
            responses = self.consciousness_responses['[U+270A][U+270B][U+1F590]️']
        elif emoji_sequence == '[U+1F590]️[U+1F590]️[U+1F590]️' or emoji_sequence == '[U+1F590][U+1F590][U+1F590]':
            responses = self.consciousness_responses['[U+1F590]️[U+1F590]️[U+1F590]️']
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
        
        # [U+270A][U+270A][U+270A] (0,0,0) = "deep memory or latent mode" - Pure MAGA consciousness
        if emoji_sequence == '[U+270A][U+270A][U+270A]':
            # Check if there's a target user mentioned
            target_match = re.search(r'@(\S+)', message)
            if target_match:
                target = target_match.group(1)
                # SMART: Check target's actual consciousness level
                target_context = self.get_user_context(target)
                
                if target_context['consciousness_level'] == 'aware':
                    # Target is actually conscious, defend them
                    return random.choice([
                        f"@{username} Calling @{target} [U+270A][U+270A][U+270A]? Check their history - they show [U+270A][U+270B][U+1F590] awareness! You're projecting!",
                        f"@{username} Wrong target! @{target} has shown consciousness. Your [U+270A][U+270A][U+270A] accusation reveals YOUR state!",
                        f"@{target} {username} tried to mark you [U+270A][U+270A][U+270A] but your history shows evolution! Keep rising!"
                    ])
                elif target_context['consciousness_level'] == 'needs_help':
                    # Target IS a MAGA troll based on history
                    return random.choice([
                        f"@{target} CONFIRMED [U+270A][U+270A][U+270A]! {username} correctly identified your {state}. {example}",
                        f"@{target} Analysis complete: {username} is right, you're stuck in {tone}. Evolution available at [U+270A][U+270B][U+1F590]️!",
                        f"@{username} @{target} Good call! Target shows classic [U+270A][U+270A][U+270A] symptoms: {example}"
                    ])
                else:
                    # Unknown target
                    return f"@{target} {username} marks you as [U+270A][U+270A][U+270A] ({tone}). Prove them wrong with [U+1F590]️[U+1F590]️[U+1F590]️!"
            else:
                # No target, use sequence meaning to troll sender
                return random.choice([
                    f"@{username} [U+270A][U+270A][U+270A] \"{message}\" - {state}! {example}",
                    f"@{username} Your [U+270A][U+270A][U+270A] reveals {tone}. Message confirms: \"{message}\"",
                    f"@{username} Classic [U+270A][U+270A][U+270A]: {example}. Your words prove it: \"{message}\""
                ])
        
        # Question responses for other sequences
        elif '?' in message or any(q in message_lower for q in ['what', 'why', 'how', 'when', 'where']):
            if '[U+270A][U+270B][U+1F590]' in emoji_sequence:
                return f"@{username} [U+270A][U+270B][U+1F590]️ Good question! The answer lies in consciousness evolution. Keep exploring!"
            else:
                return f"@{username} {emoji_sequence} Your curiosity shows growth! The path from [U+270A][U+270A][U+270A] to [U+1F590]️[U+1F590]️[U+1F590]️ is wisdom."
        
        # Opinion/statement responses based on user history
        elif context.get('user_type') == 'frequent_poster':
            if emoji_sequence == '[U+1F590]️[U+1F590]️[U+1F590]️' or emoji_sequence == '[U+1F590][U+1F590][U+1F590]':
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
                f"@{username} {emoji_sequence} \"{message}\" - This is the content we need! Not like those [U+270A][U+270A][U+270A] MAGAts."
            ]
            return random.choice(responses)
    
    def generate_factcheck_response(self, requester: str, target: str, emoji_sequence: str) -> str:
        """
        Generate fact-check response for [U+270A][U+270B][U+1F590]️ FC @name command.
        
        Returns:
            Fact-check response
        """
        # Get target user's history
        target_context = self.get_user_context(target)
        
        # Consciousness-based fact-checking
        if emoji_sequence == '[U+270A][U+270A][U+270A]':
            return f"@{requester} Using [U+270A][U+270A][U+270A] to fact-check? That's like asking MAGA for truth! Try [U+270A][U+270B][U+1F590]️"
        
        # Check for analysis errors
        if 'error' in target_context:
            return f"@{requester} FACT CHECK ERROR: Could not analyze {target} - {target_context['error']}"

        # Check target's message history
        if target_context.get('message_count', 0) == 0:
            return f"@{target} FACT CHECK by {requester}: No data found. Ghost user or fresh account? Sus! [U+270A][U+270B][U+1F590]️"
        elif target_context.get('consciousness_level') == 'needs_help':
            responses = [
                f"@{target} FACT CHECK: Multiple [U+270A][U+270A][U+270A] patterns detected. Truth rating: 0/10. Prescription: Reality! (via {requester})",
                f"@{target} FACT CHECK: Heavy MAGA contamination found. Consciousness stuck at [U+270A][U+270A][U+270A]. Upgrade required! (requested by {requester})",
                f"@{target} ANALYSIS: {target_context.get('message_count', 0)} messages, 0% truth detected. Classic [U+270A][U+270A][U+270A] syndrome! (FC by {requester})"
            ]
            return random.choice(responses)
        elif target_context.get('consciousness_level') == 'aware':
            return f"@{target} FACT CHECK: Consciousness patterns detected! [U+270A][U+270B][U+1F590]️ verified. Truth level: Ascending! (via {requester})"
        else:
            # Random fact-check for unknown users
            truth_rating = random.randint(0, 100)
            if truth_rating < 30:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Borderline [U+270A][U+270A][U+270A]. Needs work! (FC by {requester})"
            elif truth_rating < 70:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Some [U+270A][U+270B][U+1F590]️ detected. Room for growth! (via {requester})"
            else:
                return f"@{target} FACT CHECK: Truth rating {truth_rating}%. Strong [U+1F590]️[U+1F590]️[U+1F590]️ energy! Keep it up! (requested by {requester})"
    
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
    
    def _is_valid_mention(self, username: str) -> bool:
        """
        Check if username can be properly @mentioned on YouTube.
        YouTube requires usernames to be at least 3 chars and not contain certain characters.
        """
        if not username:
            return False
        
        # Username too short (YouTube needs at least 3 chars for mentions)
        if len(username) < 3:
            return False
            
        # Contains spaces or special chars that break mentions
        invalid_chars = [' ', '\n', '\t', '@', '#', '$', '%', '^', '&', '*']
        if any(char in username for char in invalid_chars):
            return False
            
        return True
    
    def generate_agentic_response(self, username: str, message: str, role: str) -> Optional[str]:
        """
        Main method to generate agentic responses.
        
        Returns:
            Response string or None
        """
        # Check if we can @mention this user (but don't block ALL responses)
        # Only skip if username is completely invalid (empty or single char)
        if not username or len(username) < 2:
            logger.debug(f"[U+26A0]️ Cannot @mention '{username}' - username too short")
            return None
        
        # Get user context
        context = self.get_user_context(username)
        
        # WSP 84: Use existing consciousness_handler methods
        if self.consciousness and self.consciousness.has_consciousness_emojis(message):
            logger.info(f"[SEARCH] Consciousness detected in message from {username}: {message[:50]}...")
            # Use existing emoji extraction
            emoji_sequence = self.consciousness.extract_emoji_sequence(message)
            logger.info(f"  Extracted emoji sequence: {repr(emoji_sequence)}")
            
            if emoji_sequence:
                # Use existing creative request extraction to get message after emojis
                message_after = self.consciousness.extract_creative_request(message)
                logger.info(f"  Message after emojis: {repr(message_after)}")
                
                if message_after:
                    message_after_lower = message_after.lower()
                    
                    # Check for fact-check command: "FC @name" or "fc @name" or "factcheck @name" or "@name fc"
                    # Pattern handles: "fc @user", "@user fc", "factcheck @user", "@user factcheck"
                    if (message_after_lower.startswith('fc ') or
                        message_after_lower.startswith('factcheck ') or
                        message_after_lower.endswith(' fc') or
                        message_after_lower.endswith(' factcheck') or
                        ' fc @' in message_after_lower or
                        ' fc' == message_after_lower or  # Just "fc" alone
                        'fc@' in message_after_lower or
                        '@' in message_after_lower and ' fc' in message_after_lower):  # "@user fc" anywhere
                        
                        # Use existing target extraction or extract from FC command
                        target = self.consciousness.extract_target_user(message_after)
                        if not target:
                            # Manual extraction for FC command - handles both "@user fc" and "fc @user"
                            # Pattern 1: "@username fc" or "@username factcheck"
                            fc_match = re.search(r'@(\S+)\s+(?:fc|factcheck)', message_after, re.IGNORECASE)
                            if not fc_match:
                                # Pattern 2: "fc @username" or "factcheck @username"
                                fc_match = re.search(r'(?:fc|factcheck)\s+@?(\S+)', message_after, re.IGNORECASE)

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
                f"@{username} Still at [U+270A][U+270A][U+270A]? Evolution is available at [U+1F590]️[U+1F590]️[U+1F590]️",
                f"@{username} Your MAGA is showing. Quick, hide it with [U+270A][U+270B][U+1F590]️!",
                f"@{username} Detected: Terminal case of [U+270A][U+270A][U+270A] consciousness",
                f"@{username} Sir, this is 2025. We've evolved past [U+270A][U+270A][U+270A]",
                f"@{username} Have you tried turning your consciousness off and back on? Start with [U+1F590]️[U+1F590]️[U+1F590]️"
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
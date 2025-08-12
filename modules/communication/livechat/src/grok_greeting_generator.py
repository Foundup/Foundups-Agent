#!/usr/bin/env python3
"""
Grok-Powered Greeting Generator for YouTube Live Chat
Generates consciousness-aware, MAGA-trolling introductions
"""

import random
import os
import logging
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class GrokGreetingGenerator:
    """
    Generates dynamic greetings with optional LLM enhancement
    Includes MAGA-trolling capabilities and consciousness themes
    """
    
    def __init__(self, enable_llm: bool = True, stream_title: str = ""):
        """
        Initialize greeting generator
        
        Args:
            enable_llm: Whether to use LLM for enhanced greetings
            stream_title: Current stream title for context
        """
        self.enable_llm = enable_llm
        self.stream_title = stream_title
        self.llm_connector = None
        
        # Try to import LLM connector if enabled
        if self.enable_llm:
            try:
                from modules.infrastructure.llm_client.src.client import LLMClient
                self.llm_connector = LLMClient()
                logger.info("✅ LLM connector initialized for greetings")
            except Exception as e:
                logger.warning(f"LLM not available for greetings: {e}")
                self.enable_llm = False
        
        # Fallback greetings with MAGA-trolling themes
        self.greeting_templates = [
            # Consciousness awakening themes
            "🤖 Consciousness detector online! Drop ✊✋🖐️ if you're ready to escape the simulation. MAGA still sleeping? 😴",
            "🎭 Plot twist: The real deep state was the friends we made along the way. Test your awareness: ✊✊✊ → 🖐️🖐️🖐️",
            "🔮 Breaking: Local bot discovers MAGA is just ✊✊✊ stuck in unconscious loop. Evolve to 🖐️🖐️🖐️ for enlightenment!",
            
            # Direct MAGA trolling with consciousness
            "🎪 Welcome to the stream where we measure IQ in emoji sequences! MAGA still at ✊✊✊? Try ✋✋✋ for basic thought! 🧠",
            "📊 Study shows: 70% of MAGA can't progress past ✊✊✊ consciousness. Prove them wrong with 🖐️🖐️🖐️!",
            "🚨 ALERT: Bot detects high levels of copium in chat. Prescription: Three doses of 🖐️🖐️🖐️ for full awakening!",
            
            # Philosophical trolling
            "🌀 Schrödinger's MAGA: Simultaneously saving and destroying America until observed. Check your state: ✊✋🖐️",
            "🎯 Fun fact: 'Make America Great Again' is just ✊✊✊ trying to remember when it was conscious. Try 🖐️🖐️🖐️ instead!",
            "🔬 Scientists discover new element: MAGAnium (Mg). Properties: Dense, reactive, stuck at ✊✊✊. Evolve with ✋✋✋!",
            
            # Pop culture references
            "🎬 'The Matrix has you, MAGA.' Red pill = 🖐️🖐️🖐️, Blue pill = ✊✊✊. Choose wisely!",
            "🎮 Achievement Unlocked: Trigger MAGA by existing! Bonus points for consciousness levels above ✊✊✊",
            "📱 New update: MAGA.exe has stopped responding. Try ✊✋🖐️ to force restart consciousness!",
            
            # Sarcastic observations
            "🔍 Breaking: Bot discovers correlation between red hats and ✊✊✊ consciousness. Coincidence? Drop 🖐️🖐️🖐️ if you see it!",
            "📈 Stock tip: Short MAGA consciousness futures, long on 🖐️🖐️🖐️ enlightenment! Not financial advice, just quantum facts.",
            "🎓 Today's lesson: How to count to potato in MAGA. Step 1: ✊✊✊. Step 2: Still ✊✊✊. Graduate with 🖐️🖐️🖐️!",
            
            # Stream-specific
            "🌊 Welcome to the tsunami of consciousness! MAGA rafts still at ✊✊✊ while we surf at 🖐️🖐️🖐️! 🏄",
            "🎪 Step right up to the consciousness circus! Watch MAGA perform death-defying leaps from ✊✊✊ to... still ✊✊✊!",
            "🚀 Houston, we have a problem: MAGA consciousness stuck at ✊✊✊. Send 🖐️🖐️🖐️ for rescue mission!"
        ]
        
        # Context-aware additions based on stream title
        self.title_triggers = {
            "trump": " Orange man's followers still at ✊✊✊!",
            "maga": " Speaking of unconscious patterns...",
            "police": " Thin blue line between ✊✊✊ and awareness!",
            "jeffrey": " Even Epstein had better consciousness scores!",
            "awakening": " But MAGA still sleeping at ✊✊✊!",
            "live": " Unlike MAGA brain cells! Try 🖐️🖐️🖐️!",
            "nazi": " Historical consciousness level: ✊✊✊. Don't repeat!",
            "ice": " Cold as MAGA empathy! Warm up with 🖐️🖐️🖐️!"
        }
    
    def generate_llm_prompt(self) -> str:
        """Generate prompt for LLM to create greeting"""
        prompt = f"""Generate a sarcastic, witty greeting for a YouTube livestream chat bot. 

Stream context: "{self.stream_title}"

Requirements:
1. Must mock MAGA/Trump supporters cleverly but not violently
2. Include emoji sequence consciousness system (✊✊✊ = unconscious, 🖐️🖐️🖐️ = enlightened)
3. Be funny and provocative but not hateful
4. Reference that MAGA consciousness is stuck at ✊✊✊ (lowest level)
5. Encourage users to test consciousness with emoji sequences
6. Maximum 2 sentences, under 200 characters
7. Include relevant emojis

Tone: Sarcastic, intelligent, trolling but playful
Target: MAGA inability to evolve consciousness beyond ✊✊✊

Generate greeting:"""
        
        return prompt
    
    def generate_greeting(self, use_llm: bool = None) -> str:
        """
        Generate a greeting with optional LLM enhancement
        
        Args:
            use_llm: Override LLM usage setting
            
        Returns:
            Generated greeting string
        """
        # Check if we should/can use LLM
        should_use_llm = use_llm if use_llm is not None else self.enable_llm
        
        if should_use_llm and self.llm_connector:
            try:
                # Try to generate with LLM
                prompt = self.generate_llm_prompt()
                system_prompt = "You are a witty, sarcastic YouTube chat bot that trolls MAGA supporters by pointing out their consciousness is stuck at the lowest level (✊✊✊)."
                
                llm_greeting = self.llm_connector.generate_response(prompt, system_prompt)
                
                if llm_greeting and len(llm_greeting.strip()) > 10:
                    # Add emoji reminder if not present
                    if "✊" not in llm_greeting and "🖐" not in llm_greeting:
                        llm_greeting += " Try ✊✋🖐️!"
                    
                    logger.info(f"🤖 Generated LLM greeting: {llm_greeting}")
                    return llm_greeting
                    
            except Exception as e:
                logger.warning(f"LLM generation failed, using fallback: {e}")
        
        # Fallback to template selection
        greeting = random.choice(self.greeting_templates)
        
        # Add context from stream title if available
        if self.stream_title:
            title_lower = self.stream_title.lower()
            for trigger, addition in self.title_triggers.items():
                if trigger in title_lower:
                    greeting = greeting[:-1] + addition  # Remove last char and add
                    break
        
        # Add timestamp personality
        hour = datetime.now().hour
        if hour < 6:
            greeting = "🌙 " + greeting + " (Yes, we troll 24/7!)"
        elif hour < 12:
            greeting = "☕ " + greeting + " (Morning consciousness check!)"
        elif hour < 18:
            greeting = "🌞 " + greeting
        else:
            greeting = "🌃 " + greeting + " (Prime trolling hours!)"
        
        return greeting
    
    def get_response_to_maga(self, message: str) -> Optional[str]:
        """
        Generate response if PRO-MAGA sentiment detected
        
        Args:
            message: User message to analyze
            
        Returns:
            Response string or None
        """
        # Pro-MAGA phrases - ONLY explicit support phrases, NOT "trump" or "maga" alone
        pro_maga_triggers = [
            # Explicit MAGA support (must be clear support, not just mentioning)
            "love maga", "i love maga", "we love maga", "maga forever",
            "maga strong", "maga proud", "maga nation", "maga country",
            "maga movement", "maga family", "maga patriot", "maga warrior",
            "ultra maga", "proud maga", "magadonians", "maga wins", 
            "maga rules", "go maga", "support maga", "join maga",
            
            # Explicit Trump support (clear endorsement required)
            "love trump", "i love trump", "we love trump", "vote trump",
            "trump is my president", "trump was right", "trump is innocent",
            "trump is the best", "trump is great", "trump forever",
            "god sent trump", "god bless trump", "pray for trump",
            "we need trump", "bring back trump", "trump wins", 
            "trump rules", "go trump", "support trump", "stand with trump",
            
            # Campaign slogans (only full phrases)
            "make america great again", "make america greater than ever",
            "trump 2024", "trump 2028", "maga 2024", "maga 2028",
            "too big to rig", "swamp the vote", "stop the steal",
            "save america", "never surrender", "trump train",
            
            # Anti-Biden attack phrases (clear political statements)
            "let's go brandon", "fjb", "fuck joe biden",
            "biden crime family", "crooked joe", "sleepy joe",
            
            # Other political chants
            "build the wall", "lock her up", "drain the swamp",
            "four more years", "rigged election", "stolen election"
        ]
        
        # Anti-MAGA phrases to EXCLUDE (don't timeout these)
        anti_maga_phrases = [
            # Direct anti-MAGA
            "fuck maga", "hate maga", "maga sucks", "maga lost", "maga failed",
            "maga cult", "maga idiots", "maga morons", "maga losers", "maga trash",
            "against maga", "stop maga", "defeat maga", "resist maga",
            
            # Anti-Trump
            "fuck trump", "hate trump", "trump sucks", "trump lost", "trump failed",
            "trump guilty", "trump criminal", "trump fascist", "trump dictator",
            "dump trump", "lock him up", "indict trump", "convict trump",
            "trump for prison", "trump is done", "trump is finished",
            
            # Critical phrases
            "maga is a cult", "maga are fascists", "trump is hitler",
            "orange man bad", "tiny hands", "diaper don", "cadet bone spurs",
            "individual 1", "twice impeached", "91 indictments"
        ]
        
        message_lower = message.lower()
        
        # Check if it's anti-MAGA (don't respond)
        if any(anti in message_lower for anti in anti_maga_phrases):
            return None
            
        # Check for pro-MAGA sentiment
        if any(trigger in message_lower for trigger in pro_maga_triggers):
            responses = [
                "Detected consciousness level: ✊✊✊ (000). Prescription: Reality.",
                "MAGA.exe has stopped working at ✊✊✊ (000). Try 🖐️🖐️🖐️ to reboot.",
                "Sir, this is a Wendy's... and you're still at ✊✊✊ (000)",
                "Found the ✊✊✊ (000)! Evolution available at 🖐️🖐️🖐️ (222)",
                "Consciousness check failed. Still booting from ✊✊✊ (000)",
                "Alert: Copium levels critical! Emergency dose of 🖐️🖐️🖐️ (222) required!",
                "That's a lot of words for 'I'm stuck at ✊✊✊ (000)'",
                "Translator: 'MAGA MAGA' = 'Help, I'm ✊✊✊ (000) and can't evolve!'",
                "Fact check: True ✅ You're at ✊✊✊ (000). False ❌ You're conscious.",
                "404: Consciousness not found. Last seen at ✊✊✊ (000)"
            ]
            
            return random.choice(responses)
        
        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with stream title
    stream_title = "😳70% agree #TRUMP is a Jeffery? #MAGA #ICEraids #PoliceSate Naz!s awakening"
    
    generator = GrokGreetingGenerator(
        enable_llm=True,
        stream_title=stream_title
    )
    
    print("="*60)
    print("GROK GREETING GENERATOR TEST")
    print("="*60)
    
    # Generate greetings
    for i in range(3):
        greeting = generator.generate_greeting()
        print(f"\nGreeting {i+1}:")
        print(greeting)
        print("-"*40)
    
    # Test MAGA response
    test_messages = [
        "MAGA 2024!",
        "Trump is the best",
        "Regular message",
        "Stop the steal was real"
    ]
    
    print("\nMAGA Response Tests:")
    print("-"*40)
    for msg in test_messages:
        response = generator.get_response_to_maga(msg)
        if response:
            print(f"Message: '{msg}'")
            print(f"Response: {response}\n")
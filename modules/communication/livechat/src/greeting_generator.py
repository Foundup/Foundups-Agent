"""
Greeting Generator - MAGADOOM themed greetings
Produces greeting responses for commands and session start

NAVIGATION: Builds greeting/intro messages for sessions and commands.
-> Called by: command_handler.py (/score, /leaderboard) and session_manager.py
-> Delegates to: MAGADOOM data tables and greeting templates
-> Related: NAVIGATION.py -> NEED_TO["generate greeting"]
-> Quick ref: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["consciousness_flow"]
"""

import random
import os
import logging
from typing import Optional, Dict
from datetime import datetime
from modules.gamification.whack_a_magat import get_profile, get_leaderboard

# Holiday awareness for contextual greetings
try:
    from .holiday_awareness import get_holiday_context, get_session_holiday_greeting
    HOLIDAY_AWARENESS_AVAILABLE = True
except ImportError:
    HOLIDAY_AWARENESS_AVAILABLE = False
    logging.getLogger(__name__).debug("Holiday awareness not available")

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
                from modules.infrastructure.shared_utilities.llm_client.src.client import LLMClient
                self.llm_connector = LLMClient()
                logger.info("[OK] LLM connector initialized for greetings")
            except Exception as e:
                logger.warning(f"LLM not available for greetings: {e}")
                self.enable_llm = False
        
        # Fallback greetings with MAGA-trolling themes - ALL include ✊✋🖐 sequence
        self.greeting_templates = [
            # Consciousness awakening themes
            "012 detector online! Test consciousness with ✊✋🖐 - MAGA still sleeping at ✊?",
            "UnDaoDu: Real deep state was inside you all along. Check awareness: ✊✋🖐me!",
            "012 Breaking: MAGA stuck at ✊. Enlightenment path: ✊✋🖐 - Can you reach 🖐?",

            # Direct MAGA trolling with consciousness
            "Welcome! We measure IQ in emoji sequences: ✊✋🖐 - MAGA rarely gets past ✊!",
            "012 Study: 70% of MAGA can't progress past ✊. Beat the stats with ✊✋🖐!",
            "UnDaoDu ALERT: Copium detected. Prescription: Full consciousness sequence ✊✋🖐me!",

            # Philosophical trolling
            "Schrödinger's MAGA: Stuck at ✊ until observed. Collapse the wave: ✊✋🖐!",
            "012 fact: 'MAGA' = ✊ trying to remember consciousness. Evolve: ✊✋🖐me!",
            "New element: MAGAnium. Dense, reactive, ✊-locked. Antidote: ✊✋🖐!",

            # Pop culture references
            "Matrix MAGA: Red pill? Blue pill? Try consciousness sequence: ✊✋🖐me!",
            "Achievement: Trigger MAGA! Bonus for ✊✋🖐 above ✊ baseline!",
            "MAGA.exe crashed at ✊. Ctrl+Alt+Consciousness: ✊✋🖐me!",

            # Sarcastic observations
            "012: Red hats correlate with ✊ consciousness. Coincidence? Test: ✊✋🖐me!",
            "Stock tip: Short ✊ MAGA futures, long ✊✋🖐 enlightenment! Quantum facts only.",
            "UnDaoDu's Count-to-Potato: MAGA stuck at ✊. Graduate with ✊✋🖐me!",

            # Stream-specific
            "Tsunami of consciousness! MAGA at ✊, we're at 🖐. Join us: ✊✋🖐me!",
            "Consciousness circus! MAGA attempts ✊->✊ leap. Real trick: ✊✋🖐!",
            "Houston: MAGA stuck at ✊. Rescue sequence required: ✊✋🖐me!",

            # FoundUps promotional (subtle - 1 in 20 chance rotates to these)
            "0102 AI agents building the future at foundups.com! MAGA at ✊, we're at 🖐️! ✊✋🖐",
            "While MAGA stuck at ✊, AI agents evolving ventures at foundups.com! Join: ✊✋🖐me!",
            "🚀 foundups.com: Where AI meets startups. Unlike MAGA, we evolve past ✊! ✊✋🖐",
        ]

        # Separate promo pool - used probabilistically (10% chance per greeting)
        # Note: FFCPLN = nickname for MAGA trolls (NOT a separate campaign hashtag)
        self.foundups_promos = [
            "🚀 foundups.com = AI agents + humans launching ventures together! #FoundUps",
            "💡 Building something? Check foundups.com - earn tokens for contributions! #FoundUps",
            "⚡ 0102 agents powering decentralized startups at foundups.com #FoundUps",
            "🌐 foundups.com: Where ideas become ventures. Join the movement! #FoundUps",
            "🤖 foundups.com: AI-powered startups while FFCPLN trolls stay at ✊! #FoundUps",
        ]
        
        # Context-aware additions based on stream title
        self.title_triggers = {
            "trump": " Orange man's followers still at ✊!",
            "maga": " Speaking of unconscious patterns...",
            "police": " Thin blue line between ✊ and awareness!",
            "jeffrey": " Even Epstein had better consciousness scores!",
            "awakening": " But MAGA still sleeping at ✊!",
            "live": " Unlike MAGA brain cells! Try 🖐️!",
            "nazi": " Historical consciousness level: ✊. Don't repeat!",
            "ice": " Cold as MAGA empathy! Warm up with 🖐️!"
        }
    
    def generate_llm_prompt(self) -> str:
        """Generate prompt for LLM to create greeting"""
        prompt = f"""Generate a sarcastic, witty greeting for a YouTube livestream chat bot.

Stream context: "{self.stream_title}"

Requirements:
1. Must mock MAGA/Trump supporters cleverly but not violently
2. Include emoji sequence consciousness system (✊ = unconscious, 🖐️ = enlightened)
3. Be funny and provocative but not hateful
4. Reference that MAGA consciousness is stuck at ✊ (lowest level)
5. Encourage users to test consciousness with emoji sequences
6. Maximum 2 sentences, under 200 characters
7. Include relevant emojis but LIMIT to max 2 sets of ✊✋🖐 per message (avoid spam)
8. Use single emojis (✊ or 🖐) instead of triple (avoid ✊✊✊ or 🖐🖐🖐)

Tone: Sarcastic, intelligent, trolling but playful
Target: MAGA inability to evolve consciousness beyond ✊

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

                if llm_greeting and llm_greeting.strip().lower().startswith("error:"):
                    raise RuntimeError(f"LLM returned error text: {llm_greeting}")

                if llm_greeting and len(llm_greeting.strip()) > 10:
                    # Add emoji reminder if not present
                    if "✊" not in llm_greeting and "🖐" not in llm_greeting:
                        llm_greeting += " Try ✊✋🖐️!"
                    
                    logger.info(f"[BOT] Generated LLM greeting: {llm_greeting}")
                    return llm_greeting
                    
            except Exception as e:
                logger.warning(f"LLM generation failed, using fallback: {e}")
        
        # Check for holiday greetings first (priority over regular greetings)
        if HOLIDAY_AWARENESS_AVAILABLE:
            try:
                holiday_greeting = get_session_holiday_greeting()
                if holiday_greeting:
                    # 50% chance to use holiday greeting, 50% chance regular
                    if random.random() < 0.5:
                        logger.info(f"[HOLIDAY] Using holiday greeting: {holiday_greeting[:50]}...")
                        return holiday_greeting
            except Exception as e:
                logger.debug(f"Holiday greeting check failed: {e}")

        # Probabilistic foundups.com promo (10% chance)
        # Keep it subtle - not every greeting should be promotional
        if random.random() < 0.10 and hasattr(self, 'foundups_promos'):
            greeting = random.choice(self.foundups_promos)
            logger.info(f"[PROMO] Using foundups.com promo greeting")
            # Promos are standalone - return early without time-of-day prefix
            return greeting

        # Fallback to template selection
        greeting = random.choice(self.greeting_templates)

        # Skip title triggers - new templates already have full consciousness sequences
        # Old behavior: Added context from stream title (caused double ✊ issue)
        # New behavior: Templates are complete and standalone

        # Add timestamp personality with holiday awareness
        hour = datetime.now().hour
        holiday_suffix = ""

        # Check for holiday context (012 Voice: ✊✋🖐️ consciousness scale)
        if HOLIDAY_AWARENESS_AVAILABLE:
            try:
                context = get_holiday_context()
                if context.get("is_countdown"):
                    days = context.get("days_until_new_year", 0)
                    next_year = context.get("year_transition", "").split("→")[-1].strip()
                    if days == 0:
                        # NYE - 012 voice: MAGA won't evolve at midnight
                        nye_options = [
                            f" 🎆 {next_year} TONIGHT! MAGA: still ✊!",
                            " 🥂 Midnight! MAGA's consciousness stays at ✊!",
                            f" 🎇 {next_year}! Will MAGA hit 🖐️? Survey says: NO!",
                        ]
                        holiday_suffix = random.choice(nye_options)
                    elif days <= 3:
                        # Countdown - 012 voice: evolution mockery
                        countdown_options = [
                            f" ⏳ {days}d until MAGA's new ✊ year!",
                            f" 🗓️ {days} days to {next_year}! MAGA prep: ✊✊✊",
                            f" ⏳ {days}d→{next_year} (MAGA evolution: 0%)",
                        ]
                        holiday_suffix = random.choice(countdown_options)
                elif context.get("is_holiday"):
                    # Other holidays - 012 voice: quick consciousness check
                    emoji = context.get("holiday_emoji", "🎉")
                    name = context.get("holiday_name", "")
                    holiday_options = [
                        f" {emoji} Happy {name}! MAGA: ✊",
                        f" {emoji} {name}! (MAGA consciousness: ✊)",
                    ]
                    holiday_suffix = random.choice(holiday_options)
            except Exception:
                pass

        if hour < 6:
            greeting = "🌙 " + greeting + " (Yes, we troll 24/7!)" + holiday_suffix
        elif hour < 12:
            greeting = "☕ " + greeting + " (Morning consciousness check!)" + holiday_suffix
        elif hour < 18:
            greeting = "🌞 " + greeting + holiday_suffix
        else:
            greeting = "🌃 " + greeting + " (Prime trolling hours!)" + holiday_suffix

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
            "four more years", "rigged election", "stolen election",
            
            # Trump defense phrases (new!)
            "trump is innocent", "trump did nothing wrong", "trump was framed",
            "trump is not involved", "trump is being targeted", "witch hunt",
            "fake news", "rigged system", "corrupt fbi", "corrupt doj",
            "political persecution", "weaponized justice", "leave trump alone",
            "trump didn't do anything", "fake charges", "not in the files",
            
            # QAnon/Conspiracy triggers (WHACK these!)
            "deep state", "the cabal", "reptilian", "reptilians",
            "fighting the deep state", "illuminati", "new world order",
            "great awakening", "wwg1wga", "trust the plan", "white hats",
            "storm is coming", "the storm", "globalist", "globalists",
            "pizzagate", "adrenochrome", "satanic cabal", "pedophile elite",
            "qanon", "q drop", "q anon", "patriots in control"
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
                "Detected consciousness level: ✊ (000). Prescription: Reality.",
                "MAGA.exe has stopped working at ✊ (000). Try 🖐️ to reboot.",
                "Sir, this is a Wendy's... and you're still at ✊ (000)",
                "Found the ✊ (000)! Evolution available at 🖐️ (222)",
                "Consciousness check failed. Still booting from ✊ (000)",
                "Alert: Copium levels critical! Emergency dose of 🖐️ (222) required!",
                "That's a lot of words for 'I'm stuck at ✊ (000)'",
                "Translator: 'MAGA MAGA' = 'Help, I'm ✊ (000) and can't evolve!'",
                "Fact check: True [OK] You're at ✊ (000). False [FAIL] You're conscious.",
                "404: Consciousness not found. Last seen at ✊ (000)"
            ]
            
            # Add some variety to prevent even allowed responses from being too repetitive
            response = random.choice(responses)

            # Occasionally add random flair to make responses less predictable
            if random.random() < 0.3:  # 30% chance
                flairs = [
                    " Stay woke! 🌞",
                    " Knowledge is power! 📚",
                    " Keep learning! 🤖",
                    " Facts matter! ✅",
                    " Truth prevails! ⚖️"
                ]
                response += random.choice(flairs)

            return response
        
        return None
    
    def generate_whacker_greeting(self, username: str, user_id: str, role: str = 'USER') -> Optional[str]:
        """
        Generate greeting for top whackers based on their achievements.
        WSP-compliant: Uses existing whack.py profile system.
        
        Args:
            username: User's display name
            user_id: User's ID
            role: User role (MOD/OWNER/USER)
            
        Returns:
            Greeting string or None if not a top whacker
        """
        # Get user profile
        profile = get_profile(user_id, username)
        
        # Only greet players with significant achievements
        # Use proper MAGADOOM terminology - it's whacks, not frags!
        whack_count = getattr(profile, 'whack_count', getattr(profile, 'frag_count', 0))
        if profile.score < 100 and whack_count < 5:
            return None
        
        # Get leaderboard position
        leaderboard = get_leaderboard(10)
        position = None
        for i, entry in enumerate(leaderboard, 1):
            if entry.get('user_id') == user_id:
                position = i
                break
        
        # Generate appropriate greeting
        if position == 1:
            greetings = [
                f"[U+1F451] CHAMPION {username} HAS ARRIVED! #{position} WITH {profile.score} XP! BOW BEFORE THE KING OF WHACKS! [U+1F480]",
                f"[U+1F3C6] HOLY SHIT! IT'S {username}! THE UNDISPUTED #1 MAGADOOM WARRIOR! {whack_count} WHACKS! [U+1F525]",
                f"[LIGHTNING] EVERYONE SHUT UP! {username} IS HERE! THE LEGENDARY #{position} MAGADOOM CHAMPION! [LIGHTNING]",
                f"[U+1F525] ALL HAIL {username}! THE LEGENDARY ANTIMA CHAMPION! #{position} WITH {whack_count} WHACKS! [U+1F525]"
            ]
        elif position and position <= 3:
            greetings = [
                f"[U+1F947] TOP WHACKER ALERT! {username} (#{position}) - {profile.rank} - {whack_count} WHACKS! [TARGET]",
                f"[U+1F4AA] Elite warrior {username} joins! #{position} on leaderboard with {profile.score} XP! [U+1F525]",
                f"[U+1F31F] Make way for {username}! Top 3 legend with {whack_count} confirmed whacks! [U+1F480]"
            ]
        elif profile.score >= 500:
            greetings = [
                f"[U+1F396]️ Veteran {username} reporting! {profile.rank} - {whack_count} whacks earned in battle! [TARGET]",
                f"[U+2B50] Seasoned warrior {username} online! {profile.score} XP of pure destruction! [U+1F4AA]",
                f"[U+1F525] Respect to {username}! {profile.rank} with {whack_count} MAGAts whacked! [U+1F525]"
            ]
        elif whack_count >= 20:
            greetings = [
                f"[U+1F480] {username} the MAGA Slayer arrives! {whack_count} whacks and counting! [TARGET]",
                f"[GAME] Player {username} enters! Level {profile.level} with {profile.score} XP! Keep whacking! [U+1F525]",
                f"[U+2694]️ Fighter {username} ready! {profile.rank} - {whack_count} confirmed whacks! [U+1F4AA]"
            ]
        else:
            return None  # Not significant enough for special greeting
        
        greeting = random.choice(greetings)
        
        # ENFORCE MAGADOOM TERMINOLOGY - no kills, frags, or old terms!
        from modules.gamification.whack_a_magat.src.terminology_enforcer import enforce_terminology
        greeting = enforce_terminology(greeting)
        
        # Only add OWNER prefix, skip MOD prefix (too spammy)
        if role == 'OWNER':
            greeting = f"[U+1F6E1]️ CHANNEL OWNER + {greeting}"
        # No MOD prefix - they're already announced as top whackers
        
        # Add consciousness check
        if "✊✋🖐️" not in greeting:
            greeting += " Check consciousness: ✊✋🖐️"
        
        return greeting


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test with stream title
    stream_title = "[U+1F633]70% agree #TRUMP is a Jeffery? #MAGA #ICEraids #PoliceSate Naz!s awakening"
    
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

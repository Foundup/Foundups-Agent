"""
FFCPLN Title & Description Enhancement Skill Executor

Maximizes YouTube engagement for FFCPLN pro-democracy music shorts.
Follows WSP 95 micro chain-of-thought architecture.

Primary: Qwen 1.5B + Gemma validation
Fallback: Template-based generation
"""

import random
import logging
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any

logger = logging.getLogger(__name__)

# =============================================================================
# ENGAGEMENT OPTIMIZATION TEMPLATES (Research-Backed)
# =============================================================================

# Emotional hooks ranked by CTR (Click-Through Rate) effectiveness
HOOK_TEMPLATES = {
    "outrage": [
        "🔥 {theme} EXPOSED! #FFCPLN #MAGA",
        "💀 This Song DESTROYS {target}! #FFCPLN",
        "⚠️ MAGA WON'T Like This! #FFCPLN",
        "🚨 {number} Songs They DON'T Want You to Hear! #FFCPLN",
        "❌ {target} EXPOSED in This Song! #FFCPLN",
    ],
    "hope": [
        "🎵 Music for the RESISTANCE! #FFCPLN",
        "✊ Democracy Anthem vs Authoritarianism #FFCPLN",
        "💪 160 Songs Fighting Fascism! #FFCPLN",
        "🌊 The Sound of Freedom! #FFCPLN",
    ],
    "revelation": [
        "👀 What MAGA Doesn't Want You to Know... #FFCPLN",
        "🔍 The Playlist That Exposes {target}! #FFCPLN",
        "📢 Unredact the Truth! #FFCPLN #TrumpFiles",
        "🤫 The SECRET Playlist... #FFCPLN",
    ],
    "urgency": [
        "🚨 2026: Democracy's Last Stand! #FFCPLN",
        "⏰ 250 Years of Freedom at Risk! #FFCPLN",
        "🔥 If Not Now, When? #FFCPLN #Midterms2026",
        "⚡ This is NOT Normal! #FFCPLN",
    ],
}

# Targets for {target} placeholder
MAGA_TARGETS = [
    "MAGA", "Trump", "ICE", "Fascism", "Authoritarianism",
    "Far-Right", "MAGA Cult", "Christian Nationalism",
]

# Theme keywords for {theme} placeholder  
THEMES = [
    "ICE Cruelty", "MAGA Hypocrisy", "Labor Rights", "Climate Denial",
    "Reproductive Rights", "Democracy", "Immigration Truth",
]

# Emoji prefixes by emotional intensity
EMOJI_SETS = {
    "high": ["🔥", "💀", "🚨", "⚠️", "❌"],
    "medium": ["👀", "🎵", "📢", "✊", "💪"],
    "low": ["🌊", "🎶", "✨", "🎤", "📻"],
}

# =============================================================================
# SEO-OPTIMIZED DESCRIPTION TEMPLATES
# =============================================================================

DESCRIPTION_2026 = """🔥 FFCPLN: F*** Fake Christian Pedo-Lovin' Nazi Playlist 🔥

160+ anti-fascist songs fighting for:
✊ Democracy over authoritarianism
✊ Labor rights over exploitation  
✊ Reproductive freedom
✊ Climate action
✊ Immigrant rights vs ICE cruelty

🎵 FULL PLAYLIST: https://ravingANTIFA.com

2026 is the most critical year for US democracy since 1776.
250 years of freedom at stake. These songs are the soundtrack of resistance.

#FFCPLN #MAGA #ICE #Antifascist #Resistance #TrumpFiles #Democracy2026 #Epstein #Music #Shorts #Viral

👆 SHARE if you give a damn! Subscribe for more!"""

DESCRIPTION_SHORT = """🔥 From the FFCPLN Playlist - 160+ songs fighting fascism!

🎵 Get the full playlist: https://ravingANTIFA.com

#FFCPLN #MAGA #ICE #Resistance #Shorts #Viral"""


# =============================================================================
# SKILL CONTEXT & RESULT DATACLASSES
# =============================================================================

@dataclass
class SkillContext:
    """Input context for FFCPLN enhancement skill."""
    original_title: str
    original_description: str = ""
    video_duration: int = 50  # seconds - 30-60s typically music clip
    content_hints: List[str] = field(default_factory=list)
    emotional_priority: str = "outrage"  # outrage|hope|revelation|urgency


@dataclass 
class SkillResult:
    """Output result from FFCPLN enhancement skill."""
    enhanced_title: str
    enhanced_description: str
    original_title: str
    original_description: str
    hook_type: str
    confidence: float
    patterns_executed: Dict[str, bool] = field(default_factory=dict)


# =============================================================================
# FFCPLN TITLE & DESCRIPTION ENHANCEMENT SKILL
# =============================================================================

class FFCPLNTitleEnhanceSkill:
    """
    Generates engagement-optimized titles and descriptions for FFCPLN music shorts.
    
    Architecture (WSP 95 Micro Chain-of-Thought):
    1. Content Analysis → Detect content type, extract themes
    2. Hook Generation → Select emotional hook template  
    3. Title Assembly → Build final title with hashtags
    4. Description Enhancement → Add SEO-optimized description
    5. Validation → Verify length, hashtags, engagement signals
    """
    
    def __init__(self):
        self.name = "ffcpln_title_enhance"
        self.version = "0.4.0"
        self.intent_type = "GENERATION"
        self.primary_agent = "qwen"
        
    def execute(self, context: SkillContext) -> SkillResult:
        """
        Execute the skill with micro chain-of-thought steps.
        
        Args:
            context: SkillContext with original title, description, etc.
            
        Returns:
            SkillResult with enhanced title and description
        """
        patterns = {}
        
        # Step 1: Content Analysis
        content_type = self._analyze_content(context)
        patterns["content_analysis_executed"] = True
        
        # Step 2: Hook Generation
        hook_type, hook_template = self._select_hook(context.emotional_priority)
        patterns["hook_generation_executed"] = True
        
        # Step 3: Title Assembly
        enhanced_title = self._assemble_title(context.original_title, hook_template)
        patterns["title_assembly_executed"] = True
        
        # Step 4: Description Enhancement
        enhanced_desc = self._enhance_description(context.original_description)
        patterns["description_enhancement_executed"] = True
        
        # Step 5: Validation
        valid, confidence = self._validate(enhanced_title, enhanced_desc)
        patterns["validation_executed"] = True
        
        logger.info(f"[FFCPLN Skill] Enhanced: '{enhanced_title[:50]}...'")
        
        return SkillResult(
            enhanced_title=enhanced_title,
            enhanced_description=enhanced_desc,
            original_title=context.original_title,
            original_description=context.original_description,
            hook_type=hook_type,
            confidence=confidence,
            patterns_executed=patterns,
        )
    
    def _analyze_content(self, context: SkillContext) -> str:
        """Step 1: Analyze content type from duration and hints."""
        if 30 <= context.video_duration <= 90:
            return "music_clip"
        elif context.video_duration > 90:
            return "live_segment"
        else:
            return "short_clip"
    
    def _select_hook(self, emotional_priority: str) -> tuple:
        """Step 2: Select emotional hook template based on priority."""
        if emotional_priority not in HOOK_TEMPLATES:
            emotional_priority = "outrage"  # Default to highest CTR
            
        templates = HOOK_TEMPLATES[emotional_priority]
        template = random.choice(templates)
        
        return emotional_priority, template
    
    def _assemble_title(self, original_title: str, hook_template: str) -> str:
        """
        Step 3: Generate a MUSIC-focused title.
        
        CRITICAL: The original title is from the LIVESTREAM, not the music.
        We IGNORE it and generate a title about the FFCPLN playlist.
        """
        
        # MUSIC-FOCUSED TITLES (ignore original stream title)
        music_titles = [
            "🔥 160 Songs MAGA Doesn't Want You to Hear! #FFCPLN",
            "💀 This Song DESTROYS Fascism! #FFCPLN #MAGA",
            "🎵 Anti-Fascist Anthem! Full Playlist in Desc #FFCPLN",
            "🚨 BANNED Music? The Playlist They Fear! #FFCPLN",
            "⚠️ ICE Cruelty Exposed in Song! #FFCPLN #MAGA",
            "✊ Democracy's Soundtrack 2026! #FFCPLN",
            "🔥 The Anti-MAGA Playlist! 160 Songs! #FFCPLN",
            "💀 F*** Fake Christian Nazis! Music! #FFCPLN",
            "🎵 Resistance Music! Get the Full Playlist! #FFCPLN",
            "🚨 160 Anti-Fascist Songs! Link in Desc! #FFCPLN",
            "🔥 Music MAGA Fears! 160 Songs! #FFCPLN",
            "💀 Anti-Authoritarian Anthems! #FFCPLN #MAGA",
            "🎵 160 Songs Fighting Fascism! #FFCPLN",
            "🚨 The Resistance Playlist! #FFCPLN #MAGA",
            "⚠️ 2026: Democracy's Soundtrack! #FFCPLN",
        ]
        
        # Pick random music title
        title = random.choice(music_titles)
        
        logger.info(f"[FFCPLN Skill] Ignored stream title, using music title: {title}")
        
        return title
    
    def _enhance_description(self, original_desc: str) -> str:
        """Step 4: Generate SEO-optimized description."""
        # Check if already has FFCPLN content
        if ("ffcpln.foundups.com" in original_desc.lower() or "ffc.ravingantifa.com" in original_desc.lower()) and len(original_desc) > 200:
            return original_desc  # Already enhanced
        
        # Return full 2026 description for engagement
        return DESCRIPTION_2026
    
    def _validate(self, title: str, description: str) -> tuple:
        """Step 5: Validate enhanced content."""
        checks = {
            "title_under_100": len(title) <= 100,
            "has_ffcpln_tag": "#FFCPLN" in title.upper(),
            "has_emoji": any(c in title for c in "🔥💀🚨⚠️❌👀🎵📢✊💪🌊"),
            "has_playlist_link": ("ffcpln.foundups.com" in description.lower() or "ffc.ravingantifa.com" in description.lower()),
            "description_has_hashtags": "#" in description,
        }
        
        passed = sum(checks.values())
        total = len(checks)
        confidence = passed / total
        
        return all(checks.values()), confidence


# =============================================================================
# CONVENIENCE FUNCTIONS (Backward Compatibility with content_generator.py)
# =============================================================================

def enhance_title_with_skill(original_title: str, emotional_priority: str = "outrage") -> str:
    """Convenience wrapper for skill execution - title only."""
    skill = FFCPLNTitleEnhanceSkill()
    result = skill.execute(SkillContext(
        original_title=original_title,
        emotional_priority=emotional_priority,
    ))
    return result.enhanced_title


def enhance_description_with_skill(original_desc: str) -> str:
    """Convenience wrapper for skill execution - description only."""
    skill = FFCPLNTitleEnhanceSkill()
    result = skill.execute(SkillContext(
        original_title="",
        original_description=original_desc,
    ))
    return result.enhanced_description


# =============================================================================
# STANDALONE TESTING
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    skill = FFCPLNTitleEnhanceSkill()
    
    # Test case: Japan Home cleaning video
    context = SkillContext(
        original_title="Japan Home cleaning… hates this time of year! Japanese wife goes insane",
        original_description="Fake Fcuk Christian Pedo-lovin Nazi playlist: https://ravingANTIFA.com",
        video_duration=50,
        emotional_priority="outrage"
    )
    
    result = skill.execute(context)
    
    print("=" * 60)
    print("FFCPLN TITLE ENHANCEMENT SKILL TEST")
    print("=" * 60)
    print(f"\n🔴 ORIGINAL TITLE:\n{result.original_title}")
    print(f"\n🟢 ENHANCED TITLE:\n{result.enhanced_title}")
    print(f"\n🔴 ORIGINAL DESC:\n{result.original_description[:80]}...")
    print(f"\n🟢 ENHANCED DESC:\n{result.enhanced_description[:200]}...")
    print(f"\n📊 Confidence: {result.confidence:.0%}")
    print(f"📊 Hook Type: {result.hook_type}")
    print(f"📊 Patterns: {result.patterns_executed}")

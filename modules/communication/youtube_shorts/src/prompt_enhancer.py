"""
Move2Japan Prompt Enhancement System

Multi-stage prompt engineering for Veo 3 video generation.
Incorporates:
- Japan trending topics (2025)
- Move2Japan brand voice (fun, cheeky, authentic)
- Anti-MAGA positioning (progress, inclusion, facts)
- Viral engagement hooks
"""

import random
from typing import Optional
import google.generativeai as genai


class Move2JapanPromptEnhancer:
    """
    Advanced prompt enhancement for Move2Japan YouTube Shorts.

    Creates engaging, authentic Japan content that:
    - Showcases real Japan (not stereotypes)
    - Appeals to progressive values (anti-MAGA)
    - Uses trending formats and topics
    - Maximizes viral potential
    """

    def __init__(self):
        """Initialize prompt enhancer with style guidelines."""

        # Japan 2025 trending topics
        self.trending_topics = [
            "BeReal-style authentic moments",
            "LINE social commerce",
            "K-beauty (fwee cosmetics)",
            "Angel Mode pastel aesthetics",
            "TikTok viral challenges",
            "Sustainability initiatives",
            "Plant-based ramen",
            "Neo-retro Showa nostalgia",
            "Digital nomad cafes"
        ]

        # Visual style templates
        self.visual_styles = {
            "cinematic_reveal": "smooth pan revealing hidden details, golden hour lighting, cinematic composition",
            "pov_discovery": "first-person perspective, natural movement, surprising discovery moment",
            "cultural_moment": "everyday Japanese scene, uniquely cultural detail, emotional payoff",
            "nature_urban_blend": "natural beauty integrated with modern urban life, harmonious contrast",
            "cozy_comfort": "warm lighting, intimate framing, satisfying sensory details",
            "viral_trend": "trending format, playful execution, highly shareable moment"
        }

        # Anti-MAGA positioning (implicit through values)
        self.progressive_values = [
            "multicultural harmony (diverse people enjoying Japan together)",
            "environmental consciousness (sustainable practices, clean energy)",
            "gender equality (women in leadership, non-traditional roles)",
            "scientific/technological progress (innovation, evidence-based)",
            "inclusivity (LGBTQ+ friendly spaces, accessibility)",
            "community over individualism (cooperative culture)",
            "education and expertise (valuing knowledge, craft mastery)",
            "fact-based reality (real experiences vs propaganda)"
        ]

        # Engagement hooks
        self.hooks = {
            "surprise": [
                "You won't believe",
                "Wait until you see",
                "This will blow your mind",
                "Nobody talks about this"
            ],
            "pov": [
                "POV: You discover",
                "POV: Your first time",
                "POV: You realize",
                "POV: The moment when"
            ],
            "secret": [
                "Locals hide this from tourists",
                "The secret spot nobody knows",
                "Hidden gem only Japanese people visit",
                "What guidebooks won't tell you"
            ],
            "anti_maga": [
                "Why Japan gets it right",
                "Facts MAGA won't accept",
                "This is what progress looks like",
                "Real democracy in action"
            ]
        }

    def enhance(
        self,
        simple_topic: str,
        include_anti_maga: bool = False,
        use_trending: bool = True,
        style: Optional[str] = None
    ) -> str:
        """
        Enhance simple topic into Veo 3-optimized prompt.

        Args:
            simple_topic: User's simple topic (e.g., "cherry blossoms")
            include_anti_maga: Add subtle progressive values positioning
            use_trending: Incorporate 2025 trending elements
            style: Visual style template to use (or random if None)

        Returns:
            str: Enhanced Veo 3 prompt (optimized for video generation)
        """

        # Select visual style
        if style is None or style not in self.visual_styles:
            style = random.choice(list(self.visual_styles.keys()))

        style_template = self.visual_styles[style]

        # Build enhancement components
        components = []

        # Add location specificity
        components.append(self._add_location(simple_topic))

        # Add cultural authenticity
        components.append(self._add_cultural_elements(simple_topic))

        # Add trending elements if requested
        if use_trending:
            components.append(self._add_trending_elements(simple_topic))

        # Add progressive values if requested
        if include_anti_maga:
            components.append(self._add_progressive_values())

        # Add sensory details
        components.append(self._add_sensory_details(simple_topic))

        # Add camera movement
        components.append(self._add_camera_movement())

        # Add lighting
        components.append(self._add_lighting())

        # Add human element
        components.append(self._add_human_element())

        # Add talking baby (Move2Japan signature - ALWAYS included)
        components.append(self._add_talking_baby())

        # Combine into final prompt
        enhanced_prompt = ", ".join([c for c in components if c])

        # Add visual style template
        enhanced_prompt += f", {style_template}"

        return enhanced_prompt

    def _add_location(self, topic: str) -> str:
        """Add specific Japanese location."""
        locations = {
            "cherry blossom": "Meguro River, Tokyo",
            "ramen": "Dotonbori, Osaka",
            "temple": "Fushimi Inari, Kyoto",
            "street": "Shibuya, Tokyo",
            "garden": "Kenrokuen, Kanazawa",
            "mountain": "Mount Fuji from Hakone",
            "cafe": "Kichijoji, Tokyo",
            "train": "Yamanote Line, Tokyo",
            "vending machine": "Late-night Tokyo street",
            "onsen": "Hakone mountain resort"
        }

        for keyword, location in locations.items():
            if keyword in topic.lower():
                return f"Specific location: {location}"

        return "Authentic Japanese location"

    def _add_cultural_elements(self, topic: str) -> str:
        """Add uniquely Japanese cultural details."""
        elements = [
            "traditional wooden architecture details",
            "perfectly arranged seasonal decorations",
            "respectful bowing between people",
            "meticulous food presentation",
            "zen garden raked gravel patterns",
            "colorful noren curtains swaying",
            "seasonal wagashi confections",
            "handwritten Japanese calligraphy signs",
            "precisely folded origami cranes",
            "traditional tatami mat texture"
        ]

        return random.choice(elements)

    def _add_trending_elements(self, topic: str) -> str:
        """Add 2025 trending topics/formats."""
        return f"trending style: {random.choice(self.trending_topics)}"

    def _add_progressive_values(self) -> str:
        """Add subtle progressive positioning (anti-MAGA)."""
        return random.choice(self.progressive_values)

    def _add_sensory_details(self, topic: str) -> str:
        """Add sensory immersion."""
        sensory = [
            "steam rising with visible particles",
            "soft glow reflecting in rain puddles",
            "gentle breeze moving fabric/leaves",
            "warm light spilling through doorways",
            "delicate water droplets on surfaces",
            "subtle lens flare from natural light",
            "atmospheric mist drifting through air",
            "rich texture and depth of field"
        ]

        return random.choice(sensory)

    def _add_camera_movement(self) -> str:
        """Add dynamic camera work."""
        movements = [
            "slow smooth pan from left to right",
            "gradual zoom revealing intricate details",
            "subtle tracking shot following movement",
            "gentle tilt up to reveal the scene",
            "circular orbit around the subject",
            "smooth dolly in for intimate framing",
            "low angle ascending to eye level",
            "pull back to show full context"
        ]

        return random.choice(movements)

    def _add_lighting(self) -> str:
        """Add cinematic lighting."""
        lighting = [
            "golden hour warm soft light",
            "neon glow with vibrant color palette",
            "dappled sunlight through leaves",
            "soft diffused overcast luminosity",
            "dramatic side lighting creating depth",
            "warm interior amber illumination",
            "cool blue twilight atmosphere",
            "high-key bright natural daylight"
        ]

        return random.choice(lighting)

    def _add_human_element(self) -> str:
        """Add relatable human presence."""
        humans = [
            "a person pauses in genuine wonder",
            "someone smiles with quiet satisfaction",
            "a local nods approvingly",
            "a child points excitedly",
            "friends share a knowing glance",
            "a craftsperson works with focused care",
            "a elderly person moves gracefully",
            "a young professional discovers something new"
        ]

        return random.choice(humans)

    def _add_talking_baby(self) -> str:
        """Add adorable talking baby character (Move2Japan signature element)."""
        baby_narrations = [
            "cute baby in tiny yukata giggling and babbling 'Japan! Japan!' with pure excitement",
            "adorable toddler pointing with chubby fingers saying 'Ooh! Pretty!' in awe",
            "baby in traditional Japanese outfit making excited 'wow!' sounds with big sparkling eyes",
            "little one waddling into frame in kimono-style onesie with infectious baby laugh",
            "baby bouncing happily saying 'Move! Japan!' in adorable baby voice with huge smile",
            "toddler clapping tiny hands together exclaiming 'Amazing!' with joyful squeals",
            "cute baby reaching out saying 'Want go Japan!' with hopeful bright eyes",
            "baby narrator doing voice-over in adorable babble-English explaining the scene"
        ]

        return random.choice(baby_narrations)

    def create_anti_maga_japan_prompt(self, topic: str) -> str:
        """
        Create prompt that subtly positions Japan as progressive alternative.

        Examples of implicit anti-MAGA messaging:
        - Universal healthcare (vs US system)
        - Gun-free society (safety, no school shootings)
        - High-speed rail (infrastructure investment)
        - Clean energy (environmental leadership)
        - Mask-wearing respect (community health)
        - Education excellence (valuing expertise)
        - Low crime (social cohesion)
        - Worker protections (vs exploitation)

        Args:
            topic: User's topic

        Returns:
            str: Prompt highlighting progressive Japan vs regressive MAGA
        """

        anti_maga_themes = {
            "healthcare": "person using Japan's universal healthcare at affordable clinic, no bankruptcy, just routine care with dignity",
            "safety": "children walking to school alone safely, no armed guards needed, society built on trust not fear",
            "trains": "bullet train departing precisely on time, infrastructure investment that actually works, not crumbling like MAGA states",
            "masks": "people respectfully wearing masks during cold season, caring about community health, science-based behavior",
            "education": "students in well-funded public school, learning critical thinking, not book bans",
            "climate": "solar panels on traditional roofs, renewable energy integrated into daily life, future-focused society",
            "guns": "police officer without gun successfully de-escalating situation, civilized society, no 2nd Amendment worship",
            "voting": "easy accessible voting stations with automatic registration, democracy that works"
        }

        # Check if topic matches anti-MAGA theme
        for keyword, theme_prompt in anti_maga_themes.items():
            if keyword in topic.lower():
                return self.enhance(theme_prompt, include_anti_maga=True)

        # Default: Add general progressive values
        return self.enhance(topic, include_anti_maga=True)

    def create_viral_hook(self, topic: str, hook_type: str = "surprise") -> str:
        """
        Create viral-optimized opening hook.

        Args:
            topic: Video topic
            hook_type: Type of hook (surprise, pov, secret, anti_maga)

        Returns:
            str: Viral hook phrase
        """

        if hook_type not in self.hooks:
            hook_type = "surprise"

        hook_phrase = random.choice(self.hooks[hook_type])

        return f"{hook_phrase}: {topic}"


# Example usage
if __name__ == "__main__":
    enhancer = Move2JapanPromptEnhancer()

    # Example 1: Simple enhancement
    topic1 = "Cherry blossoms in Tokyo"
    enhanced1 = enhancer.enhance(topic1)
    print(f"Topic: {topic1}")
    print(f"Enhanced: {enhanced1}\n")

    # Example 2: Anti-MAGA positioning
    topic2 = "Japan's universal healthcare"
    enhanced2 = enhancer.create_anti_maga_japan_prompt(topic2)
    print(f"Topic: {topic2}")
    print(f"Enhanced: {enhanced2}\n")

    # Example 3: Viral hook
    topic3 = "Vending machine with hot soup"
    hook3 = enhancer.create_viral_hook(topic3, "surprise")
    print(f"Hook: {hook3}")

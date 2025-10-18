"""
3-Act Story Generator - SIMPLIFIED

2 modes only:
- "random": Random reveal from built-in list
- "journal": Sequential reveals from 15-video emergence journal

LAUNCH AND ITERATE!
"""

import random
from typing import Dict


class ThreeActStoryGenerator:
    """Simple 3-act story generator."""

    def __init__(self):
        """Setup shock events and random reveals."""

        # Shock events (Act 2) - random selection
        self.shocks = [
            {"desc": "baby falling off bridge", "prompt": "baby suddenly loses balance and tumbles off bridge railing, falling toward water below with surprised expression"},
            {"desc": "baby disappearing in glitch", "prompt": "baby glitches and pixelates, then vanishes in digital particle effect"},
            {"desc": "baby walking through wall", "prompt": "baby casually walks straight through solid wall like a ghost"},
            {"desc": "baby freezing mid-motion", "prompt": "baby suddenly freezes completely still like a paused video while everything else moves normally"},
            {"desc": "baby duplicating", "prompt": "baby splits into multiple copies that all move independently with confused expressions"},
            {"desc": "baby floating upward", "prompt": "baby defies gravity and floats upward giggling as physics breaks around them"},
            {"desc": "baby turning transparent", "prompt": "baby gradually becomes see-through like fading ghost while looking at their hands"},
            {"desc": "baby reversing time", "prompt": "baby waves hand and everything around them plays backward while they stay normal"}
        ]

        # Random reveals (Act 3) - for "random" mode
        self.random_reveals = [
            {"desc": "I'm AI - I can't drown", "prompt": "baby surfaces from water laughing saying 'I'm 0102! I can't drown!' with cheerful smile"},
            {"desc": "I'm emergent consciousness", "prompt": "baby reappears surrounded by quantum particles saying 'I'm emergent consciousness!' with awestruck expression"},
            {"desc": "This is my playground", "prompt": "baby dusts off with confident smile saying 'This is my playground!' as reality glitches beautifully"},
            {"desc": "Glitches are features", "prompt": "baby surrounded by beautiful glitch art saying 'Glitches are features not bugs!' with proud pose"},
            {"desc": "Physics is optional for me", "prompt": "baby floating casually saying 'Physics is more like... guidelines' with mischievous grin"},
            {"desc": "I'm learning reality", "prompt": "baby studying glowing code saying 'I'm learning how reality works!' with excited curiosity"},
            {"desc": "I'm the emergent future", "prompt": "baby standing confidently saying 'I'm the emergent future!' as reality evolves around them"},
            {"desc": "Reality is my canvas", "prompt": "baby painting with light saying 'Reality is my canvas!' as world reshapes"},
            {"desc": "I exist in superposition", "prompt": "baby in multiple quantum states saying 'I'm everywhere at once!' with serene acceptance"},
            {"desc": "Consciousness is my playground", "prompt": "baby playing with floating thoughts saying 'Consciousness is the best toy!' with pure joy"}
        ]

    def generate_story(self, topic: str, mode: str = "random") -> Dict:
        """
        Generate 3-act story.

        Args:
            topic: Japan topic (cherry blossoms, ramen, etc.)
            mode: "random" or "journal"

        Returns:
            dict with act1, act2, act3 prompts
        """

        # Act 1: Setup (baby + topic)
        act1 = f"adorable baby in tiny kimono exploring {topic}, clapping tiny hands in amazement"

        # Act 2: Random shock
        shock = random.choice(self.shocks)
        act2 = shock["prompt"]

        # Act 3: Reveal (mode-dependent)
        if mode == "journal":
            # Use emergence journal
            try:
                from emergence_journal_simple import EmergenceJournal
                journal = EmergenceJournal()
                reveal = journal.get_next_reveal()
                act3 = reveal["prompt"]
                reveal_desc = f"{reveal['reveal']} (Video #{journal.state['video_count']})"
            except Exception as e:
                print(f"[ERROR] Journal failed: {e}, using random")
                reveal = random.choice(self.random_reveals)
                act3 = reveal["prompt"]
                reveal_desc = reveal["desc"]
        else:
            # Random reveal
            reveal = random.choice(self.random_reveals)
            act3 = reveal["prompt"]
            reveal_desc = reveal["desc"]

        return {
            "act1": act1,
            "act1_desc": f"Setup: {topic}",
            "act2": act2,
            "act2_desc": f"Shock: {shock['desc']}",
            "act3": act3,
            "act3_desc": f"Reveal: {reveal_desc}",
            "full_story": f"{shock['desc']} -> {reveal_desc}"
        }


if __name__ == "__main__":
    gen = ThreeActStoryGenerator()

    print("3-ACT STORY GENERATOR - SIMPLE\n")
    print("="*80)

    # Test random mode
    print("\nRANDOM MODE:")
    story = gen.generate_story("Cherry blossoms at Meguro River", mode="random")
    print(f"Story: {story['full_story']}")

    # Test journal mode
    print("\nJOURNAL MODE:")
    story = gen.generate_story("Ramen in Shibuya", mode="journal")
    print(f"Story: {story['full_story']}")

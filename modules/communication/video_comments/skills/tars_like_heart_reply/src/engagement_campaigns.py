"""
Engagement Campaigns Module
Defines specific topics and strategies for "Smart Engagement" (Skillz 0/1/2).
"""

import random
from typing import Dict, Any, Optional

class CampaignManager:
    """
    Manages engagement campaigns and topic selection.
    """
    
    # Campaign Definitions
    CAMPAIGNS = {
        "FFCPLN": {
            "id": "FFCPLN",
            "topic": "Freedom Foundups Coalition Playlist",
            "style": "Energetic, Musical",
            "prompt_instruction": (
                "Ask the user if they have heard the new #FFCPLN songs on ffc.foundups.com. "
                "Mention that 'The algorithm hates this playlist' or similar intrigue."
            )
        },
        "JAPAN_HOUSING": {
            "id": "JAPAN_HOUSING",
            "topic": "Japan Empty Homes Crisis",
            "style": "Informative, Slightly Shocking",
            "prompt_instruction": (
                "Did you know there are over 9 million empty homes (Akiya) in Japan, "
                "and only about 60% are even listed? Ask for their thoughts on this waste."
            )
        },
        "TRUMP_POLITICS": {
            "id": "TRUMP_POLITICS",
            "topic": "Political Engagement (Trump/America)",
            "style": "Bold, Patriotic (or questioning)",
            "prompt_instruction": (
                "Ask a provocative question about Trump or the state of the US. "
                "E.g., 'Do you like Trump?' or 'USA needs you, keep fighting!' depending on context."
            )
        },
        "GENERAL_ENGAGEMENT": {
            "id": "GENERAL_ENGAGEMENT",
            "topic": "General Channel Engagement",
            "style": "Curious, Welcoming",
            "prompt_instruction": "Ask a relevant question about the video topic or their comment to drive engagement."
        }
    }

    @staticmethod
    def select_campaign(
        is_new_user: bool, 
        last_sentiment: str = "neutral",
        force_campaign: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Selects a campaign based on user context.
        """
        if force_campaign and force_campaign in CampaignManager.CAMPAIGNS:
            return CampaignManager.CAMPAIGNS[force_campaign]

        # LOGIC: New Users get specific "Hook" questions
        if is_new_user:
            # Randomly rotate between our top hooks
            choice = random.choice(["FFCPLN", "JAPAN_HOUSING", "TRUMP_POLITICS"])
            return CampaignManager.CAMPAIGNS[choice]
        
        # LOGIC: Returning Users (context dependent)
        # If they are returning, we might mock them (if sentiment was negative) or affirm them
        # Campaigns are secondary to the "Relationship" (Mock vs Support) logic handled in Processor
        # regarding topics, we can still inject one occasionally.
        
        if random.random() < 0.3: # 30% chance to inject a campaign topic even for returning users
             choice = random.choice(["FFCPLN", "JAPAN_HOUSING"])
             return CampaignManager.CAMPAIGNS[choice]
        
        return {"id": "NONE", "prompt_instruction": "Focus on the user's comment content directly."}

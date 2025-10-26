# -*- coding: utf-8 -*-
"""
Qwen-Powered Duke Nukem Announcer
WSP-Compliant: Integrates Duke Nukem callouts with banter engine via Qwen intelligence
WSP 90 Compliant: UTF-8 encoding enforced

Features:
- Monitors top 10 MAGADOOM leaderboard for active/past sprees
- Injects Duke Nukem callouts into 50% of banter responses
- Uses Qwen to intelligently select announcement moments
- Proactive spree announcements (not just reactive to timeouts)
"""

import logging
import random
import time
from typing import Optional, Dict, List, Any, Tuple
from datetime import datetime, timedelta

# Import whack system for leaderboard access
from modules.gamification.whack_a_magat.src.whack import get_leaderboard, get_profile
from modules.gamification.whack_a_magat.src.spree_tracker import get_active_sprees, get_best_sprees

# Import Qwen for intelligent announcement decisions
try:
    from holo_index.qwen_advisor.llm_engine import QwenInferenceEngine
    QWEN_AVAILABLE = True
except ImportError:
    QWEN_AVAILABLE = False
    logging.warning("Qwen not available - using fallback announcement logic")

logger = logging.getLogger(__name__)


class QwenDukeAnnouncer:
    """
    Qwen-powered Duke Nukem announcer that monitors leaderboard and generates
    proactive spree announcements for the banter engine.
    """
    
    def __init__(self):
        self.qwen_engine = None
        if QWEN_AVAILABLE:
            try:
                self.qwen_engine = QwenInferenceEngine(
                    max_tokens=100,
                    temperature=0.9  # High temperature for creative Duke callouts
                )
                logger.info("🔥 Qwen Duke Announcer initialized with AI intelligence")
            except Exception as e:
                logger.warning(f"Qwen initialization failed: {e}")
        
        # Duke Nukem callout templates
        self.duke_callouts = {
            "spree_active": [
                "🎮 {name} on a {streak}-WHACK KILLING SPREE! 'Come get some!'",
                "💀 {name} is DOMINATING with {streak} whacks! 'Hail to the king, baby!'",
                "🔥 {name} - {streak} WHACKS IN A ROW! 'Damn, I'm good!'",
                "⚡ {name} UNSTOPPABLE: {streak} FRAGS! 'It's time to kick ass!'",
                "☠️ {name} is GODLIKE! {streak} whacks! 'Rest in pieces!'"
            ],
            "spree_ended": [
                "💥 {name}'s {streak}-whack spree just ended! 'Shake it baby!'",
                "🎯 {name} finished with {streak} frags! 'Groovy!'",
                "🏆 {name} completed a {streak}-whack run! 'Impressive!'"
            ],
            "leaderboard_top": [
                "👑 {name} LEADING the board with {score} XP! 'Who wants some?!'",
                "🌟 {name} at #1 - {score} points! 'Nobody steals our chicks!'",
                "🔥 Top dog {name}: {score} XP! 'I've got balls of steel!'"
            ],
            "milestone_reached": [
                "🎆 {name} just hit {milestone}! 'Blow it out your ass!'",
                "💀 {name} reached {milestone} frags! 'You're an inspiration!'",
                "⚡ MILESTONE: {name} - {milestone}! 'Let God sort 'em out!'"
            ]
        }
        
        # Tracking
        self.last_announcement_time = 0
        self.announcement_cooldown = 30  # 30 seconds between Duke announcements
        self.announced_sprees = set()  # Track which sprees we've announced
        self.last_leaderboard_check = 0
        self.leaderboard_cache = []
        
    def should_inject_duke_callout(self) -> bool:
        """
        Decide if we should inject a Duke callout (50% chance + cooldown check).
        """
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_announcement_time < self.announcement_cooldown:
            return False
        
        # 50% chance
        return random.random() < 0.5
    
    def get_duke_announcement(self, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Generate a Duke Nukem announcement based on current leaderboard/spree state.
        
        Uses Qwen to intelligently select the best announcement type.
        
        Args:
            context: Optional context about current chat (user message, etc.)
            
        Returns:
            Duke callout string or None
        """
        if not self.should_inject_duke_callout():
            return None
        
        try:
            # Get current game state
            game_state = self._get_game_state()
            
            if not game_state:
                return None
            
            # Use Qwen to decide WHAT to announce
            announcement = self._generate_intelligent_announcement(game_state, context)
            
            if announcement:
                self.last_announcement_time = time.time()
                logger.info(f"🎮 Duke announcement: {announcement[:60]}...")
                
            return announcement
            
        except Exception as e:
            logger.error(f"Duke announcement error: {e}")
            return None
    
    def _get_game_state(self) -> Optional[Dict[str, Any]]:
        """
        Gather current game state: leaderboard, active sprees, etc.
        """
        current_time = time.time()
        
        # Cache leaderboard for 60 seconds
        if current_time - self.last_leaderboard_check > 60:
            self.leaderboard_cache = get_leaderboard(limit=10)
            self.last_leaderboard_check = current_time
        
        if not self.leaderboard_cache:
            return None
        
        # Get active sprees
        active_sprees = get_active_sprees()
        
        # Get best sprees (recent history)
        best_sprees = get_best_sprees(limit=5)
        
        return {
            "leaderboard": self.leaderboard_cache,
            "active_sprees": active_sprees,
            "best_sprees": best_sprees,
            "top_player": self.leaderboard_cache[0] if self.leaderboard_cache else None
        }
    
    def _generate_intelligent_announcement(
        self, 
        game_state: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Use Qwen to intelligently generate the best Duke announcement.
        
        Falls back to rule-based selection if Qwen unavailable.
        """
        if self.qwen_engine and QWEN_AVAILABLE:
            return self._qwen_announcement(game_state, context)
        else:
            return self._fallback_announcement(game_state)
    
    def _qwen_announcement(
        self,
        game_state: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Use Qwen to generate intelligent Duke Nukem announcement.
        """
        try:
            # Build prompt for Qwen
            prompt = self._build_qwen_prompt(game_state, context)
            
            system_prompt = (
                "You are Duke Nukem announcing MAGADOOM leaderboard status. "
                "Pick the BEST announcement type: spree_active, leaderboard_top, or milestone_reached. "
                "Respond with ONLY the category name, nothing else."
            )
            
            # Get Qwen's decision
            decision = self.qwen_engine.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=20
            )
            
            # Parse decision and generate announcement
            announcement_type = decision.strip().lower()
            
            if "spree" in announcement_type and game_state["active_sprees"]:
                spree = game_state["active_sprees"][0]
                return self._format_spree_announcement(spree)
            
            elif "leaderboard" in announcement_type or "top" in announcement_type:
                top_player = game_state["top_player"]
                if top_player:
                    return self._format_leaderboard_announcement(top_player)
            
            elif "milestone" in announcement_type:
                return self._format_milestone_announcement(game_state)
            
            # Fallback
            return self._fallback_announcement(game_state)
            
        except Exception as e:
            logger.warning(f"Qwen announcement failed: {e}, using fallback")
            return self._fallback_announcement(game_state)
    
    def _build_qwen_prompt(
        self,
        game_state: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> str:
        """
        Build prompt for Qwen decision-making.
        """
        prompt_parts = ["Current MAGADOOM game state:"]
        
        # Top player
        if game_state["top_player"]:
            top = game_state["top_player"]
            prompt_parts.append(f"- Top player: {top['name']} with {top['score']} XP")
        
        # Active sprees
        if game_state["active_sprees"]:
            spree = game_state["active_sprees"][0]
            prompt_parts.append(f"- Active spree: {spree['mod_name']} on {spree['frag_count']}-frag run")
        
        # Recent best
        if game_state["best_sprees"]:
            best = game_state["best_sprees"][0]
            prompt_parts.append(f"- Recent best: {best['mod_name']} - {best['frag_count']} frags")
        
        prompt_parts.append("\nWhat should Duke announce? (spree_active / leaderboard_top / milestone_reached)")
        
        return "\n".join(prompt_parts)
    
    def _fallback_announcement(self, game_state: Dict[str, Any]) -> Optional[str]:
        """
        Fallback rule-based announcement selection.
        """
        # Priority 1: Active sprees
        if game_state["active_sprees"]:
            spree = game_state["active_sprees"][0]
            # Don't re-announce same spree
            spree_id = f"{spree['mod_id']}_{spree['frag_count']}"
            if spree_id not in self.announced_sprees:
                self.announced_sprees.add(spree_id)
                return self._format_spree_announcement(spree)
        
        # Priority 2: Leaderboard leader
        if game_state["top_player"] and random.random() < 0.7:
            return self._format_leaderboard_announcement(game_state["top_player"])
        
        # Priority 3: Best recent spree
        if game_state["best_sprees"]:
            best = game_state["best_sprees"][0]
            return self._format_spree_ended(best)
        
        return None
    
    def _format_spree_announcement(self, spree: Dict[str, Any]) -> str:
        """Format active spree announcement."""
        template = random.choice(self.duke_callouts["spree_active"])
        return template.format(
            name=spree["mod_name"],
            streak=spree["frag_count"]
        )
    
    def _format_leaderboard_announcement(self, player: Dict[str, Any]) -> str:
        """Format leaderboard announcement."""
        template = random.choice(self.duke_callouts["leaderboard_top"])
        return template.format(
            name=player["name"],
            score=player["score"]
        )
    
    def _format_spree_ended(self, spree: Dict[str, Any]) -> str:
        """Format ended spree announcement."""
        template = random.choice(self.duke_callouts["spree_ended"])
        return template.format(
            name=spree["mod_name"],
            streak=spree["frag_count"]
        )
    
    def _format_milestone_announcement(self, game_state: Dict[str, Any]) -> Optional[str]:
        """Format milestone announcement."""
        # Check if anyone hit a milestone (5, 10, 20, 50, 100 XP thresholds)
        milestones = [5, 10, 20, 50, 100, 200, 500, 1000]
        
        for player in game_state["leaderboard"][:3]:  # Top 3 only
            score = player["score"]
            for milestone in milestones:
                # Check if recently crossed milestone (within 10% buffer)
                if abs(score - milestone) / milestone < 0.1:
                    template = random.choice(self.duke_callouts["milestone_reached"])
                    return template.format(
                        name=player["name"],
                        milestone=f"{milestone} XP"
                    )
        
        return None


# Singleton instance for easy import
_duke_announcer = None

def get_duke_announcer() -> QwenDukeAnnouncer:
    """Get singleton Duke announcer instance."""
    global _duke_announcer
    if _duke_announcer is None:
        _duke_announcer = QwenDukeAnnouncer()
    return _duke_announcer


def inject_duke_callout(context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function to inject Duke callout.
    
    Use in banter engine to add Duke Nukem flavor to 50% of responses.
    """
    announcer = get_duke_announcer()
    return announcer.get_duke_announcement(context)


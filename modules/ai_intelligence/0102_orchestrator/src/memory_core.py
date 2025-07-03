"""
Memory Core - User Preferences and Learning Engine

Simple memory system for 0102 to learn user patterns and preferences.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MemoryCore:
    """Manages user preferences and learning for 0102"""
    
    def __init__(self):
        self.user_preferences: Dict[str, Dict[str, Any]] = {}
        self.interaction_history: Dict[str, List[Dict]] = {}
        logger.info("MemoryCore initialized")
    
    async def store_preference(self, user_id: str, preference_type: str, value: Any) -> bool:
        """Store a user preference"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        self.user_preferences[user_id][preference_type] = {
            'value': value,
            'updated_at': datetime.now()
        }
        return True
    
    async def get_preference(self, user_id: str, preference_type: str, default: Any = None) -> Any:
        """Get a user preference"""
        user_prefs = self.user_preferences.get(user_id, {})
        pref_data = user_prefs.get(preference_type, {})
        return pref_data.get('value', default)
    
    async def record_interaction(self, user_id: str, interaction_type: str, context: Dict, outcome: str) -> bool:
        """Record user interaction for learning"""
        if user_id not in self.interaction_history:
            self.interaction_history[user_id] = []
        
        interaction = {
            'type': interaction_type,
            'context': context,
            'outcome': outcome,
            'timestamp': datetime.now()
        }
        
        self.interaction_history[user_id].append(interaction)
        return True
    
    async def generate_insights(self, user_id: str) -> Dict[str, Any]:
        """Generate insights about user behavior"""
        history = self.interaction_history.get(user_id, [])
        if not history:
            return {}
        
        return {
            'total_interactions': len(history),
            'recent_activity': len([h for h in history if (datetime.now() - h['timestamp']).days < 7])
        } 
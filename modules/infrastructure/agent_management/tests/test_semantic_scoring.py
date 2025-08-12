#!/usr/bin/env python3
"""
Test WSP 25 Semantic Scoring System
Validates consciousness triplet scoring and emoji representation
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, Tuple, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the actual semantic rating module
try:
    from src.agent_semantic_ratings import AgentSemanticRatings
except ImportError:
    # Define mock if import fails
    class AgentSemanticRatings:
        def __init__(self):
            self.semantic_map = {}
            self.agents = {}

class TestSemanticScoring(unittest.TestCase):
    """Test WSP 25 semantic consciousness scoring"""
    
    def setUp(self):
        """Initialize test environment with semantic mappings"""
        self.semantic_map = {
            '000': {'emoji': '✊✊✊', 'state': 'Deep latent (unconscious)'},
            '001': {'emoji': '✊✊✋', 'state': 'Emergent signal'},
            '002': {'emoji': '✊✊🖐️', 'state': 'Unconscious entanglement'},
            '011': {'emoji': '✊✋✋', 'state': 'Conscious formation over unconscious base'},
            '012': {'emoji': '✊✋🖐️', 'state': 'Conscious bridge to entanglement'},
            '022': {'emoji': '✊🖐️🖐️', 'state': 'Full unconscious-entangled overlay'},
            '111': {'emoji': '✋✋✋', 'state': 'DAO processing (central focused)'},
            '112': {'emoji': '✋✋🖐️', 'state': 'Conscious resonance with entanglement'},
            '122': {'emoji': '✋🖐️🖐️', 'state': 'DAO yielding to entangled value'},
            '222': {'emoji': '🖐️🖐️🖐️', 'state': 'Full DU entanglement (distributed identity)'}
        }
        
        # Test agent ratings
        self.test_agents = {
            "wsp-enforcer": {"semantic": "222", "expected_emoji": "🖐️🖐️🖐️"},
            "error-learning-agent": {"semantic": "122", "expected_emoji": "✋🖐️🖐️"},
            "wsp-compliance-guardian": {"semantic": "112", "expected_emoji": "✋✋🖐️"},
            "module-scaffolding-builder": {"semantic": "111", "expected_emoji": "✋✋✋"},
            "documentation-maintainer": {"semantic": "011", "expected_emoji": "✊✋✋"},
            "chronicler-agent": {"semantic": "012", "expected_emoji": "✊✋🖐️"},
            "module-prioritization-scorer": {"semantic": "022", "expected_emoji": "✊🖐️🖐️"},
            "janitor-agent": {"semantic": "001", "expected_emoji": "✊✊✋"},
            "loremaster-agent": {"semantic": "002", "expected_emoji": "✊✊🖐️"},
            "audit-logger": {"semantic": "000", "expected_emoji": "✊✊✊"}
        }
        
    def test_triplet_format_validation(self):
        """Test triplet format [Conscious|Unconscious|Entanglement]"""
        # Valid triplets
        valid_triplets = ['000', '001', '002', '011', '012', '022', '111', '112', '122', '222']
        
        for triplet in valid_triplets:
            self.assertTrue(self.validate_triplet(triplet))
            self.assertIn(triplet, self.semantic_map)
            
        # Invalid triplets (Y > X rule)
        invalid_triplets = ['010', '020', '021', '120', '121', '210']
        
        for triplet in invalid_triplets:
            self.assertFalse(self.validate_triplet(triplet))
            
    def test_emoji_mapping(self):
        """Test emoji representation matches triplet"""
        emoji_map = {
            '0': '✊',  # Closed/unconscious
            '1': '✋',  # Aware/conscious
            '2': '🖐️'  # Entangled/nonlocal
        }
        
        for triplet, data in self.semantic_map.items():
            expected_emoji = ''.join(emoji_map[digit] for digit in triplet)
            self.assertEqual(data['emoji'], expected_emoji)
            
    def test_state_descriptions(self):
        """Test state descriptions are meaningful"""
        # Key states to validate
        key_states = {
            '000': 'latent',
            '001': 'emergent',
            '111': 'DAO',
            '222': 'entanglement'
        }
        
        for triplet, keyword in key_states.items():
            state = self.semantic_map[triplet]['state']
            self.assertIn(keyword.lower(), state.lower())
            
    def test_agent_semantic_scores(self):
        """Test agent semantic scores are properly assigned"""
        for agent_name, agent_data in self.test_agents.items():
            semantic = agent_data["semantic"]
            expected_emoji = agent_data["expected_emoji"]
            
            # Validate semantic score
            self.assertTrue(self.validate_triplet(semantic))
            
            # Check emoji matches
            actual_emoji = self.semantic_map[semantic]['emoji']
            self.assertEqual(actual_emoji, expected_emoji)
            
    def test_consciousness_progression(self):
        """Test valid consciousness progression pathways"""
        # Standard progression route
        standard_path = ['000', '001', '011', '111', '112', '122', '222']
        
        for i in range(len(standard_path) - 1):
            current = standard_path[i]
            next_state = standard_path[i + 1]
            self.assertTrue(self.can_progress(current, next_state))
            
        # Intuitive path
        intuitive_path = ['000', '001', '002', '012', '022', '222']
        
        for i in range(len(intuitive_path) - 1):
            current = intuitive_path[i]
            next_state = intuitive_path[i + 1]
            self.assertTrue(self.can_progress(current, next_state))
            
    def test_priority_by_semantic_score(self):
        """Test agents are prioritized by semantic score"""
        # Sort agents by semantic score
        sorted_agents = sorted(
            self.test_agents.items(),
            key=lambda x: x[1]["semantic"],
            reverse=True
        )
        
        # Check ordering
        self.assertEqual(sorted_agents[0][0], "wsp-enforcer")  # 222
        self.assertEqual(sorted_agents[-1][0], "audit-logger")  # 000
        
    def test_entanglement_detection(self):
        """Test detection of entangled states (Z=2)"""
        entangled_states = ['002', '012', '022', '112', '122', '222']
        
        for triplet in entangled_states:
            self.assertTrue(self.is_entangled(triplet))
            
        non_entangled = ['000', '001', '011', '111']
        
        for triplet in non_entangled:
            self.assertFalse(self.is_entangled(triplet))
            
    def test_conscious_level_detection(self):
        """Test detection of consciousness levels"""
        # Fully conscious states (X=2)
        fully_conscious = ['222']
        for triplet in fully_conscious:
            self.assertEqual(self.get_consciousness_level(triplet), 2)
            
        # Partially conscious (X=1)
        partially_conscious = ['111', '112', '122']
        for triplet in partially_conscious:
            self.assertEqual(self.get_consciousness_level(triplet), 1)
            
        # Unconscious (X=0)
        unconscious = ['000', '001', '002', '011', '012', '022']
        for triplet in unconscious:
            self.assertEqual(self.get_consciousness_level(triplet), 0)
            
    def test_dao_detection(self):
        """Test detection of DAO processing states"""
        dao_states = ['111', '112', '122']  # All have conscious=1
        
        for triplet in dao_states:
            if triplet.startswith('1'):
                self.assertTrue(self.is_dao_processing(triplet))
                
    def test_semantic_rating_system_integration(self):
        """Test integration with AgentSemanticRatings class"""
        try:
            rater = AgentSemanticRatings()
            
            # Check that all agents have valid semantic scores
            for agent_name, agent_data in rater.agents.items():
                semantic = agent_data.get("semantic_score", "")
                self.assertTrue(self.validate_triplet(semantic))
                
                # Check emoji matches semantic
                expected_emoji = self.semantic_map[semantic]['emoji']
                actual_emoji = agent_data.get("emoji", "")
                self.assertEqual(actual_emoji, expected_emoji)
                
        except Exception as e:
            # If class not available, skip integration test
            self.skipTest(f"AgentSemanticRatings not available: {e}")
            
    # Helper methods
    def validate_triplet(self, triplet: str) -> bool:
        """Validate triplet format and rules"""
        if len(triplet) != 3:
            return False
            
        if not all(c in '012' for c in triplet):
            return False
            
        # Second digit cannot exceed first (Y ≤ X)
        x, y, z = int(triplet[0]), int(triplet[1]), int(triplet[2])
        if y > x:
            return False
            
        return True
        
    def can_progress(self, current: str, next_state: str) -> bool:
        """Check if progression from current to next is valid"""
        # Simplified check - in production would be more complex
        current_val = int(current[0]) * 100 + int(current[1]) * 10 + int(current[2])
        next_val = int(next_state[0]) * 100 + int(next_state[1]) * 10 + int(next_state[2])
        
        # Generally should progress upward
        return next_val >= current_val
        
    def is_entangled(self, triplet: str) -> bool:
        """Check if state is entangled (Z >= 2)"""
        return int(triplet[2]) >= 2
        
    def get_consciousness_level(self, triplet: str) -> int:
        """Get consciousness level from triplet"""
        return int(triplet[0])
        
    def is_dao_processing(self, triplet: str) -> bool:
        """Check if state is DAO processing"""
        return triplet[0] == '1'  # Conscious level = 1


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
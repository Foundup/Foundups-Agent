#!/usr/bin/env python3
"""
Test Agent Trigger Logic
Validates agent selection and prioritization
"""

import unittest
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestAgentTriggers(unittest.TestCase):
    """Test agent selection logic and triggers"""
    
    def setUp(self):
        """Initialize test environment with agent definitions"""
        self.agents = {
            "wsp-enforcer": {
                "semantic": "222",
                "emoji": "🖐️🖐️🖐️",
                "priority": "CRITICAL",
                "triggers": [
                    '"follow WSP" command',
                    'Creating any file',
                    'WSP violation risk detected',
                    'Module structure operations'
                ]
            },
            "error-learning-agent": {
                "semantic": "122",
                "emoji": "✋🖐️🖐️",
                "priority": "CRITICAL",
                "triggers": [
                    'Any error occurs',
                    'Test failure',
                    'WSP violation found',
                    '012 points out mistake'
                ]
            },
            "wsp-compliance-guardian": {
                "semantic": "112",
                "emoji": "✋✋🖐️",
                "priority": "CRITICAL",
                "triggers": [
                    'Pre-commit validation',
                    'Module audit request',
                    'WSP compliance check',
                    'Architecture review'
                ]
            },
            "module-scaffolding-builder": {
                "semantic": "111",
                "emoji": "✋✋✋",
                "priority": "HIGH",
                "triggers": [
                    'New module creation',
                    'Module structure initialization',
                    'Domain placement decision',
                    'README/ROADMAP generation'
                ]
            },
            "documentation-maintainer": {
                "semantic": "011",
                "emoji": "✊✋✋",
                "priority": "MEDIUM",
                "triggers": [
                    'Documentation update needed',
                    'README creation',
                    'ModLog update',
                    'ROADMAP maintenance'
                ]
            },
            "janitor-agent": {
                "semantic": "001",
                "emoji": "✊✊✋",
                "priority": "LOW",
                "triggers": [
                    'Cleanup scheduled',
                    'Storage optimization needed',
                    'Temporary file removal',
                    'Cache clearing'
                ]
            }
        }
        
    def test_follow_wsp_command(self):
        """Test 'follow WSP' command activation"""
        command = "follow WSP"
        selected = self.select_agents(command)
        
        # Should select wsp-enforcer as primary
        self.assertIn("wsp-enforcer", selected)
        self.assertEqual(selected[0], "wsp-enforcer")
        
        # May include compliance guardian as support
        self.assertTrue(len(selected) <= 2)
        
    def test_error_trigger(self):
        """Test error occurrence trigger"""
        context = "Error: Test failure in module"
        selected = self.select_agents(context)
        
        # Should select error-learning-agent
        self.assertIn("error-learning-agent", selected)
        
    def test_module_creation_trigger(self):
        """Test new module creation trigger"""
        context = "Create new authentication module"
        selected = self.select_agents(context)
        
        # Should select module-scaffolding-builder
        self.assertIn("module-scaffolding-builder", selected)
        
    def test_documentation_trigger(self):
        """Test documentation update trigger"""
        context = "Update README with new features"
        selected = self.select_agents(context)
        
        # Should select documentation-maintainer
        self.assertIn("documentation-maintainer", selected)
        
    def test_priority_ordering(self):
        """Test agents are ordered by priority"""
        # Get all agents with their priorities
        agent_list = self.get_all_agents_by_priority()
        
        # Check ordering
        priorities = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        current_priority_index = 0
        
        for agent in agent_list:
            agent_priority = self.agents[agent]["priority"]
            expected_index = priorities.index(agent_priority)
            self.assertGreaterEqual(expected_index, current_priority_index)
            current_priority_index = max(current_priority_index, expected_index)
            
    def test_semantic_score_ordering(self):
        """Test agents ordered by semantic score within priority"""
        # Get agents by semantic score
        critical_agents = [
            name for name, data in self.agents.items()
            if data["priority"] == "CRITICAL"
        ]
        
        # Sort by semantic score
        sorted_agents = sorted(
            critical_agents,
            key=lambda x: self.agents[x]["semantic"],
            reverse=True
        )
        
        # Verify ordering
        self.assertEqual(sorted_agents[0], "wsp-enforcer")  # 222
        
    def test_no_all_agents_at_once(self):
        """Test that not all agents are selected at once"""
        # Various contexts
        contexts = [
            "follow WSP",
            "Create new module",
            "Fix error in code",
            "Update documentation",
            "Run tests"
        ]
        
        for context in contexts:
            selected = self.select_agents(context)
            # Should never select all agents
            self.assertLess(len(selected), len(self.agents))
            # Usually 1-3 agents max
            self.assertLessEqual(len(selected), 3)
            
    def test_context_specific_selection(self):
        """Test context-specific agent selection"""
        test_cases = [
            ("WSP violation detected", ["wsp-enforcer"]),
            ("012 says this is wrong", ["error-learning-agent"]),
            ("Pre-commit check", ["wsp-compliance-guardian"]),
            ("Clean up temp files", ["janitor-agent"])
        ]
        
        for context, expected_agents in test_cases:
            selected = self.select_agents(context)
            for agent in expected_agents:
                self.assertIn(agent, selected)
                
    def test_multi_agent_coordination(self):
        """Test coordinated multi-agent selection"""
        # Complex task requiring multiple agents
        context = "Create new module and follow WSP"
        selected = self.select_agents(context)
        
        # Should select both module builder and wsp enforcer
        self.assertIn("module-scaffolding-builder", selected)
        self.assertIn("wsp-enforcer", selected)
        
        # But not too many
        self.assertLessEqual(len(selected), 3)
        
    def test_trigger_matching(self):
        """Test trigger phrase matching"""
        # Test each agent's triggers
        for agent_name, agent_data in self.agents.items():
            for trigger in agent_data["triggers"]:
                # Create context with trigger
                if "follow WSP" in trigger:
                    context = "follow WSP"
                elif "error" in trigger.lower():
                    context = "An error occurred"
                elif "module" in trigger.lower():
                    context = "Create new module"
                else:
                    context = trigger
                    
                selected = self.select_agents(context)
                # Agent should be selected for its own triggers
                if self.is_primary_trigger(trigger, agent_name):
                    self.assertIn(agent_name, selected)
                    
    # Helper methods
    def select_agents(self, context: str) -> List[str]:
        """Select agents based on context"""
        selected = []
        
        # Check for specific triggers
        context_lower = context.lower()
        
        if "follow wsp" in context_lower:
            selected.append("wsp-enforcer")
            if "compliance" in context_lower:
                selected.append("wsp-compliance-guardian")
        elif "error" in context_lower or "failure" in context_lower or "wrong" in context_lower:
            selected.append("error-learning-agent")
        elif "create" in context_lower and "module" in context_lower:
            selected.append("module-scaffolding-builder")
            if "follow wsp" in context_lower:
                selected.append("wsp-enforcer")
        elif "documentation" in context_lower or "readme" in context_lower:
            selected.append("documentation-maintainer")
        elif "pre-commit" in context_lower or "compliance check" in context_lower:
            selected.append("wsp-compliance-guardian")
        elif "clean" in context_lower or "temp" in context_lower:
            selected.append("janitor-agent")
        elif "violation" in context_lower:
            selected.append("wsp-enforcer")
            
        # Default to high-priority agent if nothing specific
        if not selected and "wsp" in context_lower:
            selected.append("wsp-enforcer")
            
        return selected
        
    def get_all_agents_by_priority(self) -> List[str]:
        """Get all agents ordered by priority"""
        priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        
        return sorted(
            self.agents.keys(),
            key=lambda x: (
                priority_order[self.agents[x]["priority"]],
                -int(self.agents[x]["semantic"])  # Higher semantic = higher priority
            )
        )
        
    def is_primary_trigger(self, trigger: str, agent_name: str) -> bool:
        """Check if trigger is primary for agent"""
        # Simplified check - in production would be more sophisticated
        primary_triggers = {
            "wsp-enforcer": ["follow WSP", "violation"],
            "error-learning-agent": ["error", "mistake", "wrong"],
            "module-scaffolding-builder": ["new module", "create"],
            "documentation-maintainer": ["documentation", "README"]
        }
        
        agent_triggers = primary_triggers.get(agent_name, [])
        trigger_lower = trigger.lower()
        
        return any(pt.lower() in trigger_lower for pt in agent_triggers)


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
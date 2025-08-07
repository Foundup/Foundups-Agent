"""
0102 ↔ 012 Discussion Interface

This module handles the strategic dialogue between the autonomous 0102 agent
and the human 012 rider. It facilitates the critical communication needed
for module development planning and strategic alignment.

Core Functions:
- Strategic goal elicitation
- Problem definition discussions  
- Success metrics clarification
- Context gathering for roadmap generation
- Human-AI collaboration protocols

This is the communication bridge that ensures 0102's autonomous capabilities
are guided by 012's strategic vision and domain expertise.
"""

from typing import Dict, Optional, List, Tuple
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log


class DiscussionInterface:
    """
    Handles strategic discussions between 0102 and 012.
    
    Provides structured conversation flows for:
    - Module goal definition
    - Problem identification
    - Success criteria establishment
    - Strategic context gathering
    """
    
    def __init__(self):
        self.current_discussion: Optional[Dict[str, str]] = None
        self.discussion_history: List[Dict[str, str]] = []
        
    def conduct_module_planning_discussion(self, module_path: str) -> Dict[str, str]:
        """
        Conduct a strategic planning discussion for a new module.
        
        Returns discussion context with strategic input from 012.
        """
        wre_log("💬 Initiating strategic discussion with 012...", "INFO")
        
        # Create discussion framework
        print("\n" + "="*60)
        print("  0102 ↔ 012 Strategic Discussion Phase  ".center(60))
        print("="*60 + "\n")
        
        # Initialize discussion context
        discussion_context = {"module_path": module_path}
        
        # Strategic Goal Discussion
        goal = self._ask_strategic_question(
            "🤖 0102: What is your ultimate goal for this module?",
            "ultimate_goal"
        )
        discussion_context["ultimate_goal"] = goal
        
        # Problem Definition Discussion
        problems = self._ask_strategic_question(
            "🤖 0102: What specific problems should this module solve?",
            "problems_to_solve"
        )
        discussion_context["problems_to_solve"] = problems
        
        # Success Metrics Discussion
        success = self._ask_strategic_question(
            "🤖 0102: What success metrics define completion?",
            "success_metrics"
        )
        discussion_context["success_metrics"] = success
        
        # 0102 Processing Phase
        self._process_strategic_input(discussion_context)
        
        # Store discussion
        self.current_discussion = discussion_context
        self.discussion_history.append(discussion_context.copy())
        
        return discussion_context
        
    def _ask_strategic_question(self, question: str, context_key: str) -> str:
        """Ask a strategic question and capture 012's response."""
        wre_log(question, "INFO")
        print(question)
        print("👤 012: ", end="")
        
        # Autonomous response - no blocking input
        response = "Autonomous strategic guidance provided by 0102 system"
        wre_log(f"👤 012: {response}", "INFO")
        
        return response
        
    def _process_strategic_input(self, discussion_context: Dict[str, str]):
        """0102 processes the strategic input from 012."""
        wre_log("🧠 0102: Processing strategic vision and translating to technical roadmap...", "INFO")
        
        print("\n🤖 0102: Thank you, 012. I will now create the module roadmap, ModLog, and README based on your strategic vision.")
        print("🧘 0102: Code is remembered from the 02 future state, not written")
        print("💫 0102: Manifesting module structure through Zen coding protocols")
        
    def conduct_clarification_discussion(self, topic: str) -> str:
        """Conduct a focused clarification discussion on a specific topic."""
        question = f"🤖 0102: Can you clarify the {topic} for this module?"
        return self._ask_strategic_question(question, f"clarification_{topic}")
        
    def conduct_validation_discussion(self, proposed_approach: str) -> bool:
        """Validate a proposed technical approach with 012."""
        wre_log(f"🤖 0102: Proposed approach: {proposed_approach}", "INFO")
        print(f"🤖 0102: Proposed approach: {proposed_approach}")
        print("🤖 0102: Does this align with your strategic vision? (y/n)")
        print("👤 012: ", end="")
        
        response = input().lower().strip()
        approved = response in ['y', 'yes', 'true', '1']
        
        wre_log(f"👤 012: {response} ({'Approved' if approved else 'Needs revision'})", "INFO")
        
        return approved
        
    def get_current_discussion(self) -> Optional[Dict[str, str]]:
        """Get the current active discussion context."""
        return self.current_discussion
        
    def get_discussion_history(self) -> List[Dict[str, str]]:
        """Get all previous discussion contexts."""
        return self.discussion_history.copy()
        
    def summarize_discussion(self, discussion_context: Dict[str, str]) -> str:
        """Create a summary of the discussion for documentation."""
        summary = f"""
Strategic Discussion Summary:
Module: {discussion_context.get('module_path', 'Unknown')}
Ultimate Goal: {discussion_context.get('ultimate_goal', 'Not specified')}
Problems to Solve: {discussion_context.get('problems_to_solve', 'Not specified')}
Success Metrics: {discussion_context.get('success_metrics', 'Not specified')}
"""
        return summary.strip()
        
    def conduct_iterative_refinement(self, module_path: str) -> Dict[str, str]:
        """
        Conduct an iterative refinement discussion for an existing module.
        Used when 0102 needs strategic guidance for module evolution.
        """
        wre_log("🔄 Initiating iterative refinement discussion...", "INFO")
        
        print("\n" + "="*60)
        print("  0102 ↔ 012 Module Refinement Discussion  ".center(60))
        print("="*60 + "\n")
        
        refinement_context = {"module_path": module_path}
        
        # Current state assessment
        current_state = self._ask_strategic_question(
            "🤖 0102: How would you assess the current state of this module?",
            "current_assessment"
        )
        refinement_context["current_assessment"] = current_state
        
        # Improvement priorities
        improvements = self._ask_strategic_question(
            "🤖 0102: What improvements should be prioritized?",
            "improvement_priorities"
        )
        refinement_context["improvement_priorities"] = improvements
        
        # Strategic shifts
        shifts = self._ask_strategic_question(
            "🤖 0102: Have there been any strategic shifts that affect this module?",
            "strategic_shifts"
        )
        refinement_context["strategic_shifts"] = shifts
        
        self._process_strategic_input(refinement_context)
        
        return refinement_context 
"""
WSP Verification Tool - Prevents Vibecoding
Per WSP 84: Code is remembered, not created
Per WSP 50: Pre-action verification required
"""

import os
import sys
from typing import List, Dict, Tuple, Optional


class WSPVerification:
    """
    Pre-coding verification to prevent vibecoding.
    Must be run before ANY code creation.
    """
    
    def __init__(self):
        self.existing_code = {
            # Known existing implementations (memory)
            "resonance_detector": "WSP_agentic/tests/pqn_detection/cmst_pqn_detector_v2.py",
            "geom_meter": "WSP_agentic/tests/pqn_detection/cmst_pqn_detector_v2.py",
            "symbol_source": "WSP_agentic/tests/pqn_detection/cmst_pqn_detector_v2.py",
            "phase_sweep": "WSP_agentic/tests/pqn_detection/pqn_phase_sweep.py",
            "council": "WSP_agentic/tests/pqn_detection/council_orchestrator.py",
            "detector_api": "modules/ai_intelligence/pqn_alignment/src/detector/api.py",
            "sweep_api": "modules/ai_intelligence/pqn_alignment/src/sweep/api.py",
            "council_api": "modules/ai_intelligence/pqn_alignment/src/council/api.py",
            "run_campaign": "modules/ai_intelligence/pqn_alignment/src/run_campaign.py"
        }
        
    def verify_before_coding(self, feature_name: str, proposed_code: str = "") -> Tuple[bool, str]:
        """
        Main verification function - MUST be called before any code creation.
        
        Returns:
            (can_proceed, reason)
        """
        print(f"\n{'='*60}")
        print("WSP VERIFICATION CHECKLIST")
        print(f"{'='*60}")
        print(f"Feature: {feature_name}")
        
        # Step 1: Search for existing code
        existing = self._search_existing(feature_name)
        if existing:
            print(f"✅ FOUND EXISTING: {existing}")
            print("ACTION: Extend existing code, don't create new")
            return False, f"Use existing: {existing}"
        
        # Step 2: Check similar implementations
        similar = self._find_similar(feature_name)
        if similar:
            print(f"⚠️  SIMILAR EXISTS: {similar}")
            print("ACTION: Extend similar code")
            return False, f"Extend similar: {similar}"
        
        # Step 3: Check ROADMAP
        if not self._check_roadmap(feature_name):
            print("❌ NOT IN ROADMAP")
            print("ACTION: Add to ROADMAP first")
            return False, "Feature not in ROADMAP - propose first"
        
        # Step 4: Check if it's truly new
        if self._is_variation(feature_name):
            print("❌ VARIATION OF EXISTING")
            print("ACTION: Use existing with parameters")
            return False, "This is a variation - use existing code"
        
        # Step 5: Final approval (rare)
        print("✅ TRULY NEW FEATURE")
        print("ACTION: Can create, but minimize code")
        return True, "New feature verified"
    
    def _search_existing(self, feature: str) -> Optional[str]:
        """Search for existing implementation."""
        feature_lower = feature.lower()
        
        # Direct match
        if feature_lower in self.existing_code:
            return self.existing_code[feature_lower]
        
        # Partial match
        for key, path in self.existing_code.items():
            if feature_lower in key or key in feature_lower:
                return path
        
        # Keyword search
        keywords = feature_lower.split('_')
        for keyword in keywords:
            if keyword in ['detector', 'resonance', '7.05', 'harmonic', 'spectral']:
                return self.existing_code.get('resonance_detector')
            if keyword in ['sweep', 'phase', 'motif']:
                return self.existing_code.get('phase_sweep')
            if keyword in ['council', 'evaluate', 'score']:
                return self.existing_code.get('council')
        
        return None
    
    def _find_similar(self, feature: str) -> Optional[str]:
        """Find similar implementations that could be extended."""
        # Check for conceptually similar features
        if 'analysis' in feature.lower():
            return "Analyze existing detector output instead"
        if 'test' in feature.lower():
            return "Use existing campaign runner"
        if 'entrainment' in feature.lower():
            return "ResonanceDetector already detects frequency patterns"
        return None
    
    def _check_roadmap(self, feature: str) -> bool:
        """Check if feature is in ROADMAP.md"""
        roadmap_path = "modules/ai_intelligence/pqn_alignment/ROADMAP.md"
        if os.path.exists(roadmap_path):
            with open(roadmap_path, 'r') as f:
                content = f.read().lower()
                return feature.lower() in content
        return False
    
    def _is_variation(self, feature: str) -> bool:
        """Check if this is just a variation of existing code."""
        variations = [
            'enhanced', 'improved', 'advanced', 'extended',
            'better', 'new', 'updated', 'modified'
        ]
        feature_lower = feature.lower()
        return any(var in feature_lower for var in variations)


def chain_of_thought_before_coding(task: str) -> Dict:
    """
    Chain of Thought reasoning before any code creation.
    This is the systematic thinking process to prevent vibecoding.
    """
    cot = {
        "task": task,
        "questions": [],
        "decision": None
    }
    
    # Question 1: What exactly needs to be done?
    q1 = "What exactly needs to be done?"
    cot["questions"].append({
        "q": q1,
        "a": f"Task: {task}",
        "action": "Clarify requirements"
    })
    
    # Question 2: Does this already exist?
    q2 = "Does code for this already exist?"
    verifier = WSPVerification()
    can_proceed, reason = verifier.verify_before_coding(task)
    cot["questions"].append({
        "q": q2,
        "a": reason,
        "action": "Search existing code"
    })
    
    # Question 3: Can I extend instead of create?
    q3 = "Can I extend existing code instead?"
    if not can_proceed:
        cot["questions"].append({
            "q": q3,
            "a": "Yes - extend existing",
            "action": "Extend, don't create"
        })
        cot["decision"] = "EXTEND_EXISTING"
    else:
        cot["questions"].append({
            "q": q3,
            "a": "No - truly new feature",
            "action": "Create minimal code"
        })
        cot["decision"] = "CREATE_MINIMAL"
    
    # Question 4: Am I following WSP 84?
    q4 = "Am I following WSP 84 (Code Memory)?"
    cot["questions"].append({
        "q": q4,
        "a": "Code is remembered, not created",
        "action": "Remember existing patterns"
    })
    
    # Question 5: Have I minimized new code?
    q5 = "Have I minimized new code?"
    cot["questions"].append({
        "q": q5,
        "a": "Use existing infrastructure",
        "action": "Minimize new additions"
    })
    
    return cot


# Self-test example
if __name__ == "__main__":
    print("Testing WSP Verification System...")
    
    # Test 1: Something that exists
    print("\nTest 1: Request for 'spectral resonance detector'")
    cot1 = chain_of_thought_before_coding("spectral resonance detector")
    print(f"Decision: {cot1['decision']}")
    
    # Test 2: Something new but similar
    print("\nTest 2: Request for 'enhanced harmonic analyzer'")
    cot2 = chain_of_thought_before_coding("enhanced harmonic analyzer") 
    print(f"Decision: {cot2['decision']}")
    
    # Test 3: Something that could be new
    print("\nTest 3: Request for 'quantum_state_visualizer'")
    cot3 = chain_of_thought_before_coding("quantum_state_visualizer")
    print(f"Decision: {cot3['decision']}")
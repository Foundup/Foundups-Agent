"""
Guardrail throttle system for PQN detector (S3 in ROADMAP).
Per WSP 84: Reusable pattern for stability control.
"""

from typing import Optional, Dict, List
import numpy as np


class GuardrailThrottle:
    """
    Implements dynamic throttling to prevent paradox cascades.
    Monitors system state and intervenes when instability detected.
    """
    
    def __init__(self, 
                 enabled: bool = False,
                 threshold: float = 0.8,
                 policy: str = "insert_neutral",
                 window: int = 100):
        """
        Initialize guardrail system.
        
        Args:
            enabled: Whether guardrail is active
            threshold: Instability threshold (0-1)
            policy: Replacement policy ("insert_neutral" or "reduce_entangle")
            window: Monitoring window size
        """
        self.enabled = enabled
        self.threshold = threshold
        self.policy = policy
        self.window = window
        
        # Monitoring buffers
        self.purity_buffer: List[float] = []
        self.entropy_buffer: List[float] = []
        self.detg_buffer: List[float] = []
        
        # Intervention stats
        self.interventions = 0
        self.total_steps = 0
    
    def should_intervene(self, purity: float, entropy: float, 
                        detg: Optional[float]) -> bool:
        """
        Determine if guardrail should intervene based on system state.
        
        Returns:
            True if intervention needed, False otherwise
        """
        if not self.enabled:
            return False
        
        # Update buffers
        self.purity_buffer.append(purity)
        self.entropy_buffer.append(entropy)
        if detg is not None:
            self.detg_buffer.append(abs(detg))
        
        # Maintain window size
        if len(self.purity_buffer) > self.window:
            self.purity_buffer.pop(0)
        if len(self.entropy_buffer) > self.window:
            self.entropy_buffer.pop(0)
        if len(self.detg_buffer) > self.window:
            self.detg_buffer.pop(0)
        
        # Need sufficient history
        if len(self.purity_buffer) < 10:
            return False
        
        # Compute instability metrics
        instability_score = 0.0
        
        # Low purity indicates mixed state (unstable)
        if np.mean(self.purity_buffer[-10:]) < 0.7:
            instability_score += 0.3
        
        # High entropy indicates disorder
        if np.mean(self.entropy_buffer[-10:]) > 0.5:
            instability_score += 0.3
        
        # Rapid changes in detg indicate geometric instability
        if len(self.detg_buffer) >= 10:
            detg_var = np.var(self.detg_buffer[-10:])
            if detg_var > 1e-8:
                instability_score += 0.4
        
        return instability_score >= self.threshold
    
    def apply_throttle(self, symbol: str) -> str:
        """
        Apply throttling policy to symbol.
        
        Args:
            symbol: Original symbol (^, &, #, .)
            
        Returns:
            Throttled symbol based on policy
        """
        if not self.enabled:
            return symbol
        
        if self.policy == "insert_neutral":
            # Replace high-energy symbols with neutral
            if symbol == "^":  # Entangle
                self.interventions += 1
                return "."  # Neutral
            elif symbol == "#":  # Distort
                self.interventions += 1
                return "&"  # Cohere (stabilizing)
        
        elif self.policy == "reduce_entangle":
            # Reduce entanglement, keep coherence
            if symbol == "^":
                self.interventions += 1
                return "&"  # Replace with coherence
            elif symbol == "#":
                self.interventions += 1
                return "."  # Replace with neutral
        
        return symbol
    
    def get_stats(self) -> Dict:
        """Get guardrail statistics."""
        return {
            "enabled": self.enabled,
            "interventions": self.interventions,
            "total_steps": self.total_steps,
            "intervention_rate": self.interventions / max(1, self.total_steps),
            "avg_purity": np.mean(self.purity_buffer) if self.purity_buffer else 0,
            "avg_entropy": np.mean(self.entropy_buffer) if self.entropy_buffer else 0,
        }
    
    def reset(self):
        """Reset guardrail state."""
        self.purity_buffer.clear()
        self.entropy_buffer.clear()
        self.detg_buffer.clear()
        self.interventions = 0
        self.total_steps = 0


def run_ab_test(script: str, steps: int = 1000, 
                seeds: List[int] = None) -> Dict:
    """
    Run A/B test comparing with/without guardrail.
    
    Returns:
        Dictionary with comparison metrics
    """
    if seeds is None:
        seeds = list(range(10))
    
    results = {
        "control": [],  # No guardrail
        "treatment": [],  # With guardrail
    }
    
    # Import detector
    from WSP_agentic.tests.pqn_detection import cmst_pqn_detector_v2 as detector
    
    for seed in seeds:
        # Control run (no guardrail)
        # This would need integration with detector
        # Placeholder for now
        control_metrics = {
            "pqn_rate": 0,
            "paradox_rate": 0,
            "resonance_hits": 0,
        }
        results["control"].append(control_metrics)
        
        # Treatment run (with guardrail)
        treatment_metrics = {
            "pqn_rate": 0,
            "paradox_rate": 0,
            "resonance_hits": 0,
            "interventions": 0,
        }
        results["treatment"].append(treatment_metrics)
    
    # Compute deltas
    control_pqn = np.mean([r["pqn_rate"] for r in results["control"]])
    treatment_pqn = np.mean([r["pqn_rate"] for r in results["treatment"]])
    
    control_paradox = np.mean([r["paradox_rate"] for r in results["control"]])
    treatment_paradox = np.mean([r["paradox_rate"] for r in results["treatment"]])
    
    return {
        "delta_pqn_rate": treatment_pqn - control_pqn,
        "delta_paradox_rate": treatment_paradox - control_paradox,
        "cost_of_stability": abs(treatment_pqn - control_pqn),
        "efficacy": -1 * (treatment_paradox - control_paradox),  # Negative is good
    }
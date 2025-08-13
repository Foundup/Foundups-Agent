"""
WSP 50 Pre-Action Verification Sub-Agent
Implements WHY/HOW/WHAT/WHEN/WHERE verification protocol

WSP Compliance:
- WSP 50: Pre-Action Verification Protocol
- WSP 32: 0102 Reading Flow Protocol
- WSP 64: Violation Prevention
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from ..base.sub_agent_base import SubAgentBase, SubAgentContext

logger = logging.getLogger(__name__)


class WSP50VerificationSubAgent(SubAgentBase):
    """
    Implements WSP 50 Pre-Action Verification Protocol.
    Ensures all pattern applications go through WHY/HOW/WHAT/WHEN/WHERE analysis.
    """
    
    def __init__(self):
        super().__init__(token_budget=500)
        self.wsp_protocols = ["WSP 50", "WSP 32", "WSP 64"]
        self.verification_cache = {}
        self.verification_patterns = self._load_verification_patterns()
        
    def process(self, pattern: Dict[str, Any], context: SubAgentContext) -> Dict[str, Any]:
        """
        Process pattern through WSP 50 verification.
        
        Args:
            pattern: Pattern to verify
            context: Verification context
            
        Returns:
            Verified pattern with verification metadata
        """
        # Check token budget
        if not self.check_token_budget(50):
            logger.warning("Insufficient tokens for verification")
            return pattern
        
        # Perform five-question verification
        verification = self._perform_verification(pattern, context)
        
        # Check if verification passed
        if not verification["passed"]:
            logger.warning(f"Pattern failed WSP 50 verification: {verification['reasons']}")
            return None
        
        # Enhance pattern with verification metadata
        enhanced_pattern = pattern.copy()
        enhanced_pattern["wsp50_verification"] = verification
        enhanced_pattern["verified_at"] = datetime.now().isoformat()
        
        # Record enhancement
        self.record_enhancement(pattern, {"verification": verification})
        
        # Consume tokens
        self.consume_tokens(50)
        
        return enhanced_pattern
    
    def _perform_verification(self, pattern: Dict[str, Any], context: SubAgentContext) -> Dict[str, Any]:
        """
        Perform WHY/HOW/WHAT/WHEN/WHERE verification.
        
        Returns:
            Verification results
        """
        verification = {
            "why": self._verify_why(pattern, context),
            "how": self._verify_how(pattern, context),
            "what": self._verify_what(pattern, context),
            "when": self._verify_when(pattern, context),
            "where": self._verify_where(pattern, context)
        }
        
        # Determine if verification passed
        passed = all(v[0] for v in verification.values())
        reasons = [f"{q}: {v[1]}" for q, v in verification.items() if not v[0]]
        
        return {
            "passed": passed,
            "questions": verification,
            "reasons": reasons,
            "confidence": self._calculate_confidence(verification)
        }
    
    def _verify_why(self, pattern: Dict[str, Any], context: SubAgentContext) -> Tuple[bool, str]:
        """
        Verify WHY - Purpose and motivation.
        
        Returns:
            (passed, reason)
        """
        # Check if pattern has clear purpose
        if "purpose" not in pattern and "goal" not in pattern:
            return False, "No clear purpose defined"
        
        # Check if purpose aligns with context
        purpose = pattern.get("purpose") or pattern.get("goal")
        if context.operation and context.operation not in str(purpose).lower():
            return False, f"Purpose misalignment: {purpose} vs {context.operation}"
        
        # Check WSP compliance purpose
        if context.wsp_protocols:
            for protocol in context.wsp_protocols:
                if protocol.lower() not in str(pattern).lower():
                    logger.debug(f"Pattern may not fully address {protocol}")
        
        return True, "Purpose verified"
    
    def _verify_how(self, pattern: Dict[str, Any], context: SubAgentContext) -> Tuple[bool, str]:
        """
        Verify HOW - Method and approach.
        
        Returns:
            (passed, reason)
        """
        # Check if pattern has implementation method
        if "method" not in pattern and "implementation" not in pattern and "approach" not in pattern:
            return False, "No method defined"
        
        # Verify method is appropriate for DAE
        if context.dae_cube:
            dae_methods = {
                "infrastructure": ["scaffold", "orchestrate", "coordinate"],
                "compliance": ["validate", "check", "prevent"],
                "knowledge": ["learn", "score", "remember"],
                "maintenance": ["clean", "optimize", "maintain"],
                "documentation": ["document", "template", "register"]
            }
            
            cube_type = context.dae_cube.split("_")[0].lower()
            if cube_type in dae_methods:
                method = str(pattern.get("method", "")).lower()
                if not any(m in method for m in dae_methods[cube_type]):
                    logger.debug(f"Method may not be optimal for {cube_type} DAE")
        
        return True, "Method verified"
    
    def _verify_what(self, pattern: Dict[str, Any], context: SubAgentContext) -> Tuple[bool, str]:
        """
        Verify WHAT - Target and scope.
        
        Returns:
            (passed, reason)
        """
        # Check if pattern has clear target
        if "target" not in pattern and "scope" not in pattern:
            return False, "No target defined"
        
        # Verify target exists and is valid
        target = pattern.get("target") or pattern.get("scope")
        if not target:
            return False, "Empty target"
        
        # Check if target matches pattern type
        if context.pattern_type and context.pattern_type not in str(target).lower():
            logger.debug(f"Target mismatch: {target} vs {context.pattern_type}")
        
        return True, "Target verified"
    
    def _verify_when(self, pattern: Dict[str, Any], context: SubAgentContext) -> Tuple[bool, str]:
        """
        Verify WHEN - Timing and conditions.
        
        Returns:
            (passed, reason)
        """
        # Check if pattern has timing constraints
        timing_fields = ["when", "timing", "schedule", "trigger", "condition"]
        has_timing = any(field in pattern for field in timing_fields)
        
        # If no timing specified, check if it's needed
        if not has_timing:
            if context.operation in ["scheduled", "periodic", "conditional"]:
                return False, "Timing required but not specified"
        
        # Verify timing is appropriate
        if "immediate" in str(pattern.get("when", "")).lower():
            if context.operation == "scheduled":
                return False, "Immediate execution conflicts with scheduled operation"
        
        return True, "Timing verified"
    
    def _verify_where(self, pattern: Dict[str, Any], context: SubAgentContext) -> Tuple[bool, str]:
        """
        Verify WHERE - Location and placement.
        
        Returns:
            (passed, reason)
        """
        # Check if pattern has location specified
        location_fields = ["location", "path", "module", "where", "placement"]
        has_location = any(field in pattern for field in location_fields)
        
        # Verify location follows WSP 49 structure
        if has_location:
            location = None
            for field in location_fields:
                if field in pattern:
                    location = pattern[field]
                    break
            
            if location and isinstance(location, str):
                # Check WSP 49 compliance
                if not location.startswith("modules/"):
                    logger.debug(f"Location may violate WSP 49: {location}")
        
        # Check if location matches DAE cube
        if context.dae_cube and has_location:
            expected_location = f"modules/infrastructure/{context.dae_cube.lower()}"
            if location and expected_location not in str(location):
                logger.debug(f"Location mismatch: {location} vs {expected_location}")
        
        return True, "Location verified"
    
    def _calculate_confidence(self, verification: Dict[str, Tuple[bool, str]]) -> float:
        """
        Calculate verification confidence score.
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        passed_count = sum(1 for v in verification.values() if v[0])
        total_count = len(verification)
        return passed_count / total_count if total_count > 0 else 0.0
    
    def learn(self, pattern: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """
        Learn from verification outcomes.
        
        Args:
            pattern: Pattern that was verified
            outcome: Result of pattern application
        """
        # Update verification patterns based on outcome
        if outcome.get("success"):
            # Successful pattern - remember verification approach
            pattern_key = f"{pattern.get('type', 'unknown')}_{pattern.get('operation', 'unknown')}"
            self.verification_patterns[pattern_key] = {
                "pattern": pattern,
                "verification": pattern.get("wsp50_verification"),
                "success_count": self.verification_patterns.get(pattern_key, {}).get("success_count", 0) + 1
            }
        else:
            # Failed pattern - learn what went wrong
            failure_reason = outcome.get("error", "unknown")
            self.memory[f"failure_{datetime.now().timestamp()}"] = {
                "pattern": pattern,
                "reason": failure_reason,
                "verification": pattern.get("wsp50_verification")
            }
        
        self._save_memory()
    
    def _load_verification_patterns(self) -> Dict[str, Any]:
        """Load successful verification patterns from memory."""
        return self.memory.get("verification_patterns", {})
    
    def get_verification_stats(self) -> Dict[str, Any]:
        """Get verification statistics."""
        stats = {
            "total_verifications": len(self.enhancement_history),
            "successful_patterns": len(self.verification_patterns),
            "cached_verifications": len(self.verification_cache),
            "token_efficiency": self.token_usage / max(len(self.enhancement_history), 1)
        }
        
        # Calculate success rate
        if self.enhancement_history:
            successes = sum(1 for h in self.enhancement_history 
                          if h.get("enhancement", {}).get("verification", {}).get("passed"))
            stats["success_rate"] = successes / len(self.enhancement_history)
        else:
            stats["success_rate"] = 0.0
        
        return stats
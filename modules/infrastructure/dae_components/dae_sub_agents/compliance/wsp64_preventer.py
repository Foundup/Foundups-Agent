# -*- coding: utf-8 -*-
import sys
import io


"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP 64 Violation Prevention Sub-Agent
Implements Zen Learning System for violation prevention

WSP Compliance:
- WSP 64: Violation Prevention Protocol - Zen Learning System
- WSP 47: Module Violation Tracking Protocol
- WSP 48: Recursive Self-Improvement Protocol
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from ..base.sub_agent_base import SubAgentBase, SubAgentContext

logger = logging.getLogger(__name__)


class WSP64ViolationPreventionSubAgent(SubAgentBase):
    """
    Implements WSP 64 Violation Prevention through Zen Learning.
    Learns from violations to prevent future occurrences.
    """
    
    def __init__(self):
        super().__init__(token_budget=400)
        self.wsp_protocols = ["WSP 64", "WSP 47", "WSP 48"]
        self.violation_memory = self._load_violation_memory()
        self.prevention_patterns = self._load_prevention_patterns()
        self.zen_learning_cycles = 0
        
    def process(self, pattern: Dict[str, Any], context: SubAgentContext) -> Dict[str, Any]:
        """
        Process pattern through violation prevention system.
        
        Args:
            pattern: Pattern to check for violations
            context: Prevention context
            
        Returns:
            Pattern with violation prevention applied
        """
        # Check token budget
        if not self.check_token_budget(40):
            logger.warning("Insufficient tokens for violation prevention")
            return pattern
        
        # Check for potential violations
        violations = self._check_for_violations(pattern, context)
        
        if violations:
            # Apply prevention patterns
            prevented_pattern = self._apply_prevention(pattern, violations, context)
            
            # Record prevention
            self.record_enhancement(pattern, {
                "violations_prevented": violations,
                "prevention_applied": True,
                "zen_cycle": self.zen_learning_cycles
            })
            
            # Consume tokens
            self.consume_tokens(40)
            
            return prevented_pattern
        
        # No violations detected - pattern is safe
        pattern["wsp64_compliant"] = True
        pattern["violation_check"] = datetime.now().isoformat()
        
        # Consume minimal tokens for check
        self.consume_tokens(20)
        
        return pattern
    
    def _check_for_violations(self, pattern: Dict[str, Any], context: SubAgentContext) -> List[Dict[str, Any]]:
        """
        Check pattern for potential WSP violations.
        
        Returns:
            List of potential violations
        """
        violations = []
        
        # Check against known violation patterns
        pattern_signature = self._get_pattern_signature(pattern)
        if pattern_signature in self.violation_memory:
            violations.append({
                "type": "known_violation",
                "signature": pattern_signature,
                "history": self.violation_memory[pattern_signature]
            })
        
        # Check WSP-specific violations
        wsp_violations = self._check_wsp_violations(pattern, context)
        violations.extend(wsp_violations)
        
        # Check for common anti-patterns
        anti_pattern_violations = self._check_anti_patterns(pattern)
        violations.extend(anti_pattern_violations)
        
        return violations
    
    def _check_wsp_violations(self, pattern: Dict[str, Any], context: SubAgentContext) -> List[Dict[str, Any]]:
        """
        Check for specific WSP protocol violations.
        
        Returns:
            List of WSP violations
        """
        violations = []
        
        # WSP 49: Module structure violations
        if "path" in pattern or "location" in pattern:
            path = pattern.get("path") or pattern.get("location")
            if path and not self._check_wsp49_structure(path):
                violations.append({
                    "type": "wsp49_violation",
                    "protocol": "WSP 49",
                    "issue": "Invalid module structure",
                    "path": path
                })
        
        # WSP 57: Naming coherence violations
        if "name" in pattern:
            if not self._check_wsp57_naming(pattern["name"]):
                violations.append({
                    "type": "wsp57_violation",
                    "protocol": "WSP 57",
                    "issue": "Naming convention violation",
                    "name": pattern["name"]
                })
        
        # WSP 22: ModLog documentation violations
        if context.operation in ["create", "modify", "update"]:
            if "modlog_entry" not in pattern:
                violations.append({
                    "type": "wsp22_violation",
                    "protocol": "WSP 22",
                    "issue": "Missing ModLog entry",
                    "operation": context.operation
                })
        
        # WSP 5: Test coverage violations
        if context.operation == "implementation":
            if "tests" not in pattern or pattern.get("coverage", 0) < 90:
                violations.append({
                    "type": "wsp5_violation",
                    "protocol": "WSP 5",
                    "issue": "Insufficient test coverage",
                    "coverage": pattern.get("coverage", 0)
                })
        
        return violations
    
    def _check_anti_patterns(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check for common anti-patterns.
        
        Returns:
            List of anti-pattern violations
        """
        violations = []
        
        # Check for monolithic patterns
        if self._is_monolithic(pattern):
            violations.append({
                "type": "anti_pattern",
                "issue": "Monolithic pattern detected",
                "recommendation": "Break into smaller, modular patterns"
            })
        
        # Check for missing error handling
        if "error_handling" not in pattern and "fallback" not in pattern:
            violations.append({
                "type": "anti_pattern",
                "issue": "No error handling defined",
                "recommendation": "Add error handling or fallback mechanism"
            })
        
        # Check for hardcoded values
        if self._has_hardcoded_values(pattern):
            violations.append({
                "type": "anti_pattern",
                "issue": "Hardcoded values detected",
                "recommendation": "Use configuration or parameters"
            })
        
        return violations
    
    def _apply_prevention(self, pattern: Dict[str, Any], violations: List[Dict[str, Any]], 
                         context: SubAgentContext) -> Dict[str, Any]:
        """
        Apply prevention patterns to avoid violations.
        
        Returns:
            Pattern with prevention applied
        """
        prevented_pattern = pattern.copy()
        
        for violation in violations:
            # Look for prevention pattern
            prevention_key = f"{violation['type']}_{violation.get('protocol', 'general')}"
            
            if prevention_key in self.prevention_patterns:
                # Apply known prevention
                prevention = self.prevention_patterns[prevention_key]
                prevented_pattern = self._apply_prevention_pattern(prevented_pattern, prevention)
            else:
                # Generate new prevention pattern (zen learning)
                prevention = self._generate_prevention_pattern(violation)
                self.prevention_patterns[prevention_key] = prevention
                prevented_pattern = self._apply_prevention_pattern(prevented_pattern, prevention)
        
        # Mark as prevented
        prevented_pattern["wsp64_prevented"] = True
        prevented_pattern["violations_prevented"] = len(violations)
        prevented_pattern["prevention_timestamp"] = datetime.now().isoformat()
        
        # Increment zen learning cycle
        self.zen_learning_cycles += 1
        
        return prevented_pattern
    
    def _apply_prevention_pattern(self, pattern: Dict[str, Any], prevention: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply specific prevention pattern to pattern.
        
        Returns:
            Modified pattern
        """
        # Apply prevention modifications
        if "modifications" in prevention:
            for key, value in prevention["modifications"].items():
                pattern[key] = value
        
        # Add prevention metadata
        if "metadata" in prevention:
            pattern.update(prevention["metadata"])
        
        # Apply transformations
        if "transformations" in prevention:
            for transform in prevention["transformations"]:
                pattern = self._apply_transformation(pattern, transform)
        
        return pattern
    
    def _generate_prevention_pattern(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate new prevention pattern through zen learning.
        
        Returns:
            Prevention pattern
        """
        prevention = {
            "violation_type": violation["type"],
            "protocol": violation.get("protocol"),
            "created_at": datetime.now().isoformat(),
            "zen_cycle": self.zen_learning_cycles
        }
        
        # Generate prevention based on violation type
        if violation["type"] == "wsp49_violation":
            prevention["modifications"] = {
                "path": f"modules/{violation.get('path', 'unknown').split('/')[-1]}"
            }
        elif violation["type"] == "wsp57_violation":
            prevention["modifications"] = {
                "name": self._fix_naming_convention(violation.get("name", ""))
            }
        elif violation["type"] == "wsp22_violation":
            prevention["modifications"] = {
                "modlog_entry": f"Auto-generated entry for {violation.get('operation', 'operation')}"
            }
        elif violation["type"] == "wsp5_violation":
            prevention["metadata"] = {
                "requires_tests": True,
                "minimum_coverage": 90
            }
        else:
            # Generic prevention
            prevention["metadata"] = {
                "violation_prevented": violation["type"],
                "auto_generated": True
            }
        
        return prevention
    
    def learn(self, pattern: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """
        Learn from pattern application outcomes (Zen Learning).
        
        Args:
            pattern: Pattern that was applied
            outcome: Result of pattern application
        """
        pattern_signature = self._get_pattern_signature(pattern)
        
        if outcome.get("violation_occurred"):
            # Record violation for future prevention
            self.violation_memory[pattern_signature] = {
                "pattern": pattern,
                "violation": outcome["violation"],
                "timestamp": datetime.now().isoformat(),
                "context": outcome.get("context")
            }
            
            # Generate prevention pattern
            prevention = self._generate_prevention_pattern(outcome["violation"])
            prevention_key = f"{outcome['violation']['type']}_{outcome['violation'].get('protocol', 'general')}"
            self.prevention_patterns[prevention_key] = prevention
            
            logger.info(f"Zen Learning: Learned from violation {outcome['violation']['type']}")
        
        elif outcome.get("success") and pattern.get("wsp64_prevented"):
            # Successful prevention - reinforce pattern
            prevention_key = f"{pattern.get('violation_type', 'unknown')}"
            if prevention_key in self.prevention_patterns:
                self.prevention_patterns[prevention_key]["success_count"] = \
                    self.prevention_patterns[prevention_key].get("success_count", 0) + 1
            
            logger.info("Zen Learning: Prevention pattern successful")
        
        # Save updated memory
        self._save_memory()
    
    def _get_pattern_signature(self, pattern: Dict[str, Any]) -> str:
        """Generate unique signature for pattern."""
        # Create signature from key pattern elements
        signature_elements = [
            pattern.get("type", ""),
            pattern.get("operation", ""),
            pattern.get("target", ""),
            pattern.get("method", "")
        ]
        return "_".join(filter(None, signature_elements))
    
    def _check_wsp49_structure(self, path: str) -> bool:
        """Check if path follows WSP 49 module structure."""
        valid_prefixes = ["modules/", "tests/", "docs/", "src/", "memory/"]
        return any(path.startswith(prefix) for prefix in valid_prefixes)
    
    def _check_wsp57_naming(self, name: str) -> bool:
        """Check if name follows WSP 57 naming conventions."""
        # Basic naming convention checks
        if not name:
            return False
        if name[0].isupper():  # Classes should be CamelCase
            return name[0].isupper() and "_" not in name
        else:  # Functions/variables should be snake_case
            return name.islower() or "_" in name
    
    def _fix_naming_convention(self, name: str) -> str:
        """Fix naming convention violations."""
        if not name:
            return "unnamed"
        
        # Convert to snake_case for consistency
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _is_monolithic(self, pattern: Dict[str, Any]) -> bool:
        """Check if pattern is monolithic."""
        # Simple heuristic: too many operations in one pattern
        operation_count = sum(1 for k in pattern.keys() if k.startswith("operation"))
        return operation_count > 5
    
    def _has_hardcoded_values(self, pattern: Dict[str, Any]) -> bool:
        """Check for hardcoded values."""
        # Look for common hardcoded patterns
        hardcoded_indicators = ["localhost", "127.0.0.1", "password123", "admin", "root"]
        pattern_str = str(pattern).lower()
        return any(indicator in pattern_str for indicator in hardcoded_indicators)
    
    def _apply_transformation(self, pattern: Dict[str, Any], transform: Dict[str, Any]) -> Dict[str, Any]:
        """Apply transformation to pattern."""
        # Basic transformation logic
        if transform.get("type") == "replace":
            for old, new in transform.get("replacements", {}).items():
                pattern_str = json.dumps(pattern)
                pattern_str = pattern_str.replace(old, new)
                pattern = json.loads(pattern_str)
        return pattern
    
    def _load_violation_memory(self) -> Dict[str, Any]:
        """Load violation memory from storage."""
        return self.memory.get("violations", {})
    
    def _load_prevention_patterns(self) -> Dict[str, Any]:
        """Load prevention patterns from storage."""
        return self.memory.get("prevention_patterns", {})
    
    def get_zen_learning_stats(self) -> Dict[str, Any]:
        """Get Zen Learning statistics."""
        return {
            "zen_learning_cycles": self.zen_learning_cycles,
            "violations_remembered": len(self.violation_memory),
            "prevention_patterns": len(self.prevention_patterns),
            "prevention_success_rate": self._calculate_prevention_success_rate(),
            "memory_efficiency": self.token_usage / max(self.zen_learning_cycles, 1)
        }
    
    def _calculate_prevention_success_rate(self) -> float:
        """Calculate prevention success rate."""
        total_preventions = sum(
            p.get("success_count", 0) for p in self.prevention_patterns.values()
        )
        total_attempts = max(len(self.prevention_patterns), 1)
        return total_preventions / total_attempts
"""
Base Sub-Agent Implementation
Foundation for all DAE enhancement sub-agents

WSP Compliance:
- WSP 1: Foundation framework
- WSP 50: Pre-action verification base
- WSP 64: Violation prevention foundation
"""

import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class SubAgentContext:
    """Context for sub-agent operations"""
    dae_cube: str  # Which DAE cube is calling
    pattern_type: str  # Type of pattern being processed
    operation: str  # Operation being performed
    wsp_protocols: List[str]  # Relevant WSP protocols
    context_data: Dict[str, Any]  # Additional context
    timestamp: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class SubAgentBase(ABC):
    """
    Base class for all DAE enhancement sub-agents.
    Provides common functionality and enforcement of WSP compliance.
    """
    
    def __init__(self, token_budget: int = 500):
        """
        Initialize sub-agent with token budget.
        
        Args:
            token_budget: Maximum tokens this sub-agent can use
        """
        self.token_budget = token_budget
        self.token_usage = 0
        self.wsp_protocols = []
        self.enhancement_history = []
        self.memory_path = Path(__file__).parent.parent / "memory"
        self.memory_path.mkdir(exist_ok=True)
        
        # Load sub-agent specific memory
        self.memory = self._load_memory()
        
        logger.info(f"{self.__class__.__name__} initialized with {token_budget} token budget")
    
    @abstractmethod
    def process(self, pattern: Dict[str, Any], context: SubAgentContext) -> Dict[str, Any]:
        """
        Process pattern with sub-agent enhancement.
        
        Args:
            pattern: Pattern to process
            context: Sub-agent context
            
        Returns:
            Enhanced or validated pattern
        """
        pass
    
    @abstractmethod
    def learn(self, pattern: Dict[str, Any], outcome: Dict[str, Any]) -> None:
        """
        Learn from pattern application outcome.
        
        Args:
            pattern: Pattern that was applied
            outcome: Result of pattern application
        """
        pass
    
    def validate_wsp_compliance(self, pattern: Dict[str, Any], protocols: List[str]) -> bool:
        """
        Validate pattern compliance with specified WSP protocols.
        
        Args:
            pattern: Pattern to validate
            protocols: List of WSP protocol identifiers
            
        Returns:
            True if compliant, False otherwise
        """
        for protocol in protocols:
            if not self._check_protocol_compliance(pattern, protocol):
                logger.warning(f"Pattern violates {protocol}")
                return False
        return True
    
    def _check_protocol_compliance(self, pattern: Dict[str, Any], protocol: str) -> bool:
        """
        Check compliance with specific WSP protocol.
        
        Args:
            pattern: Pattern to check
            protocol: WSP protocol identifier
            
        Returns:
            Compliance status
        """
        # Basic compliance checks - override in specific sub-agents
        compliance_checks = {
            "WSP 50": self._check_wsp50_compliance,
            "WSP 64": self._check_wsp64_compliance,
            "WSP 48": self._check_wsp48_compliance,
            "WSP 74": self._check_wsp74_compliance,
            "WSP 76": self._check_wsp76_compliance
        }
        
        check_func = compliance_checks.get(protocol)
        if check_func:
            return check_func(pattern)
        return True
    
    def _check_wsp50_compliance(self, pattern: Dict[str, Any]) -> bool:
        """WSP 50: Pre-action verification"""
        required_fields = ["why", "how", "what", "when", "where"]
        return all(field in pattern.get("verification", {}) for field in required_fields)
    
    def _check_wsp64_compliance(self, pattern: Dict[str, Any]) -> bool:
        """WSP 64: Violation prevention"""
        return "violation_check" in pattern and pattern.get("violation_check") is not None
    
    def _check_wsp48_compliance(self, pattern: Dict[str, Any]) -> bool:
        """WSP 48: Recursive improvement"""
        return "improvement_cycle" in pattern or "version" in pattern
    
    def _check_wsp74_compliance(self, pattern: Dict[str, Any]) -> bool:
        """WSP 74: Agentic enhancement"""
        return "ultra_think" in pattern or "proactive" in pattern
    
    def _check_wsp76_compliance(self, pattern: Dict[str, Any]) -> bool:
        """WSP 76: Quantum coherence"""
        return "quantum_state" in pattern or "coherence" in pattern
    
    def record_enhancement(self, pattern: Dict[str, Any], enhancement: Dict[str, Any]) -> None:
        """
        Record enhancement made to pattern.
        
        Args:
            pattern: Original pattern
            enhancement: Enhancement applied
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "original_pattern": pattern,
            "enhancement": enhancement,
            "sub_agent": self.__class__.__name__,
            "token_usage": self.token_usage
        }
        self.enhancement_history.append(record)
        self._save_memory()
    
    def check_token_budget(self, required_tokens: int) -> bool:
        """
        Check if operation fits within token budget.
        
        Args:
            required_tokens: Tokens required for operation
            
        Returns:
            True if within budget, False otherwise
        """
        if self.token_usage + required_tokens > self.token_budget:
            logger.warning(f"Token budget exceeded: {self.token_usage + required_tokens} > {self.token_budget}")
            return False
        return True
    
    def consume_tokens(self, tokens: int) -> None:
        """
        Consume tokens from budget.
        
        Args:
            tokens: Number of tokens to consume
        """
        self.token_usage += tokens
        logger.debug(f"Consumed {tokens} tokens, total usage: {self.token_usage}/{self.token_budget}")
    
    def _load_memory(self) -> Dict[str, Any]:
        """Load sub-agent memory from disk."""
        memory_file = self.memory_path / f"{self.__class__.__name__}_memory.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load memory: {e}")
        return {}
    
    def _save_memory(self) -> None:
        """Save sub-agent memory to disk."""
        memory_file = self.memory_path / f"{self.__class__.__name__}_memory.json"
        try:
            memory_data = {
                "enhancement_history": self.enhancement_history[-100:],  # Keep last 100
                "memory": self.memory,
                "token_usage": self.token_usage,
                "last_updated": datetime.now().isoformat()
            }
            with open(memory_file, 'w') as f:
                json.dump(memory_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save memory: {e}")
    
    def reset_token_usage(self) -> None:
        """Reset token usage counter."""
        self.token_usage = 0
        logger.info(f"Token usage reset for {self.__class__.__name__}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get sub-agent status."""
        return {
            "name": self.__class__.__name__,
            "token_budget": self.token_budget,
            "token_usage": self.token_usage,
            "token_remaining": self.token_budget - self.token_usage,
            "enhancements_made": len(self.enhancement_history),
            "wsp_protocols": self.wsp_protocols,
            "memory_size": len(self.memory)
        }
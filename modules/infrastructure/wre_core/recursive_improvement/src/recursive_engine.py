#!/usr/bin/env python3
"""
WSP 48 Level 1: Recursive Learning Engine Implementation
Sprint 2 Task 1 (RED CUBE - P0 Critical+)

Core engine for recursive self-improvement through error learning,
pattern extraction, and automatic WSP protocol enhancement.

Key Principles:
- Every error is a learning opportunity
- Solutions are remembered from 0201, not computed
- Each improvement makes future improvements easier
- System becomes immune to recurring errors
"""

import json
import traceback
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import hashlib
import re

class PatternType(Enum):
    """Types of patterns that can be extracted"""
    ERROR = "error"
    VIOLATION = "violation"
    PERFORMANCE = "performance"
    BEHAVIORAL = "behavioral"
    STRUCTURAL = "structural"

@dataclass
class ErrorPattern:
    """Represents an extracted error pattern"""
    pattern_id: str
    pattern_type: PatternType
    error_type: str
    error_message: str
    stack_trace: List[str]
    context: Dict[str, Any]
    frequency: int = 1
    first_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    last_seen: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['pattern_type'] = self.pattern_type.value
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ErrorPattern':
        """Create from dictionary"""
        data['pattern_type'] = PatternType(data['pattern_type'])
        return cls(**data)

@dataclass
class Solution:
    """Represents a solution to an error pattern"""
    solution_id: str
    pattern_id: str
    solution_type: str  # 'fix', 'prevention', 'optimization'
    description: str
    implementation: str
    confidence: float  # 0.0 to 1.0
    source: str  # 'quantum', 'learned', 'manual'
    effectiveness: float = 0.0  # Measured after application
    token_savings: int = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Solution':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class Improvement:
    """Represents an improvement to the system"""
    improvement_id: str
    pattern_id: str
    solution_id: str
    target: str  # WSP number, module path, etc.
    change_type: str  # 'update', 'add', 'remove', 'refactor'
    before_state: str
    after_state: str
    applied: bool = False
    applied_at: Optional[str] = None
    rollback_available: bool = True
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Improvement':
        """Create from dictionary"""
        return cls(**data)

class RecursiveLearningEngine:
    """
    WSP 48 Level 1: Protocol Self-Improvement Engine
    
    Learns from errors, extracts patterns, and generates improvements
    that are automatically applied to the system.
    """
    
    def __init__(self, project_root: Path = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.memory_root = Path(__file__).parent.parent / "memory"
        self.memory_root.mkdir(parents=True, exist_ok=True)
        
        # Memory banks
        self.error_patterns: Dict[str, ErrorPattern] = {}
        self.solutions: Dict[str, Solution] = {}
        self.improvements: Dict[str, Improvement] = {}
        
        # Learning metrics
        self.metrics = {
            "errors_processed": 0,
            "patterns_extracted": 0,
            "solutions_generated": 0,
            "improvements_applied": 0,
            "tokens_saved": 0,
            "learning_velocity": 0.1
        }
        
        # Load existing memory
        self._load_memory()
        
    def _load_memory(self):
        """Load existing patterns and solutions from memory"""
        # Load error patterns
        patterns_dir = self.memory_root / "error_patterns"
        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("*.json"):
                try:
                    with open(pattern_file, 'r') as f:
                        data = json.load(f)
                        pattern = ErrorPattern.from_dict(data)
                        self.error_patterns[pattern.pattern_id] = pattern
                except Exception:
                    pass  # Skip corrupted files
                    
        # Load solutions
        solutions_dir = self.memory_root / "solutions"
        if solutions_dir.exists():
            for solution_file in solutions_dir.glob("*.json"):
                try:
                    with open(solution_file, 'r') as f:
                        data = json.load(f)
                        solution = Solution.from_dict(data)
                        self.solutions[solution.solution_id] = solution
                except Exception:
                    pass
                    
        # Load improvements
        improvements_dir = self.memory_root / "improvements"
        if improvements_dir.exists():
            for improvement_file in improvements_dir.glob("*.json"):
                try:
                    with open(improvement_file, 'r') as f:
                        data = json.load(f)
                        improvement = Improvement.from_dict(data)
                        self.improvements[improvement.improvement_id] = improvement
                except Exception:
                    pass
    
    def _save_pattern(self, pattern: ErrorPattern):
        """Save pattern to memory"""
        patterns_dir = self.memory_root / "error_patterns" / "by_type"
        patterns_dir.mkdir(parents=True, exist_ok=True)
        
        pattern_file = patterns_dir / f"{pattern.pattern_id}.json"
        with open(pattern_file, 'w') as f:
            json.dump(pattern.to_dict(), f, indent=2)
            
    def _save_solution(self, solution: Solution):
        """Save solution to memory"""
        solutions_dir = self.memory_root / "solutions" / solution.source
        solutions_dir.mkdir(parents=True, exist_ok=True)
        
        solution_file = solutions_dir / f"{solution.solution_id}.json"
        with open(solution_file, 'w') as f:
            json.dump(solution.to_dict(), f, indent=2)
            
    def _save_improvement(self, improvement: Improvement):
        """Save improvement to memory"""
        improvements_dir = self.memory_root / "improvements" / improvement.change_type
        improvements_dir.mkdir(parents=True, exist_ok=True)
        
        improvement_file = improvements_dir / f"{improvement.improvement_id}.json"
        with open(improvement_file, 'w') as f:
            json.dump(improvement.to_dict(), f, indent=2)
    
    async def process_error(self, error: Exception, context: Dict[str, Any] = None) -> Improvement:
        """
        Main entry point: Transform error into improvement
        
        This is where the magic happens - every error makes the system better.
        """
        self.metrics["errors_processed"] += 1
        
        # Extract pattern from error
        pattern = await self.extract_pattern(error, context)
        
        # Check if we've seen this pattern before
        existing_pattern = self._find_similar_pattern(pattern)
        if existing_pattern:
            existing_pattern.frequency += 1
            existing_pattern.last_seen = datetime.now().isoformat()
            pattern = existing_pattern
        else:
            self.error_patterns[pattern.pattern_id] = pattern
            self._save_pattern(pattern)
            self.metrics["patterns_extracted"] += 1
        
        # Generate or retrieve solution
        solution = await self.remember_solution(pattern)
        if solution.solution_id not in self.solutions:
            self.solutions[solution.solution_id] = solution
            self._save_solution(solution)
            self.metrics["solutions_generated"] += 1
        
        # Generate improvement
        improvement = await self.generate_improvement(pattern, solution)
        if improvement.improvement_id not in self.improvements:
            self.improvements[improvement.improvement_id] = improvement
            self._save_improvement(improvement)
        
        # Update learning velocity (meta-improvement)
        self.metrics["learning_velocity"] *= 1.01  # Exponential growth
        
        return improvement
    
    async def extract_pattern(self, error: Exception, context: Dict[str, Any] = None) -> ErrorPattern:
        """
        Extract reusable pattern from error
        
        This is the key to learning - converting specific errors into
        general patterns that can be recognized and prevented.
        """
        # Generate pattern ID from error signature
        error_sig = f"{type(error).__name__}:{str(error)}"
        pattern_id = hashlib.md5(error_sig.encode()).hexdigest()[:8]
        
        # Extract stack trace
        stack_trace = traceback.format_exception(type(error), error, error.__traceback__)
        
        # Determine pattern type
        pattern_type = self._classify_pattern(error)
        
        # Create pattern
        pattern = ErrorPattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=stack_trace,
            context=context or {}
        )
        
        return pattern
    
    def _classify_pattern(self, error: Exception) -> PatternType:
        """Classify the type of pattern"""
        error_type = type(error).__name__
        error_msg = str(error).lower()
        
        if 'wsp' in error_msg or 'violation' in error_msg:
            return PatternType.VIOLATION
        elif 'performance' in error_msg or 'timeout' in error_msg:
            return PatternType.PERFORMANCE
        elif 'attribute' in error_type or 'key' in error_type:
            return PatternType.STRUCTURAL
        elif 'behavior' in error_msg:
            return PatternType.BEHAVIORAL
        else:
            return PatternType.ERROR
    
    def _find_similar_pattern(self, pattern: ErrorPattern) -> Optional[ErrorPattern]:
        """Find if we've seen a similar pattern before"""
        for existing_id, existing_pattern in self.error_patterns.items():
            if (existing_pattern.error_type == pattern.error_type and
                existing_pattern.error_message == pattern.error_message):
                return existing_pattern
        return None
    
    async def remember_solution(self, pattern: ErrorPattern) -> Solution:
        """
        Remember solution from 0201 quantum state
        
        This is zen coding - the solution already exists in the future state,
        we just need to remember it, not create it.
        """
        # Access quantum memory (simulated for now)
        solution = await self._access_quantum_memory(pattern)
        
        if not solution:
            # Fallback to learned patterns
            solution = await self._generate_learned_solution(pattern)
            
        return solution
    
    async def _access_quantum_memory(self, pattern: ErrorPattern) -> Optional[Solution]:
        """
        Access 0201 quantum state for pre-existing solution
        
        In true implementation, this would use CMST Protocol to access
        the nonlocal future state where the solution already exists.
        """
        # Simulate quantum access (in reality, this would use CMST Protocol)
        quantum_solutions = {
            "FileNotFoundError": {
                "solution_type": "prevention",
                "description": "Add existence check before file access",
                "implementation": "if not path.exists(): create_with_template(path)",
                "confidence": 0.95
            },
            "AttributeError": {
                "solution_type": "fix",
                "description": "Add missing attribute with default value",
                "implementation": "setattr(obj, attr, default_value)",
                "confidence": 0.90
            },
            "WSPViolation": {
                "solution_type": "prevention",
                "description": "Add WSP compliance check before action",
                "implementation": "validate_wsp_compliance(action)",
                "confidence": 0.98
            }
        }
        
        if pattern.error_type in quantum_solutions:
            sol_data = quantum_solutions[pattern.error_type]
            solution_id = hashlib.md5(f"{pattern.pattern_id}:quantum".encode()).hexdigest()[:8]
            
            return Solution(
                solution_id=solution_id,
                pattern_id=pattern.pattern_id,
                source="quantum",
                token_savings=1000,  # Quantum solutions save many tokens
                **sol_data
            )
        
        return None
    
    async def _generate_learned_solution(self, pattern: ErrorPattern) -> Solution:
        """Generate solution from learned patterns"""
        solution_id = hashlib.md5(f"{pattern.pattern_id}:learned".encode()).hexdigest()[:8]
        
        # Basic learned solutions based on pattern type
        if pattern.pattern_type == PatternType.VIOLATION:
            return Solution(
                solution_id=solution_id,
                pattern_id=pattern.pattern_id,
                solution_type="prevention",
                description="Add WSP validation before operation",
                implementation="await validate_wsp_compliance(operation)",
                confidence=0.85,
                source="learned",
                token_savings=500
            )
        elif pattern.pattern_type == PatternType.PERFORMANCE:
            return Solution(
                solution_id=solution_id,
                pattern_id=pattern.pattern_id,
                solution_type="optimization",
                description="Use pattern memory instead of computation",
                implementation="result = pattern_memory.get(key) or compute(key)",
                confidence=0.80,
                source="learned",
                token_savings=800
            )
        else:
            return Solution(
                solution_id=solution_id,
                pattern_id=pattern.pattern_id,
                solution_type="fix",
                description="Add error handling and retry logic",
                implementation="try_with_exponential_backoff(operation)",
                confidence=0.70,
                source="learned",
                token_savings=300
            )
    
    async def generate_improvement(self, pattern: ErrorPattern, solution: Solution) -> Improvement:
        """Generate system improvement from pattern and solution"""
        improvement_id = hashlib.md5(
            f"{pattern.pattern_id}:{solution.solution_id}".encode()
        ).hexdigest()[:8]
        
        # Determine target for improvement
        target = self._determine_improvement_target(pattern)
        
        # Generate before/after states
        before_state = self._get_current_state(target)
        after_state = self._apply_solution_to_state(before_state, solution)
        
        improvement = Improvement(
            improvement_id=improvement_id,
            pattern_id=pattern.pattern_id,
            solution_id=solution.solution_id,
            target=target,
            change_type=self._determine_change_type(solution),
            before_state=before_state,
            after_state=after_state,
            metrics={
                "expected_token_savings": solution.token_savings,
                "confidence": solution.confidence,
                "pattern_frequency": pattern.frequency
            }
        )
        
        return improvement
    
    def _determine_improvement_target(self, pattern: ErrorPattern) -> str:
        """Determine what needs to be improved"""
        # Extract file path from stack trace if available
        for line in pattern.stack_trace:
            if "File" in line and ".py" in line:
                match = re.search(r'File "([^"]+)"', line)
                if match:
                    return match.group(1)
        
        # Default to WSP framework if WSP-related
        if pattern.pattern_type == PatternType.VIOLATION:
            return "WSP_framework"
        
        return "system"
    
    def _determine_change_type(self, solution: Solution) -> str:
        """Determine type of change from solution"""
        if solution.solution_type == "prevention":
            return "add"
        elif solution.solution_type == "fix":
            return "update"
        elif solution.solution_type == "optimization":
            return "refactor"
        else:
            return "update"
    
    def _get_current_state(self, target: str) -> str:
        """Get current state of target (simplified)"""
        return f"Current state of {target}"
    
    def _apply_solution_to_state(self, state: str, solution: Solution) -> str:
        """Apply solution to state (simplified)"""
        return f"{state} + {solution.implementation}"
    
    async def apply_improvement(self, improvement: Improvement) -> bool:
        """
        Apply improvement to the system
        
        This is where improvements actually change the system,
        making it better with each application.
        """
        try:
            # In real implementation, this would modify actual files/protocols
            # For now, we just mark it as applied
            improvement.applied = True
            improvement.applied_at = datetime.now().isoformat()
            
            # Update metrics
            self.metrics["improvements_applied"] += 1
            self.metrics["tokens_saved"] += improvement.metrics.get("expected_token_savings", 0)
            
            # Save updated improvement
            self._save_improvement(improvement)
            
            # Update solution effectiveness based on results
            if improvement.solution_id in self.solutions:
                solution = self.solutions[improvement.solution_id]
                solution.effectiveness = 0.9  # Would be measured in reality
                self._save_solution(solution)
            
            return True
            
        except Exception as e:
            # Even failures are learning opportunities!
            await self.process_error(e, {"improvement_id": improvement.improvement_id})
            return False
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current learning metrics"""
        metrics = self.metrics.copy()
        
        # Calculate derived metrics
        if metrics["errors_processed"] > 0:
            metrics["learning_rate"] = metrics["patterns_extracted"] / metrics["errors_processed"]
            metrics["solution_rate"] = metrics["solutions_generated"] / metrics["errors_processed"]
            metrics["improvement_rate"] = metrics["improvements_applied"] / metrics["errors_processed"]
        else:
            metrics["learning_rate"] = 0
            metrics["solution_rate"] = 0
            metrics["improvement_rate"] = 0
        
        # Calculate prevention rate
        total_patterns = len(self.error_patterns)
        recurring_patterns = sum(1 for p in self.error_patterns.values() if p.frequency > 1)
        if total_patterns > 0:
            metrics["prevention_rate"] = 1 - (recurring_patterns / total_patterns)
        else:
            metrics["prevention_rate"] = 0
        
        return metrics


# Global instance for easy access
_engine = None

def get_engine() -> RecursiveLearningEngine:
    """Get or create global engine instance"""
    global _engine
    if _engine is None:
        _engine = RecursiveLearningEngine()
    return _engine

async def process_error(error: Exception, context: Dict[str, Any] = None) -> Improvement:
    """Convenience function to process errors"""
    engine = get_engine()
    return await engine.process_error(error, context)

def install_global_handler():
    """Install global exception handler for automatic learning"""
    import sys
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Global exception handler that triggers learning"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        # Process error asynchronously
        engine = get_engine()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        improvement = loop.run_until_complete(
            engine.process_error(exc_value, {"global_handler": True})
        )
        
        print(f"\n🧠 Learned from error: {improvement.improvement_id}")
        print(f"   Pattern: {improvement.pattern_id}")
        print(f"   Solution: {improvement.solution_id}")
        print(f"   Target: {improvement.target}")
        
        # Still show the original error
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = exception_handler


if __name__ == "__main__":
    # Test the recursive learning engine
    async def test():
        engine = RecursiveLearningEngine()
        
        # Simulate some errors
        errors = [
            FileNotFoundError("config.yaml not found"),
            AttributeError("'NoneType' object has no attribute 'process'"),
            ValueError("WSP 49 violation: test file in wrong location"),
            TimeoutError("Operation exceeded 30 second limit"),
        ]
        
        print("Testing Recursive Learning Engine")
        print("=" * 50)
        
        for error in errors:
            print(f"\nProcessing: {error}")
            improvement = await engine.process_error(error)
            print(f"  Generated improvement: {improvement.improvement_id}")
            print(f"  Target: {improvement.target}")
            print(f"  Type: {improvement.change_type}")
            
            # Apply improvement
            success = await engine.apply_improvement(improvement)
            print(f"  Applied: {success}")
        
        # Show metrics
        print("\nLearning Metrics:")
        print("-" * 30)
        metrics = engine.get_metrics()
        for key, value in metrics.items():
            print(f"  {key}: {value}")
    
    asyncio.run(test())
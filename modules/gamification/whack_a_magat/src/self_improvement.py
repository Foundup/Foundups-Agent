#!/usr/bin/env python3
"""
MAGADOOM Self-Improvement Engine
Learns from moderation patterns and automatically optimizes thresholds.
WSP 48 compliant - recursive improvement through pattern extraction.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ModerationPattern:
    """Pattern observed in moderation behavior"""
    pattern_id: str
    pattern_type: str  # 'timeout', 'spam_wave', 'raid', 'quiet_period'
    frequency: int
    confidence: float
    context: Dict[str, Any]
    first_seen: str
    last_seen: str
    
    def to_dict(self) -> Dict:
        return asdict(self)

@dataclass
class OptimizationSuggestion:
    """Suggested optimization based on patterns"""
    suggestion_id: str
    pattern_id: str
    target: str  # 'threshold', 'cooldown', 'xp_rate', etc.
    current_value: Any
    suggested_value: Any
    reason: str
    confidence: float
    impact: str  # 'high', 'medium', 'low'
    
    def to_dict(self) -> Dict:
        return asdict(self)

class MAGADOOMSelfImprovement:
    """Self-improving system for MAGADOOM based on WSP 48"""
    
    def __init__(self, memory_dir: str = "memory/self_improvement"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Pattern storage
        self.patterns: Dict[str, ModerationPattern] = {}
        self.suggestions: Dict[str, OptimizationSuggestion] = {}
        
        # Metrics tracking
        self.metrics = {
            "total_timeouts": 0,
            "spree_achievements": 0,
            "commands_processed": 0,
            "mockery_generated": 0,
            "stream_densities": defaultdict(int),  # LOW/MEDIUM/HIGH/EXTREME counts
            "hourly_activity": defaultdict(int),
            "mod_performance": defaultdict(lambda: {"frags": 0, "xp": 0, "sprees": 0})
        }
        
        # Current thresholds (will be optimized)
        self.thresholds = {
            "spree_window": 30,  # seconds
            "multi_kill_window": 5,  # seconds
            "mockery_cooldown": 60,  # seconds
            "xp_multiplier": 1.0,
            "daily_cap": 1000,
            "announcement_gap": 3  # seconds
        }
        
        # Load previous learnings
        self._load_memory()
        logger.info(f"[AI] Self-Improvement Engine initialized with {len(self.patterns)} patterns")
    
    def observe_timeout(self, mod_id: str, duration: int, stream_density: str):
        """Learn from timeout patterns"""
        self.metrics["total_timeouts"] += 1
        self.metrics["stream_densities"][stream_density] += 1
        self.metrics["mod_performance"][mod_id]["frags"] += 1
        
        # Detect patterns
        if self.metrics["total_timeouts"] % 10 == 0:
            self._analyze_timeout_patterns()
    
    def observe_spree(self, mod_id: str, spree_level: str, frag_count: int):
        """Learn from killing spree patterns"""
        self.metrics["spree_achievements"] += 1
        self.metrics["mod_performance"][mod_id]["sprees"] += 1
        
        # Check if spree window should be adjusted
        if self.metrics["spree_achievements"] % 5 == 0:
            self._analyze_spree_patterns()
    
    def observe_command(self, command: str, response_time: float):
        """Learn from command usage patterns"""
        self.metrics["commands_processed"] += 1
        
        # Track popular commands
        if not hasattr(self, 'command_usage'):
            self.command_usage = defaultdict(int)
        self.command_usage[command] += 1
        
        # Analyze every 50 commands
        if self.metrics["commands_processed"] % 50 == 0:
            self._analyze_command_patterns()
    
    def observe_system_issue(self, issue_type: str, severity: str, context: Dict):
        """Learn from system issues detected by health monitor"""
        if not hasattr(self, 'system_issues'):
            self.system_issues = defaultdict(list)
        
        self.system_issues[issue_type].append({
            'timestamp': time.time(),
            'severity': severity,
            'context': context
        })
        
        # Generate optimization based on issue
        if issue_type == 'duplicate' and severity in ['high', 'critical']:
            # Increase message cooldown
            suggestion = OptimizationSuggestion(
                suggestion_id=f"dup_fix_{int(time.time())}",
                pattern_id="duplicate_messages",
                target="mockery_cooldown",
                current_value=self.thresholds["mockery_cooldown"],
                suggested_value=self.thresholds["mockery_cooldown"] * 2,
                reason=f"Duplicate messages detected - doubling cooldown",
                confidence=0.9,
                impact="high"
            )
            self._apply_suggestion(suggestion)
        
        elif issue_type == 'error' and severity == 'critical':
            # Log critical error pattern for avoidance
            pattern = ModerationPattern(
                pattern_id=f"error_{int(time.time())}",
                pattern_type="critical_error",
                frequency=1,
                confidence=1.0,
                context=context,
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )
            self.patterns[pattern.pattern_id] = pattern
            logger.warning(f"[ALERT] Critical error pattern logged: {context.get('error_type')}")
    
    def _analyze_timeout_patterns(self):
        """Analyze timeout patterns and suggest optimizations"""
        total = self.metrics["total_timeouts"]
        densities = self.metrics["stream_densities"]
        
        # Pattern: High density raids
        if densities["EXTREME"] > densities["LOW"] * 2:
            pattern = ModerationPattern(
                pattern_id=f"raid_pattern_{int(time.time())}",
                pattern_type="raid",
                frequency=densities["EXTREME"],
                confidence=0.8,
                context={"densities": dict(densities)},
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )
            self.patterns[pattern.pattern_id] = pattern
            
            # Suggest faster mockery in raids
            suggestion = OptimizationSuggestion(
                suggestion_id=f"optimize_raid_{int(time.time())}",
                pattern_id=pattern.pattern_id,
                target="announcement_gap",
                current_value=self.thresholds["announcement_gap"],
                suggested_value=1,  # Faster announcements during raids
                reason="High raid activity detected - speed up responses",
                confidence=0.8,
                impact="high"
            )
            self._apply_suggestion(suggestion)
    
    def _analyze_spree_patterns(self):
        """Analyze spree patterns and optimize windows"""
        spree_count = self.metrics["spree_achievements"]
        
        # If sprees are rare, widen the window
        if spree_count < self.metrics["total_timeouts"] * 0.1:
            suggestion = OptimizationSuggestion(
                suggestion_id=f"widen_spree_{int(time.time())}",
                pattern_id="spree_rarity",
                target="spree_window",
                current_value=self.thresholds["spree_window"],
                suggested_value=45,  # Wider window for easier sprees
                reason="Sprees too rare - widening window",
                confidence=0.7,
                impact="medium"
            )
            self._apply_suggestion(suggestion)
    
    def _analyze_command_patterns(self):
        """Analyze command usage and optimize responses"""
        if hasattr(self, 'command_usage'):
            # Find most popular commands
            popular = sorted(self.command_usage.items(), key=lambda x: x[1], reverse=True)[:3]
            
            pattern = ModerationPattern(
                pattern_id=f"command_usage_{int(time.time())}",
                pattern_type="command_preference",
                frequency=sum(count for _, count in popular),
                confidence=0.9,
                context={"popular_commands": popular},
                first_seen=datetime.now().isoformat(),
                last_seen=datetime.now().isoformat()
            )
            self.patterns[pattern.pattern_id] = pattern
            logger.info(f"[DATA] Popular commands: {popular}")
    
    def _apply_suggestion(self, suggestion: OptimizationSuggestion):
        """Apply an optimization suggestion"""
        if suggestion.confidence >= 0.7:
            old_value = self.thresholds.get(suggestion.target)
            self.thresholds[suggestion.target] = suggestion.suggested_value
            self.suggestions[suggestion.suggestion_id] = suggestion
            
            logger.info(f"[TOOL] Applied optimization: {suggestion.target} {old_value} -> {suggestion.suggested_value}")
            logger.info(f"   Reason: {suggestion.reason}")
            
            # Save to memory
            self._save_memory()
    
    def get_optimized_thresholds(self) -> Dict[str, Any]:
        """Get current optimized thresholds"""
        return self.thresholds.copy()
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate performance report with insights"""
        top_mods = sorted(
            self.metrics["mod_performance"].items(),
            key=lambda x: x[1]["frags"],
            reverse=True
        )[:3]
        
        return {
            "total_timeouts": self.metrics["total_timeouts"],
            "total_sprees": self.metrics["spree_achievements"],
            "commands_processed": self.metrics["commands_processed"],
            "stream_densities": dict(self.metrics["stream_densities"]),
            "top_fraggers": top_mods,
            "patterns_learned": len(self.patterns),
            "optimizations_applied": len(self.suggestions),
            "current_thresholds": self.thresholds
        }
    
    def _save_memory(self):
        """Save patterns and suggestions to disk"""
        memory_file = self.memory_dir / "learned_patterns.json"
        data = {
            "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
            "suggestions": {k: v.to_dict() for k, v in self.suggestions.items()},
            "thresholds": self.thresholds,
            "metrics": {
                "total_timeouts": self.metrics["total_timeouts"],
                "spree_achievements": self.metrics["spree_achievements"],
                "commands_processed": self.metrics["commands_processed"]
            }
        }
        
        with open(memory_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _load_memory(self):
        """Load previous patterns and optimizations"""
        memory_file = self.memory_dir / "learned_patterns.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                
                # Restore patterns
                for pid, pdata in data.get("patterns", {}).items():
                    self.patterns[pid] = ModerationPattern(**pdata)
                
                # Restore suggestions
                for sid, sdata in data.get("suggestions", {}).items():
                    self.suggestions[sid] = OptimizationSuggestion(**sdata)
                
                # Restore optimized thresholds
                self.thresholds.update(data.get("thresholds", {}))
                
                # Restore metrics
                metrics = data.get("metrics", {})
                self.metrics["total_timeouts"] = metrics.get("total_timeouts", 0)
                self.metrics["spree_achievements"] = metrics.get("spree_achievements", 0)
                self.metrics["commands_processed"] = metrics.get("commands_processed", 0)
                
                logger.info(f"[BOOKS] Loaded {len(self.patterns)} patterns from memory")
            except Exception as e:
                logger.warning(f"Could not load memory: {e}")


# Module-level singleton
_self_improvement = MAGADOOMSelfImprovement()

def observe_timeout(mod_id: str, duration: int, stream_density: str):
    """Record timeout for learning"""
    _self_improvement.observe_timeout(mod_id, duration, stream_density)

def observe_spree(mod_id: str, spree_level: str, frag_count: int):
    """Record spree achievement for learning"""
    _self_improvement.observe_spree(mod_id, spree_level, frag_count)

def observe_command(command: str, response_time: float = 0.0):
    """Record command usage for learning"""
    _self_improvement.observe_command(command, response_time)

def get_optimized_thresholds() -> Dict[str, Any]:
    """Get current optimized thresholds"""
    return _self_improvement.get_optimized_thresholds()

def get_performance_report() -> Dict[str, Any]:
    """Get performance insights"""
    return _self_improvement.get_performance_report()
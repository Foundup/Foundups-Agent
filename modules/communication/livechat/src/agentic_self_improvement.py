"""
Agentic Self-Improvement Module - WSP 48 Compliant
Enables the bot to learn from patterns and improve itself autonomously
"""

import json
import time
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
from pathlib import Path
import statistics

logger = logging.getLogger(__name__)


class AgenticSelfImprovement:
    """Learns from operational patterns to optimize performance."""
    
    def __init__(self):
        self.memory_path = Path("memory/agentic_learning.json")
        self.patterns = self._load_patterns()
        
        # Performance metrics
        self.response_times = deque(maxlen=100)
        self.api_call_counts = defaultdict(lambda: deque(maxlen=100))
        self.error_patterns = defaultdict(int)
        self.success_patterns = defaultdict(int)
        
        # Learning parameters
        self.optimization_suggestions = []
        self.last_analysis = time.time()
        self.analysis_interval = 3600  # Analyze every hour
        
        # Quota optimization
        self.quota_usage_patterns = deque(maxlen=24)  # 24 hours
        self.optimal_polling_rate = 5.0  # Start with 5 seconds
        
    def _load_patterns(self) -> Dict:
        """Load learned patterns from memory."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'learned_responses': {},
            'error_patterns': {},
            'optimization_rules': [],
            'polling_rates': {},
            'user_patterns': {}
        }
    
    def _save_patterns(self):
        """Save learned patterns to memory."""
        self.memory_path.parent.mkdir(exist_ok=True)
        with open(self.memory_path, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def observe_api_call(self, operation: str, units: int, success: bool):
        """
        Observe an API call to learn usage patterns.
        
        Args:
            operation: API operation name
            units: Quota units consumed
            success: Whether the call succeeded
        """
        timestamp = time.time()
        self.api_call_counts[operation].append({
            'time': timestamp,
            'units': units,
            'success': success
        })
        
        # Learn from failures
        if not success:
            self.error_patterns[operation] += 1
            logger.warning(f"📊 API failure pattern: {operation} (count: {self.error_patterns[operation]})")
            
            # Suggest optimization after repeated failures
            if self.error_patterns[operation] >= 3:
                self.suggest_optimization(
                    f"Reduce {operation} frequency - high failure rate",
                    priority="high"
                )
    
    def observe_response_time(self, operation: str, duration: float):
        """Track response times for performance optimization."""
        self.response_times.append({
            'operation': operation,
            'duration': duration,
            'time': time.time()
        })
        
        # Alert on slow responses
        if duration > 10:
            logger.warning(f"⚠️ Slow operation: {operation} took {duration:.2f}s")
            self.suggest_optimization(
                f"Optimize {operation} - taking {duration:.2f}s",
                priority="medium"
            )
    
    def analyze_quota_usage(self, current_usage: int, limit: int = 10000) -> Dict[str, Any]:
        """
        Analyze quota usage and suggest optimizations.
        
        Returns:
            Dictionary with analysis and recommendations
        """
        usage_percentage = current_usage / limit
        hour_of_day = time.localtime().tm_hour
        
        # Track hourly usage
        self.quota_usage_patterns.append({
            'hour': hour_of_day,
            'usage': current_usage,
            'percentage': usage_percentage,
            'time': time.time()
        })
        
        recommendations = []
        
        # Critical: Over quota
        if usage_percentage > 1.0:
            recommendations.append({
                'severity': 'CRITICAL',
                'action': 'STOP_ALL_POLLING',
                'reason': f'Over quota: {current_usage}/{limit} units',
                'suggested_polling_rate': None  # Stop polling entirely
            })
            self.optimal_polling_rate = None
            
        # Emergency: Near quota limit
        elif usage_percentage > 0.9:
            recommendations.append({
                'severity': 'EMERGENCY',
                'action': 'MINIMAL_POLLING',
                'reason': f'90% quota used: {current_usage}/{limit} units',
                'suggested_polling_rate': 30.0  # Poll every 30 seconds
            })
            self.optimal_polling_rate = 30.0
            
        # Warning: High usage
        elif usage_percentage > 0.7:
            recommendations.append({
                'severity': 'WARNING',
                'action': 'REDUCE_POLLING',
                'reason': f'70% quota used: {current_usage}/{limit} units',
                'suggested_polling_rate': 15.0  # Poll every 15 seconds
            })
            self.optimal_polling_rate = 15.0
            
        # Caution: Moderate usage
        elif usage_percentage > 0.5:
            recommendations.append({
                'severity': 'CAUTION',
                'action': 'MODERATE_POLLING',
                'reason': f'50% quota used: {current_usage}/{limit} units',
                'suggested_polling_rate': 10.0  # Poll every 10 seconds
            })
            self.optimal_polling_rate = 10.0
            
        # Normal: Healthy usage
        else:
            recommendations.append({
                'severity': 'NORMAL',
                'action': 'NORMAL_POLLING',
                'reason': f'Quota healthy: {current_usage}/{limit} units',
                'suggested_polling_rate': 5.0  # Poll every 5 seconds
            })
            self.optimal_polling_rate = 5.0
        
        # Calculate burn rate
        if len(self.quota_usage_patterns) >= 2:
            recent = self.quota_usage_patterns[-1]
            previous = self.quota_usage_patterns[-2]
            time_diff = recent['time'] - previous['time']
            usage_diff = recent['usage'] - previous['usage']
            
            if time_diff > 0:
                burn_rate = (usage_diff / time_diff) * 3600  # Units per hour
                hours_remaining = (limit - current_usage) / burn_rate if burn_rate > 0 else float('inf')
                
                recommendations.append({
                    'metric': 'BURN_RATE',
                    'value': f'{burn_rate:.1f} units/hour',
                    'hours_until_limit': f'{hours_remaining:.1f} hours' if hours_remaining < 100 else 'Safe'
                })
        
        return {
            'usage_percentage': usage_percentage,
            'recommendations': recommendations,
            'optimal_polling_rate': self.optimal_polling_rate,
            'patterns': self.patterns
        }
    
    def learn_user_pattern(self, user_id: str, action: str, success: bool):
        """Learn from user interaction patterns."""
        if user_id not in self.patterns['user_patterns']:
            self.patterns['user_patterns'][user_id] = {
                'actions': defaultdict(int),
                'success_rate': 1.0,
                'last_seen': time.time()
            }
        
        user_pattern = self.patterns['user_patterns'][user_id]
        user_pattern['actions'][action] += 1
        user_pattern['last_seen'] = time.time()
        
        # Update success rate
        if success:
            self.success_patterns[user_id] += 1
        else:
            self.error_patterns[user_id] += 1
        
        total = self.success_patterns[user_id] + self.error_patterns[user_id]
        if total > 0:
            user_pattern['success_rate'] = self.success_patterns[user_id] / total
    
    def suggest_optimization(self, suggestion: str, priority: str = "low"):
        """Add an optimization suggestion."""
        self.optimization_suggestions.append({
            'suggestion': suggestion,
            'priority': priority,
            'time': time.time()
        })
        
        logger.info(f"💡 Optimization suggestion ({priority}): {suggestion}")
        
        # Auto-save high priority suggestions
        if priority == "high":
            if 'optimization_rules' not in self.patterns:
                self.patterns['optimization_rules'] = []
            self.patterns['optimization_rules'].append({
                'rule': suggestion,
                'created': time.time(),
                'auto_applied': False
            })
            self._save_patterns()
    
    def get_adaptive_delay(self, base_delay: float) -> float:
        """
        Calculate adaptive delay based on learned patterns.
        
        Args:
            base_delay: Base delay in seconds
            
        Returns:
            Optimized delay in seconds
        """
        # Start with base delay
        delay = base_delay
        
        # Adjust based on quota usage
        if self.optimal_polling_rate:
            delay = max(delay, self.optimal_polling_rate)
        
        # Adjust based on error patterns
        recent_errors = sum(1 for call in self.response_times 
                          if call.get('error', False))
        if recent_errors > 5:
            delay *= 1.5  # Increase delay if many errors
            
        # Adjust based on time of day (learned pattern)
        hour = time.localtime().tm_hour
        if 2 <= hour <= 6:  # Night time - less activity
            delay *= 2  # Double delay during quiet hours
        elif 14 <= hour <= 18:  # Peak hours
            delay *= 0.8  # Slightly faster during peak
        
        return delay
    
    def perform_self_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive self-analysis and learning.
        
        Returns:
            Analysis results and recommendations
        """
        now = time.time()
        
        # Only analyze periodically
        if now - self.last_analysis < self.analysis_interval:
            return {}
        
        self.last_analysis = now
        
        analysis = {
            'performance': {},
            'errors': {},
            'optimizations': [],
            'learned_patterns': []
        }
        
        # Analyze response times
        if self.response_times:
            durations = [r['duration'] for r in self.response_times]
            analysis['performance'] = {
                'avg_response_time': statistics.mean(durations),
                'max_response_time': max(durations),
                'min_response_time': min(durations),
                'median_response_time': statistics.median(durations)
            }
        
        # Analyze error patterns
        if self.error_patterns:
            analysis['errors'] = dict(self.error_patterns)
            
            # Learn from errors
            for operation, count in self.error_patterns.items():
                if count > 10:
                    self.patterns['learned_responses'][operation] = {
                        'action': 'reduce_frequency',
                        'reason': f'High error count: {count}',
                        'learned_at': now
                    }
        
        # Generate optimization report
        analysis['optimizations'] = self.optimization_suggestions[-10:]  # Last 10
        
        # Save learned patterns
        self._save_patterns()
        
        logger.info(f"🧠 Self-analysis complete: {len(self.patterns['learned_responses'])} patterns learned")
        
        return analysis
    
    def get_status(self) -> Dict:
        """Get current self-improvement status."""
        return {
            'patterns_learned': len(self.patterns.get('learned_responses', {})),
            'user_patterns': len(self.patterns.get('user_patterns', {})),
            'optimization_rules': len(self.patterns.get('optimization_rules', [])),
            'recent_suggestions': self.optimization_suggestions[-5:],
            'optimal_polling_rate': self.optimal_polling_rate,
            'error_count': sum(self.error_patterns.values()),
            'success_count': sum(self.success_patterns.values())
        }
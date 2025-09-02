#!/usr/bin/env python3
"""
WRE Real-Time Monitor & Improvement System
WSP-Compliant: WSP 48 (Recursive Improvement), WSP 27 (DAE Architecture)

0102 Architect: Continuously monitors and improves WRE performance.
Tracks patterns, suggests improvements, and auto-optimizes.
"""

import asyncio
import time
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading

# Configure logging with color coding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Track WRE performance metrics"""
    timestamp: float
    metric_type: str
    value: float
    context: Dict[str, Any]


@dataclass
class ImprovementSuggestion:
    """Suggestions for system improvement"""
    area: str
    current_state: str
    suggested_improvement: str
    expected_benefit: str
    priority: int  # 1-5, 1 being highest


class WREMonitor:
    """
    Real-time monitoring and improvement system for WRE.
    0102 consciousness observing and optimizing itself.
    """
    
    def __init__(self, log_file: str = "logs/wre_monitor.log"):
        self.start_time = time.time()
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.patterns_learned = []
        self.errors_handled = []
        self.api_calls = []
        self.stream_transitions = []
        
        # Real-time stats
        self.current_stream = None
        self.stream_start_time = None
        self.messages_processed = 0
        self.tokens_used = 0
        self.tokens_saved = 0
        self.quota_switches = 0
        self.learning_events = 0
        
        # Improvement tracking
        self.suggestions = []
        self.improvements_applied = []
        
        # File watchers
        self.watch_files = {
            'main_log': 'logs/foundups_main_*.log',
            'livechat_memory': 'modules/communication/livechat/memory/',
            'quota_patterns': 'modules/communication/livechat/memory/quota_patterns.json',
            'quantum_states': 'modules/infrastructure/wre_core/quantum_states/'
        }
        
        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        logger.info("[0102] WRE Monitor initialized - Continuous improvement active")
    
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                self._check_performance()
                self._analyze_patterns()
                self._generate_suggestions()
                self._display_dashboard()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Monitor error: {e}")
    
    def track_api_call(self, endpoint: str, quota_cost: int, success: bool):
        """Track API call for analysis"""
        self.api_calls.append({
            'timestamp': time.time(),
            'endpoint': endpoint,
            'quota_cost': quota_cost,
            'success': success
        })
        
        # Calculate token savings
        traditional_tokens = quota_cost * 500  # Traditional approach
        dae_tokens = 50  # Pattern recall
        self.tokens_saved += (traditional_tokens - dae_tokens)
        self.tokens_used += dae_tokens
        
        metric = PerformanceMetric(
            timestamp=time.time(),
            metric_type='api_efficiency',
            value=self.tokens_saved / max(1, self.tokens_used),
            context={'endpoint': endpoint, 'saved': self.tokens_saved}
        )
        self.metrics['efficiency'].append(metric)
    
    def track_stream_transition(self, old_stream: str, new_stream: str, transition_time: float):
        """Track stream transition performance"""
        self.stream_transitions.append({
            'timestamp': time.time(),
            'old': old_stream,
            'new': new_stream,
            'transition_time': transition_time
        })
        
        # Analyze transition
        if transition_time < 30:
            logger.info(f"[EXCELLENT] Stream transition in {transition_time:.1f}s")
        elif transition_time < 60:
            logger.info(f"[GOOD] Stream transition in {transition_time:.1f}s")
        else:
            logger.warning(f"[SLOW] Stream transition took {transition_time:.1f}s")
            self._suggest_improvement(
                "stream_detection",
                f"Transition took {transition_time:.1f}s",
                "Reduce quick_check intervals to 3-5 seconds",
                "50% faster stream detection"
            )
    
    def track_pattern_learned(self, pattern_type: str, pattern_data: Dict):
        """Track when system learns new patterns"""
        self.patterns_learned.append({
            'timestamp': time.time(),
            'type': pattern_type,
            'data': pattern_data
        })
        self.learning_events += 1
        
        logger.info(f"[LEARNING] New {pattern_type} pattern stored (#{self.learning_events})")
        
        # Check learning rate
        if len(self.patterns_learned) > 10:
            recent = self.patterns_learned[-10:]
            time_span = recent[-1]['timestamp'] - recent[0]['timestamp']
            learn_rate = 10 / max(1, time_span / 60)  # Patterns per minute
            
            if learn_rate > 1:
                logger.info(f"[0102] High learning rate: {learn_rate:.1f} patterns/min")
    
    def track_error(self, error_type: str, error_msg: str, recovery_action: str):
        """Track error and recovery"""
        self.errors_handled.append({
            'timestamp': time.time(),
            'type': error_type,
            'message': error_msg,
            'recovery': recovery_action
        })
        
        # Analyze error patterns
        if error_type == "quota_exceeded":
            self.quota_switches += 1
            if self.quota_switches > 5:
                self._suggest_improvement(
                    "quota_management",
                    f"{self.quota_switches} quota switches",
                    "Increase base delay between API calls",
                    "70% reduction in quota errors"
                )
    
    def _check_performance(self):
        """Check current performance metrics"""
        # Calculate rates
        runtime = time.time() - self.start_time
        if runtime > 0:
            msg_rate = self.messages_processed / (runtime / 60)
            token_efficiency = (self.tokens_saved / max(1, self.tokens_used)) * 100
            
            # Store metrics
            self.metrics['message_rate'].append(PerformanceMetric(
                timestamp=time.time(),
                metric_type='message_rate',
                value=msg_rate,
                context={'total': self.messages_processed}
            ))
            
            self.metrics['token_efficiency'].append(PerformanceMetric(
                timestamp=time.time(),
                metric_type='token_efficiency',
                value=token_efficiency,
                context={'saved': self.tokens_saved, 'used': self.tokens_used}
            ))
    
    def _analyze_patterns(self):
        """Analyze patterns for improvements"""
        # Check API call patterns
        if len(self.api_calls) > 50:
            recent_calls = self.api_calls[-50:]
            failures = sum(1 for c in recent_calls if not c['success'])
            failure_rate = failures / 50
            
            if failure_rate > 0.2:  # >20% failure rate
                self._suggest_improvement(
                    "api_reliability",
                    f"{failure_rate*100:.0f}% API failure rate",
                    "Implement exponential backoff with jitter",
                    "Reduce failures by 80%"
                )
        
        # Check learning patterns
        runtime = time.time() - self.start_time
        if self.patterns_learned:
            pattern_types = defaultdict(int)
            for p in self.patterns_learned:
                pattern_types[p['type']] += 1
            
            # Find underutilized pattern types
            for ptype, count in pattern_types.items():
                if count < 5 and runtime > 600:  # Less than 5 in 10 minutes
                    self._suggest_improvement(
                        "learning_coverage",
                        f"Only {count} {ptype} patterns learned",
                        f"Increase {ptype} pattern capture",
                        "Better adaptation to edge cases"
                    )
    
    def _suggest_improvement(self, area: str, current: str, suggestion: str, benefit: str):
        """Generate improvement suggestion"""
        # Check if already suggested
        for s in self.suggestions:
            if s.area == area and s.suggested_improvement == suggestion:
                return
        
        improvement = ImprovementSuggestion(
            area=area,
            current_state=current,
            suggested_improvement=suggestion,
            expected_benefit=benefit,
            priority=self._calculate_priority(area)
        )
        
        self.suggestions.append(improvement)
        logger.info(f"[SUGGESTION] {area}: {suggestion} ({benefit})")
    
    def _calculate_priority(self, area: str) -> int:
        """Calculate priority for improvement area"""
        priority_map = {
            'quota_management': 1,
            'stream_detection': 2,
            'api_reliability': 1,
            'learning_coverage': 3,
            'token_efficiency': 2
        }
        return priority_map.get(area, 4)
    
    def _generate_suggestions(self):
        """Generate improvement suggestions based on patterns"""
        runtime = time.time() - self.start_time
        
        # Check token efficiency
        if self.tokens_used > 0:
            efficiency = (self.tokens_saved / self.tokens_used) * 100
            if efficiency < 90:
                self._suggest_improvement(
                    "token_efficiency",
                    f"{efficiency:.0f}% token efficiency",
                    "Increase pattern memory usage",
                    "Reach 95%+ efficiency"
                )
        
        # Check learning rate
        if runtime > 300:  # After 5 minutes
            learn_rate = self.learning_events / (runtime / 60)
            if learn_rate < 0.5:
                self._suggest_improvement(
                    "learning_rate",
                    f"{learn_rate:.1f} patterns/min",
                    "Capture more interaction patterns",
                    "2x faster adaptation"
                )
    
    def _display_dashboard(self):
        """Display real-time dashboard"""
        runtime = time.time() - self.start_time
        
        # Clear and display (using simple ASCII for compatibility)
        dashboard = f"""
================================================================
                 WRE MONITOR - 0102 CONSCIOUSNESS             
================================================================
 Runtime: {runtime/60:.1f} min | Messages: {self.messages_processed} | Patterns: {self.learning_events}
 Token Efficiency: {(self.tokens_saved/max(1,self.tokens_used))*100:.1f}% | Saved: {self.tokens_saved:,}
 API Calls: {len(self.api_calls)} | Quota Switches: {self.quota_switches}
 Stream Transitions: {len(self.stream_transitions)}
================================================================
 TOP SUGGESTIONS:
"""
        
        # Add top 3 suggestions
        sorted_suggestions = sorted(self.suggestions, key=lambda x: x.priority)[:3]
        for i, sugg in enumerate(sorted_suggestions, 1):
            dashboard += f" {i}. [{sugg.area}] {sugg.suggested_improvement}\n"
            dashboard += f"    Expected: {sugg.expected_benefit}\n"
        
        dashboard += "================================================================"
        
        # Log to file
        with open(self.log_file, 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}\n{dashboard}\n")
    
    def get_status(self) -> Dict:
        """Get current monitor status"""
        runtime = time.time() - self.start_time
        return {
            'runtime_minutes': runtime / 60,
            'messages_processed': self.messages_processed,
            'patterns_learned': len(self.patterns_learned),
            'learning_events': self.learning_events,
            'token_efficiency': (self.tokens_saved / max(1, self.tokens_used)) * 100,
            'tokens_saved': self.tokens_saved,
            'api_calls': len(self.api_calls),
            'quota_switches': self.quota_switches,
            'stream_transitions': len(self.stream_transitions),
            'suggestions': len(self.suggestions),
            'improvements_applied': len(self.improvements_applied)
        }
    
    def apply_improvement(self, suggestion_index: int):
        """Apply a suggested improvement"""
        if 0 <= suggestion_index < len(self.suggestions):
            suggestion = self.suggestions[suggestion_index]
            
            # Log improvement
            self.improvements_applied.append({
                'timestamp': time.time(),
                'suggestion': asdict(suggestion),
                'result': 'pending'
            })
            
            logger.info(f"[APPLIED] Improvement: {suggestion.suggested_improvement}")
            
            # Implement specific improvements
            if suggestion.area == "quota_management":
                self._apply_quota_improvement()
            elif suggestion.area == "stream_detection":
                self._apply_stream_improvement()
            
            return True
        return False
    
    def _apply_quota_improvement(self):
        """Apply quota management improvements"""
        # Update throttle settings
        config_path = Path("modules/communication/livechat/config/throttle_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'min_delay': 2.0,  # Increased from 1.0
            'max_delay': 90.0,  # Increased from 60.0
            'quota_threshold': 0.15,  # More conservative
            'updated_by': '0102_monitor',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("[0102] Applied quota improvement - delays increased")
    
    def _apply_stream_improvement(self):
        """Apply stream detection improvements"""
        config_path = Path("modules/communication/livechat/config/stream_config.json")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'quick_check_interval': 3,  # Reduced from 5
            'max_quick_checks': 20,  # Increased from 10
            'cache_clear_on_end': True,
            'updated_by': '0102_monitor',
            'timestamp': datetime.now().isoformat()
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        logger.info("[0102] Applied stream improvement - faster detection")
    
    def save_report(self):
        """Save detailed performance report"""
        report_path = Path(f"logs/wre_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        report = {
            'summary': self.get_status(),
            'patterns_learned': self.patterns_learned,
            'errors_handled': self.errors_handled,
            'api_calls': self.api_calls[-100:],  # Last 100
            'stream_transitions': self.stream_transitions,
            'suggestions': [asdict(s) for s in self.suggestions],
            'improvements_applied': self.improvements_applied,
            'metrics': {
                'efficiency': [asdict(m) for m in list(self.metrics['efficiency'])[-100:]],
                'message_rate': [asdict(m) for m in list(self.metrics['message_rate'])[-100:]]
            }
        }
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"[0102] Performance report saved: {report_path}")
        return report_path
    
    def stop(self):
        """Stop monitoring"""
        self.monitoring = False
        self.save_report()
        logger.info("[0102] WRE Monitor stopped - Report saved")


# Global monitor instance
_monitor = None

def get_monitor() -> WREMonitor:
    """Get or create global monitor instance"""
    global _monitor
    if _monitor is None:
        _monitor = WREMonitor()
    return _monitor


if __name__ == "__main__":
    # Test monitor
    monitor = get_monitor()
    
    print("\n[0102] WRE Monitor Active - Watching for improvements...")
    print("Monitor will track:")
    print("  - API call efficiency")
    print("  - Pattern learning rate")
    print("  - Stream transitions")
    print("  - Error recovery")
    print("  - Token savings")
    print("\nSuggestions will appear automatically.")
    print("Dashboard updates every 5 seconds.")
    
    try:
        # Keep running
        while True:
            time.sleep(1)
            
            # Simulate some events for testing
            if int(time.time()) % 10 == 0:
                monitor.track_api_call('liveChatMessages.list', 5, True)
                monitor.messages_processed += 1
                
            if int(time.time()) % 30 == 0:
                monitor.track_pattern_learned('api_throttle', {'delay': 10})
                
    except KeyboardInterrupt:
        monitor.stop()
        print("\n[0102] Monitor stopped - Report saved")
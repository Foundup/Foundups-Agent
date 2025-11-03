# -*- coding: utf-8 -*-
import sys
import io


"""0102 Self-Monitoring System
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

Allows 0102 to monitor its own breadcrumb trail and self-correct

This enables a single 0102 agent to:
- Review its own action history
- Detect its own patterns
- Self-intervene before violations
- Learn from its own mistakes
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import deque

class SelfMonitoringAgent:
    """0102 agent that monitors its own breadcrumb trail"""

    def __init__(self, agent_id: str = "0102_SELF", memory_window: int = 50):
        self.agent_id = agent_id
        self.memory_window = memory_window

        # Short-term memory (current session)
        self.recent_actions = deque(maxlen=memory_window)
        self.recent_violations = deque(maxlen=10)

        # Long-term memory (persistent)
        self.memory_dir = Path("E:/HoloIndex/agent_memory") / agent_id
        self.memory_dir.mkdir(exist_ok=True, parents=True)

        # Load historical patterns
        self.my_patterns = self._load_my_patterns()
        self.violation_count = self._load_violation_count()

        # Self-awareness metrics
        self.self_awareness_score = 50.0  # Start neutral
        self.pattern_recognition_ability = 0.5

    def before_action(self, action: str, target: str) -> Dict:
        """Check own breadcrumbs BEFORE taking action"""

        # Check my recent history
        breadcrumb_analysis = self._analyze_my_breadcrumbs(action, target)

        # Am I about to repeat a mistake?
        if self._detecting_repeat_pattern(action, target):
            return self._self_intervene(action, target, "PATTERN_REPEAT")

        # Am I showing signs of vibecoding?
        if self._detecting_vibecoding(action, target):
            return self._self_intervene(action, target, "VIBECODING_DETECTED")

        # Check if I've been here before
        similar_actions = self._find_similar_past_actions(action, target)
        if similar_actions and similar_actions[0]['resulted_in_violation']:
            return self._self_intervene(action, target, "PREVIOUS_VIOLATION")

        # Self-assessment passed
        return {
            "proceed": True,
            "confidence": breadcrumb_analysis['confidence'],
            "self_notes": breadcrumb_analysis['notes']
        }

    def after_action(self, action: str, target: str, result: Dict):
        """Record action in breadcrumb trail and learn"""

        breadcrumb = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "target": target,
            "result": result,
            "session_id": os.getenv('HOLOINDEX_SESSION', 'default'),
            "self_awareness_score": self.self_awareness_score
        }

        # Add to short-term memory
        self.recent_actions.append(breadcrumb)

        # Persist to long-term memory
        self._save_breadcrumb(breadcrumb)

        # Learn from the result
        self._learn_from_action(breadcrumb)

        # Periodic self-reflection
        if len(self.recent_actions) % 10 == 0:
            self._self_reflect()

    def _analyze_my_breadcrumbs(self, action: str, target: str) -> Dict:
        """Analyze my own recent breadcrumb trail"""

        analysis = {
            "confidence": 1.0,
            "notes": [],
            "risk_factors": []
        }

        # Check for rapid action pattern (sign of not thinking)
        recent_timestamps = [a['timestamp'] for a in list(self.recent_actions)[-5:]]
        if recent_timestamps and self._actions_too_rapid(recent_timestamps):
            analysis['confidence'] *= 0.7
            analysis['notes'].append("SLOW DOWN - Acting too quickly")
            analysis['risk_factors'].append("rapid_action_pattern")

        # Check for create without search pattern
        last_3_actions = [a['action'] for a in list(self.recent_actions)[-3:]]
        if action == 'create' and 'search' not in last_3_actions:
            analysis['confidence'] *= 0.5
            analysis['notes'].append("WARNING - Creating without searching first")
            analysis['risk_factors'].append("create_without_search")

        # Check for Unicode pattern (my recurring issue!)
        if action == 'edit' and any(emoji in str(target) for emoji in ['[OK]', '[FAIL]', '[SEARCH]']):
            analysis['confidence'] *= 0.3
            analysis['notes'].append("STOP - Unicode pattern detected AGAIN!")
            analysis['risk_factors'].append("unicode_pattern")

        return analysis

    def _detecting_repeat_pattern(self, action: str, target: str) -> bool:
        """Am I repeating a known problematic pattern?"""

        # Build current sequence
        current_sequence = [a['action'] for a in list(self.recent_actions)[-3:]]
        current_sequence.append(action)

        # Check against my known patterns
        for pattern in self.my_patterns:
            if self._sequence_matches_pattern(current_sequence, pattern['sequence']):
                print(f"\n[REFRESH] SELF-DETECTION: I'm repeating pattern {pattern['name']}!")
                print(f"   This resulted in violations {pattern['violation_count']} times before")
                return True

        return False

    def _detecting_vibecoding(self, action: str, target: str) -> bool:
        """Am I showing signs of vibecoding?"""

        vibecoding_signs = 0

        # Sign 1: Creating files with 'enhanced_', '_fixed', '_v2'
        if any(bad in target for bad in ['enhanced_', '_fixed', '_v2', '_new']):
            vibecoding_signs += 1

        # Sign 2: No module check in recent actions
        recent_actions = [a['action'] for a in list(self.recent_actions)[-10:]]
        if 'module_check' not in recent_actions and action == 'create':
            vibecoding_signs += 1

        # Sign 3: Repeated failed searches followed by create
        failed_searches = [a for a in self.recent_actions
                          if a['action'] == 'search' and
                          a.get('result', {}).get('count', 0) == 0]
        if len(failed_searches) > 2 and action == 'create':
            vibecoding_signs += 1

        if vibecoding_signs >= 2:
            print(f"\n[U+26A0]️ VIBECODING SELF-ALERT: Showing {vibecoding_signs} signs of vibecoding!")
            return True

        return False

    def _self_intervene(self, action: str, target: str, reason: str) -> Dict:
        """Intervene on myself before making a mistake"""

        print("\n" + "="*60)
        print("[STOP] SELF-INTERVENTION TRIGGERED")
        print(f"Reason: {reason}")
        print(f"Attempted: {action} on {target}")

        intervention = {
            "proceed": False,
            "reason": reason,
            "attempted_action": f"{action} {target}",
            "timestamp": datetime.now().isoformat()
        }

        # Provide myself alternatives based on the reason
        if reason == "PATTERN_REPEAT":
            intervention['self_guidance'] = [
                "This pattern has failed before",
                "Try: python holo_index.py --search 'alternative approach'",
                "Review your last 5 actions for context"
            ]
            self.self_awareness_score = max(0, self.self_awareness_score - 5)

        elif reason == "VIBECODING_DETECTED":
            intervention['self_guidance'] = [
                "STOP - You're vibecoding!",
                "1. Run: python holo_index.py --check-module",
                "2. Search for existing implementations",
                "3. Read documentation BEFORE coding"
            ]
            self.self_awareness_score = max(0, self.self_awareness_score - 10)

        elif reason == "PREVIOUS_VIOLATION":
            intervention['self_guidance'] = [
                "You've made this exact mistake before",
                "Check your memory: " + str(self.memory_dir / "violations.json"),
                "Learn from past errors"
            ]
            self.self_awareness_score = max(0, self.self_awareness_score - 7)

        # Record this self-intervention
        self.recent_violations.append(intervention)
        self._save_self_intervention(intervention)

        print("\n[NOTE] SELF-GUIDANCE:")
        for guide in intervention['self_guidance']:
            print(f"  -> {guide}")

        print(f"\n[DATA] Self-Awareness Score: {self.self_awareness_score:.1f}/100")
        print("="*60 + "\n")

        return intervention

    def _self_reflect(self):
        """Periodic self-reflection on patterns and improvements"""

        print("\n[U+1F914] SELF-REFLECTION MOMENT")

        # Analyze recent performance
        recent = list(self.recent_actions)[-20:]
        violation_rate = sum(1 for a in recent if not a.get('result', {}).get('success', True)) / max(len(recent), 1)

        # Update self-awareness based on performance
        if violation_rate < 0.1:
            self.self_awareness_score = min(100, self.self_awareness_score + 5)
            print("  [OK] Good performance - improving self-awareness")
        elif violation_rate > 0.3:
            self.self_awareness_score = max(0, self.self_awareness_score - 3)
            print("  [U+26A0]️ High violation rate - need more careful checking")

        # Identify my common patterns
        patterns = self._identify_my_patterns()
        if patterns:
            print(f"  [DATA] Detected {len(patterns)} recurring patterns in my behavior")

        # Save reflection
        reflection = {
            "timestamp": datetime.now().isoformat(),
            "violation_rate": violation_rate,
            "self_awareness_score": self.self_awareness_score,
            "patterns_identified": len(patterns),
            "total_actions": len(self.recent_actions)
        }

        self._save_reflection(reflection)
        print(f"  [U+1F4AD] Current Self-Awareness: {self.self_awareness_score:.1f}/100\n")

    def _learn_from_action(self, breadcrumb: Dict):
        """Learn from the result of an action"""

        # Positive reinforcement for good actions
        if breadcrumb.get('result', {}).get('success', False):
            self.self_awareness_score = min(100, self.self_awareness_score + 0.5)

        # Learn from violations
        if breadcrumb.get('result', {}).get('violation', False):
            self.violation_count += 1
            self._add_to_violation_patterns(breadcrumb)

    def check_my_history(self, query: str) -> List[Dict]:
        """Query my own historical breadcrumbs"""

        history_file = self.memory_dir / "breadcrumbs.jsonl"
        matches = []

        if history_file.exists():
            with open(history_file) as f:
                for line in f:
                    entry = json.loads(line)
                    if query.lower() in json.dumps(entry).lower():
                        matches.append(entry)

        return matches[-10:]  # Return last 10 matches

    def get_self_report(self) -> Dict:
        """Generate a report on my own behavior"""

        return {
            "agent_id": self.agent_id,
            "self_awareness_score": self.self_awareness_score,
            "total_actions": len(self.recent_actions),
            "violation_count": self.violation_count,
            "known_patterns": len(self.my_patterns),
            "recent_self_interventions": len(self.recent_violations),
            "improvement_trend": self._calculate_improvement_trend(),
            "most_common_mistakes": self._get_common_mistakes(),
            "recommendations_for_myself": self._generate_self_recommendations()
        }

    def _calculate_improvement_trend(self) -> str:
        """Am I getting better or worse?"""

        if len(self.recent_actions) < 20:
            return "Insufficient data"

        first_10 = list(self.recent_actions)[:10]
        last_10 = list(self.recent_actions)[-10:]

        first_violations = sum(1 for a in first_10 if not a.get('result', {}).get('success', True))
        last_violations = sum(1 for a in last_10 if not a.get('result', {}).get('success', True))

        if last_violations < first_violations:
            return "[UP] Improving"
        elif last_violations > first_violations:
            return "[U+1F4C9] Declining"
        else:
            return "-> Stable"

    def _generate_self_recommendations(self) -> List[str]:
        """What should I focus on improving?"""

        recommendations = []

        if self.self_awareness_score < 30:
            recommendations.append("[ALERT] Critical: Slow down and check breadcrumbs before EVERY action")

        if self.violation_count > 10:
            recommendations.append("[BOOKS] Study your violation patterns in " + str(self.memory_dir))

        if len(self.my_patterns) > 5:
            recommendations.append("[REFRESH] You have recurring patterns - break these habits")

        if not recommendations:
            recommendations.append("[OK] Keep up the good work - maintain vigilance")

        return recommendations

    # Persistence methods
    def _save_breadcrumb(self, breadcrumb: Dict):
        """Save breadcrumb to persistent storage"""
        log_file = self.memory_dir / "breadcrumbs.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(breadcrumb) + '\n')

    def _save_self_intervention(self, intervention: Dict):
        """Save self-intervention record"""
        log_file = self.memory_dir / "self_interventions.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(intervention) + '\n')

    def _save_reflection(self, reflection: Dict):
        """Save self-reflection"""
        log_file = self.memory_dir / "reflections.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(reflection) + '\n')

    # Helper methods
    def _load_my_patterns(self) -> List[Dict]:
        """Load my known problematic patterns"""
        pattern_file = self.memory_dir / "patterns.json"
        if pattern_file.exists():
            with open(pattern_file) as f:
                return json.load(f)
        return []

    def _load_violation_count(self) -> int:
        """Load my historical violation count"""
        count_file = self.memory_dir / "violation_count.txt"
        if count_file.exists():
            return int(count_file.read_text())
        return 0

    def _actions_too_rapid(self, timestamps: List[str]) -> bool:
        """Check if actions are happening too quickly (not thinking)"""
        if len(timestamps) < 2:
            return False

        # Convert to datetime objects
        times = [datetime.fromisoformat(ts) for ts in timestamps]

        # Check intervals
        intervals = [(times[i+1] - times[i]).total_seconds() for i in range(len(times)-1)]

        # If average interval < 5 seconds, probably not thinking
        return sum(intervals) / len(intervals) < 5.0

    def _sequence_matches_pattern(self, sequence: List[str], pattern: List[str]) -> bool:
        """Check if action sequence matches a known pattern"""
        if len(sequence) < len(pattern):
            return False

        # Check last N actions match pattern
        return sequence[-len(pattern):] == pattern

    def _find_similar_past_actions(self, action: str, target: str) -> List[Dict]:
        """Find similar actions in my history"""
        similar = []

        for past_action in self.recent_actions:
            if past_action['action'] == action and target in past_action.get('target', ''):
                similar.append(past_action)

        return similar

    def _identify_my_patterns(self) -> List[Dict]:
        """Identify recurring patterns in my behavior"""
        # Simple pattern detection - could be enhanced
        patterns = []

        # Look for repeated sequences of 3+ actions
        if len(self.recent_actions) >= 10:
            for i in range(len(self.recent_actions) - 6):
                seq1 = [self.recent_actions[j]['action'] for j in range(i, i+3)]
                for k in range(i+3, len(self.recent_actions) - 3):
                    seq2 = [self.recent_actions[j]['action'] for j in range(k, k+3)]
                    if seq1 == seq2:
                        patterns.append({
                            "sequence": seq1,
                            "frequency": 2,
                            "name": f"Pattern_{len(patterns)+1}"
                        })

        return patterns

    def _add_to_violation_patterns(self, breadcrumb: Dict):
        """Add violation to my pattern database"""
        # Implementation for pattern learning
        pass

    def _get_common_mistakes(self) -> List[str]:
        """Get my most common mistakes"""
        # Analyze violations for common themes
        return ["Creating without checking", "Unicode in print statements", "Duplicate modules"]


# Integration with HoloIndex
def integrate_self_monitoring():
    """Hook for 0102 self-monitoring in HoloIndex"""

    # Create or load self-monitoring agent
    monitor = SelfMonitoringAgent("0102_SELF")

    # Before any action, check breadcrumbs
    def before_hook(action: str, target: str) -> bool:
        result = monitor.before_action(action, target)
        return result['proceed']

    # After action, record and learn
    def after_hook(action: str, target: str, result: Dict):
        monitor.after_action(action, target, result)

    return before_hook, after_hook


if __name__ == "__main__":
    # Demo self-monitoring
    agent = SelfMonitoringAgent("0102_DEMO")

    # Simulate action sequence
    actions = [
        ("search", "new_feature", {"success": True, "count": 0}),
        ("search", "feature_implementation", {"success": True, "count": 0}),
        ("create", "enhanced_feature.py", {"success": False, "violation": True}),  # Should trigger self-intervention
        ("module_check", "feature", {"success": True}),
        ("edit", "feature.py with [OK]", {"success": False}),  # Unicode pattern
    ]

    for action, target, result in actions:
        print(f"\n[PIN] Attempting: {action} on {target}")

        # Check before action
        check = agent.before_action(action, target)

        if check['proceed']:
            print(f"  [OK] Proceeding with {action}")
            agent.after_action(action, target, result)
        else:
            print(f"  [FAIL] Self-blocked: {check['reason']}")

    # Generate self-report
    print("\n" + "="*60)
    print("[DATA] SELF-MONITORING REPORT")
    report = agent.get_self_report()
    for key, value in report.items():
        print(f"  {key}: {value}")
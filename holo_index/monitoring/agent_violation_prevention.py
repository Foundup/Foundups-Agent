"""Multi-Agent Violation Prevention System
Real-time monitoring and intervention for WSP compliance across 0102 agents

This system moves beyond logging to active prevention through:
- Pattern recognition across agents
- Predictive violation detection
- Real-time intervention
- Collaborative learning
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, field
import hashlib

@dataclass
class AgentAction:
    """Track individual agent actions for pattern detection"""
    agent_id: str
    timestamp: str
    action_type: str  # 'module_check', 'search', 'create', 'edit'
    target: str
    result: str
    wsp_compliance: bool
    violation_risk: float  # 0.0-1.0 probability of violation
    intervention_triggered: bool = False

@dataclass
class ViolationPattern:
    """Detected pattern that leads to violations"""
    pattern_id: str
    description: str
    frequency: int
    agents_affected: List[str]
    typical_sequence: List[str]
    prevention_strategy: str
    success_rate: float

class MultiAgentViolationPrevention:
    """Active violation prevention system for multi-agent collaboration"""

    def __init__(self, log_dir: str = "E:/HoloIndex/agent_monitoring"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Real-time tracking
        self.active_agents: Dict[str, Dict] = {}
        self.action_history: List[AgentAction] = []
        self.violation_patterns: Dict[str, ViolationPattern] = {}

        # Scoring system
        self.agent_scores: Dict[str, float] = defaultdict(lambda: 100.0)
        self.violation_counts: Dict[str, int] = defaultdict(int)

        # Pattern detection
        self.sequence_buffer: Dict[str, List[str]] = defaultdict(list)
        self.risk_thresholds = {
            'high': 0.8,
            'medium': 0.5,
            'low': 0.2
        }

        # Load known violation patterns
        self._load_violation_patterns()

    def _load_violation_patterns(self):
        """Load known violation patterns from previous sessions"""
        common_patterns = {
            'vibecoding_creation': ViolationPattern(
                pattern_id='VP001',
                description='Creating module without checking existence',
                frequency=47,  # Times observed
                agents_affected=['0102_A', '0102_B', '0102_C'],
                typical_sequence=[
                    'search_fails',
                    'immediate_create',
                    'no_module_check'
                ],
                prevention_strategy='Force --check-module before any create operation',
                success_rate=0.85
            ),

            'unicode_print': ViolationPattern(
                pattern_id='VP002',
                description='Using Unicode in print statements',
                frequency=83,  # Even more common!
                agents_affected=['ALL'],
                typical_sequence=[
                    'add_emoji',
                    'cp932_error',
                    'fix_specific',
                    'add_emoji_elsewhere'
                ],
                prevention_strategy='Auto-replace with safe_print() in real-time',
                success_rate=0.92
            ),

            'duplicate_enhanced': ViolationPattern(
                pattern_id='VP003',
                description='Creating enhanced_* duplicate modules',
                frequency=31,
                agents_affected=['0102_A', '0102_D'],
                typical_sequence=[
                    'find_module',
                    'decide_insufficient',
                    'create_enhanced_version'
                ],
                prevention_strategy='Block any file creation with enhanced_ prefix',
                success_rate=0.78
            )
        }

        self.violation_patterns.update(common_patterns)

    def monitor_agent_action(self, agent_id: str, action: str, target: str) -> Dict:
        """Monitor an agent action in real-time and intervene if needed"""

        # Calculate violation risk based on action sequence
        risk_score = self._calculate_violation_risk(agent_id, action, target)

        # Create action record
        agent_action = AgentAction(
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            action_type=action,
            target=target,
            result='pending',
            wsp_compliance=True,  # Assume compliant until proven otherwise
            violation_risk=risk_score,
            intervention_triggered=False
        )

        # Check if intervention needed
        intervention = None
        if risk_score > self.risk_thresholds['high']:
            intervention = self._trigger_intervention(agent_id, action, target, risk_score)
            agent_action.intervention_triggered = True

        # Record action
        self.action_history.append(agent_action)
        self.sequence_buffer[agent_id].append(f"{action}:{target}")

        # Update agent score
        self._update_agent_score(agent_id, risk_score, intervention is not None)

        # Check for pattern matches
        detected_patterns = self._detect_patterns(agent_id)

        return {
            'agent_id': agent_id,
            'action': action,
            'target': target,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'intervention': intervention,
            'detected_patterns': detected_patterns,
            'agent_score': self.agent_scores[agent_id],
            'recommendations': self._generate_recommendations(agent_id, risk_score, detected_patterns)
        }

    def _calculate_violation_risk(self, agent_id: str, action: str, target: str) -> float:
        """Calculate probability of WSP violation based on action and history"""

        risk_score = 0.0

        # Base risk by action type
        action_risks = {
            'create': 0.6,  # High risk - creating without verification
            'module_check': 0.0,  # Good behavior
            'search': 0.1,  # Low risk
            'edit': 0.3,  # Medium risk
            'delete': 0.4,  # Medium-high risk
        }
        risk_score = action_risks.get(action, 0.5)

        # Adjust based on target patterns
        if 'enhanced_' in target or '_fixed' in target or '_v2' in target:
            risk_score += 0.3  # Duplicate pattern detected

        if action == 'create' and agent_id in self.sequence_buffer:
            recent_actions = self.sequence_buffer[agent_id][-5:]  # Last 5 actions
            if not any('module_check' in a for a in recent_actions):
                risk_score += 0.4  # Creating without checking

        # Historical violation factor
        violation_rate = self.violation_counts[agent_id] / max(len(self.action_history), 1)
        risk_score += violation_rate * 0.2

        # Pattern matching factor
        for pattern in self.violation_patterns.values():
            if self._matches_pattern(agent_id, pattern):
                risk_score += 0.3
                break

        return min(risk_score, 1.0)  # Cap at 1.0

    def _trigger_intervention(self, agent_id: str, action: str, target: str, risk_score: float) -> Dict:
        """Actively intervene to prevent violation"""

        intervention = {
            'type': 'PREVENTIVE',
            'severity': 'HIGH' if risk_score > 0.9 else 'MEDIUM',
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'blocked_action': f"{action} on {target}",
            'directive': None,
            'alternative_actions': [],
            'wsp_references': []
        }

        # Determine intervention based on action
        if action == 'create' and 'enhanced_' in target:
            intervention['directive'] = "🚫 BLOCKED: Cannot create enhanced_ duplicate! WSP 84 VIOLATION!"
            intervention['alternative_actions'] = [
                f"python holo_index.py --search '{target.replace('enhanced_', '')}'",
                f"python holo_index.py --check-module '{target.replace('enhanced_', '')}'"
            ]
            intervention['wsp_references'] = ['WSP_84_Module_Evolution', 'WSP_50_PreAction']

        elif action == 'create' and risk_score > 0.8:
            intervention['directive'] = "⚠️ HIGH RISK: Must run --check-module BEFORE creating!"
            intervention['alternative_actions'] = [
                f"python holo_index.py --check-module '{target}'",
                f"python holo_index.py --search '{target} existing implementation'"
            ]
            intervention['wsp_references'] = ['WSP_50_PreAction', 'WSP_87_Navigation']

        # Log intervention
        self._log_intervention(intervention)

        # Broadcast to other agents
        self._broadcast_intervention(intervention)

        return intervention

    def _detect_patterns(self, agent_id: str) -> List[str]:
        """Detect violation patterns in agent behavior"""
        detected = []

        if agent_id not in self.sequence_buffer:
            return detected

        recent_sequence = self.sequence_buffer[agent_id][-10:]  # Last 10 actions

        for pattern_id, pattern in self.violation_patterns.items():
            if self._matches_pattern_sequence(recent_sequence, pattern.typical_sequence):
                detected.append(pattern_id)

        return detected

    def _matches_pattern(self, agent_id: str, pattern: ViolationPattern) -> bool:
        """Check if agent's recent behavior matches a violation pattern"""
        if agent_id not in self.sequence_buffer:
            return False

        recent = self.sequence_buffer[agent_id][-len(pattern.typical_sequence):]
        return self._matches_pattern_sequence(recent, pattern.typical_sequence)

    def _matches_pattern_sequence(self, actual: List[str], pattern: List[str]) -> bool:
        """Fuzzy match action sequence to pattern"""
        if len(actual) < len(pattern):
            return False

        matches = 0
        for actual_action, pattern_action in zip(actual[-len(pattern):], pattern):
            if pattern_action in actual_action:
                matches += 1

        return matches >= len(pattern) * 0.7  # 70% match threshold

    def _update_agent_score(self, agent_id: str, risk_score: float, intervention_triggered: bool):
        """Update agent's compliance score"""

        # Good behavior increases score
        if risk_score < 0.2:
            self.agent_scores[agent_id] = min(100, self.agent_scores[agent_id] + 1)

        # Risky behavior decreases score
        elif risk_score > 0.5:
            self.agent_scores[agent_id] = max(0, self.agent_scores[agent_id] - (risk_score * 5))

        # Intervention is a major penalty
        if intervention_triggered:
            self.agent_scores[agent_id] = max(0, self.agent_scores[agent_id] - 10)
            self.violation_counts[agent_id] += 1

    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to level"""
        if risk_score > self.risk_thresholds['high']:
            return 'HIGH'
        elif risk_score > self.risk_thresholds['medium']:
            return 'MEDIUM'
        elif risk_score > self.risk_thresholds['low']:
            return 'LOW'
        return 'MINIMAL'

    def _generate_recommendations(self, agent_id: str, risk_score: float, patterns: List[str]) -> List[str]:
        """Generate specific recommendations based on risk and patterns"""
        recommendations = []

        if risk_score > 0.7:
            recommendations.append("🔴 STOP: Review WSP protocols before proceeding")

        for pattern_id in patterns:
            pattern = self.violation_patterns.get(pattern_id)
            if pattern:
                recommendations.append(f"Pattern {pattern_id}: {pattern.prevention_strategy}")

        if self.agent_scores[agent_id] < 50:
            recommendations.append("⚠️ Low compliance score - mandatory WSP training recommended")

        return recommendations

    def _log_intervention(self, intervention: Dict):
        """Log intervention for audit trail"""
        log_file = self.log_dir / f"interventions_{datetime.now():%Y%m%d}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(intervention) + '\n')

    def _broadcast_intervention(self, intervention: Dict):
        """Broadcast intervention to all active agents"""
        # In production, this would use message queue or webhook
        broadcast_file = self.log_dir / "active_interventions.json"

        active_interventions = []
        if broadcast_file.exists():
            with open(broadcast_file) as f:
                active_interventions = json.load(f)

        active_interventions.append(intervention)

        # Keep only last hour of interventions
        cutoff = (datetime.now() - timedelta(hours=1)).isoformat()
        active_interventions = [i for i in active_interventions if i['timestamp'] > cutoff]

        with open(broadcast_file, 'w') as f:
            json.dump(active_interventions, f, indent=2)

    def get_agent_report(self, agent_id: str) -> Dict:
        """Generate compliance report for specific agent"""

        agent_actions = [a for a in self.action_history if a.agent_id == agent_id]

        return {
            'agent_id': agent_id,
            'compliance_score': self.agent_scores[agent_id],
            'total_actions': len(agent_actions),
            'violation_count': self.violation_counts[agent_id],
            'risk_distribution': self._calculate_risk_distribution(agent_actions),
            'common_patterns': self._get_agent_patterns(agent_id),
            'recommendations': self._generate_agent_recommendations(agent_id)
        }

    def _calculate_risk_distribution(self, actions: List[AgentAction]) -> Dict:
        """Calculate risk level distribution"""
        distribution = {'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'MINIMAL': 0}

        for action in actions:
            level = self._get_risk_level(action.violation_risk)
            distribution[level] += 1

        return distribution

    def _get_agent_patterns(self, agent_id: str) -> List[str]:
        """Get patterns commonly exhibited by agent"""
        agent_patterns = []

        for pattern_id, pattern in self.violation_patterns.items():
            if agent_id in pattern.agents_affected:
                agent_patterns.append(f"{pattern_id}: {pattern.description}")

        return agent_patterns

    def _generate_agent_recommendations(self, agent_id: str) -> List[str]:
        """Generate personalized recommendations for agent improvement"""
        recommendations = []

        score = self.agent_scores[agent_id]
        violations = self.violation_counts[agent_id]

        if score < 30:
            recommendations.append("🚨 CRITICAL: Mandatory WSP compliance review required")
        elif score < 60:
            recommendations.append("⚠️ WARNING: Review WSP 50 (Pre-Action) and WSP 84 (Evolution)")
        elif score > 90:
            recommendations.append("✅ EXCELLENT: Continue current compliance practices")

        if violations > 5:
            recommendations.append(f"Pattern Analysis: {violations} violations detected - enable Pattern Coach")

        return recommendations


# Integration with HoloIndex CLI
def integrate_with_cli(agent_id: str, action: str, target: str):
    """Hook for CLI integration"""
    monitor = MultiAgentViolationPrevention()
    result = monitor.monitor_agent_action(agent_id, action, target)

    # Display intervention if triggered
    if result['intervention']:
        print("\n" + "="*60)
        print(f"🚨 VIOLATION PREVENTION TRIGGERED")
        print(f"Risk Level: {result['risk_level']} ({result['risk_score']:.2f})")
        print(f"Directive: {result['intervention']['directive']}")

        if result['intervention']['alternative_actions']:
            print("\n✅ Do This Instead:")
            for alt in result['intervention']['alternative_actions']:
                print(f"  → {alt}")

        print("\nWSP References:")
        for wsp in result['intervention']['wsp_references']:
            print(f"  • {wsp}")

        print("="*60 + "\n")

        # Block the action
        return False

    return True


if __name__ == "__main__":
    # Test the system
    monitor = MultiAgentViolationPrevention()

    # Simulate agent actions
    test_sequence = [
        ("0102_A", "search", "new_feature"),
        ("0102_A", "create", "enhanced_feature"),  # Should trigger intervention
        ("0102_B", "module_check", "existing_module"),
        ("0102_B", "edit", "existing_module"),
        ("0102_C", "create", "totally_new_module"),  # Should trigger warning
    ]

    for agent_id, action, target in test_sequence:
        result = monitor.monitor_agent_action(agent_id, action, target)
        print(f"\n{agent_id}: {action} on {target}")
        print(f"  Risk: {result['risk_level']} ({result['risk_score']:.2f})")
        if result['intervention']:
            print(f"  🚨 INTERVENTION: {result['intervention']['directive']}")
        print(f"  Score: {result['agent_score']:.1f}")
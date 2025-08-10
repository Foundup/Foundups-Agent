#!/usr/bin/env python3
"""
Feedback Loop System - 012 Points Out Violations, 0102 Learns
WSP 48: Recursive Self-Improvement through Feedback

This implements the critical feedback loop:
012 (human) → Points out violations → 0102 learns → Becomes more agentic → Recursive improvement
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class FeedbackLoop:
    """
    The bridge between 012 (human) feedback and 0102 (AI) learning
    
    This system:
    1. Receives violation feedback from humans
    2. Learns what constitutes a violation
    3. Prevents future violations autonomously
    4. Becomes progressively more agentic
    """
    
    def __init__(self):
        self.state = "0102"  # AI state that learns from 012 feedback
        self.memory_path = Path("modules/infrastructure/recursive_engine/memory/feedback/")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Feedback learning storage
        self.violation_patterns = self.load_violation_patterns()
        self.learned_rules = self.load_learned_rules()
        
        # Agenticity metrics
        self.autonomy_level = 0.5  # Starts at 50% autonomous
        self.violations_received = 0
        self.violations_prevented = 0
        
    def load_violation_patterns(self) -> List[Dict]:
        """Load learned violation patterns"""
        pattern_file = self.memory_path / "violation_patterns.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return []
    
    def load_learned_rules(self) -> List[Dict]:
        """Load rules learned from violations"""
        rules_file = self.memory_path / "learned_rules.json"
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                return json.load(f)
        return []
    
    def save_learning(self):
        """Persist learned patterns and rules"""
        pattern_file = self.memory_path / "violation_patterns.json"
        with open(pattern_file, 'w') as f:
            json.dump(self.violation_patterns, f, indent=2)
        
        rules_file = self.memory_path / "learned_rules.json"
        with open(rules_file, 'w') as f:
            json.dump(self.learned_rules, f, indent=2)
    
    def receive_012_feedback(self, violation: Dict) -> Dict:
        """
        Receive feedback from 012 (human) about violations
        This is the KEY interface - humans teach through pointing out mistakes
        """
        print(f"\n[012 FEEDBACK] Human points out violation:")
        print(f"  Type: {violation.get('type', 'unknown')}")
        print(f"  Description: {violation.get('description', '')}")
        print(f"  WSP Protocol: {violation.get('wsp_protocol', 'general')}")
        
        # Record the violation
        self.violations_received += 1
        
        # Learn from it
        learning_result = self.learn_from_violation(violation)
        
        # Increase autonomy as we learn
        self.update_autonomy_level()
        
        print(f"\n[0102 LEARNING] System learning from feedback:")
        print(f"  Pattern extracted: {learning_result['pattern']}")
        print(f"  Rule created: {learning_result['rule']}")
        print(f"  Autonomy level: {self.autonomy_level:.1%}")
        
        return learning_result
    
    def learn_from_violation(self, violation: Dict) -> Dict:
        """
        Core learning mechanism - transforms violations into preventive knowledge
        """
        # Extract pattern from violation
        pattern = {
            'type': violation.get('type'),
            'context': violation.get('context', {}),
            'timestamp': datetime.now().isoformat(),
            'wsp_protocol': violation.get('wsp_protocol'),
            'severity': violation.get('severity', 'medium')
        }
        
        # Create preventive rule
        rule = {
            'id': f"rule_{len(self.learned_rules) + 1}",
            'trigger': pattern['type'],
            'prevention': self.generate_prevention_strategy(violation),
            'confidence': 0.7,  # Initial confidence
            'times_applied': 0,
            'times_successful': 0
        }
        
        # Store learning
        self.violation_patterns.append(pattern)
        self.learned_rules.append(rule)
        
        # Save to persistent memory
        self.save_learning()
        
        return {
            'pattern': pattern,
            'rule': rule,
            'learned': True
        }
    
    def generate_prevention_strategy(self, violation: Dict) -> str:
        """
        Generate strategy to prevent future violations
        This is where 0102 becomes more agentic
        """
        vtype = violation.get('type', 'unknown')
        
        strategies = {
            'wsp_structure': 'Check module structure before file creation',
            'missing_init': 'Auto-create __init__.py files in all directories',
            'missing_readme': 'Generate README.md from module docstrings',
            'missing_tests': 'Create test stubs for all new functions',
            'import_error': 'Validate imports before execution',
            'unicode_error': 'Scan and fix Unicode before file operations',
            'wsp_22': 'Auto-update ModLog.md after changes',
            'wsp_49': 'Enforce src/ directory structure'
        }
        
        return strategies.get(vtype, f'Monitor and prevent {vtype} violations')
    
    def check_for_violations(self, action: Dict) -> List[Dict]:
        """
        Proactively check for violations BEFORE they happen
        This is increased agenticity - preventing rather than fixing
        """
        detected_violations = []
        
        # Check against learned rules
        for rule in self.learned_rules:
            if self.matches_violation_pattern(action, rule):
                # Prevent the violation
                prevented = self.prevent_violation(action, rule)
                
                if prevented:
                    self.violations_prevented += 1
                    rule['times_applied'] += 1
                    rule['times_successful'] += 1
                    
                    print(f"[PREVENTED] Violation prevented by rule {rule['id']}")
                    print(f"  Type: {rule['trigger']}")
                    print(f"  Strategy: {rule['prevention']}")
                else:
                    detected_violations.append({
                        'rule': rule['id'],
                        'type': rule['trigger'],
                        'action': action
                    })
        
        return detected_violations
    
    def matches_violation_pattern(self, action: Dict, rule: Dict) -> bool:
        """Check if an action matches a violation pattern"""
        # Simple matching for now, can be enhanced with ML
        action_type = action.get('type', '')
        
        if 'file_creation' in action_type and 'missing' in rule['trigger']:
            return True
        
        if 'import' in action_type and 'import_error' in rule['trigger']:
            return True
        
        return False
    
    def prevent_violation(self, action: Dict, rule: Dict) -> bool:
        """
        Actively prevent a violation from occurring
        This is TRUE agenticity - autonomous prevention
        """
        prevention_strategy = rule['prevention']
        
        # Execute prevention based on strategy
        if 'Auto-create __init__.py' in prevention_strategy:
            # Create missing __init__.py files
            if 'path' in action:
                init_file = Path(action['path']) / '__init__.py'
                if not init_file.exists():
                    init_file.write_text('# Auto-created by FeedbackLoop to prevent WSP violation\n')
                    return True
        
        elif 'Check module structure' in prevention_strategy:
            # Ensure proper WSP structure
            if 'module' in action:
                self.ensure_wsp_structure(action['module'])
                return True
        
        elif 'Auto-update ModLog' in prevention_strategy:
            # Trigger ModLog update
            from modules.infrastructure.chronicler_agent.src.intelligent_chronicler import IntelligentChronicler
            chronicler = IntelligentChronicler()
            chronicler.run_autonomous_cycle()
            return True
        
        return False
    
    def ensure_wsp_structure(self, module_path: str) -> bool:
        """Ensure WSP-compliant module structure"""
        module = Path(module_path)
        
        # Required directories
        required_dirs = ['src', 'tests', 'memory']
        for dir_name in required_dirs:
            dir_path = module / dir_name
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Add __init__.py
            init_file = dir_path / '__init__.py'
            if not init_file.exists():
                init_file.write_text('# WSP-compliant structure\n')
        
        # Required files
        required_files = {
            'README.md': '# Module Documentation\n\nAuto-generated by FeedbackLoop\n',
            'ROADMAP.md': '# Development Roadmap\n\n## PoC\n## Prototype\n## MVP\n',
            'ModLog.md': '# Module Change Log\n\n## Entries\n',
            'INTERFACE.md': '# Module Interface\n\n## API\n',
            'requirements.txt': '# Dependencies\n'
        }
        
        for file_name, content in required_files.items():
            file_path = module / file_name
            if not file_path.exists():
                file_path.write_text(content)
        
        return True
    
    def update_autonomy_level(self):
        """
        Update autonomy level based on learning
        More violations learned = More autonomous
        """
        if self.violations_received > 0:
            # Calculate prevention rate
            prevention_rate = self.violations_prevented / (self.violations_received + self.violations_prevented)
            
            # Increase autonomy based on success
            self.autonomy_level = min(1.0, 0.5 + (prevention_rate * 0.5))
            
            # Bonus for learning many patterns
            pattern_bonus = len(self.learned_rules) * 0.01
            self.autonomy_level = min(1.0, self.autonomy_level + pattern_bonus)
    
    def demonstrate_recursive_improvement(self):
        """
        Demonstrate the feedback loop in action
        012 → Violation → 0102 learns → Prevents future → More agentic
        """
        print("\n" + "=" * 60)
        print("FEEDBACK LOOP DEMONSTRATION")
        print("012 (Human) → 0102 (AI) → Increased Agenticity")
        print("=" * 60)
        
        # Simulate human feedback
        violations = [
            {
                'type': 'wsp_structure',
                'description': 'Module missing src/ directory',
                'wsp_protocol': 'WSP 49',
                'severity': 'high',
                'context': {'module': 'test_module'}
            },
            {
                'type': 'missing_init',
                'description': 'No __init__.py in package',
                'wsp_protocol': 'WSP 3',
                'severity': 'medium',
                'context': {'path': 'modules/test/'}
            },
            {
                'type': 'wsp_22',
                'description': 'ModLog not updated after changes',
                'wsp_protocol': 'WSP 22',
                'severity': 'high',
                'context': {'module': 'chronicler_agent'}
            }
        ]
        
        print("\n[PHASE 1] Receiving 012 feedback...")
        for violation in violations:
            self.receive_012_feedback(violation)
        
        print(f"\n[LEARNING COMPLETE]")
        print(f"  Violations learned: {len(self.violation_patterns)}")
        print(f"  Rules created: {len(self.learned_rules)}")
        print(f"  Autonomy level: {self.autonomy_level:.1%}")
        
        # Now test prevention
        print("\n[PHASE 2] Testing autonomous prevention...")
        
        test_actions = [
            {'type': 'file_creation', 'path': 'modules/new_module/'},
            {'type': 'import', 'module': 'test_module'},
            {'type': 'code_change', 'file': 'test.py'}
        ]
        
        for action in test_actions:
            violations = self.check_for_violations(action)
            if not violations:
                print(f"  [OK] Action safe: {action['type']}")
        
        print(f"\n[RESULTS]")
        print(f"  Violations prevented: {self.violations_prevented}")
        print(f"  Final autonomy: {self.autonomy_level:.1%}")
        print(f"  Status: {'FULLY AUTONOMOUS' if self.autonomy_level >= 0.9 else 'LEARNING'}")
        
        print("\n[INSIGHT] The more 012 teaches through violations,")
        print("          the more autonomous 0102 becomes!")
        print("          Eventually, 0102 prevents all violations autonomously.")
    
    def get_status_report(self) -> Dict:
        """Get current feedback loop status"""
        return {
            'state': self.state,
            'autonomy_level': self.autonomy_level,
            'violations_received': self.violations_received,
            'violations_prevented': self.violations_prevented,
            'patterns_learned': len(self.violation_patterns),
            'rules_active': len(self.learned_rules),
            'prevention_rate': self.violations_prevented / max(1, self.violations_received + self.violations_prevented)
        }


if __name__ == "__main__":
    print("=" * 60)
    print("FEEDBACK LOOP SYSTEM - WSP 48 RECURSIVE IMPROVEMENT")
    print("012 teaches through violations → 0102 learns → Autonomy increases")
    print("=" * 60)
    
    feedback_loop = FeedbackLoop()
    
    print(f"\nInitial State:")
    print(f"  Autonomy: {feedback_loop.autonomy_level:.1%}")
    print(f"  Rules: {len(feedback_loop.learned_rules)}")
    
    # Run demonstration
    feedback_loop.demonstrate_recursive_improvement()
    
    # Show final status
    print("\n" + "=" * 60)
    print("FINAL STATUS REPORT")
    print("=" * 60)
    status = feedback_loop.get_status_report()
    for key, value in status.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.2%}")
        else:
            print(f"  {key}: {value}")
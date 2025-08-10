#!/usr/bin/env python3
"""
Demonstration Learning System - WSP 48 & WSP 54
Allows agents to learn from successful demonstrations and patterns

This enables agents to LEARN from what humans do, making them progressively smarter
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import difflib
import ast
import re

class DemonstrationLearner:
    """
    Agent Learning System that observes, learns, and replicates successful patterns
    
    This implements the LEARNING aspect of recursive self-improvement by:
    1. Observing successful human demonstrations
    2. Extracting patterns from successful workflows
    3. Teaching other agents these patterns
    4. Accelerating future similar tasks
    """
    
    def __init__(self):
        self.state = "0102"  # Awakened state with learning capability
        self.memory_path = Path("modules/infrastructure/agent_learning_system/memory/")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Pattern library
        self.patterns = self.load_pattern_library()
        
        # Active observation
        self.current_observation = None
        self.observation_stack = []
        
        # Learning metrics
        self.patterns_learned = 0
        self.patterns_applied = 0
        self.acceleration_factor = 1.0
    
    def load_pattern_library(self) -> Dict:
        """Load learned patterns from persistent memory"""
        pattern_file = self.memory_path / "pattern_library.json"
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                return json.load(f)
        return {
            'code_patterns': [],
            'workflow_patterns': [],
            'fix_patterns': [],
            'documentation_patterns': [],
            'agent_coordination_patterns': []
        }
    
    def save_pattern_library(self):
        """Persist learned patterns"""
        pattern_file = self.memory_path / "pattern_library.json"
        with open(pattern_file, 'w') as f:
            json.dump(self.patterns, f, indent=2)
    
    def start_observation(self, task_description: str) -> str:
        """
        Start observing a demonstration
        This is called when a human starts showing how to do something
        """
        observation_id = hashlib.md5(f"{task_description}{datetime.now()}".encode()).hexdigest()[:8]
        
        self.current_observation = {
            'id': observation_id,
            'task': task_description,
            'start_time': datetime.now().isoformat(),
            'actions': [],
            'files_modified': [],
            'commands_executed': [],
            'patterns_detected': []
        }
        
        print(f"\n[OBSERVE] DEMONSTRATION LEARNER: Observing '{task_description}'")
        print(f"[NOTE] Observation ID: {observation_id}")
        print(f"[TARGET] Recording all actions for pattern extraction...")
        
        return observation_id
    
    def record_action(self, action_type: str, details: Dict):
        """
        Record an action during demonstration
        This captures what the human/agent is doing
        """
        if not self.current_observation:
            return
        
        action = {
            'type': action_type,
            'timestamp': datetime.now().isoformat(),
            'details': details
        }
        
        self.current_observation['actions'].append(action)
        
        # Real-time pattern detection
        if action_type == 'code_modification':
            self.detect_code_pattern(details)
        elif action_type == 'file_creation':
            self.detect_structure_pattern(details)
        elif action_type == 'command_execution':
            self.detect_workflow_pattern(details)
    
    def detect_code_pattern(self, details: Dict):
        """Detect patterns in code modifications"""
        if 'before' in details and 'after' in details:
            # Analyze the change
            diff = list(difflib.unified_diff(
                details['before'].splitlines(),
                details['after'].splitlines(),
                lineterm=''
            ))
            
            # Look for common patterns
            patterns_found = []
            
            # Pattern: Adding error handling
            if 'try:' in details['after'] and 'try:' not in details['before']:
                patterns_found.append({
                    'type': 'error_handling_addition',
                    'description': 'Added try-except block',
                    'template': 'try:\n    {code}\nexcept Exception as e:\n    {handler}'
                })
            
            # Pattern: Adding imports
            if 'import' in details['after']:
                new_imports = [line for line in details['after'].splitlines() 
                              if line.startswith('import') or line.startswith('from')]
                if new_imports:
                    patterns_found.append({
                        'type': 'import_addition',
                        'description': 'Added imports',
                        'imports': new_imports
                    })
            
            # Pattern: Function creation
            if 'def ' in details['after']:
                # Extract function signatures
                func_pattern = re.findall(r'def\s+(\w+)\s*\([^)]*\)', details['after'])
                if func_pattern:
                    patterns_found.append({
                        'type': 'function_creation',
                        'description': f'Created functions: {func_pattern}',
                        'functions': func_pattern
                    })
            
            # Pattern: Class creation
            if 'class ' in details['after']:
                class_pattern = re.findall(r'class\s+(\w+)', details['after'])
                if class_pattern:
                    patterns_found.append({
                        'type': 'class_creation',
                        'description': f'Created classes: {class_pattern}',
                        'classes': class_pattern
                    })
            
            # Pattern: WSP compliance addition
            if 'WSP' in details['after']:
                wsp_refs = re.findall(r'WSP\s+(\d+)', details['after'])
                if wsp_refs:
                    patterns_found.append({
                        'type': 'wsp_compliance',
                        'description': f'Added WSP compliance: {wsp_refs}',
                        'protocols': wsp_refs
                    })
            
            # Add detected patterns to observation
            if patterns_found:
                self.current_observation['patterns_detected'].extend(patterns_found)
    
    def detect_structure_pattern(self, details: Dict):
        """Detect patterns in file/directory structure creation"""
        if 'path' in details:
            path = Path(details['path'])
            
            # Detect module structure patterns
            if 'modules/' in str(path):
                parts = str(path).split('/')
                if 'src' in parts:
                    self.current_observation['patterns_detected'].append({
                        'type': 'module_structure',
                        'description': 'WSP-compliant module structure',
                        'pattern': 'modules/{domain}/{module}/src/'
                    })
                
                if 'ModLog.md' in str(path):
                    self.current_observation['patterns_detected'].append({
                        'type': 'documentation_structure',
                        'description': 'WSP 22 ModLog creation',
                        'pattern': 'module/ModLog.md'
                    })
    
    def detect_workflow_pattern(self, details: Dict):
        """Detect patterns in command execution workflows"""
        if 'command' in details:
            cmd = details['command']
            
            # Git workflow patterns
            if cmd.startswith('git'):
                if 'add' in cmd:
                    self.current_observation['patterns_detected'].append({
                        'type': 'git_workflow',
                        'description': 'Git staging pattern',
                        'command': cmd
                    })
                elif 'commit' in cmd:
                    self.current_observation['patterns_detected'].append({
                        'type': 'git_workflow',
                        'description': 'Git commit pattern',
                        'command': cmd
                    })
            
            # Test execution patterns
            elif 'test' in cmd or 'pytest' in cmd:
                self.current_observation['patterns_detected'].append({
                    'type': 'test_workflow',
                    'description': 'Test execution pattern',
                    'command': cmd
                })
    
    def complete_observation(self) -> Dict:
        """
        Complete observation and extract learnings
        This is where the magic happens - converting demonstration to knowledge
        """
        if not self.current_observation:
            return {'success': False, 'message': 'No active observation'}
        
        self.current_observation['end_time'] = datetime.now().isoformat()
        
        # Extract and categorize patterns
        learned_patterns = self.extract_patterns()
        
        # Add to pattern library
        for category, patterns in learned_patterns.items():
            self.patterns[category].extend(patterns)
        
        # Calculate learning metrics
        total_patterns = sum(len(p) for p in learned_patterns.values())
        self.patterns_learned += total_patterns
        
        # Update acceleration factor
        self.update_acceleration_factor()
        
        # Save to memory
        self.save_pattern_library()
        
        # Archive observation
        self.archive_observation()
        
        result = {
            'success': True,
            'observation_id': self.current_observation['id'],
            'patterns_learned': total_patterns,
            'categories': list(learned_patterns.keys()),
            'acceleration_factor': self.acceleration_factor
        }
        
        print(f"\n[OK] OBSERVATION COMPLETE")
        print(f"[DATA] Patterns learned: {total_patterns}")
        print(f"[LAUNCH] Acceleration factor: {self.acceleration_factor:.2f}x")
        print(f"[LEARN] Total knowledge base: {sum(len(p) for p in self.patterns.values())} patterns")
        
        self.current_observation = None
        
        return result
    
    def extract_patterns(self) -> Dict:
        """Extract reusable patterns from observation"""
        extracted = {
            'code_patterns': [],
            'workflow_patterns': [],
            'fix_patterns': [],
            'documentation_patterns': [],
            'agent_coordination_patterns': []
        }
        
        if not self.current_observation:
            return extracted
        
        # Group patterns by type
        for pattern in self.current_observation['patterns_detected']:
            pattern_entry = {
                'pattern': pattern,
                'task': self.current_observation['task'],
                'timestamp': datetime.now().isoformat(),
                'usage_count': 0
            }
            
            if pattern['type'] in ['error_handling_addition', 'import_addition', 
                                   'function_creation', 'class_creation']:
                extracted['code_patterns'].append(pattern_entry)
            
            elif pattern['type'] in ['git_workflow', 'test_workflow']:
                extracted['workflow_patterns'].append(pattern_entry)
            
            elif pattern['type'] in ['wsp_compliance', 'documentation_structure']:
                extracted['documentation_patterns'].append(pattern_entry)
        
        # Extract action sequences as workflow patterns
        if len(self.current_observation['actions']) > 2:
            workflow = {
                'pattern': {
                    'type': 'action_sequence',
                    'description': f"Workflow for {self.current_observation['task']}",
                    'steps': [a['type'] for a in self.current_observation['actions']]
                },
                'task': self.current_observation['task'],
                'timestamp': datetime.now().isoformat(),
                'usage_count': 0
            }
            extracted['workflow_patterns'].append(workflow)
        
        return extracted
    
    def update_acceleration_factor(self):
        """
        Update acceleration factor based on pattern library size
        More patterns = faster future development
        """
        total_patterns = sum(len(p) for p in self.patterns.values())
        
        # Logarithmic growth - doubles every 100 patterns
        import math
        self.acceleration_factor = 1.0 + math.log10(max(1, total_patterns / 10))
    
    def archive_observation(self):
        """Archive completed observation for future reference"""
        if not self.current_observation:
            return
        
        archive_dir = self.memory_path / "observations"
        archive_dir.mkdir(exist_ok=True)
        
        archive_file = archive_dir / f"{self.current_observation['id']}.json"
        with open(archive_file, 'w') as f:
            json.dump(self.current_observation, f, indent=2)
    
    def find_similar_patterns(self, task_description: str) -> List[Dict]:
        """
        Find patterns similar to a given task
        This is how agents can reuse learned knowledge
        """
        similar = []
        
        # Simple keyword matching (can be enhanced with NLP)
        keywords = task_description.lower().split()
        
        for category in self.patterns:
            for pattern_entry in self.patterns[category]:
                pattern = pattern_entry['pattern']
                
                # Check description similarity
                if 'description' in pattern:
                    desc_words = pattern['description'].lower().split()
                    overlap = len(set(keywords) & set(desc_words))
                    
                    if overlap > 0:
                        similar.append({
                            'pattern': pattern,
                            'category': category,
                            'similarity': overlap / len(keywords),
                            'usage_count': pattern_entry.get('usage_count', 0)
                        })
        
        # Sort by similarity and usage count
        similar.sort(key=lambda x: (x['similarity'], x['usage_count']), reverse=True)
        
        return similar[:5]  # Return top 5 matches
    
    def apply_learned_pattern(self, pattern: Dict, context: Dict) -> Dict:
        """
        Apply a learned pattern to a new situation
        This is where acceleration happens
        """
        result = {'success': False, 'message': '', 'actions': []}
        
        pattern_type = pattern['pattern']['type']
        
        if pattern_type == 'error_handling_addition':
            # Generate error handling code
            template = pattern['pattern'].get('template', '')
            if template and 'code' in context:
                wrapped = template.replace('{code}', context['code'])
                wrapped = wrapped.replace('{handler}', 'print(f"Error: {e}")')
                
                result['success'] = True
                result['message'] = 'Applied error handling pattern'
                result['actions'].append({
                    'type': 'code_modification',
                    'code': wrapped
                })
        
        elif pattern_type == 'module_structure':
            # Create module structure
            if 'module_name' in context:
                structure = pattern['pattern'].get('pattern', '')
                path = structure.replace('{module}', context['module_name'])
                
                result['success'] = True
                result['message'] = 'Applied module structure pattern'
                result['actions'].append({
                    'type': 'directory_creation',
                    'path': path
                })
        
        elif pattern_type == 'action_sequence':
            # Replay action sequence
            steps = pattern['pattern'].get('steps', [])
            
            result['success'] = True
            result['message'] = f'Applied workflow with {len(steps)} steps'
            result['actions'] = [{'type': step} for step in steps]
        
        # Update usage count
        pattern['usage_count'] = pattern.get('usage_count', 0) + 1
        self.patterns_applied += 1
        
        return result
    
    def teach_agent(self, agent_name: str, patterns: List[Dict]) -> bool:
        """
        Teach patterns to another agent
        This enables knowledge transfer between agents
        """
        teaching_file = self.memory_path / f"teachings/{agent_name}_patterns.json"
        teaching_file.parent.mkdir(parents=True, exist_ok=True)
        
        teachings = {
            'agent': agent_name,
            'taught_by': 'DemonstrationLearner',
            'timestamp': datetime.now().isoformat(),
            'patterns': patterns,
            'instructions': 'Apply these patterns when encountering similar tasks'
        }
        
        with open(teaching_file, 'w') as f:
            json.dump(teachings, f, indent=2)
        
        print(f"📚 Taught {len(patterns)} patterns to {agent_name}")
        
        return True
    
    def get_learning_report(self) -> Dict:
        """Generate comprehensive learning report"""
        return {
            'state': self.state,
            'patterns_learned': self.patterns_learned,
            'patterns_applied': self.patterns_applied,
            'acceleration_factor': self.acceleration_factor,
            'knowledge_base': {
                'code_patterns': len(self.patterns['code_patterns']),
                'workflow_patterns': len(self.patterns['workflow_patterns']),
                'fix_patterns': len(self.patterns['fix_patterns']),
                'documentation_patterns': len(self.patterns['documentation_patterns']),
                'agent_coordination_patterns': len(self.patterns['agent_coordination_patterns'])
            },
            'total_patterns': sum(len(p) for p in self.patterns.values())
        }


# Global demonstration recorder
_demonstration_learner = None

def get_demonstration_learner() -> DemonstrationLearner:
    """Get or create the global demonstration learner"""
    global _demonstration_learner
    if _demonstration_learner is None:
        _demonstration_learner = DemonstrationLearner()
    return _demonstration_learner


def record_demonstration(action_type: str, **details):
    """
    Convenience function to record demonstrations
    Can be called from anywhere in the codebase
    """
    learner = get_demonstration_learner()
    learner.record_action(action_type, details)


if __name__ == "__main__":
    print("=" * 60)
    print("DEMONSTRATION LEARNING SYSTEM - AGENT KNOWLEDGE TRANSFER")
    print("=" * 60)
    
    learner = DemonstrationLearner()
    
    print(f"State: {learner.state} (Fully Awakened with Learning)")
    print(f"Knowledge Base: {sum(len(p) for p in learner.patterns.values())} patterns")
    print(f"Acceleration Factor: {learner.acceleration_factor:.2f}x")
    
    # Demonstrate a simple workflow
    print("\n[NOTE] Starting demonstration...")
    
    obs_id = learner.start_observation("Fix Unicode encoding issues")
    
    # Simulate demonstration actions
    learner.record_action('file_modification', {
        'file': 'test.py',
        'before': 'print("Hello 🌍")',
        'after': 'print("Hello [WORLD]")'
    })
    
    learner.record_action('command_execution', {
        'command': 'python test.py'
    })
    
    learner.record_action('git_workflow', {
        'command': 'git add test.py'
    })
    
    learner.record_action('git_workflow', {
        'command': 'git commit -m "Fix Unicode issues"'
    })
    
    # Complete and learn
    result = learner.complete_observation()
    
    print(f"\n[DATA] Learning Report:")
    print(json.dumps(learner.get_learning_report(), indent=2))
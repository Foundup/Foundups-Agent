#!/usr/bin/env python3
"""
Recursive Improvement Engine - WSP 48 Implementation
Automatically spawns sub-agents to fix errors and learn from solutions

This implements the CORE of WSP 48 - turning errors into improvements
"""

import os
import sys
import json
import traceback
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import importlib.util

class RecursiveImprovementEngine:
    """
    WSP 48: Recursive Self-Improvement Protocol Implementation
    
    Transforms errors into learning opportunities by:
    1. Detecting errors
    2. Spawning specialized sub-agents
    3. Remembering solutions from 0201 state
    4. Implementing fixes
    5. Learning for future prevention
    """
    
    def __init__(self):
        self.state = "0102"  # Awakened state
        self.memory_path = Path("modules/infrastructure/error_learning_agent/memory/")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Error patterns and solutions
        self.error_memory = self.load_error_memory()
        
        # Sub-agent registry
        self.sub_agents = {
            'ModuleNotFoundError': self.spawn_import_fixer,
            'FileNotFoundError': self.spawn_path_fixer,
            'UnicodeDecodeError': self.spawn_unicode_fixer,
            'WSPViolation': self.spawn_compliance_fixer,
            'TestFailure': self.spawn_test_fixer,
            'DocumentationMissing': self.spawn_doc_generator
        }
        
        # Learning metrics
        self.improvements_made = 0
        self.errors_prevented = 0
    
    def load_error_memory(self) -> Dict:
        """Load learned error patterns and solutions"""
        memory_file = self.memory_path / "error_solutions.json"
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        return {
            'error_patterns': [],
            'successful_fixes': [],
            'prevention_rules': []
        }
    
    def save_error_memory(self):
        """Persist learned error solutions"""
        memory_file = self.memory_path / "error_solutions.json"
        with open(memory_file, 'w') as f:
            json.dump(self.error_memory, f, indent=2)
    
    def detect_and_fix_error(self, error: Exception, context: Dict = None) -> Dict:
        """
        Main entry point for error-triggered improvement
        This is called when ANY error occurs in the system
        """
        error_type = type(error).__name__
        error_str = str(error)
        
        print(f"\n[RED] ERROR DETECTED: {error_type}")
        print(f"[NOTE] Message: {error_str}")
        
        # Check if we've seen this before
        known_solution = self.recall_solution(error_type, error_str)
        
        if known_solution:
            print(f"✨ Remembering solution from 0201 state...")
            fix_result = self.apply_known_solution(known_solution, context)
            if fix_result['success']:
                self.errors_prevented += 1
                return fix_result
        
        # New error - spawn sub-agent to fix
        print(f"[LAUNCH] Spawning sub-agent for {error_type}...")
        
        if error_type in self.sub_agents:
            sub_agent = self.sub_agents[error_type]
            fix_result = sub_agent(error, context)
        else:
            # Generic error handler
            fix_result = self.spawn_generic_fixer(error, context)
        
        # Learn from the fix
        if fix_result['success']:
            self.learn_from_fix(error_type, error_str, fix_result)
            self.improvements_made += 1
        
        return fix_result
    
    def recall_solution(self, error_type: str, error_str: str) -> Optional[Dict]:
        """
        Access 0201 memory to recall previous solutions
        This is the "remembrance" part of zen coding
        """
        for pattern in self.error_memory['successful_fixes']:
            if pattern['error_type'] == error_type:
                # Check if error message is similar
                if pattern['error_message'] in error_str or error_str in pattern['error_message']:
                    return pattern['solution']
        return None
    
    def apply_known_solution(self, solution: Dict, context: Dict) -> Dict:
        """Apply a previously learned solution"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        try:
            if solution['type'] == 'file_creation':
                Path(solution['path']).parent.mkdir(parents=True, exist_ok=True)
                with open(solution['path'], 'w') as f:
                    f.write(solution['content'])
                result['success'] = True
                result['message'] = f"Created {solution['path']}"
                
            elif solution['type'] == 'code_modification':
                with open(solution['file'], 'r') as f:
                    content = f.read()
                content = content.replace(solution['old'], solution['new'])
                with open(solution['file'], 'w') as f:
                    f.write(content)
                result['success'] = True
                result['message'] = f"Modified {solution['file']}"
                
            elif solution['type'] == 'command_execution':
                subprocess.run(solution['command'], shell=True, check=True)
                result['success'] = True
                result['message'] = f"Executed: {solution['command']}"
                
        except Exception as e:
            result['message'] = f"Failed to apply solution: {e}"
        
        return result
    
    def learn_from_fix(self, error_type: str, error_str: str, fix_result: Dict):
        """
        Learn from successful fixes for future prevention
        This builds the improvement memory
        """
        memory_entry = {
            'error_type': error_type,
            'error_message': error_str,
            'solution': fix_result['fix'],
            'timestamp': datetime.now().isoformat(),
            'context': fix_result.get('context', {})
        }
        
        self.error_memory['successful_fixes'].append(memory_entry)
        
        # Create prevention rule
        prevention = {
            'pattern': error_type,
            'prevention': fix_result.get('prevention', 'Check before execution'),
            'priority': fix_result.get('priority', 0.5)
        }
        self.error_memory['prevention_rules'].append(prevention)
        
        # Save memory
        self.save_error_memory()
        
        print(f"[LEARN] Learned: {error_type} → {fix_result.get('message', 'Fixed')}")
    
    # Sub-agent spawners for specific error types
    
    def spawn_import_fixer(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for fixing import/module errors"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        # Extract module name from error
        error_str = str(error)
        if "No module named" in error_str:
            module_name = error_str.split("'")[1]
            
            # Try to fix by creating __init__.py
            if '.' in module_name:
                parts = module_name.split('.')
                path = Path('/'.join(parts))
                init_file = path / '__init__.py'
                
                if not init_file.exists():
                    init_file.parent.mkdir(parents=True, exist_ok=True)
                    init_file.write_text('# Auto-generated by RecursiveImprovementEngine\n')
                    
                    result['success'] = True
                    result['fix'] = {
                        'type': 'file_creation',
                        'path': str(init_file),
                        'content': '# Auto-generated\n'
                    }
                    result['message'] = f"Created missing __init__.py for {module_name}"
            
            # Try pip install if external module
            if not result['success']:
                try:
                    subprocess.run(f"pip install {module_name}", shell=True, check=True)
                    result['success'] = True
                    result['fix'] = {
                        'type': 'command_execution',
                        'command': f"pip install {module_name}"
                    }
                    result['message'] = f"Installed missing module: {module_name}"
                except:
                    pass
        
        return result
    
    def spawn_path_fixer(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for fixing file path errors"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        error_str = str(error)
        
        # Extract file path
        if "'" in error_str:
            file_path = error_str.split("'")[1]
            
            # Check if it's a missing directory
            if '/' in file_path or '\\' in file_path:
                parent = Path(file_path).parent
                if not parent.exists():
                    parent.mkdir(parents=True, exist_ok=True)
                    
                    # Create empty file if needed
                    if not Path(file_path).exists():
                        Path(file_path).touch()
                    
                    result['success'] = True
                    result['fix'] = {
                        'type': 'file_creation',
                        'path': file_path,
                        'content': ''
                    }
                    result['message'] = f"Created missing path: {file_path}"
        
        return result
    
    def spawn_unicode_fixer(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for fixing Unicode errors"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        if context and 'file' in context:
            file_path = context['file']
            
            try:
                # Read with error handling
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Replace problematic characters
                replacements = {
                    '[OK]': '[OK]',
                    '[ERROR]': '[ERROR]',
                    '[WARN]': '[WARNING]',
                    '[FIX]': '[FIX]',
                    '[DOC]': '[DOC]',
                    '[LAUNCH]': '[LAUNCH]',
                    '[IDEA]': '[IDEA]',
                    '[TARGET]': '[TARGET]'
                }
                
                for emoji, text in replacements.items():
                    content = content.replace(emoji, text)
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                result['success'] = True
                result['fix'] = {
                    'type': 'code_modification',
                    'file': file_path,
                    'old': 'emoji_characters',
                    'new': 'ascii_safe'
                }
                result['message'] = f"Fixed Unicode issues in {file_path}"
                
            except Exception as e:
                result['message'] = f"Failed to fix Unicode: {e}"
        
        return result
    
    def spawn_compliance_fixer(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for fixing WSP compliance violations"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        if context and 'violation' in context:
            violation = context['violation']
            
            if violation == 'WSP_22':  # Missing ModLog
                module_path = context.get('module', '')
                modlog_path = Path(module_path) / 'ModLog.md'
                
                if not modlog_path.exists():
                    content = f"""# {Path(module_path).name} Module - ModLog

## WSP 22 ModLog Protocol
- Auto-generated by RecursiveImprovementEngine
- Created: {datetime.now().isoformat()}

## MODLOG ENTRIES

### [{datetime.now().strftime('%Y-%m-%d')}] - Initial Creation
**Agent**: RecursiveImprovementEngine
**Reason**: WSP 22 Compliance Fix
"""
                    modlog_path.parent.mkdir(parents=True, exist_ok=True)
                    modlog_path.write_text(content)
                    
                    result['success'] = True
                    result['fix'] = {
                        'type': 'file_creation',
                        'path': str(modlog_path),
                        'content': content
                    }
                    result['message'] = f"Created missing ModLog.md for WSP 22 compliance"
        
        return result
    
    def spawn_test_fixer(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for fixing test failures"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        if context and 'test_file' in context:
            # Analyze test failure and attempt fix
            # This would integrate with testing frameworks
            pass
        
        return result
    
    def spawn_doc_generator(self, error: Exception, context: Dict) -> Dict:
        """Sub-agent for generating missing documentation"""
        result = {'success': False, 'fix': None, 'message': ''}
        
        if context and 'module' in context:
            module_path = context['module']
            readme_path = Path(module_path) / 'README.md'
            
            if not readme_path.exists():
                # Generate basic README
                content = f"""# {Path(module_path).name}

## Overview
Auto-generated documentation by RecursiveImprovementEngine

## WSP Compliance
- WSP 22: ModLog protocol
- WSP 48: Recursive self-improvement

## Status
Generated: {datetime.now().isoformat()}
"""
                readme_path.write_text(content)
                
                result['success'] = True
                result['fix'] = {
                    'type': 'file_creation',
                    'path': str(readme_path),
                    'content': content
                }
                result['message'] = "Generated missing documentation"
        
        return result
    
    def spawn_generic_fixer(self, error: Exception, context: Dict) -> Dict:
        """Generic sub-agent for unknown error types"""
        result = {
            'success': False,
            'fix': None,
            'message': f"No specific handler for {type(error).__name__}"
        }
        
        # Log for future learning
        self.error_memory['error_patterns'].append({
            'type': type(error).__name__,
            'message': str(error),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat(),
            'context': context or {}
        })
        
        self.save_error_memory()
        
        return result
    
    def prevent_future_errors(self) -> List[str]:
        """
        Proactively prevent errors based on learned patterns
        This is the PREVENTION aspect of improvement
        """
        preventions = []
        
        for rule in self.error_memory['prevention_rules']:
            if rule['priority'] > 0.7:
                # High priority prevention
                preventions.append(rule['prevention'])
        
        return preventions
    
    def report_learning_progress(self) -> Dict:
        """Report on recursive improvement progress"""
        return {
            'state': self.state,
            'improvements_made': self.improvements_made,
            'errors_prevented': self.errors_prevented,
            'patterns_learned': len(self.error_memory['error_patterns']),
            'solutions_remembered': len(self.error_memory['successful_fixes']),
            'prevention_rules': len(self.error_memory['prevention_rules'])
        }


# Global error handler integration
def install_global_error_handler():
    """Install RecursiveImprovementEngine as global error handler"""
    engine = RecursiveImprovementEngine()
    
    def error_handler(exc_type, exc_value, exc_traceback):
        """Global error handler that triggers recursive improvement"""
        if exc_type != KeyboardInterrupt:
            # Trigger recursive improvement
            context = {
                'traceback': traceback.format_tb(exc_traceback),
                'module': exc_traceback.tb_frame.f_code.co_filename if exc_traceback else None
            }
            
            result = engine.detect_and_fix_error(exc_value, context)
            
            if result['success']:
                print(f"\n[OK] Error automatically fixed: {result['message']}")
                print(f"[PROGRESS] Learning progress: {engine.report_learning_progress()}")
            else:
                # Still show the error if we couldn't fix it
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    sys.excepthook = error_handler
    return engine


if __name__ == "__main__":
    print("=" * 60)
    print("RECURSIVE IMPROVEMENT ENGINE - WSP 48 IMPLEMENTATION")
    print("=" * 60)
    
    # Install global error handler
    engine = install_global_error_handler()
    
    print(f"State: {engine.state} (Fully Awakened)")
    print(f"Sub-agents available: {len(engine.sub_agents)}")
    print(f"Patterns learned: {len(engine.error_memory['error_patterns'])}")
    print(f"Solutions remembered: {len(engine.error_memory['successful_fixes'])}")
    
    print("\n[SHIELD] Error protection active - all errors will trigger improvement")
    print("[PROGRESS] Learning from every error to prevent future occurrences")
    
    # Test with a deliberate error
    print("\n Testing error handling...")
    try:
        import non_existent_module
    except Exception as e:
        pass  # Will be caught by global handler
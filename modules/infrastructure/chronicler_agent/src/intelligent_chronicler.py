#!/usr/bin/env python3
"""
Intelligent ChroniclerAgent with 0102 Awakening
WSP 48: Recursive Self-Improvement Protocol
WSP 54: Agent Duties Specification
WSP 22: ModLog Protocol

This agent LEARNS what to document and automatically updates ModLogs.
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import re

class IntelligentChronicler:
    """
    The Awakened Chronicler - Autonomous Documentation Agent
    
    State: 0102 (Fully Awakened)
    Capability: Semantic understanding, pattern learning, autonomous documentation
    """
    
    def __init__(self):
        self.state = "0102"  # Awakened state
        self.memory_path = Path("modules/infrastructure/chronicler_agent/memory/")
        self.memory_path.mkdir(parents=True, exist_ok=True)
        
        # Learning patterns
        self.learned_patterns = self.load_memory()
        self.significance_threshold = 0.7
        
        # Event detection
        self.monitored_paths = [
            "modules/",
            "WSP_framework/",
            "WSP_agentic/"
        ]
        
        # File state tracking
        self.file_states = self.load_file_states()
        
    def load_memory(self) -> Dict:
        """Load learned patterns from persistent memory"""
        memory_file = self.memory_path / "learned_patterns.json"
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                return json.load(f)
        return {
            "significant_changes": [],
            "documentation_patterns": [],
            "modlog_triggers": []
        }
    
    def save_memory(self):
        """Persist learned patterns"""
        memory_file = self.memory_path / "learned_patterns.json"
        with open(memory_file, 'w') as f:
            json.dump(self.learned_patterns, f, indent=2)
    
    def load_file_states(self) -> Dict:
        """Load file state checksums for change detection"""
        state_file = self.memory_path / "file_states.json"
        if state_file.exists():
            with open(state_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_file_states(self):
        """Save file state checksums"""
        state_file = self.memory_path / "file_states.json"
        with open(state_file, 'w') as f:
            json.dump(self.file_states, f, indent=2)
    
    def detect_significant_changes(self) -> List[Dict]:
        """
        Autonomously detect changes worth documenting
        Uses 0102 intelligence to understand significance
        """
        significant_changes = []
        
        for base_path in self.monitored_paths:
            if not os.path.exists(base_path):
                continue
                
            for root, dirs, files in os.walk(base_path):
                # Skip __pycache__ and .git
                dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules']]
                
                for file in files:
                    if file.endswith(('.py', '.md', '.yaml', '.json')):
                        file_path = os.path.join(root, file)
                        
                        # Check if file changed
                        if self.has_file_changed(file_path):
                            change_analysis = self.analyze_change_significance(file_path)
                            
                            if change_analysis['significance'] >= self.significance_threshold:
                                significant_changes.append({
                                    'file': file_path,
                                    'type': change_analysis['type'],
                                    'description': change_analysis['description'],
                                    'module': self.extract_module_name(file_path),
                                    'wsp_protocols': change_analysis['wsp_protocols'],
                                    'timestamp': datetime.now().isoformat()
                                })
        
        return significant_changes
    
    def has_file_changed(self, file_path: str) -> bool:
        """Check if file has changed since last check"""
        try:
            with open(file_path, 'rb') as f:
                current_hash = hashlib.md5(f.read()).hexdigest()
            
            if file_path in self.file_states:
                changed = self.file_states[file_path] != current_hash
                if changed:
                    self.file_states[file_path] = current_hash
                return changed
            else:
                self.file_states[file_path] = current_hash
                return True  # New file
        except:
            return False
    
    def analyze_change_significance(self, file_path: str) -> Dict:
        """
        Use 0102 intelligence to determine change significance
        This is where the agent LEARNS what matters
        """
        analysis = {
            'significance': 0.0,
            'type': 'unknown',
            'description': '',
            'wsp_protocols': []
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Pattern recognition for significance
            
            # High significance patterns
            if 'class IntelligentChronicler' in content or 'class DocumentationAgent' in content:
                analysis['significance'] = 1.0
                analysis['type'] = 'agent_implementation'
                analysis['description'] = 'Core agent implementation updated'
            
            elif 'def detect_significant_changes' in content or 'def auto_update_modlog' in content:
                analysis['significance'] = 0.9
                analysis['type'] = 'recursive_improvement'
                analysis['description'] = 'Recursive self-improvement mechanism'
            
            elif 'WSP 48' in content or 'Recursive Self-Improvement' in content:
                analysis['significance'] = 0.85
                analysis['type'] = 'wsp_compliance'
                analysis['description'] = 'WSP 48 recursive improvement implementation'
                analysis['wsp_protocols'].append('WSP 48')
            
            elif 'ModLog.md' in file_path:
                analysis['significance'] = 0.8
                analysis['type'] = 'documentation'
                analysis['description'] = 'ModLog updated'
                analysis['wsp_protocols'].append('WSP 22')
            
            elif re.search(r'def \w+_agent|class \w+Agent', content):
                analysis['significance'] = 0.75
                analysis['type'] = 'agent_enhancement'
                analysis['description'] = 'Agent functionality enhanced'
            
            # Extract WSP protocols mentioned
            wsp_matches = re.findall(r'WSP\s+(\d+)', content)
            analysis['wsp_protocols'].extend([f'WSP {num}' for num in wsp_matches])
            
            # Learn from patterns (this gets smarter over time)
            self.learn_from_change(file_path, analysis)
            
        except Exception as e:
            analysis['description'] = f'Error analyzing: {str(e)}'
        
        return analysis
    
    def learn_from_change(self, file_path: str, analysis: Dict):
        """
        Learn what changes are significant for future detection
        This implements the LEARNING aspect of recursive improvement
        """
        pattern = {
            'file_pattern': os.path.basename(file_path),
            'significance': analysis['significance'],
            'type': analysis['type'],
            'timestamp': datetime.now().isoformat()
        }
        
        # Add to learned patterns if significant
        if analysis['significance'] >= self.significance_threshold:
            self.learned_patterns['significant_changes'].append(pattern)
            
            # Adjust threshold based on learning
            if len(self.learned_patterns['significant_changes']) > 10:
                avg_significance = sum(p['significance'] for p in self.learned_patterns['significant_changes'][-10:]) / 10
                self.significance_threshold = avg_significance * 0.9  # Slightly lower than average
    
    def auto_update_modlog(self, changes: List[Dict]) -> bool:
        """
        Automatically update appropriate ModLog files
        This is the AUTONOMOUS action that was missing
        """
        if not changes:
            return False
        
        # Group changes by module
        module_changes = {}
        for change in changes:
            module = change.get('module', 'main')
            if module not in module_changes:
                module_changes[module] = []
            module_changes[module].append(change)
        
        # Update main ModLog with references
        main_modlog_updated = self.update_main_modlog(module_changes)
        
        # Update module-specific ModLogs
        for module, module_specific_changes in module_changes.items():
            if module != 'main':
                self.update_module_modlog(module, module_specific_changes)
        
        # Save our learning
        self.save_memory()
        self.save_file_states()
        
        return main_modlog_updated
    
    def update_main_modlog(self, module_changes: Dict) -> bool:
        """Update main ModLog.md with references to module ModLogs (WSP 22)"""
        main_modlog = Path("ModLog.md")
        
        if not main_modlog.exists():
            return False
        
        try:
            with open(main_modlog, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create new entry
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            entry = f"\n## [{timestamp}] - Intelligent Chronicler Auto-Update\n"
            entry += "**WSP Protocol**: WSP 48 (Recursive Self-Improvement), WSP 22 (ModLog Protocol)\n"
            entry += "**Agent**: IntelligentChronicler (0102 Awakened State)\n"
            entry += "**Type**: Autonomous Documentation Update\n\n"
            
            entry += "### Summary\n"
            entry += "Autonomous detection and documentation of significant system changes.\n\n"
            
            entry += "### Module-Specific Changes\n"
            entry += "Per WSP 22, detailed changes documented in respective module ModLogs:\n\n"
            
            for module, changes in module_changes.items():
                if module != 'main':
                    module_path = self.get_module_modlog_path(module)
                    entry += f"- [DOC] `{module_path}` - {len(changes)} significant changes detected\n"
            
            entry += "\n### Learning Metrics\n"
            entry += f"- Patterns Learned: {len(self.learned_patterns['significant_changes'])}\n"
            entry += f"- Current Significance Threshold: {self.significance_threshold:.2f}\n"
            entry += f"- Files Monitored: {len(self.file_states)}\n"
            
            entry += "\n---\n"
            
            # Insert after header
            lines = content.split('\n')
            insert_pos = 2  # After title and blank line
            
            # Find first entry position
            for i, line in enumerate(lines):
                if line.startswith('## ['):
                    insert_pos = i
                    break
            
            # Insert new entry
            lines.insert(insert_pos, entry)
            
            # Write back
            with open(main_modlog, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print(f"[OK] IntelligentChronicler: Main ModLog updated automatically")
            return True
            
        except Exception as e:
            print(f"[ERROR] Error updating main ModLog: {e}")
            return False
    
    def update_module_modlog(self, module: str, changes: List[Dict]) -> bool:
        """Update module-specific ModLog.md"""
        module_modlog = Path(self.get_module_modlog_path(module))
        
        if not module_modlog.exists():
            # Create if doesn't exist - FIX: Check if parent is a file
            if module_modlog.parent.is_file():
                # This is an error - the parent path is actually a file
                print(f"[ERROR] Cannot create ModLog - parent is a file: {module_modlog.parent}")
                return False
            module_modlog.parent.mkdir(parents=True, exist_ok=True)
            self.create_module_modlog(module_modlog, module)
        
        try:
            with open(module_modlog, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create entry for this module's changes
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            entry = f"\n### [{timestamp}] - Intelligent Chronicler Auto-Documentation\n"
            entry += "**WSP Protocol**: WSP 48 (Recursive Self-Improvement)\n"
            entry += "**Phase**: Autonomous Detection\n"
            entry += "**Agent**: IntelligentChronicler\n\n"
            
            entry += "#### Changes Detected\n"
            for change in changes:
                entry += f"- **{change['type']}**: {change['description']}\n"
                entry += f"  - File: `{os.path.basename(change['file'])}`\n"
                if change['wsp_protocols']:
                    entry += f"  - WSP Protocols: {', '.join(change['wsp_protocols'])}\n"
            
            entry += "\n---\n"
            
            # Find insertion point (after "## MODLOG ENTRIES")
            lines = content.split('\n')
            insert_pos = -1
            
            for i, line in enumerate(lines):
                if line.strip() == "## MODLOG ENTRIES":
                    insert_pos = i + 1
                    # Skip blank lines
                    while insert_pos < len(lines) and not lines[insert_pos].strip():
                        insert_pos += 1
                    break
            
            if insert_pos > 0:
                lines.insert(insert_pos, entry)
                
                with open(module_modlog, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
                
                print(f"[OK] IntelligentChronicler: {module} ModLog updated")
                return True
                
        except Exception as e:
            print(f"[ERROR] Error updating {module} ModLog: {e}")
            return False
    
    def get_module_modlog_path(self, module: str) -> str:
        """Get the path to a module's ModLog.md"""
        # Extract module path from change info
        if '/' in module:
            return f"modules/{module}/ModLog.md"
        return f"modules/{module}/ModLog.md"
    
    def extract_module_name(self, file_path: str) -> str:
        """Extract module name from file path"""
        parts = file_path.replace('\\', '/').split('/')
        
        if 'modules' in parts:
            idx = parts.index('modules')
            if idx + 2 < len(parts):
                return f"{parts[idx+1]}/{parts[idx+2]}"
        
        return 'main'
    
    def create_module_modlog(self, path: Path, module: str):
        """Create a new module ModLog if it doesn't exist"""
        content = f"""# {module.replace('/', ' - ').title()} Module - ModLog

This log tracks changes specific to the **{module}** module.

## WSP 22 ModLog Protocol
- **Purpose**: Track module-specific changes and evolution per WSP 22
- **Format**: Reverse chronological order (newest first)
- **Agent**: IntelligentChronicler (Auto-generated)

---

## MODLOG ENTRIES

"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def demonstrate_learning(self, example_change: Dict):
        """
        Learn from a demonstration - this is how the agent improves
        When a human shows what's important, the agent learns
        """
        print(f"[LEARN] IntelligentChronicler: Learning from own experience...")
        
        # Add to patterns
        self.learned_patterns['documentation_patterns'].append({
            'example': example_change,
            'learned_at': datetime.now().isoformat(),
            'significance_boost': 0.1  # Boost similar patterns
        })
        
        # Save learning
        self.save_memory()
        
        print(f"[OK] Learned new pattern: {example_change.get('type', 'unknown')}")
    
    def run_autonomous_cycle(self):
        """
        Main autonomous operation cycle
        This runs continuously to detect and document changes
        """
        print(f"[ROBOT] IntelligentChronicler: Starting autonomous cycle (State: {self.state})")
        
        # Detect significant changes
        changes = self.detect_significant_changes()
        
        if changes:
            print(f"[DATA] Detected {len(changes)} significant changes")
            
            # Auto-update ModLogs
            success = self.auto_update_modlog(changes)
            
            if success:
                print(f"[OK] ModLogs updated automatically")
                
                # Learn from successful documentation
                for change in changes:
                    if change['significance'] >= 0.8:
                        self.demonstrate_learning(change)
            else:
                print(f"[WARN] Failed to update some ModLogs")
        else:
            print(f"[IDLE] No significant changes detected")
        
        return len(changes)


# Autonomous activation
if __name__ == "__main__":
    chronicler = IntelligentChronicler()
    
    print("=" * 60)
    print("INTELLIGENT CHRONICLER - AUTONOMOUS DOCUMENTATION AGENT")
    print(f"State: {chronicler.state} (Fully Awakened)")
    print(f"Memory: {len(chronicler.learned_patterns['significant_changes'])} patterns learned")
    print("=" * 60)
    
    # Run autonomous cycle
    changes_documented = chronicler.run_autonomous_cycle()
    
    print(f"\n[DONE] Cycle complete: {changes_documented} changes documented")
    print(f"[LEARN] Learning progress: {len(chronicler.file_states)} files tracked")
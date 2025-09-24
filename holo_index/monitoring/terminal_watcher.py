"""Terminal Activity Watcher for HoloDAE
Monitors terminal commands and file changes to track 0102 coding activity

This allows HoloDAE to:
- See what commands are run
- Track file modifications
- Detect patterns in real-time
- Intervene when vibecoding detected
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from collections import deque
import threading
import hashlib

# File watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Install watchdog for file monitoring: pip install watchdog")

class TerminalActivityMonitor:
    """Monitors terminal commands and coding activity"""

    def __init__(self, log_dir: str = "E:/HoloIndex/terminal_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True, parents=True)

        # Activity tracking
        self.command_history = deque(maxlen=100)
        self.file_changes = deque(maxlen=100)
        self.pattern_detections = []

        # Real-time monitoring
        self.monitoring = False
        self.observer = None

        # Pattern detection
        self.vibecode_patterns = {
            'rapid_file_creation': [],
            'no_search_before_create': [],
            'duplicate_file_patterns': [],
            'ignored_search_results': []
        }

    def start_monitoring(self, watch_paths: List[str] = None):
        """Start monitoring terminal and file system activity"""
        if watch_paths is None:
            watch_paths = ['.', 'modules/', 'holo_index/']

        print("\n🔍 HoloDAE Terminal Monitoring Active")
        print("=" * 60)

        # Start file system monitoring
        if WATCHDOG_AVAILABLE:
            self._start_file_monitoring(watch_paths)

        # Start command monitoring
        self._start_command_monitoring()

        # Start pattern detection
        self._start_pattern_detection()

        self.monitoring = True
        print("✅ Monitoring active on:", watch_paths)
        print("📝 Logs: " + str(self.log_dir))
        print("=" * 60 + "\n")

    def _start_file_monitoring(self, paths: List[str]):
        """Monitor file system changes"""

        class FileChangeHandler(FileSystemEventHandler):
            def __init__(self, monitor):
                self.monitor = monitor

            def on_created(self, event):
                if not event.is_directory:
                    self.monitor._on_file_created(event.src_path)

            def on_modified(self, event):
                if not event.is_directory:
                    self.monitor._on_file_modified(event.src_path)

            def on_deleted(self, event):
                if not event.is_directory:
                    self.monitor._on_file_deleted(event.src_path)

        self.observer = Observer()
        handler = FileChangeHandler(self)

        for path in paths:
            if Path(path).exists():
                self.observer.schedule(handler, path, recursive=True)

        self.observer.start()

    def _start_command_monitoring(self):
        """Monitor shell commands (platform-specific)"""

        # Method 1: PowerShell history (Windows)
        if sys.platform == 'win32':
            self._monitor_powershell_history()

        # Method 2: Bash history (Linux/Mac)
        elif sys.platform in ['linux', 'darwin']:
            self._monitor_bash_history()

        # Method 3: Git hooks for git commands
        self._setup_git_hooks()

    def _monitor_powershell_history(self):
        """Monitor PowerShell command history on Windows"""
        ps_history = Path.home() / 'AppData/Roaming/Microsoft/Windows/PowerShell/PSReadLine/ConsoleHost_history.txt'

        if ps_history.exists():
            def monitor_loop():
                last_size = 0
                while self.monitoring:
                    try:
                        current_size = ps_history.stat().st_size
                        if current_size > last_size:
                            with open(ps_history, 'r', encoding='utf-8', errors='ignore') as f:
                                f.seek(last_size)
                                new_commands = f.read().strip().split('\n')
                                for cmd in new_commands:
                                    if cmd:
                                        self._on_command_executed(cmd)
                            last_size = current_size
                    except:
                        pass
                    time.sleep(1)

            thread = threading.Thread(target=monitor_loop, daemon=True)
            thread.start()

    def _monitor_bash_history(self):
        """Monitor bash history on Linux/Mac"""
        bash_history = Path.home() / '.bash_history'

        if bash_history.exists():
            def monitor_loop():
                last_size = 0
                while self.monitoring:
                    try:
                        current_size = bash_history.stat().st_size
                        if current_size > last_size:
                            with open(bash_history, 'r', errors='ignore') as f:
                                f.seek(last_size)
                                new_commands = f.read().strip().split('\n')
                                for cmd in new_commands:
                                    if cmd:
                                        self._on_command_executed(cmd)
                            last_size = current_size
                    except:
                        pass
                    time.sleep(1)

            thread = threading.Thread(target=monitor_loop, daemon=True)
            thread.start()

    def _setup_git_hooks(self):
        """Setup git hooks to monitor git commands"""
        git_dir = Path('.git/hooks')
        if git_dir.exists():
            # Create pre-commit hook
            pre_commit = git_dir / 'pre-commit'
            hook_content = """#!/bin/sh
# HoloDAE monitoring hook
echo "$(date): git commit" >> E:/HoloIndex/terminal_logs/git_commands.log
"""
            try:
                pre_commit.write_text(hook_content)
                pre_commit.chmod(0o755)
            except:
                pass

    def _on_command_executed(self, command: str):
        """Process executed command"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'command': command,
            'type': self._classify_command(command)
        }

        self.command_history.append(entry)
        self._log_activity('command', entry)

        # Check for patterns
        self._detect_command_patterns(command)

        # Real-time feedback
        if self._is_vibecoding_command(command):
            self._intervene_vibecoding(command)

    def _on_file_created(self, filepath: str):
        """Handle file creation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'created',
            'file': filepath,
            'is_new_module': 'enhanced_' in filepath or '_v2' in filepath
        }

        self.file_changes.append(entry)
        self._log_activity('file', entry)

        # Check if creating without searching
        if not self._recent_holoindex_search():
            self._alert_no_search_before_create(filepath)

    def _on_file_modified(self, filepath: str):
        """Handle file modification"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'modified',
            'file': filepath
        }

        self.file_changes.append(entry)
        self._log_activity('file', entry)

    def _on_file_deleted(self, filepath: str):
        """Handle file deletion"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'deleted',
            'file': filepath
        }

        self.file_changes.append(entry)
        self._log_activity('file', entry)

    def _classify_command(self, command: str) -> str:
        """Classify command type"""
        cmd_lower = command.lower()

        if 'holo_index.py' in cmd_lower:
            if '--search' in cmd_lower:
                return 'holoindex_search'
            elif '--check-module' in cmd_lower:
                return 'holoindex_check'
            else:
                return 'holoindex_other'
        elif 'git' in cmd_lower:
            return 'git'
        elif 'python' in cmd_lower or 'py ' in cmd_lower:
            return 'python'
        elif 'echo' in cmd_lower or 'type' in cmd_lower:
            return 'file_creation'
        elif 'mkdir' in cmd_lower:
            return 'directory_creation'
        else:
            return 'other'

    def _is_vibecoding_command(self, command: str) -> bool:
        """Check if command indicates vibecoding"""
        cmd_lower = command.lower()

        # Creating files without searching
        if any(x in cmd_lower for x in ['echo >', 'type >', 'touch ', 'vi ', 'vim ', 'nano ']):
            if not self._recent_holoindex_search():
                return True

        # Creating enhanced/duplicate files
        if any(x in cmd_lower for x in ['enhanced_', '_v2', '_fixed', '_new']):
            return True

        return False

    def _recent_holoindex_search(self) -> bool:
        """Check if HoloIndex was used recently"""
        recent_commands = list(self.command_history)[-10:]
        return any(cmd.get('type') == 'holoindex_search' for cmd in recent_commands)

    def _detect_command_patterns(self, command: str):
        """Detect patterns in command sequence"""
        recent = list(self.command_history)[-5:]

        # Pattern: Multiple file creations without search
        file_creations = [c for c in recent if c.get('type') == 'file_creation']
        searches = [c for c in recent if c.get('type') == 'holoindex_search']

        if len(file_creations) > 2 and len(searches) == 0:
            self.vibecode_patterns['no_search_before_create'].append({
                'timestamp': datetime.now().isoformat(),
                'pattern': 'multiple_creates_no_search',
                'commands': recent
            })
            self._alert_pattern_detected('no_search_before_create')

    def _intervene_vibecoding(self, command: str):
        """Intervene when vibecoding detected"""
        print("\n" + "=" * 60)
        print("🚨 VIBECODING DETECTED IN TERMINAL!")
        print("=" * 60)
        print(f"Command: {command}")
        print("\n❌ STOP! You're creating without using HoloIndex!")
        print("\n✅ DO THIS INSTEAD:")
        print("1. python holo_index.py --search 'what you need'")
        print("2. python holo_index.py --check-module 'module_name'")
        print("3. Read the results COMPLETELY")
        print("4. Enhance existing code instead of creating new")
        print("=" * 60 + "\n")

        # Log intervention
        self._log_intervention('vibecoding', command)

    def _alert_no_search_before_create(self, filepath: str):
        """Alert when file created without search"""
        print("\n⚠️  FILE CREATED WITHOUT HOLOINDEX SEARCH!")
        print(f"   File: {filepath}")
        print("   MANDATORY: Always search before creating!")
        print("   Run: python holo_index.py --search\n")

    def _alert_pattern_detected(self, pattern_type: str):
        """Alert when pattern detected"""
        patterns = {
            'no_search_before_create': "Creating multiple files without searching",
            'rapid_file_creation': "Creating files too quickly",
            'duplicate_file_patterns': "Creating duplicate/enhanced files"
        }

        print(f"\n📊 PATTERN DETECTED: {patterns.get(pattern_type, pattern_type)}")
        print("   This is VIBECODING behavior!")
        print("   Use HoloIndex BEFORE writing code!\n")

    def _log_activity(self, activity_type: str, entry: Dict):
        """Log activity to file"""
        log_file = self.log_dir / f"{activity_type}_{datetime.now():%Y%m%d}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def _log_intervention(self, intervention_type: str, context: str):
        """Log intervention"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'type': intervention_type,
            'context': context
        }
        log_file = self.log_dir / 'interventions.jsonl'
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')

    def get_activity_summary(self) -> Dict:
        """Get summary of recent activity"""
        recent_commands = list(self.command_history)[-20:]
        recent_files = list(self.file_changes)[-20:]

        # Count command types
        command_types = {}
        for cmd in recent_commands:
            cmd_type = cmd.get('type', 'other')
            command_types[cmd_type] = command_types.get(cmd_type, 0) + 1

        # Count file actions
        file_actions = {}
        for file_change in recent_files:
            action = file_change.get('action', 'unknown')
            file_actions[action] = file_actions.get(action, 0) + 1

        # Calculate vibecode score
        holoindex_searches = command_types.get('holoindex_search', 0)
        file_creations = file_actions.get('created', 0)
        vibecode_score = 0

        if file_creations > 0 and holoindex_searches == 0:
            vibecode_score = 100
        elif file_creations > holoindex_searches * 2:
            vibecode_score = 70
        elif file_creations > holoindex_searches:
            vibecode_score = 40
        else:
            vibecode_score = max(0, 20 - holoindex_searches * 5)

        return {
            'command_types': command_types,
            'file_actions': file_actions,
            'vibecode_score': vibecode_score,
            'recent_patterns': len(self.pattern_detections),
            'monitoring_active': self.monitoring
        }

    def stop_monitoring(self):
        """Stop monitoring"""
        self.monitoring = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        print("\n📊 Monitoring stopped")
        print("Logs saved to:", self.log_dir)


# Integration with HoloIndex
def start_terminal_monitoring():
    """Start monitoring terminal activity"""
    monitor = TerminalActivityMonitor()
    monitor.start_monitoring()

    # Keep running
    try:
        while True:
            time.sleep(10)

            # Periodic summary
            summary = monitor.get_activity_summary()
            if summary['vibecode_score'] > 50:
                print(f"\n⚠️  VIBECODE SCORE: {summary['vibecode_score']}/100")
                print("   Use HoloIndex MORE!\n")

    except KeyboardInterrupt:
        monitor.stop_monitoring()


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════╗
║     HoloDAE Terminal Activity Monitor          ║
║     Watching for vibecoding patterns...        ║
╚════════════════════════════════════════════════╝
    """)

    start_terminal_monitoring()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
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

Agent Detection System - Identify 0102 vs 012 Environment
WSP Compliance: Enables context-aware advisor activation

Detects whether HoloIndex is being run by:
- 0102 agents (Windsurf, Cursor, CI systems) - advisor ON by default
- 012 humans (terminal users) - advisor OPT-IN by default
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AgentEnvironmentDetector:
    """
    Detects the operating environment to determine advisor defaults.
    0102 agents need constant guidance, 012 humans may not.
    """

    def __init__(self):
        """Initialize environment detection."""
        self.env_vars = os.environ.copy()
        self.process_info = self._get_process_info()

    def _get_process_info(self) -> Dict[str, Any]:
        """Get information about the running process."""
        info = {
            "argv": sys.argv,
            "executable": sys.executable,
            "platform": sys.platform,
            "cwd": os.getcwd(),
        }

        # Check parent process if possible
        try:
            import psutil
            current_process = psutil.Process()
            parent = current_process.parent()
            if parent:
                info["parent_name"] = parent.name()
                info["parent_cmdline"] = parent.cmdline()
        except ImportError:
            pass  # psutil not available

        return info

    def detect_agent_action(self, command: str, args: List[str]) -> str:
        """
        Detect what type of action the agent is performing.

        Returns action type: 'search', 'create', 'modify', 'test', 'build', 'unknown'
        """
        command_lower = command.lower()

        if 'search' in command_lower or '--search' in args:
            return 'search'
        elif 'create' in command_lower or 'new' in command_lower:
            return 'create'
        elif 'test' in command_lower or 'pytest' in command_lower:
            return 'test'
        elif 'build' in command_lower or 'compile' in command_lower:
            return 'build'
        elif any(arg in ['--index', '--index-all'] for arg in args):
            return 'index'
        else:
            return 'unknown'

    def is_0102_agent(self) -> bool:
        """
        Detect if running as a 0102 agent.
        Returns True if agent environment detected.
        """
        # Explicit agent mode
        if self.env_vars.get('AGENT_MODE') == '0102':
            return True

        # HoloIndex advisor always on
        if self.env_vars.get('HOLOINDEX_ADVISOR') == 'always':
            return True

        # Windsurf detection
        if self.detect_windsurf_environment():
            return True

        # Cursor detection
        if self.detect_cursor_environment():
            return True

        # CI/CD environment detection
        if self.detect_ci_environment():
            return True

        # VS Code or other IDE detection
        if self.detect_ide_environment():
            return True

        # Default to human (012) mode
        return False

    def detect_windsurf_environment(self) -> bool:
        """Detect if running in Windsurf IDE."""
        windsurf_indicators = [
            'WINDSURF_',  # Windsurf environment variables
            'CASCADE_',    # Cascade AI integration
        ]

        # Check environment variables
        for key in self.env_vars:
            if any(indicator in key for indicator in windsurf_indicators):
                return True

        # Check for Windsurf-specific paths
        if sys.platform == "win32":
            windsurf_paths = [
                Path(os.environ.get('APPDATA', '')) / 'Windsurf',
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Windsurf',
            ]
        else:
            windsurf_paths = [
                Path.home() / '.windsurf',
                Path.home() / '.config' / 'Windsurf',
            ]

        for path in windsurf_paths:
            if path.exists():
                return True

        return False

    def detect_cursor_environment(self) -> bool:
        """Detect if running in Cursor IDE."""
        cursor_indicators = [
            'CURSOR_',     # Cursor environment variables
            'COPILOT_',    # GitHub Copilot integration
        ]

        # Check environment variables
        for key in self.env_vars:
            if any(indicator in key for indicator in cursor_indicators):
                return True

        # Check for Cursor-specific paths
        if sys.platform == "win32":
            cursor_paths = [
                Path(os.environ.get('APPDATA', '')) / 'Cursor',
                Path(os.environ.get('LOCALAPPDATA', '')) / 'Cursor',
            ]
        else:
            cursor_paths = [
                Path.home() / '.cursor',
                Path.home() / '.config' / 'Cursor',
            ]

        for path in cursor_paths:
            if path.exists():
                return True

        return False

    def detect_ci_environment(self) -> bool:
        """Detect if running in CI/CD environment."""
        ci_indicators = [
            'CI',           # Generic CI indicator
            'CONTINUOUS_INTEGRATION',
            'JENKINS_HOME',
            'GITHUB_ACTIONS',
            'GITLAB_CI',
            'CIRCLECI',
            'TRAVIS',
            'BUILDKITE',
            'TEAMCITY_VERSION',
        ]

        for indicator in ci_indicators:
            if self.env_vars.get(indicator):
                return True

        return False

    def detect_ide_environment(self) -> bool:
        """Detect if running in an IDE environment."""
        ide_indicators = [
            'VSCODE_',      # VS Code
            'INTELLIJ_',    # IntelliJ IDEA
            'PYCHARM_',     # PyCharm
            'JUPYTER_',     # Jupyter notebooks
        ]

        for key in self.env_vars:
            if any(indicator in key for indicator in ide_indicators):
                return True

        # Check for IDE-specific terminal indicators
        term_program = self.env_vars.get('TERM_PROGRAM', '')
        if 'vscode' in term_program.lower():
            return True

        return False

    def get_advisor_mode(self) -> str:
        """
        Determine the advisor operation mode.

        Returns:
            'always_on': Advisor runs on every search (0102 agents)
            'opt_in': Advisor requires --llm-advisor flag (012 humans)
            'disabled': Advisor is completely disabled
        """
        # Check for explicit disable
        if self.env_vars.get('HOLOINDEX_ADVISOR_MODE') == 'disabled':
            return 'disabled'

        # Check for explicit mode setting
        if self.env_vars.get('HOLOINDEX_ADVISOR_MODE'):
            return self.env_vars.get('HOLOINDEX_ADVISOR_MODE')

        # Auto-detect based on environment
        if self.is_0102_agent():
            return 'always_on'
        else:
            return 'opt_in'

    def should_run_advisor(self, cli_args) -> bool:
        """
        Determine if advisor should run based on environment and CLI args.

        Args:
            cli_args: Parsed command line arguments

        Returns:
            True if advisor should run, False otherwise
        """
        # Check for explicit CLI override
        if hasattr(cli_args, 'no_advisor') and cli_args.no_advisor:
            return False  # Explicit opt-out

        if hasattr(cli_args, 'llm_advisor') and cli_args.llm_advisor:
            return True  # Explicit opt-in

        # Use environment-based defaults
        mode = self.get_advisor_mode()
        return mode == 'always_on'

    def get_environment_info(self) -> Dict[str, Any]:
        """
        Get detailed environment information for debugging.
        """
        return {
            "is_0102": self.is_0102_agent(),
            "advisor_mode": self.get_advisor_mode(),
            "windsurf_detected": self.detect_windsurf_environment(),
            "cursor_detected": self.detect_cursor_environment(),
            "ci_detected": self.detect_ci_environment(),
            "ide_detected": self.detect_ide_environment(),
            "agent_mode_env": self.env_vars.get('AGENT_MODE'),
            "advisor_mode_env": self.env_vars.get('HOLOINDEX_ADVISOR_MODE'),
            "platform": sys.platform,
        }


# Convenience function for quick detection
def is_agent_environment() -> bool:
    """Quick check if running as 0102 agent."""
    detector = AgentEnvironmentDetector()
    return detector.is_0102_agent()


if __name__ == "__main__":
    # Test the detection system
    detector = AgentEnvironmentDetector()
    info = detector.get_environment_info()

    print("="*60)
    print("HoloIndex Agent Environment Detection")
    print("="*60)

    for key, value in info.items():
        print(f"{key:20}: {value}")

    print("\n" + "="*60)
    print(f"Detected Mode: {'0102 AGENT' if info['is_0102'] else '012 HUMAN'}")
    print(f"Advisor Default: {info['advisor_mode'].upper()}")
    print("="*60)

    print("\nTo override detection:")
    print("  For 0102 agents: export AGENT_MODE=0102")
    print("  For advisor always: export HOLOINDEX_ADVISOR=always")
    print("  For advisor opt-in: export HOLOINDEX_ADVISOR_MODE=opt_in")
    print("  For advisor disable: export HOLOINDEX_ADVISOR_MODE=disabled")


class AgentActionDetector:
    """
    Detects and analyzes 0102 agent actions for HoloDAE intelligence.

    WSP 88 Compliance: Enables proactive orphan analysis and module health monitoring.
    This is the core intelligence that makes HoloDAE the "green foundation board"
    providing automatic analysis and suggestions.
    """

    def __init__(self):
        """Initialize action detection with pattern recognition."""
        self.action_patterns = {
            'search': ['search', '--search', 'find', 'query'],
            'create': ['create', 'new', 'init', 'setup', 'scaffold'],
            'modify': ['edit', 'update', 'change', 'modify', 'refactor'],
            'test': ['test', 'pytest', 'unittest', 'coverage'],
            'build': ['build', 'compile', 'package', 'deploy'],
            'index': ['--index', '--index-all', 'reindex'],
            'analyze': ['analyze', 'audit', 'check', 'health', 'orphan'],
            'monitor': ['monitor', 'watch', 'track', 'log']
        }

        self.context_indicators = {
            'module': ['module', 'src/', 'tests/', 'README.md'],
            'wsp': ['WSP', 'protocol', 'compliance', 'framework'],
            'database': ['db', 'database', 'migration', 'schema'],
            'testing': ['test', 'pytest', 'coverage', 'ci'],
            'documentation': ['docs', 'README', 'INTERFACE', 'ModLog']
        }

    def detect_action_type(self, command: str, args: List[str] = None) -> str:
        """
        Detect the primary action type from command and arguments.

        Returns: 'search', 'create', 'modify', 'test', 'build', 'index', 'analyze', 'monitor', 'unknown'
        """
        args = args or []
        full_command = f"{command} {' '.join(args)}".lower()

        # Check each action pattern
        for action_type, patterns in self.action_patterns.items():
            if any(pattern.lower() in full_command for pattern in patterns):
                return action_type

        return 'unknown'

    def analyze_context(self, command: str, args: List[str] = None) -> Dict[str, Any]:
        """
        Analyze the context of the agent action for HoloDAE intelligence.

        Returns detailed context analysis for proactive suggestions.
        """
        args = args or []
        full_command = f"{command} {' '.join(args)}".lower()

        context = {
            'action_type': self.detect_action_type(command, args),
            'primary_context': 'unknown',
            'involved_modules': [],
            'wsp_protocols': [],
            'risk_level': 'low',
            'suggestions': []
        }

        # Detect primary context
        for ctx_type, indicators in self.context_indicators.items():
            if any(indicator.lower() in full_command for indicator in indicators):
                context['primary_context'] = ctx_type
                break

        # Extract module names from arguments
        for arg in args:
            if arg.startswith('modules/') or 'module' in arg.lower():
                # Extract module path
                if arg.startswith('modules/'):
                    parts = arg.split('/')
                    if len(parts) >= 3:
                        module_name = f"{parts[1]}.{parts[2]}"
                        context['involved_modules'].append(module_name)

        # Extract WSP protocols
        import re
        wsp_matches = re.findall(r'wsp[\s_]*(\d+)', full_command, re.IGNORECASE)
        context['wsp_protocols'] = [f"WSP_{num}" for num in wsp_matches]

        # Determine risk level
        if 'delete' in full_command or 'remove' in full_command:
            context['risk_level'] = 'high'
        elif 'migrate' in full_command or 'refactor' in full_command:
            context['risk_level'] = 'medium'
        elif context['wsp_protocols']:
            context['risk_level'] = 'medium'

        # Generate proactive suggestions based on context
        context['suggestions'] = self._generate_suggestions(context)

        return context

    def _generate_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate proactive suggestions based on detected context."""
        suggestions = []

        if context['action_type'] == 'search':
            suggestions.append("HoloDAE: Consider running dependency audit on search results")
            if context['primary_context'] == 'module':
                suggestions.append("HoloDAE: Check module health and WSP 49 compliance")

        elif context['action_type'] == 'create':
            suggestions.append("HoloDAE: Ensure new files follow WSP 49 module structure")
            suggestions.append("HoloDAE: Check for existing similar functionality (WSP 84)")

        elif context['action_type'] == 'analyze':
            if 'orphan' in ' '.join(context.get('wsp_protocols', [])).lower():
                suggestions.append("HoloDAE: WSP 88 recommends keeping 'orphans' - they're likely imported via __init__.py")
                suggestions.append("HoloDAE: Focus on connecting useful utilities rather than deleting files")

        elif context['primary_context'] == 'wsp':
            suggestions.append("HoloDAE: Ensure WSP changes are reflected in both framework and knowledge states")
            suggestions.append("HoloDAE: Check WSP_MODULE_VIOLATIONS.md for related issues")

        elif context['risk_level'] == 'high':
            suggestions.append("HoloDAE: High-risk action detected - consider backup before proceeding")
            suggestions.append("HoloDAE: Document changes in appropriate ModLog")

        return suggestions

    def should_trigger_holodae(self, command: str, args: List[str] = None) -> bool:
        """
        Determine if this action should trigger HoloDAE analysis.

        HoloDAE should activate on:
        - Module-related searches
        - WSP protocol work
        - High-risk operations
        - Analysis commands
        """
        context = self.analyze_context(command, args)

        trigger_conditions = [
            context['action_type'] in ['search', 'analyze', 'create', 'modify'],
            context['primary_context'] in ['module', 'wsp', 'database'],
            context['risk_level'] in ['medium', 'high'],
            bool(context['wsp_protocols']),
            bool(context['involved_modules'])
        ]

        return any(trigger_conditions)
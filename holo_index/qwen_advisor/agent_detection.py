#!/usr/bin/env python3
"""
Agent Detection System - Identify 0102 vs 012 Environment
WSP Compliance: Enables context-aware advisor activation

Detects whether HoloIndex is being run by:
- 0102 agents (Windsurf, Cursor, CI systems) - advisor ON by default
- 012 humans (terminal users) - advisor OPT-IN by default
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any


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
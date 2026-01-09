#!/usr/bin/env python3
"""
Menu System - User interface components for HoloDAE

Provides clean interfaces for 0102 to interact with the Qwen orchestration
and 0102 arbitration system.

WSP Compliance: WSP 80 (Cube-Level DAE Orchestration)
"""

from typing import Optional, Dict, Any, List
from datetime import datetime


class HoloDAEMenuSystem:
    """Menu system for HoloDAE user interaction"""

    def __init__(self):
        """Initialize the menu system"""
        self.menu_options = {
            '00': ('[REFRESH] Manual Index', 'Refresh HoloIndex while 0102 works (--index-all)'),
            '0': ('[ROCKET] Launch HoloDAE', 'Start continuous monitoring (--start-holodae)'),
            '1': ('[SEARCH] Semantic Search', 'Find existing code before creating (--search)'),
            '2': ('[OK] WSP Compliance Check', 'Validate protocol adherence (--check-module)'),
            '3': ('[AI] Pattern Coach', 'Prevent behavioral vibecoding patterns (--pattern-coach)'),
            '4': ('[BOX] Module Analysis', 'Detect duplicate implementations (--module-analysis)'),
            '5': ('[PILL] Health Analysis', 'Check system architectural integrity (--health-check)'),
            '6': ('[GHOST] Orphan Analysis', 'Find dead code and unused modules (--wsp88)'),
            '7': ('[DATA] Performance Metrics', 'View effectiveness scores (--performance-metrics)'),
            '8': ('[BOT] LLM Advisor', 'Get AI-powered guidance (--llm-advisor with search)'),
            '9': ('[EYE] Stop Monitoring', 'Stop autonomous monitoring (--stop-holodae)'),
            '10': ('[STAT] HoloDAE Status', 'Show monitoring status (--holodae-status)'),
            '11': ('[COG] Chain-of-Thought Log', 'View AI decision process (--thought-log)'),
            '12': ('[SLOW] Slow Mode', 'Enable recursive feedback 2-3s delays (--slow-mode)'),
            '13': ('[MEMORY] Pattern Memory', 'View learned interventions (--pattern-memory)'),
            '14': ('[FEEDBACK] Memory Feedback', 'Rate memory cards (good/noisy/missing) (--memory-feedback)'),
            '15': ('[HOOK] MCP Hook Map', 'Inspect registered connectors and health (--mcp-hooks)'),
            '16': ('[LOG] MCP Action Log', 'Review recent MCP tool activity (--mcp-log)'),
            '17': ('[PUBLISH] Work Publisher', 'Monitor work completion for auto-publish (--monitor-work)'),
            '18': ('[UTF8] UTF-8 Fix', 'Auto-fix UTF-8 violations with Qwen/Gemma (main.py --training-command utf8_fix --targets <scope>)'),
            '19': ('[CHECK] System Check', 'Verify CLI wiring and generate report (--system-check)'),
            '20': ('[CTRL] Holo Controls', 'Toggle auto-index, SSD path, and startup quieting')
        }

    def show_main_menu(self) -> None:
        """Display the main HoloDAE menu for 0102 and 012 observers"""
        print("\n" + "=" * 60)
        print("HoloDAE Code Intelligence & WSP Compliance Observatory")
        print("=" * 60)
        print("0. [ROCKET] Launch HoloDAE (Autonomous Monitoring) | --start-holodae")
        print()
        print("CORE PREVENTION (Stay out of vibecoding)")
        print("1. [SEARCH] Semantic Search                        | --search")
        print("2. [OK] WSP Compliance Check                       | --check-module")
        print("3. [AI] Pattern Coach                              | --pattern-coach")
        print("4. [BOX] Module Analysis                           | --module-analysis")
        print()
        print("SUPPORT SYSTEMS (Diagnostics)")
        print("5. [PILL] Health Analysis                          | --health-check")
        print("6. [GHOST] Orphan Analysis                         | --wsp88")
        print("7. [DATA] Performance Metrics                      | --performance-metrics")
        print("8. [BOT] LLM Advisor (with search)                 | --llm-advisor")
        print()
        print("CONTINUOUS OBSERVABILITY")
        print("9. [EYE] Stop Monitoring                           | --stop-holodae")
        print("10. [STAT] HoloDAE Status                          | --holodae-status")
        print("11. [COG] Chain-of-Thought Log                     | --thought-log")
        print("12. [SLOW] Slow Mode                               | --slow-mode")
        print("13. [MEMORY] Pattern Memory                        | --pattern-memory")
        print("14. [FEEDBACK] Memory Feedback (per card)          | --memory-feedback")
        print()
        print("MCP RESEARCH BRIDGE")
        print("15. [HOOK] MCP Hook Map                            | --mcp-hooks")
        print("16. [LOG] MCP Action Log                           | --mcp-log")
        print()
        print("SYSTEM CONTROLS")
        print("17. [PUBLISH] Work Publisher (Auto Git/Social)     | --monitor-work")
        print()
        print("QWEN/GEMMA AUTONOMOUS TRAINING")
        print("18. [UTF8] UTF-8 Fix (Autonomous Remediation)      | main.py --training-command utf8_fix --targets <scope>")
        print()
        print("VERIFICATION")
        print("19. [CHECK] System Check                           | --system-check")
        print()
        print("CONTROLS")
        print("20. [CTRL] Holo Controls                           | menu only")
        print()
        print("98. Exit")
        print("------------------------------------------------------------")
        print("00. [REFRESH] Manual Index Refresh                 | --index-all")
        print("=" * 60)
    def show_sprint_dashboard(self, component_status: Optional[Dict[str, Any]] = None) -> None:
        """Display the WSP 37 sprint dashboard with component status"""
        print("\n[TARGET] HOLODAE LIVING SPRINT - WSP 37 PRIORITY MATRIX")
        print("Components turn GREEN as development completes | Real-time status & ratings")
        print("=" * 80)

        # Default component status if not provided
        if component_status is None:
            component_status = self._get_default_component_status()

        # Show components with status
        components = [
            ("chain_of_thought", "Chain-of-Thought Algorithm", "ENTIRE SYSTEM COORDINATING INTELLIGENCE"),
            ("semantic_search_engine", "Semantic Search Engine", "FINDS EXISTING CODE BEFORE VIBECODING"),
            ("pattern_coach", "Pattern Coach", "PREVENTS BEHAVIORAL VIBECODING PATTERNS"),
            ("holodae_autonomous_agent", "HoloDAE Autonomous Agent", "ENTIRE SYSTEM WORKING TOGETHER"),
            ("module_analysis_system", "Module Analysis System", "Prevents duplicate implementations"),
            ("health_analysis_engine", "Health Analysis Engine", "Architectural integrity protection")
        ]

        for comp_id, comp_name, comp_desc in components:
            status_info = component_status.get(comp_id, {})
            status_icon = status_info.get('status_icon', '[UNKNOWN]')
            effectiveness = status_info.get('effectiveness', 0.0)

            print(f"{status_icon} {comp_name} -> {comp_desc}")
            print(f"   [STATS] Effectiveness: {effectiveness:.2f}")
            print()

    def show_status_summary(self, monitoring_state: Optional[Dict[str, Any]] = None) -> None:
        """Show a compact status summary"""
        print("[DICE] WSP 37 CUBE SYSTEM: [CRITICAL] Critical [CORE] Core [ENHANCED] Enhanced [COMPLETE] Complete [EXPERIMENTAL] Experimental")
        print("[TARGET] SPRINT PRIORITY: RED -> ORANGE -> YELLOW -> GREEN -> BLUE")

        if monitoring_state:
            is_active = monitoring_state.get('is_active', False)
            uptime = monitoring_state.get('uptime_minutes', 0)
            scans = monitoring_state.get('total_scans', 0)

            if is_active:
                print(f"[MONITOR] ACTIVE: {uptime:.1f}m uptime, {scans} scans performed")
            else:
                print("[MONITOR] INACTIVE: Ready to launch")

    def _get_default_component_status(self) -> Dict[str, Any]:
        """Get default component status for demo purposes"""
        return {
            'chain_of_thought': {
                'status_icon': '[SUCCESS]',
                'effectiveness': 0.85
            },
            'semantic_search_engine': {
                'status_icon': '[SUCCESS]',
                'effectiveness': 0.95
            },
            'pattern_coach': {
                'status_icon': '[WARN]',
                'effectiveness': 0.60
            },
            'holodae_autonomous_agent': {
                'status_icon': '[SUCCESS]',
                'effectiveness': 0.90
            },
            'module_analysis_system': {
                'status_icon': '[SUCCESS]',
                'effectiveness': 0.75
            },
            'health_analysis_engine': {
                'status_icon': '[SUCCESS]',
                'effectiveness': 0.80
            }
        }

    def get_menu_choice(self, prompt: str = "Select option (0-20, 98-99): ") -> str:
        """Get menu choice from user"""
        try:
            choice = input(f"\n012> {prompt}").strip()
            return choice
        except (EOFError, KeyboardInterrupt):
            return "99"  # Default to exit on interrupt


class StatusDisplay:
    """Status display utilities for HoloDAE"""

    @staticmethod
    def show_arbitration_decision(decision: Dict[str, Any]) -> None:
        """Display an arbitration decision to 012"""
        now = datetime.now().strftime('%H:%M:%S')

        finding_type = decision.get('finding_type', 'unknown')
        description = decision.get('description', 'No description')
        action = decision.get('recommended_action', 'unknown')
        mps_score = decision.get('mps_score', 0)

        print(f"[{now}] [0102-ARBITRATION] {action.upper()}: {description}")
        print(f"        MPS Score: {mps_score} | Type: {finding_type}")

    @staticmethod
    def show_qwen_orchestration_summary(summary: Dict[str, Any]) -> None:
        """Display Qwen orchestration summary"""
        executed = summary.get('executed_components', [])
        total_time = summary.get('total_execution_time', 0.0)
        effectiveness = summary.get('overall_effectiveness', 0.0)

        print(f"[QWEN-ORCHESTRATION] Completed in {total_time:.2f}s")
        print(f"[QWEN-ORCHESTRATION] Components executed: {', '.join(executed)}")
        print(f"[QWEN-ORCHESTRATION] Effectiveness: {effectiveness:.2f}")

    @staticmethod
    def show_monitoring_heartbeat(state: Dict[str, Any]) -> None:
        """Display monitoring heartbeat status"""
        now = datetime.now().strftime('%H:%M:%S')
        idle_minutes = state.get('idle_minutes', 0)
        watched_paths = state.get('watched_paths', 1)
        last_change = state.get('last_change_time', 'never')

        if idle_minutes > 0:
            print(f"[{now}] [HOLODAE] 竢ｳ idle {idle_minutes}m 窶・watching {watched_paths} paths (last change {last_change})")
        else:
            print(f"[{now}] [HOLODAE] [ACTIVE] monitoring {watched_paths} paths")


# Convenience functions for external use
def show_main_menu() -> str:
    """Convenience function to show main menu and get choice"""
    menu_system = HoloDAEMenuSystem()
    menu_system.show_main_menu()
    return menu_system.get_menu_choice()


def show_sprint_status(component_status: Optional[Dict[str, Any]] = None) -> None:
    """Convenience function to show sprint status"""
    menu_system = HoloDAEMenuSystem()
    menu_system.show_sprint_dashboard(component_status)
    menu_system.show_status_summary()

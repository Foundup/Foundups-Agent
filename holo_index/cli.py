#!/usr/bin/env python3
"""
HoloIndex - Dual Semantic Navigation for Code + WSP
Leverages the E: SSD for ultra-fast, persistent search

WSP 87 Compliant - Prevents vibecoding by pairing code discovery with protocol guidance
"""

import argparse
import json
import os
import re
import logging
import sys
import time
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import asdict
from holo_index.utils.helpers import safe_print
from holo_index.reports.codeindex_reporter import CodeIndexReporter, resolve_module_paths

try:
    from holo_index.qwen_advisor.advisor import AdvisorContext, QwenAdvisor
    from holo_index.qwen_advisor.config import QwenAdvisorConfig
    from holo_index.qwen_advisor.telemetry import record_advisor_event
    from holo_index.qwen_advisor.rules_engine import ComplianceRulesEngine
    from holo_index.qwen_advisor.agent_detection import AgentEnvironmentDetector
    ADVISOR_AVAILABLE = True
except Exception:
    ADVISOR_AVAILABLE = False
    AdvisorContext = None  # type: ignore
    QwenAdvisor = None  # type: ignore
    QwenAdvisorConfig = None  # type: ignore

# Phase 3: Adaptive Learning Integration
try:
    from holo_index.adaptive_learning.adaptive_learning_orchestrator import AdaptiveLearningOrchestrator
    ADAPTIVE_LEARNING_AVAILABLE = True
except ImportError:
    ADAPTIVE_LEARNING_AVAILABLE = False
    record_advisor_event = None  # type: ignore

# Import extracted modules with proper path handling
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Temporarily use regular print - safe_print causing scoping issues
# TODO: Fix safe_print scoping issue

try:
    from holo_index.core import IntelligentSubroutineEngine, HoloIndex
    from holo_index.output import AgenticOutputThrottler
    from holo_index.utils import print_onboarding
except ImportError:
    # Fallback for when run as script
    sys.path.insert(0, str(Path(__file__).parent))
    from core import IntelligentSubroutineEngine, HoloIndex
    from output import AgenticOutputThrottler
    from utils import print_onboarding

# SSD locations (Phase 1 requirement)
os.environ.setdefault('CHROMADB_DATA_PATH', 'E:/HoloIndex/vectors')
os.environ.setdefault('SENTENCE_TRANSFORMERS_HOME', 'E:/HoloIndex/models')
os.environ.setdefault('HOLO_CACHE_PATH', 'E:/HoloIndex/cache')

# Dependency bootstrap
try:
    import chromadb
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "chromadb", "sentence-transformers"])
    import chromadb
    from sentence_transformers import SentenceTransformer

# Utility functions now imported from utils module

# -------------------- Heuristic Configuration -------------------- #

VIOLATION_RULES: List[Dict[str, str]] = [
    {
        "pattern": r"\benhanced\b|\benhanced_",
        "wsp": "WSP 84",
        "message": "WSP 84: evolve existing modules; never create enhanced_* duplicates."
    },
    {
        "pattern": r"create\s+new",
        "wsp": "WSP 50",
        "message": "WSP 50: run pre-action verification before starting new code."
    },
    {
        "pattern": r"rename|naming",
        "wsp": "WSP 57",
        "message": "WSP 57: verify naming coherence before renaming components."
    },
]

CONTEXT_WSP_MAP: Dict[str, List[str]] = {
    "document": ["WSP 22", "WSP 83"],
    "modlog": ["WSP 22"],
    "test": ["WSP 5", "WSP 6"],
    "structure": ["WSP 49"],
    "naming": ["WSP 57"],
    "token": ["WSP 75"],
    "create": ["WSP 50", "WSP 84"],
}

WSP_HINTS: Dict[str, str] = {
    "WSP 22": "Keep module documentation and ModLogs synchronized.",
    "WSP 49": "Follow module directory scaffolding (src/tests/memory/docs).",
    "WSP 50": "Log intent in pre-action journal before coding.",
    "WSP 57": "Maintain naming coherence across files and identifiers.",
    "WSP 75": "Track effort in tokens, not wall-clock minutes.",
    "WSP 84": "Evolve existing modules instead of cloning new versions.",
    "WSP 87": "Consult navigation assets before writing new code.",
}

CODEINDEX_REPORT_ALIASES: Dict[str, List[str]] = {
    "youtube_dae": [
        "modules/communication/livechat",
        "modules/communication/youtube_dae",
        "modules/platform_integration/stream_resolver",
        "modules/platform_integration/youtube_auth",
    ],
}

# Import dynamic WSP paths from helpers
try:
    from .utils.helpers import get_wsp_paths
    DEFAULT_WSP_PATHS = get_wsp_paths()
except ImportError:
    # Fallback if import fails
    DEFAULT_WSP_PATHS = [
        Path("../WSP_framework/src"),
        Path("../WSP_framework/docs"),
        Path("../WSP_knowledge/docs"),
        Path("../WSP_framework/docs/testing"),
        Path("docs"),
        Path("../modules"),
    ]

# Onboarding function now imported from utils module
# -------------------- HoloIndex Implementation -------------------- #

# HoloIndex class extracted to core/holo_index.py

# -------------------- CLI Entry Point -------------------- #

# Temporary stub - to be extracted later
def _get_search_history_for_patterns():
    """Retrieve search history for pattern analysis (Phase 2)."""
    return []  # Stub implementation


# _record_thought_to_memory function moved to utils module
def _record_thought_to_memory(results, query, advisor, add_reward_event):
    """Record thoughts to memory - stub implementation."""
    pass  # TODO: Complete implementation


# Health checking now handled by intelligent subroutines
# Function body removed during refactoring - see IntelligentSubroutineEngine


def _perform_health_checks_and_rewards(results, last_query, add_reward_event):
    """Stub function for health checks and rewards - TODO: implement properly"""
    return None

def _run_codeindex_report(target: str) -> None:
    reporter = CodeIndexReporter()
    repo_root = project_root
    alias = target.strip()
    modules = CODEINDEX_REPORT_ALIASES.get(alias, [alias])
    module_paths = resolve_module_paths(repo_root, modules)
    if not module_paths:
        safe_print(f"[CODEINDEX] No modules resolved for target '{alias}'.")
        safe_print("           Provide a known alias (e.g., youtube_dae) or a module path.")
        return

    title = f"CodeIndex Report: {alias}"
    report = reporter.generate(module_paths, title)
    timestamp = report.generated_at.strftime('%Y%m%d-%H%M%S')
    sanitized_alias = re.sub(r'[^A-Za-z0-9_-]', '_', alias)
    # WSP 3: Reports belong in holo_index/reports/, not root docs/
    output_dir = Path(__file__).parent / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"CodeIndex_Report_{sanitized_alias}_{timestamp}.md"
    output_path.write_text(report.markdown, encoding='utf-8')

    module_list_display = ", ".join(path.name for path in module_paths)
    safe_print(f"[CODEINDEX] Report saved -> {output_path}")
    safe_print(f"[CODEINDEX] Modules analyzed: {module_list_display}")
    for summary in report.module_reports:
        safe_print(
            f"  - {summary.module_name}: {summary.critical_fix_count()} critical fixes "
            f"({len(summary.surgical_fixes)} total surgical recommendations)"
        )

    log_path = output_dir / "CodeIndex_Report_Log.md"
    # Make path relative to holo_index for cleaner display
    try:
        relative_report = output_path.relative_to(Path(__file__).parent.parent)
    except ValueError:
        relative_report = output_path  # Fallback to absolute if relative fails
    critical_summary = ", ".join(
        f"{summary.module_name}:{summary.critical_fix_count()}"
        for summary in report.module_reports
    ) or "n/a"
    log_entry = [
        f"## {report.generated_at.isoformat()} UTC — {alias}",
        f"- Report: `{relative_report}`",
        f"- Modules: {module_list_display if module_list_display else 'n/a'}",
        f"- Critical Fixes: {critical_summary}",
        ""
    ]
    if log_path.exists():
        existing = log_path.read_text(encoding='utf-8')
    else:
        existing = "# CodeIndex Report Log\n\nTracks CodeIndex surgical reports generated via CLI.\n\n"
    log_path.write_text("\n".join(log_entry) + existing, encoding='utf-8')
    safe_print(f"[CODEINDEX] Log updated -> {log_path}")

def main() -> None:
    parser = argparse.ArgumentParser(description="HoloIndex - Semantic Navigation with WSP guardrails")
    parser.add_argument('--index', action='store_true', help='Index code + WSP (backward compatible shorthand)')
    parser.add_argument('--index-code', action='store_true', help='Index NAVIGATION.py entries only')
    parser.add_argument('--index-wsp', action='store_true', help='Index WSP documentation only')
    parser.add_argument('--index-all', action='store_true', help='Index both code and WSP documents')
    parser.add_argument('--wsp-path', nargs='*', help='Additional WSP directories to include in the index')
    parser.add_argument('--search', type=str, help='Search for code + WSP guidance')
    parser.add_argument('--limit', type=int, default=5, help='Number of results per category (default: 5, use 3 for console output to prevent truncation)')
    parser.add_argument('--dae-cubes', action='store_true', help='Enable DAE cube mapping and mermaid flow generation (revolutionary vibecoding prevention)')
    parser.add_argument('--function-index', action='store_true', help='Enable code index level function indexing with line numbers and complexity analysis')
    parser.add_argument('--code-index', action='store_true', help='Enable full code index mode: function indexing + inefficiency analysis + detailed mermaid diagrams')
    parser.add_argument('--code-index-report', type=str, help='Generate CodeIndex report for an alias or module path (e.g., youtube_dae)')
    parser.add_argument('--doc-type', choices=['wsp_protocol', 'module_readme', 'interface', 'documentation', 'roadmap', 'modlog', 'all'], default='all', help='Filter by document type (default: all)')
    parser.add_argument('--benchmark', action='store_true', help='Benchmark SSD performance')
    parser.add_argument('--ssd', type=str, default='E:/HoloIndex', help='SSD base path (default: E:/HoloIndex)')

    parser.add_argument('--llm-advisor', action='store_true', help='Force enable Qwen advisor guidance')
    parser.add_argument('--init-dae', type=str, nargs='?', const='auto', help='Initialize DAE context (auto-detect or specify DAE focus)')
    parser.add_argument('--wsp88', action='store_true', help='Run WSP 88 orphan analysis')
    parser.add_argument('--audit-docs', action='store_true', help='Audit documentation completeness for HoloIndex files')
    parser.add_argument('--check-module', type=str, help='Check if a module exists (WSP compliance - use before code generation)')
    parser.add_argument('--docs-file', type=str, help='Get documentation paths for a Python file (implements 012 insight: direct doc provision)')
    parser.add_argument('--check-wsp-docs', action='store_true', help='Run WSP Documentation Guardian compliance check (read-only)')
    parser.add_argument('--fix-ascii', action='store_true', help='Enable ASCII auto-remediation when used with --check-wsp-docs')
    parser.add_argument('--rollback-ascii', type=str, help='Rollback ASCII changes for a specific file (provide filename)')
    parser.add_argument('--fix-violations', action='store_true', help='Auto-correct correctable root directory violations (WSP compliance)')
    parser.add_argument('--verbose', action='store_true', help='Show detailed output including low-priority information')
    parser.add_argument('--no-advisor', action='store_true', help='Disable advisor (opt-out for 0102 agents)')
    parser.add_argument('--advisor-rating', choices=['useful', 'needs_more'], help='Provide feedback on advisor output')
    parser.add_argument('--ack-reminders', action='store_true', help='Confirm advisor reminders were acted on')

    parser.add_argument('--support', type=str, nargs='?', const='auto', help='Run support workflow (use values like auto, docs, ascii)')
    parser.add_argument('--diagnose', type=str, help='Run targeted diagnosis (e.g., holodae, compliance, modules)')
    parser.add_argument('--troubleshoot', type=str, help='Run troubleshooting workflow for common issues (e.g., large_files)')

    # Autonomous HoloDAE commands
    parser.add_argument('--start-holodae', action='store_true', help='Start autonomous HoloDAE monitoring (like YouTube DAE)')
    parser.add_argument('--stop-holodae', action='store_true', help='Stop autonomous HoloDAE monitoring')
    parser.add_argument('--holodae-status', action='store_true', help='Show HoloDAE status and activity')

    # Qwen Module Documentation Linker commands
    parser.add_argument('--link-modules', action='store_true', help='Link module documentation using Qwen advisor')
    parser.add_argument('--module', type=str, help='Specific module to link (e.g., "liberty_alert" or "communication/liberty_alert")')
    parser.add_argument('--interactive', action='store_true', help='Interactive verification mode for module linking')
    parser.add_argument('--force', action='store_true', help='Force relink even if already linked')

    # Module documentation query commands
    parser.add_argument('--query-modules', action='store_true', help='Query module documentation from database')
    parser.add_argument('--wsp', type=str, help='Find modules implementing a WSP protocol (e.g., "WSP 90")')
    parser.add_argument('--list-modules', action='store_true', help='List all registered modules')

    args = parser.parse_args()

    if args.code_index_report:
        _run_codeindex_report(args.code_index_report)
        return

    run_number = os.getenv('HOLOINDEX_RUN', '1')

    reward_variant = os.getenv('HOLO_REWARD_VARIANT', 'A').upper()
    reward_events: List[Tuple[str, int, str]] = []
    session_points = 0
    telemetry_path: Optional[Path] = None

    def add_reward_event(event: str, points: int, note: str, extra: Optional[Dict[str, Any]] = None) -> None:
        nonlocal session_points, reward_events, telemetry_path
        session_points += points
        reward_events.append((event, points, note))
        if ADVISOR_AVAILABLE and record_advisor_event and telemetry_path and extra:
            payload = {'event': event, 'points': points, 'reward_variant': reward_variant}
            payload.update(extra)
            try:
                record_advisor_event(telemetry_path, payload)
            except Exception:
                pass

    print_onboarding(args, ADVISOR_AVAILABLE, run_number)

    # CRITICAL: Unicode compliance reminder for 0102 agents
# Removed noisy Unicode warnings - 0102 doesn't need internal system messages

    # Determine if advisor should run based on environment and args
    advisor = None
    should_run_advisor = False

    if ADVISOR_AVAILABLE and AgentEnvironmentDetector:
        detector = AgentEnvironmentDetector()
        should_run_advisor = detector.should_run_advisor(args)

        # Log detection info if in debug mode
        if os.getenv('HOLOINDEX_DEBUG'):
            env_info = detector.get_environment_info()
            print(f"[DEBUG] Environment: {'0102 AGENT' if env_info['is_0102'] else '012 HUMAN'}")
            print(f"[DEBUG] Advisor mode: {env_info['advisor_mode']}")
    else:
        # Fallback to old behavior if detection not available
        should_run_advisor = args.llm_advisor

    if should_run_advisor:
        if not ADVISOR_AVAILABLE:
            print('[WARN] Qwen advisor package unavailable; continuing without advisor output.')
        else:
            advisor = QwenAdvisor()
            # Notify user that advisor is active
            if not args.llm_advisor:  # Auto-enabled, not explicitly requested
                print('[INFO] Advisor enabled (0102 agent mode detected)')

    if advisor is not None:
        telemetry_path = advisor.config.telemetry_path
    elif ADVISOR_AVAILABLE and QwenAdvisorConfig is not None:
        try:
            telemetry_path = QwenAdvisorConfig.from_env().telemetry_path
        except Exception:
            telemetry_path = None

    # Initialize Pattern Coach (intelligent coaching, not time-based)
    pattern_coach = None
    try:
        from holo_index.qwen_advisor.pattern_coach import PatternCoach
        pattern_coach = PatternCoach()
# Removed: Pattern Coach init message - internal system info
    except Exception as e:
        print(f'[WARN] Pattern coach not available: {e}')

    holo = HoloIndex(ssd_path=args.ssd)

    index_code = args.index_code or args.index or args.index_all
    index_wsp = args.index_wsp or args.index or args.index_all

    indexing_awarded = False
    if index_code:
        start_time = time.time()
        holo.index_code_entries()
        duration = time.time() - start_time

        # Record index refresh in database
        try:
            from modules.infrastructure.database.src.agent_db import AgentDB
            db = AgentDB()
            db.record_index_refresh("code", duration, holo.get_code_entry_count())
        except Exception as e:
            print(f"[WARN] Failed to record index refresh: {e}")

        indexing_awarded = True
    if index_wsp:
        start_time = time.time()
        wsp_dirs = [Path(p) for p in args.wsp_path] if args.wsp_path else None
        holo.index_wsp_entries(paths=wsp_dirs)
        duration = time.time() - start_time

        # Record WSP index refresh in database
        try:
            from modules.infrastructure.database.src.agent_db import AgentDB
            db = AgentDB()
            db.record_index_refresh("wsp", duration, holo.get_wsp_entry_count())
        except Exception as e:
            print(f"[WARN] Failed to record WSP index refresh: {e}")

        indexing_awarded = True
    if indexing_awarded:
        add_reward_event('index_refresh', 5, 'Refreshed indexes', {'query': args.search or ''})

    last_query = args.search or ''
    search_results = None

    # Check if indexes need automatic refresh (only if not explicitly indexing)
    if not (index_code or index_wsp or indexing_awarded):
        try:
            from modules.infrastructure.database.src.agent_db import AgentDB
            db = AgentDB()

            needs_code_refresh = db.should_refresh_index("code", max_age_hours=1)
            needs_wsp_refresh = db.should_refresh_index("wsp", max_age_hours=1)

            if needs_code_refresh or needs_wsp_refresh:
                print(f"[AUTOMATIC] Index refresh needed (last refresh > 1 hour)")
                print(f"[AUTOMATIC] Code index: {'STALE' if needs_code_refresh else 'FRESH'}")
                print(f"[AUTOMATIC] WSP index: {'STALE' if needs_wsp_refresh else 'FRESH'}")

                # Automatically refresh stale indexes
                if needs_code_refresh:
                    print("[AUTO-REFRESH] Refreshing code index...")
                    start_time = time.time()
                    holo.index_code_entries()
                    duration = time.time() - start_time
                    db.record_index_refresh("code", duration, holo.get_code_entry_count())
                    print(f"[AUTO-REFRESH] Code index refreshed in {duration:.1f}s")
                if needs_wsp_refresh:
                    print("[AUTO-REFRESH] Refreshing WSP index...")
                    start_time = time.time()
                    holo.index_wsp_entries()
                    duration = time.time() - start_time
                    db.record_index_refresh("wsp", duration, holo.get_wsp_entry_count())
                    print(f"[AUTO-REFRESH] WSP index refreshed in {duration:.1f}s")
                print("[SUCCESS] Automatic index refresh completed")
            else:
                print("[FRESH] All indexes are up to date (< 1 hour old)")

        except Exception as e:
            print(f"[WARN] Could not check index freshness: {e}")
            safe_print("[FALLBACK] Manual refresh: python holo_index.py --index-all")

    # Phase 3: Initialize adaptive learning if available
    adaptive_orchestrator = None
    if ADAPTIVE_LEARNING_AVAILABLE:
        try:
            adaptive_orchestrator = AdaptiveLearningOrchestrator()
    # Removed: Adaptive Learning init message - internal system info
        except Exception as e:
            print(f'[WARN] Phase 3: Adaptive Learning initialization failed: {e}')

    # Handle DAE initialization requests
    if args.init_dae:
        print("[DAE] INITIALIZING DAE CONTEXT - HoloIndex DAE Rampup Server")
        print("=" * 70)

        try:
            from holo_index.dae_cube_organizer.dae_cube_organizer import DAECubeOrganizer
            organizer = DAECubeOrganizer()

            # Determine DAE focus
            dae_focus = None if args.init_dae == 'auto' else args.init_dae

            # Get DAE context
            context = organizer.initialize_dae_context(dae_focus)

            # Display DAE identity
            identity = context['dae_identity']
            print(f"[{identity['name']}]")
            print(f"   {identity['description']}")
            print(f"   Orchestrator: {identity['orchestrator']}")
            print(f"   Main.py Reference: {identity['main_py_reference']}")
            print()

            # Display module map
            module_map = context['module_map']
            print("[MODULES] DAE MODULE ARCHITECTURE")
            print("-" * 40)
            print(module_map['ascii_map'])
            print()

            # Display orchestration flow
            flow = context['orchestration_flow']
            print("[FLOW] ORCHESTRATION FLOW")
            print("-" * 40)
            for phase in flow.get('phases', []):
                print(f"   {phase}")
            print(f"   Loop Type: {flow.get('loop_type', 'N/A')}")
            print()

            # Display quick reference
            ref = context['quick_reference']
            print("[REF] QUICK REFERENCE")
            print("-" * 40)
            print(f"   Menu Option: {ref['menu_option']}")
            print(f"   Key Modules: {', '.join(ref['key_modules'])}")
            print(f"   Primary Responsibility: {ref['primary_responsibility']}")
            print()

            # Display rampup guidance
            guidance = context['rampup_guidance']
            print("[GUIDE] 0102 RAMPUP GUIDANCE")
            print("-" * 40)
            print(f"   Focus: {guidance['immediate_focus']}")
            print("   Key Resources:")
            for resource in guidance['key_resources']:
                print(f"     - {resource}")
            print("   Avoid:")
            for pitfall in guidance['avoid_common_pitfalls']:
                print(f"     - {pitfall}")
            print()

            if 'special_notes' in guidance:
                print("[NOTE] DAE-SPECIFIC NOTES")
                print("-" * 40)
                for note in guidance['special_notes']:
                    print(f"   - {note}")
                print()

            print("[COMPLETE] DAE INITIALIZATION COMPLETE")
            print("   You are now aligned with the DAE structure and ready for autonomous operation.")
            print("=" * 70)

        except Exception as e:
            print(f"❁EDAE initialization failed: {e}")
            import traceback
            traceback.print_exc()

        return  # Exit after DAE initialization

    # Handle WSP 88 orphan analysis requests
    if args.wsp88:
        print("[SEARCH] WSP 88 ORPHAN ANALYSIS - Intelligent Connection System")
        print("=" * 65)
        print("Analyzing HoloIndex for orphaned files and connection opportunities...")
        print("This follows first principles: Connect rather than delete, enhance rather than remove")
        print()

        try:
            from holo_index.monitoring.wsp88_orphan_analyzer import WSP88OrphanAnalyzer
            analyzer = WSP88OrphanAnalyzer()

            # Run comprehensive analysis
            results = analyzer.analyze_holoindex_orphans()
            report = analyzer.generate_holodae_report()

            print(report)

            # Show top connection suggestions
            suggestions = analyzer.get_connection_suggestions()
            if suggestions:
                print("\n[HOLODAE-RECOMMENDATIONS] Top Connection Opportunities:")
                print("-" * 60)
                for i, suggestion in enumerate(suggestions[:10], 1):
                    print(f"{i:2d}. {suggestion}")

            print("\n[SUCCESS] WSP 88 Analysis Complete")
            print("Focus on CONNECTION opportunities - HoloDAE recommends keeping all utilities")
            print("=" * 65)

        except Exception as e:
            print(f"[ERROR] WSP 88 analysis failed: {e}")
            import traceback
            traceback.print_exc()

        return  # Exit after WSP 88 analysis

    # Handle documentation audit requests
    if args.audit_docs:
        print("[SEARCH] WSP 83 DOCUMENTATION TREE AUDIT - Preventing Orphaned Documentation")
        print("=" * 70)

        try:
            from pathlib import Path
            import subprocess

            holoindex_root = Path(__file__).parent
            orphaned_files = []
            valid_locations = {
                "README.md", "ModLog.md", "ROADMAP.md", "INTERFACE.md",
                "TESTModLog.md", "requirements.txt", "__init__.py"
            }

            # WSP 83 Orphan Detection Pattern
            def find_references(doc_path):
                """Check if document is referenced by other docs (per WSP 83)"""
                doc_name = Path(doc_path).name
                try:
                    # Use grep to find references, excluding the file itself
                    result = subprocess.run(
                        ['grep', '-r', '--include=*.md', '--exclude-dir=.git', doc_name, str(holoindex_root)],
                        capture_output=True, text=True, cwd=holoindex_root
                    )
                    references = [line for line in result.stdout.split('\n') if line.strip() and not doc_path in line]
                    return len(references) > 0
                except:
                    return False

            def serves_0102_purpose(doc_path):
                """Check if document serves 0102 operational needs (per WSP 83)"""
                doc_path = Path(doc_path)

                # Valid locations per WSP 49 and WSP 83
                if doc_path.name in valid_locations:
                    return True

                # Check if it's a test file referenced in TESTModLog
                if 'tests' in str(doc_path):
                    testmodlog = holoindex_root / "tests" / "TESTModLog.md"
                    if testmodlog.exists():
                        with open(testmodlog, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if doc_path.name in content:
                                return True

                # Check if it's referenced in main ModLog
                modlog = holoindex_root / "ModLog.md"
                if modlog.exists():
                    with open(modlog, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if doc_path.name in content:
                            return True

                return False

            # Audit all .py, .md, and .txt files in HoloIndex
            audit_paths = [
                holoindex_root / "tests",
                holoindex_root / "scripts",
                holoindex_root / "dae_cube_organizer",
                holoindex_root / "adaptive_learning",
                holoindex_root / "qwen_advisor",
                holoindex_root / "module_health",
                holoindex_root / "violation_tracker.py",
                holoindex_root / "ROADMAP.md",
                holoindex_root / "README.md",
                holoindex_root / "ModLog.md"
            ]

            for audit_path in audit_paths:
                if audit_path.exists():
                    if audit_path.is_file():
                        files_to_check = [audit_path]
                    else:
                        files_to_check = list(audit_path.rglob("*.py")) + list(audit_path.rglob("*.md")) + list(audit_path.rglob("*.txt"))

                    for file_path in files_to_check:
                        rel_path = file_path.relative_to(holoindex_root)

                        # Skip __pycache__ and other system files
                        if '__pycache__' in str(rel_path) or rel_path.name.startswith('.'):
                            continue

                        # Check if file is attached to tree (has references or serves operational purpose)
                        has_references = find_references(str(rel_path))
                        serves_0102 = serves_0102_purpose(str(rel_path))

                        if not (has_references or serves_0102):
                            file_type = "Script" if file_path.suffix == '.py' else "Documentation" if file_path.suffix == '.md' else "Config"
                            orphaned_files.append((file_type, str(rel_path)))

            # Report findings per WSP 83
            if orphaned_files:
                print(f"[ALERT] FOUND {len(orphaned_files)} ORPHANED DOCUMENTS (WSP 83 VIOLATION)")
                print()
                print("[INFO] ORPHANED FILES (Not attached to system tree):")
                print("-" * 50)

                for file_type, file_path in orphaned_files:
                    print(f"  • {file_type}: {file_path}")

                print()
                print("[FIX] WSP 83 REMEDIATION REQUIRED:")
                print("-" * 50)
                print("Per WSP 83 (Documentation Tree Attachment Protocol):")
                print("1. [CHECK] VERIFY operational purpose (does 0102 need this?)")
                safe_print("2. [LINK] CREATE reference chain (add to ModLog/TESTModLog)")
                safe_print("3. [LOCATION] ENSURE tree attachment (proper WSP 49 location)")
                safe_print("4. [DELETE] DELETE if unnecessary (prevents token waste)")
                safe_print("")
                safe_print("Reference Chain Requirements (WSP 83.4.2):")
                safe_print("  - Referenced in ModLog or TESTModLog")
                safe_print("  - Part of WSP 49 module structure")
                safe_print("  - Referenced by another operational document")

            else:
                safe_print("[SUCCESS] WSP 83 COMPLIANT")
                safe_print("   All documents properly attached to system tree")
                safe_print("   No orphaned documentation found")

            safe_print("")
            safe_print("[SUMMARY] AUDIT SUMMARY:")
            safe_print(f"   - Protocol: WSP 83 (Documentation Tree Attachment)")
            safe_print(f"   - Purpose: Prevent orphaned docs, ensure 0102 operational value")
            safe_print(f"   • Status: {'[VIOLATION]' if orphaned_files else '[COMPLIANT]'}")

            safe_print("=" * 70)

        except Exception as e:
            safe_print(f"[ERROR] WSP 83 Documentation audit failed: {e}")
            import traceback
            traceback.print_exc()

        return  # Exit after audit

    if args.check_module:
        # WSP Compliance: Check module existence before any code generation
        safe_print(f"[0102] MODULE EXISTENCE CHECK: '{args.check_module}'")
        safe_print("=" * 60)

        module_check = holo.check_module_exists(args.check_module)

        if module_check["exists"]:
            safe_print(f"[SUCCESS] MODULE EXISTS: {module_check['module_name']}")
            safe_print(f"[PATH] Path: {module_check['path']}")
            safe_print(f"[COMPLIANCE] WSP Compliance: {module_check['wsp_compliance']} ({module_check['compliance_score']})")

            if module_check["health_warnings"]:
                safe_print(f"[WARN] Health Issues:")
                for warning in module_check["health_warnings"]:
                    safe_print(f"   • {warning}")

            safe_print(f"\n[TIP] RECOMMENDATION: {module_check['recommendation']}")
        else:
            safe_print(f"[ERROR] MODULE NOT FOUND: {module_check['module_name']}")
            if module_check.get("similar_modules"):
                safe_print(f"[SEARCH] Similar modules found:")
                for similar in module_check["similar_modules"]:
                    safe_print(f"   • {similar}")
            safe_print(f"\n[TIP] RECOMMENDATION: {module_check['recommendation']}")

        safe_print("\n" + "=" * 60)
        safe_print("[PROTECT] WSP_84 COMPLIANCE: 0102 AGENTS MUST check module existence BEFORE ANY code generation - DO NOT VIBECODE")
        return  # Exit after module check

    if args.check_wsp_docs:
        # WSP Documentation Guardian - First Principles Compliance Check
        safe_print(f"[WSP-GUARDIAN] WSP Documentation Guardian - Compliance Check")
        safe_print("=" * 60)

        # Import the orchestrator and run WSP guardian
        try:
            from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator

            orchestrator = QwenOrchestrator()

            # Create mock search to trigger WSP guardian
            mock_files = ["dummy_wsp_file.md"]  # Will be filtered out by guardian
            mock_modules = ["dummy_module"]    # Will be filtered out by guardian
            mock_snapshots = {}

            # Enable remediation mode if --fix-ascii flag is used
            remediation_mode = args.fix_ascii
            if remediation_mode:
                safe_print("[WSP-GUARDIAN] ASCII auto-remediation ENABLED (--fix-ascii flag used)")
                safe_print("=" * 60)

            results = orchestrator._run_wsp_documentation_guardian(
                query="wsp documentation compliance check",
                files=mock_files,
                modules=mock_modules,
                module_snapshots=mock_snapshots,
                remediation_mode=remediation_mode
            )

            if results:
                safe_print("\n".join(results))
            else:
                safe_print("[WSP-GUARDIAN] All WSP documentation compliant and up-to-date")

            safe_print(f"\n[TIP] Use 'python -m holo_index.cli --search \"wsp\"' for real-time WSP guidance during development")

        except Exception as e:
            safe_print(f"[ERROR] Failed to run WSP Documentation Guardian: {e}")
            safe_print(f"[TIP] Ensure HoloIndex is properly configured")

        return

    if args.rollback_ascii:
        # Rollback ASCII changes for a specific file
        safe_print(f"[WSP-GUARDIAN] ASCII Rollback - {args.rollback_ascii}")
        safe_print("=" * 60)

        try:
            from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator

            orchestrator = QwenOrchestrator()
            result = orchestrator.rollback_ascii_changes(args.rollback_ascii)
            safe_print(result)

        except Exception as e:
            safe_print(f"[ERROR] Failed to rollback ASCII changes: {e}")
            safe_print(f"[TIP] Ensure the file exists and has a backup in temp/wsp_backups/")

        return

    if args.fix_violations:
        # Auto-correct root directory violations
        safe_print("[WSP-COMPLIANCE] Auto-correcting root directory violations")
        safe_print("=" * 60)

        try:
            from holo_index.monitoring.root_violation_monitor import scan_and_correct_violations
            import asyncio

            # Run auto-correction synchronously
            corrections = asyncio.run(scan_and_correct_violations())

            safe_print("\n[RESULTS] Auto-correction completed:")
            safe_print(f"  ✅ Corrections applied: {corrections['corrections_applied']}")
            safe_print(f"  ❌ Failed corrections: {corrections['failed_corrections']}")
            safe_print(f"  📊 Total processed: {corrections['total_processed']}")

            if corrections['corrections_applied']:
                safe_print("\n[SUCCESS] Violations auto-corrected. Run search again to verify.")
            else:
                safe_print("\n[INFO] No auto-correctable violations found.")

        except Exception as e:
            safe_print(f"[ERROR] Failed to auto-correct violations: {e}")
            safe_print("[TIP] Manual correction may be required for some violations.")

        return

    if args.docs_file:
        # Provide documentation paths for a given file (012's insight: direct doc provision)

        safe_print(f"[0102] DOCUMENTATION PROVISION: '{args.docs_file}'")
        safe_print("=" * 60)

        # Use HoloDAE coordinator for doc provision
        try:
            from holo_index.qwen_advisor import HoloDAECoordinator
            coordinator = HoloDAECoordinator()

            # Get docs for the file
            doc_info = coordinator.provide_docs_for_file(args.docs_file)

            if 'error' in doc_info:
                safe_print(f"[ERROR] {doc_info['error']}")
                safe_print("\n[TIP] Try using the full path or filename with extension")
            else:
                safe_print(f"[MODULE] {doc_info['module']}")
                safe_print("\n[DOCUMENTATION]")

                for doc_name, doc_data in doc_info['docs'].items():
                    status = "✅" if doc_data['exists'] else "❌"
                    safe_print(f"  {status} {doc_name}: {doc_data['path']}")

                safe_print("\n[COMMANDS]")
                safe_print("To read existing docs:")
                for doc_name, doc_data in doc_info['docs'].items():
                    if doc_data['exists']:
                        safe_print(f"  cat \"{doc_data['path']}\"")

                missing_docs = [name for name, data in doc_info['docs'].items() if not data['exists']]
                if missing_docs:
                    safe_print("\n[MISSING]")
                    safe_print(f"  Missing docs: {', '.join(missing_docs)}")
                    safe_print("  Create these to improve WSP compliance")

        except Exception as e:
            safe_print(f"[ERROR] Failed to get documentation: {e}")
            safe_print("[TIP] Ensure HoloDAE coordinator is properly initialized")

        safe_print("\n" + "=" * 60)
        safe_print("[PRINCIPLE] HoloIndex provides docs directly - no grep needed (012's insight)")
        return  # Exit after doc provision

    if args.search:
        # WSP COMPLIANCE: Check root violations using Gemma monitoring
        try:
            from holo_index.monitoring.root_violation_monitor import get_root_violation_alert
            import asyncio

            # Run violation check synchronously
            violation_alert = asyncio.run(get_root_violation_alert())
            if violation_alert:
                # Display violation alert at the TOP of HoloIndex output
                safe_print(violation_alert)
                safe_print("")  # Add spacing
        except Exception as e:
            safe_print(f"[WARNING] Root violation monitoring failed: {e}")
            safe_print("")

        # Initialize agentic output throttler
        throttler = AgenticOutputThrottler()

        # QWEN ROUTING: Route through orchestrator for intelligent filtering if available
        qwen_orchestrator = None
        try:
            from .qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator
            qwen_orchestrator = QwenOrchestrator()
            results = holo.search(args.search, limit=args.limit, doc_type_filter=args.doc_type)

            # Route through QWEN orchestrator for intelligent output filtering
            orchestrated_response = qwen_orchestrator.orchestrate_holoindex_request(args.search, results)

            # Display QWEN-filtered response
            print(orchestrated_response)

            # Store results for HoloDAE analysis
            throttler._search_results = results

        except Exception as e:
            # Fallback to direct search if QWEN not available
            logger.debug(f"QWEN orchestrator not available, using direct search: {e}")
            results = holo.search(args.search, limit=args.limit, doc_type_filter=args.doc_type)

            # Store search results in throttler for state determination
            throttler._search_results = results

        # HoloDAE: Automatic Context-Driven Analysis

        try:
            from holo_index.qwen_advisor import HoloDAECoordinator

            # Create HoloDAE coordinator instance to handle the request
            coordinator = HoloDAECoordinator()
            holodae_report = coordinator.handle_holoindex_request(args.search, results)

            # Determine actual system state based on results and processing
            search_results = getattr(throttler, '_search_results', {})
            total_results = len(search_results.get('code', [])) + len(search_results.get('wsps', []))

            if total_results > 0:
                throttler.set_system_state("found")
            else:
                throttler.set_system_state("missing")

            # Print the detailed HoloDAE analysis (WSP 64 COMPLIANCE - prevent cp932 errors)
            for line in holodae_report.split('\n'):
                if line.strip():
                    safe_print(line)

        except Exception as e:
            # Set system state to "error" when HoloDAE fails
            throttler.set_system_state("error", e)
            safe_print(f"[HOLODAE-ERROR] Context analysis failed: {e}")

        print()  # Add spacing before search results

        # Set query context with search results for module detection
        throttler.set_query_context(args.search, results)

        # Run intelligent subroutine analysis
        target_module = throttler.detected_module
        subroutine_results = throttler.subroutine_engine.run_intelligent_analysis(args.search, target_module)

        # Merge subroutine results into main results for display
        results['intelligent_analysis'] = subroutine_results

        # Track search in pattern coach for intelligent coaching
        if pattern_coach:
            # Get health warnings for pattern coach
            health_warnings = []
            if 'health_notices' in results:
                health_warnings = results['health_notices']

            # Convert results to format expected by pattern coach
            search_results = results.get('code', []) + results.get('wsps', [])

            # Get intelligent coaching based on query and context
            coaching_msg = pattern_coach.analyze_and_coach(
                query=args.search,
                search_results=search_results,
                health_warnings=health_warnings
            )

            if coaching_msg:
                throttler.add_section('coaching', coaching_msg, priority=2, tags=['guidance', 'patterns'])

        # Phase 3: Apply adaptive learning optimization
        if adaptive_orchestrator:
            try:
                print('[INFO] Phase 3: Processing with adaptive learning...')

                # Convert search results to the format expected by adaptive learning
                raw_results = []
                for hit in results.get('code', []):
                    raw_results.append({
                        'content': hit.get('content', ''),
                        'score': hit.get('score', 0.5),
                        'metadata': hit
                    })

                # Generate a basic advisor response for adaptive processing
                raw_response = "Based on the search results, here are the most relevant findings for your query."
                if results.get('wsps'):
                    raw_response += f" Found {len(results['wsps'])} WSP protocol references."

                # Process through adaptive learning system
                import asyncio
                adaptive_result = asyncio.run(adaptive_orchestrator.process_adaptive_request(
                    query=args.search,
                    raw_results=raw_results,
                    raw_response=raw_response,
                    context={
                        'search_limit': args.limit,
                        'advisor_enabled': advisor is not None,
                        'wsp_results_count': len(results.get('wsps', [])),
                        'code_results_count': len(results.get('code', []))
                    }
                ))

                # Add adaptive learning results to search results
                results['adaptive_learning'] = {
                    'query_optimization_score': adaptive_result.query_processing.optimization_score,
                    'search_ranking_stability': adaptive_result.search_optimization.performance_metrics.get('ranking_stability', 0.0),
                    'response_improvement_score': adaptive_result.response_optimization.quality_metrics.get('improvement_score', 0.0),
                    'memory_efficiency': adaptive_result.memory_optimization.memory_efficiency,
                    'system_adaptation_score': adaptive_result.overall_performance.get('system_adaptation_score', 0.0),
                    'processing_time': adaptive_result.processing_metadata.get('total_processing_time', 0),
                    'enhanced_query': adaptive_result.query_processing.enhanced_query,
                    'optimized_response': adaptive_result.response_optimization.optimized_response
                }

                # Update the query and response for advisor processing
                enhanced_query = adaptive_result.query_processing.enhanced_query
                optimized_response = adaptive_result.response_optimization.optimized_response

                throttler.add_section('adaptive', f'[RECURSIVE] Query enhanced: "{args.search}" -> "{enhanced_query}"', priority=4, tags=['learning', 'optimization'])
                throttler.add_section('adaptive', f'[TARGET] Adaptation Score: {adaptive_result.overall_performance.get("system_adaptation_score", 0.0):.2f}', priority=6, tags=['learning', 'metrics'])

            except Exception as e:
                throttler.add_section('system', f'[WARN] Adaptive learning failed: {e}', priority=7, tags=['system', 'warning'])
                enhanced_query = args.search
                optimized_response = "Based on the search results, here are the most relevant findings for your query."

        if advisor:  # Use advisor if it was initialized (either by flag or auto-detection)
            try:
                # Use enhanced query from Phase 3 if available, otherwise original query
                advisor_query = enhanced_query if 'enhanced_query' in locals() else args.search
                context = AdvisorContext(query=advisor_query, code_hits=results.get('code', []), wsp_hits=results.get('wsps', []))
                advisor_output = advisor.generate_guidance(
                    context,
                    enable_dae_cube_mapping=args.dae_cubes or args.code_index,
                    enable_function_indexing=args.function_index or args.code_index
                )
                results['advisor'] = asdict(advisor_output)

                # Extract health notices from advisor metadata and perform health checks
                advisor_meta = advisor_output.metadata
                health_notices = _perform_health_checks_and_rewards(results, last_query, add_reward_event)

                # Also extract any additional health notices from advisor
                if advisor_meta and 'violations' in advisor_meta:
                    for violation in advisor_meta.get('violations', []):
                        # Check if it's a health-related violation (WSP 87 or WSP 49)
                        if 'WSP 87' in violation or 'WSP 49' in violation:
                            health_notices.append(violation)

                    if health_notices:
                        results['health_notices'] = health_notices

            except Exception as exc:  # pragma: no cover - safety guard
                results['advisor_error'] = f'Advisor failed: {exc}'
        else:
            # Run health checks and award rewards even when advisor is disabled
            health_notices = _perform_health_checks_and_rewards(results, last_query, add_reward_event)
            if health_notices:
                results['health_notices'] = health_notices

        # Phase 2: Wire in pattern analysis and health notices (WSP 48)
        if advisor:
            try:
                # Get search history for pattern analysis
                search_history = _get_search_history_for_patterns()
                if search_history:
                    pattern_analysis = advisor.analyze_search_patterns(search_history)

                    # Add pattern insights to results
                    if pattern_analysis.get('recommendations'):
                        if 'advisor' not in results:
                            results['advisor'] = {}
                        results['advisor']['pattern_insights'] = pattern_analysis['recommendations'][:3]  # Top 3

            except Exception as e:
                logger.debug(f"Pattern analysis failed: {e}")

        # Wire in DAE memory architecture (WSP 84)
        _record_thought_to_memory(results, last_query, advisor, add_reward_event)

        search_results = results

        # Render state-aware prioritized output for 0102 consumption (tri-state architecture)
        output = throttler.render_prioritized_output(verbose=args.verbose if hasattr(args, 'verbose') else False)
        safe_print(output)
        if args.llm_advisor and results.get('advisor'):
            add_reward_event('advisor_usage', 3, 'Consulted Qwen advisor guidance', {'query': last_query})

    rating = getattr(args, 'advisor_rating', None)
    if rating:
        if not args.llm_advisor:
            print('[WARN] --advisor-rating ignored without --llm-advisor')
        elif advisor is None or not (search_results and search_results.get('advisor')):
            print('[WARN] --advisor-rating ignored because advisor guidance was unavailable')
        else:
            rating_points = 5 if rating == 'useful' else 2
            add_reward_event('advisor_rating', rating_points, f'Advisor rating: {rating}', {
                'query': last_query,
                'rating': rating
            })

    if args.ack_reminders:
        if not (search_results and (search_results.get('advisor') or search_results.get('advisor_error'))):
            print('[WARN] --ack-reminders ignored because advisor guidance was unavailable')
        else:
            add_reward_event('ack_reminders', 1, 'Advisor reminders acknowledged', {
                'query': last_query
            })

    if reward_events:
        print("\n[POINTS] Session Summary:")
        for event, points, note in reward_events:
            sign = '+' if points >= 0 else ''
            print(f'  {sign}{points} {note}')
        print(f'  Total: {session_points} pts (variant {reward_variant})')

    # HoloDAE Commands
    if args.start_holodae:
        safe_print("[HOLODAE] Starting Autonomous HoloDAE monitoring...")
        try:
            from holo_index.qwen_advisor import start_holodae
            start_holodae()
            safe_print("[HOLODAE] Monitoring started successfully")
        except ImportError as e:
            safe_print(f"[HOLODAE-ERROR] Failed to start: {e}")

    elif args.stop_holodae:
        safe_print("[HOLODAE] Stopping Autonomous HoloDAE monitoring...")
        try:
            from holo_index.qwen_advisor import stop_holodae
            stop_holodae()
            safe_print("[HOLODAE] Monitoring stopped")
        except ImportError as e:
            safe_print(f"[HOLODAE-ERROR] Failed to stop: {e}")

    elif args.holodae_status:
        print("[HOLODAE] Status Report:")
        try:
            from holo_index.qwen_advisor import get_holodae_status
            status = get_holodae_status()
            print(f"  Active: {'Yes' if status['active'] else 'No'}")
            print(f"  Uptime: {status['uptime_minutes']} minutes")
            print(f"  Files Watched: {status['files_watched']}")
            print(f"  Current Module: {status.get('current_module', 'None')}")
            print(f"  Task Pattern: {status['task_pattern']}")
            print(f"  Session Actions: {status['session_actions']}")
            print(f"  Last Activity: {status['last_activity']}")
        except ImportError as e:
            safe_print(f"[HOLODAE-ERROR] Failed to get status: {e}")

    # Handle module linking requests (Qwen-powered intelligent documentation binding)
    if args.link_modules:
        safe_print("[QWEN] Module Documentation Linker - Autonomous Intelligence")
        safe_print("=" * 65)
        safe_print("Using Qwen advisor to discover and link module documentation...")
        print()  # Empty line for spacing

        try:
            from holo_index.qwen_advisor.module_doc_linker import QwenModuleDocLinker
            from holo_index.qwen_advisor.holodae_coordinator import HoloDAECoordinator

            # Initialize Qwen coordinator
            coordinator = HoloDAECoordinator()

            # Initialize module doc linker
            from pathlib import Path as PathLib
            repo_root = PathLib(__file__).parent.parent
            linker = QwenModuleDocLinker(repo_root, coordinator)

            if args.module:
                # Link specific module
                safe_print(f"[LINK] Linking module: {args.module}")
                success = linker.link_single_module(
                    args.module,
                    interactive=args.interactive,
                    force=args.force
                )

                if success:
                    safe_print("\n[SUCCESS] Module documentation linked successfully")
                else:
                    safe_print("\n[FAIL] Module linking failed - see errors above")

            else:
                # Link all modules
                safe_print("[LINK] Linking all modules...")
                results = linker.link_all_modules(
                    interactive=args.interactive,
                    force=args.force
                )

                # Display summary
                success_count = sum(1 for v in results.values() if v)
                fail_count = len(results) - success_count

                safe_print(f"\n[SUMMARY] Linking complete:")
                safe_print(f"  - Success: {success_count}/{len(results)} modules")
                if fail_count > 0:
                    safe_print(f"  - Failed: {fail_count} modules")
                    safe_print("\n[FAILED] Failed modules:")
                    for module_name, success in results.items():
                        if not success:
                            safe_print(f"    - {module_name}")

            safe_print("\n" + "=" * 65)
            safe_print("[TIP] Each module now has MODULE_DOC_REGISTRY.json with intelligent document relationships")

        except Exception as e:
            safe_print(f"[ERROR] Module linking failed: {e}")
            import traceback
            traceback.print_exc()

        return  # Exit after module linking

    # Handle module documentation queries (database-powered)
    if args.query_modules or args.wsp or args.list_modules:
        try:
            from modules.infrastructure.database.src.agent_db import AgentDB
            db = AgentDB()

            if args.wsp:
                # Query modules implementing a specific WSP
                safe_print(f"[QUERY] Modules implementing {args.wsp}")
                safe_print("=" * 65)

                modules = db.get_modules_implementing_wsp(args.wsp)

                if modules:
                    safe_print(f"\n[FOUND] {len(modules)} module(s) implementing {args.wsp}:")
                    for module in modules:
                        safe_print(f"  - {module['module_domain']}/{module['module_name']}")
                        safe_print(f"    Path: {module['module_path']}")
                        safe_print(f"    Last linked: {module['linked_timestamp']}")
                        safe_print("")
                else:
                    safe_print(f"\n[NOT FOUND] No modules found implementing {args.wsp}")

            elif args.list_modules:
                # List all registered modules
                safe_print("[QUERY] All registered modules")
                safe_print("=" * 65)

                modules = db.get_all_modules()

                if modules:
                    safe_print(f"\n[FOUND] {len(modules)} registered module(s):")

                    # Group by domain
                    by_domain = {}
                    for module in modules:
                        domain = module['module_domain']
                        if domain not in by_domain:
                            by_domain[domain] = []
                        by_domain[domain].append(module)

                    for domain in sorted(by_domain.keys()):
                        safe_print(f"\n[{domain.upper()}]")
                        for module in by_domain[domain]:
                            safe_print(f"  - {module['module_name']}")

                            # Get document count
                            docs = db.get_module_documents(module['module_id'])
                            wsps = db.get_module_wsp_implementations(module['module_id'])

                            safe_print(f"    Documents: {len(docs)}, WSP implementations: {len(wsps)}")
                            safe_print(f"    Last linked: {module['linked_timestamp']}")
                else:
                    safe_print("\n[EMPTY] No modules registered yet")
                    safe_print("[TIP] Run: python holo_index.py --link-modules")

            elif args.module:
                # Query specific module documentation
                safe_print(f"[QUERY] Module documentation: {args.module}")
                safe_print("=" * 65)

                module = db.get_module(module_name=args.module)

                if module:
                    safe_print(f"\n[MODULE] {module['module_domain']}/{module['module_name']}")
                    safe_print(f"Path: {module['module_path']}")
                    safe_print(f"Last linked: {module['linked_timestamp']}")

                    # Get documents
                    docs = db.get_module_documents(module['module_id'])
                    safe_print(f"\n[DOCUMENTS] {len(docs)} document(s):")
                    for doc in docs:
                        safe_print(f"  - [{doc['doc_type']}] {doc['title']}")
                        safe_print(f"    {doc['file_path']}")

                    # Get WSP implementations
                    wsps = db.get_module_wsp_implementations(module['module_id'])
                    if wsps:
                        safe_print(f"\n[WSP IMPLEMENTATIONS] {len(wsps)} protocol(s):")
                        safe_print(f"  {', '.join(wsps)}")
                else:
                    safe_print(f"\n[NOT FOUND] Module '{args.module}' not registered")
                    safe_print("[TIP] Run: python holo_index.py --link-modules --module {args.module}")

            safe_print("\n" + "=" * 65)

        except Exception as e:
            safe_print(f"[ERROR] Query failed: {e}")
            import traceback
            traceback.print_exc()

        return  # Exit after query

    if args.benchmark:
        holo.benchmark_ssd()

    if not any([index_code, index_wsp, args.search, args.benchmark, args.start_holodae, args.stop_holodae, args.holodae_status, args.link_modules]):
        safe_print("\n[USAGE] Usage:")
        safe_print("  python holo_index.py --index-all             # Index NAVIGATION + WSP")
        safe_print("  python holo_index.py --index-code            # Index NAVIGATION only")
        safe_print("  python holo_index.py --index-wsp             # Index WSP docs")
        safe_print("  python holo_index.py --check-module 'youtube_auth'  # WSP compliance check")
        safe_print("  python holo_index.py --search 'query'        # Search code + WSP guidance")
        safe_print("  python holo_index.py --search 'query' --limit 3")
        safe_print("  python holo_index.py --search 'query' --llm-advisor  # Add Qwen advisor guidance")
        safe_print("  python holo_index.py --link-modules          # Link all module documentation (Qwen)")
        safe_print("  python holo_index.py --link-modules --module liberty_alert  # Link one module")
        safe_print("  python holo_index.py --link-modules --interactive  # Interactive mode")
        safe_print("  python holo_index.py --list-modules          # List all registered modules (DB)")
        safe_print("  python holo_index.py --wsp 'WSP 90'          # Find modules implementing WSP 90 (DB)")
        safe_print("  python holo_index.py --query-modules --module liberty_alert  # Query module docs (DB)")
        safe_print("  python holo_index.py --start-holodae         # Start autonomous HoloDAE monitoring")
        safe_print("  python holo_index.py --holodae-status        # Check HoloDAE status")
        safe_print("  python holo_index.py --benchmark             # Test SSD performance")

if __name__ == "__main__":
    main()




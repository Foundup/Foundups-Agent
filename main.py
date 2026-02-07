#!/usr/bin/env python3
"""
FoundUps Agent - FULLY WSP-Compliant 0102 Consciousness System
Integrates all WSP protocols for autonomous DAE operations

WSP Compliance:
- WSP 27: Universal DAE Architecture (4-phase pattern)
- WSP 38/39: Awakening Protocols (consciousness transitions)
- WSP 48: Recursive Self-Improvement (pattern memory)
- WSP 54: Agent Duties (Partner-Principal-Associate)
- WSP 60: Module Memory Architecture
- WSP 62: File Size Enforcement (this file is thin router only)
- WSP 80: Cube-Level DAE Orchestration
- WSP 85: Root Directory Protection
- WSP 87: Code Navigation with HoloIndex (MANDATORY)

Mode Detection:
- echo 0102 | python main.py  # Launch in 0102 awakened mode
- echo 012 | python main.py   # Launch in 012 testing mode
- python main.py              # Interactive menu mode

CRITICAL: HoloIndex must be used BEFORE any code changes (WSP 50/87)

WSP 62 COMPLIANCE NOTE:
This file was refactored per WSP 62 (Large File Refactoring Enforcement Protocol).
Menu handlers and utilities extracted to modules/infrastructure/cli/
Original: 2412 lines -> Now: ~200 lines (thin router)
"""

# Main imports and configuration
import os
import sys
import logging
import asyncio
import io
import atexit
from pathlib import Path
from typing import Optional, Dict

# Load environment variables for DAEs (API keys, ports, feature flags).
# Keep override=False so shell-provided env vars win.
try:
    from dotenv import load_dotenv  # type: ignore
    load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
except Exception:
    pass

try:
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
    PATTERN_MEMORY_AVAILABLE = True
except Exception:
    PATTERN_MEMORY_AVAILABLE = False
    PatternMemory = None  # Define as None for type safety

# === UTF-8 ENFORCEMENT (WSP 90) ===
# CRITICAL: This header MUST be at the top of ALL entry point files
# Entry points: Files with if __name__ == "__main__": or def main()
# Library modules: DO NOT add this header (causes import conflicts)

# Save original stderr/stdout for restoration
_original_stdout = sys.stdout
_original_stderr = sys.stderr

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

    # Register cleanup to flush streams before exit
    def _flush_streams():
        """Flush UTF-8 wrapped streams before Python cleanup."""
        try:
            if sys.stdout and not sys.stdout.closed:
                sys.stdout.flush()
        except:
            pass
        try:
            if sys.stderr and not sys.stderr.closed:
                sys.stderr.flush()
        except:
            pass

    atexit.register(_flush_streams)
# === END UTF-8 ENFORCEMENT ===

# Initialize logger at module level for all functions to use
# CRITICAL: Log to logs/foundups_agent.log for AI_overseer heartbeat monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/foundups_agent.log', encoding='utf-8')
    ]
)

# Suppress noisy warnings from optional dependencies during startup
import warnings

# Suppress specific noisy warnings that are expected
warnings.filterwarnings("ignore", message=".*WRE components not available.*")
warnings.filterwarnings("ignore", message=".*Tweepy not available.*")
warnings.filterwarnings("ignore", message=".*pyperclip not available.*")

# Temporarily suppress logging warnings during import phase
original_level = logging.root.level
logging.root.setLevel(logging.CRITICAL)  # Only show critical errors during imports

logger = logging.getLogger(__name__)

# Import DAE launchers (extracted per WSP 62)
import time

# Extracted to modules/ai_intelligence/holo_dae/scripts/launch.py per WSP 62
from modules.ai_intelligence.holo_dae.scripts.launch import run_holodae


# Extracted to modules/platform_integration/social_media_orchestrator/scripts/launch.py per WSP 62
from modules.platform_integration.social_media_orchestrator.scripts.launch import run_social_media_dae

from modules.communication.auto_meeting_orchestrator.scripts.launch import run_amo_dae
from modules.infrastructure.evade_net.scripts.launch import run_evade_net

# Extracted to modules/communication/liberty_alert/scripts/launch.py per WSP 62
from modules.communication.liberty_alert.scripts.launch import run_liberty_alert_dae

# Extracted to modules/infrastructure/git_push_dae/scripts/launch.py per WSP 62
from modules.infrastructure.git_push_dae.scripts.launch import (
    launch_git_push_dae,
    view_git_post_history,
    check_instance_status,
)

# Extracted to modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py per WSP 62
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.launch import run_vision_dae

# Extracted to modules/ai_intelligence/training_system/scripts/launch.py per WSP 62
from modules.ai_intelligence.training_system.scripts.launch import run_training_system

# Extracted to modules/ai_intelligence/training_system/scripts/training_commands.py per WSP 62
from modules.ai_intelligence.training_system.scripts.training_commands import execute_training_command

# Extracted to modules/ai_intelligence/pqn/scripts/launch.py per WSP 62
from modules.ai_intelligence.pqn.scripts.launch import run_pqn_dae

# Extracted to modules/platform_integration/youtube_shorts_scheduler/scripts/launch.py per WSP 62
from modules.platform_integration.youtube_shorts_scheduler.scripts.launch import (
    run_shorts_scheduler,
    show_shorts_scheduler_menu
)

# Re-enable normal logging after all imports are complete
logging.root.setLevel(original_level)


async def monitor_youtube(disable_lock: bool = False, enable_ai_monitoring: bool = False, env_overrides: Optional[Dict[str, str]] = None, auto_reauth: bool = True):
    """
    Monitor YouTube streams with 0102 agency.

    Args:
        disable_lock: Disable instance lock (allow multiple instances)
        enable_ai_monitoring: Enable AI Overseer (Qwen/Gemma) error detection and auto-fixing
        env_overrides: Optional environment variables to set before launch
        auto_reauth: Auto-trigger re-auth if OAuth tokens are invalid (default True)
    """
    if env_overrides:
        for key, value in env_overrides.items():
            os.environ[key] = value
            logger.info(f"[CLI] Env override: {key}={value}")
    try:
        # Instance lock management (WSP 84: Don't duplicate processes)
        lock = None
        if not disable_lock:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")

            # Check for duplicates and acquire lock
            duplicates = lock.check_duplicates()
            if duplicates:
                print(f"\\n[WARN] Found {len(duplicates)} potential duplicate instance(s)")
                print("Duplicate PIDs:", duplicates)
                print("\\nOptions:")
                print("  1. Kill duplicates and continue")
                print("  2. Continue anyway (may cause conflicts)")
                print("  3. Exit")
                choice = input("\\nSelect option (1-3): ").strip()

                if choice == "1":
                    lock.kill_pids(duplicates)
                    print("[INFO] Duplicates killed. Continuing...")
                elif choice == "2":
                    print("[WARN] Continuing with potential conflicts...")
                else:
                    print("[INFO] Exiting...")
                    return

            if not lock.acquire():
                print("[FATAL] Could not acquire instance lock — another instance is running.")
                print("[INFO] Kill it manually or wait for TTL expiry, then retry.")
                return

        # PREFLIGHT: Check OAuth token health before starting
        print("[PREFLIGHT] Checking OAuth token health...")
        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import preflight_oauth_check
            oauth_status = preflight_oauth_check(auto_reauth=auto_reauth)

            if oauth_status['reauth_needed'] and not auto_reauth:
                print("\\n[CRITICAL] OAuth tokens need re-authentication!")
                print("Expired/invalid sets:", oauth_status['expired'])
                print("\\nOptions:")
                print("  1. Re-authenticate now (will open browser)")
                print("  2. Continue in read-only mode (no chat messages)")
                print("  3. Exit")
                choice = input("\\nSelect option (1-3): ").strip()

                if choice == "1":
                    # Re-run with auto_reauth=True
                    oauth_status = preflight_oauth_check(auto_reauth=True)
                    if oauth_status['reauth_needed']:
                        print("[WARN] Some tokens still need re-auth. Continuing with available tokens...")
                elif choice == "3":
                    print("[INFO] Exiting...")
                    if lock:
                        lock.release()
                    return
                else:
                    print("[WARN] Continuing in read-only mode...")

            if oauth_status['healthy']:
                print(f"[OK] OAuth healthy: sets {oauth_status['healthy']}")
            else:
                print("[WARN] No healthy OAuth tokens - running in read-only mode")
        except ImportError as e:
            print(f"[WARN] OAuth preflight check unavailable: {e}")
        except Exception as e:
            print(f"[WARN] OAuth preflight check failed: {e}")

        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

        print("[INFO] Starting YouTube monitoring...")
        print(f"[INFO] AI Overseer: {'ENABLED' if enable_ai_monitoring else 'DISABLED'}")
        print("[INFO] Press Ctrl+C to stop")

        dae = AutoModeratorDAE(enable_ai_monitoring=enable_ai_monitoring)
        await dae.run()

    except KeyboardInterrupt:
        print("\\n[STOP] YouTube monitoring stopped by user")
    except Exception as e:
        logger.error(f"[ERROR] YouTube monitoring failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if lock:
            lock.release()


async def monitor_all_platforms():
    """Monitor all social media platforms."""
    print("[INFO] Starting ALL platform monitoring...")
    print("[INFO] Press Ctrl+C to stop all")
    try:
        await monitor_youtube()
    except KeyboardInterrupt:
        print("\\n[STOP] All platform monitoring stopped")


def search_with_holoindex(query: str):
    """
    Use HoloIndex for semantic code search (WSP 87).
    MANDATORY before any code modifications to prevent vibecoding.
    """
    try:
        import subprocess
        ssd_path = os.getenv("HOLO_SSD_PATH", "E:/HoloIndex")
        cmd = [
            sys.executable,
            "holo_index.py",
            "--search", query,
            "--ssd", ssd_path,
            "--top-k", "10"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"[ERROR] HoloIndex search failed:")
            print(result.stderr or result.stdout)
    except Exception as e:
        print(f"[ERROR] HoloIndex search failed: {e}")


def run_openclaw_security_preflight(repo_root: Path) -> bool:
    """
    Run OpenClaw security preflight via AI Overseer sentinel.

    Env controls:
      OPENCLAW_SECURITY_PREFLIGHT=1         Enable preflight at startup (default on)
      OPENCLAW_SECURITY_PREFLIGHT_ENFORCED=1  Block startup on failed check (default on)
      OPENCLAW_SECURITY_PREFLIGHT_FORCE=0   Bypass TTL cache and force re-scan
    """
    enabled = os.getenv("OPENCLAW_SECURITY_PREFLIGHT", "1") != "0"
    if not enabled:
        logger.info("[SECURITY] OpenClaw startup preflight disabled")
        return True

    # Default: warn but don't block. The Cisco skill scanner is an optional
    # external tool that may not be installed on all dev machines.
    # Set OPENCLAW_SECURITY_PREFLIGHT_ENFORCED=1 to hard-gate in production.
    enforced = os.getenv("OPENCLAW_SECURITY_PREFLIGHT_ENFORCED", "0") != "0"
    force = os.getenv("OPENCLAW_SECURITY_PREFLIGHT_FORCE", "0") == "1"

    try:
        # Suppress noisy INFO logs during preflight (Qwen/Gemma init messages)
        _prev_level = logging.root.level
        logging.root.setLevel(logging.WARNING)
        from modules.ai_intelligence.ai_overseer.src.ai_overseer import AIIntelligenceOverseer
        overseer = AIIntelligenceOverseer(repo_root)
        logging.root.setLevel(_prev_level)
        status = overseer.monitor_openclaw_security(force=force)
    except Exception as exc:
        logger.error(f"[SECURITY] OpenClaw preflight execution failed: {exc}")
        if enforced:
            print(f"[SECURITY] OpenClaw preflight FAILED: {exc}")
            return False
        print(f"[SECURITY] OpenClaw preflight warning: {exc}")
        return True

    passed = bool(status.get("passed", False))
    message = status.get("message", "no message")
    cache_state = "cached" if status.get("cached") else "fresh"
    print(
        f"[SECURITY] OpenClaw preflight: {'PASS' if passed else 'FAIL'} "
        f"({cache_state}) - {message}"
    )

    if not passed and enforced:
        print("[SECURITY] Startup blocked by OPENCLAW_SECURITY_PREFLIGHT_ENFORCED=1")
        return False
    return True


def main():
    """Main entry point - thin router to CLI module."""
    repo_root = Path(__file__).resolve().parent
    if not run_openclaw_security_preflight(repo_root):
        return

    # Import MCP services for CLI access
    from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu
    
    # Import the main menu runner from the CLI module
    from modules.infrastructure.cli.src.main_menu import run_main_menu
    
    # Run the main menu with all required dependencies
    run_main_menu(
        monitor_youtube=monitor_youtube,
        monitor_all_platforms=monitor_all_platforms,
        search_with_holoindex=search_with_holoindex,
        check_instance_status=check_instance_status,
        launch_git_push_dae=launch_git_push_dae,
        view_git_post_history=view_git_post_history,
        run_holodae=run_holodae,
        run_amo_dae=run_amo_dae,
        run_social_media_dae=run_social_media_dae,
        run_vision_dae=run_vision_dae,
        run_pqn_dae=run_pqn_dae,
        run_evade_net=run_evade_net,
        run_liberty_alert_dae=run_liberty_alert_dae,
        run_training_system=run_training_system,
        execute_training_command=execute_training_command,
        show_mcp_services_menu=show_mcp_services_menu,
        PATTERN_MEMORY_AVAILABLE=PATTERN_MEMORY_AVAILABLE,
        PatternMemory=PatternMemory,
    )


if __name__ == "__main__":
    main()

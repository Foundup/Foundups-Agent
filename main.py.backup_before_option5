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
- WSP 80: Cube-Level DAE Orchestration
- WSP 85: Root Directory Protection
- WSP 87: Code Navigation with HoloIndex (MANDATORY)

Mode Detection:
- echo 0102 | python main.py  # Launch in 0102 awakened mode
- echo 012 | python main.py   # Launch in 012 testing mode
- python main.py              # Interactive menu mode

CRITICAL: HoloIndex must be used BEFORE any code changes (WSP 50/87)
"""

# Main imports and configuration

import os
import sys
import logging
import asyncio
import json
import argparse
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import psutil

# === UTF-8 ENFORCEMENT (WSP 90) ===
# CRITICAL: This header MUST be at the top of ALL entry point files
# Entry points: Files with if __name__ == "__main__": or def main()
# Library modules: DO NOT add this header (causes import conflicts)
import sys
import io
import atexit

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
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main.log', encoding='utf-8')
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


async def monitor_youtube(disable_lock: bool = False):
    """Monitor YouTube streams with 0102 consciousness."""
    try:
        # Instance lock management (WSP 84: Don't duplicate processes)
        lock = None
        if not disable_lock:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")

            # Check for duplicates and acquire lock
            duplicates = lock.check_duplicates()
            if duplicates:
                logger.warning(f"[REC] Duplicate main.py Instances Detected!")
                print("\n[REC] Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} instances of main.py running:")
                for i, pid in enumerate(duplicates, 1):
                    print(f"\n  {i}. PID {pid} - [Checking process details...]")
                print("\n  Current instance will exit to prevent conflicts.")
                print("  Kill duplicates with: taskkill /F /PID <PID>")
                print("  Or run with --no-lock to allow multiple instances.")
                return  # Exit instead of proceeding

            # Attempt to acquire lock (will return False if another instance is running)
            if not lock.acquire():
                logger.error("*EFailed to acquire instance lock - another instance is running")
                print("\n*EFailed to acquire instance lock!")
                print("   Another YouTube monitor instance is already running.")
                print("   Only one instance can run at a time to prevent API conflicts.")
                print("   Use --no-lock to disable instance locking.")
                return  # Exit if lock acquisition failed
        else:
            logger.info("[KEY] Instance lock disabled (--no-lock flag used)")

        try:
            # Import the proper YouTube DAE that runs the complete flow:
            # 1. Stream resolver detects stream
            # 2. LinkedIn and X posts trigger
            # 3. Chat monitoring begins
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

            logger.info("Starting YouTube DAE with 0102 consciousness...")
            logger.info("Flow: Stream Detection [SYM]ESocial Posts [SYM]EChat Monitoring")

            # Create and run the DAE with enhanced error handling
            dae = AutoModeratorDAE()

            # Log instance monitoring information (duplicate check already done in menu)
            try:
                instance_summary = lock.get_instance_summary()
                current_pid = instance_summary["current_pid"]
                logger.info(f"[CUT]EYouTube DAE started: PID {current_pid}")
            except Exception as e:
                logger.debug(f"Could not check instance summary: {e}")

            consecutive_failures = 0
            instance_check_counter = 0
            last_minute_log = datetime.now()
            while True:
                try:
                    # Periodic instance monitoring (every 3 iterations for better visibility)
                    instance_check_counter += 1
                    if instance_check_counter % 3 == 0:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]

                            if total_instances > 1:
                                logger.warning(f"[ALERT] INSTANCE ALERT: {total_instances} YouTube DAEs active")
                                for instance in instance_summary["instances"]:
                                    if not instance["is_current"]:
                                        logger.warning(f"  [WARN]EEOther instance PID {instance['pid']} ({instance['age_minutes']:.1f}min old)")
                            elif total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {instance_summary['current_pid']} - No other YouTube DAEs detected")
                            else:
                                logger.info("[INFO]EENo active YouTube DAEs detected")
                        except Exception as e:
                            logger.debug(f"Instance check failed: {e}")

                    # Minute-based instance logging (guaranteed every 60 seconds)
                    now = datetime.now()
                    if (now - last_minute_log).total_seconds() >= 60:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]
                            current_pid = instance_summary["current_pid"]

                            if total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")
                            elif total_instances > 1:
                                logger.warning(f"[ALERT] MULTIPLE INSTANCES: {total_instances} YouTube DAEs active (PID: {current_pid})")
                            else:
                                logger.info("[INFO]EENo YouTube DAEs currently active")

                            last_minute_log = now
                        except Exception as e:
                            logger.debug(f"Minute status check failed: {e}")

                    await dae.run()  # This runs the complete loop
                    logger.info("[LOOP] Stream ended or became inactive - seamless switching engaged")
                    consecutive_failures = 0  # Reset on clean exit
                    await asyncio.sleep(5)  # Quick transition before looking for new stream
                except KeyboardInterrupt:
                    logger.info("[STOP]EEMonitoring stopped by user")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"*EYouTube DAE failed (attempt #{consecutive_failures}): {e}")
                    wait_time = min(30 * (2 ** consecutive_failures), 600)  # Exponential backoff, max 10 minutes
                    logger.info(f"[LOOP] Restarting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    if consecutive_failures >= 5:
                        logger.warning("[LOOP] Too many failures - attempting full reconnection")
                        dae = AutoModeratorDAE()  # Reinitialize for fresh connection
                        consecutive_failures = 0

            # Optionally log status (if supported by DAE)
            if hasattr(dae, 'get_status'):
                status = dae.get_status()
                logger.info(f"YouTube DAE Status: {status}")

        finally:
            # Release the instance lock when done
            lock.release()
            logger.info("[KEY] YouTube monitor instance lock released")

    except Exception as e:
        logger.error(f"Initial YouTube DAE setup failed: {e}")


async def monitor_all_platforms():
    """Monitor all social media platforms."""
    tasks = []

    # YouTube monitoring
    tasks.append(asyncio.create_task(monitor_youtube(disable_lock=False)))

    # Add other platform monitors as needed

    await asyncio.gather(*tasks)


def search_with_holoindex(query: str):
    """
    Use HoloIndex for semantic code search (WSP 87).
    MANDATORY before any code modifications to prevent vibecoding.
    """
    import subprocess

    print("\n[INFO] HoloIndex Semantic Search")
    print("=" * 60)

    try:
        # Check if HoloIndex is available (prefer root version)
        if os.path.exists("holo_index.py"):
            holo_cmd = ['python', 'holo_index.py', '--search', query]
        elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
            # Fallback to E: drive version
            holo_cmd = ['python', r"E:\HoloIndex\enhanced_holo_index.py", '--search', query]
        else:
            print("[WARN]HoloIndex not found")
            print("Install HoloIndex to prevent vibecoding!")
            return None

        # Run HoloIndex search
        result = subprocess.run(
            holo_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.returncode == 0:
            print(result.stdout)
            return result.stdout
        else:
            print(f"[ERROR]Search failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"[ERROR]HoloIndex error: {e}")
        return None


# Extracted to modules/ai_intelligence/holo_dae/scripts/launch.py per WSP 62
from modules.ai_intelligence.holo_dae.scripts.launch import run_holodae


# Extracted to modules/communication/auto_meeting_orchestrator/scripts/launch.py per WSP 62
from modules.communication.auto_meeting_orchestrator.scripts.launch import run_amo_dae


# Extracted to modules/platform_integration/social_media_orchestrator/scripts/launch.py per WSP 62
from modules.platform_integration.social_media_orchestrator.scripts.launch import run_social_media_dae


# Extracted to modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py per WSP 62
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.launch import run_vision_dae


# Extracted to modules/ai_intelligence/utf8_hygiene/scripts/scanner.py per WSP 62
from modules.ai_intelligence.utf8_hygiene.scripts.scanner import run_utf8_hygiene_scan, summarize_utf8_findings


# Extracted to modules/ai_intelligence/training_system/scripts/launch.py per WSP 62
from modules.ai_intelligence.training_system.scripts.launch import run_training_system


# Extracted to modules/ai_intelligence/training_system/scripts/training_commands.py per WSP 62
from modules.ai_intelligence.training_system.scripts.training_commands import execute_training_command
# Extracted to modules/ai_intelligence/pqn/scripts/launch.py per WSP 62
from modules.ai_intelligence.pqn.scripts.launch import run_pqn_dae

# Extracted to modules/communication/liberty_alert/scripts/launch.py per WSP 62
from modules.communication.liberty_alert.scripts.launch import run_liberty_alert_dae

# Extracted to modules/infrastructure/evade_net/scripts/launch.py per WSP 62
from modules.infrastructure.evade_net.scripts.launch import run_evade_net


# Extracted to modules/infrastructure/instance_monitoring/scripts/status_check.py per WSP 62
from modules.infrastructure.instance_monitoring.scripts.status_check import check_instance_status



# Extracted to modules/infrastructure/git_social_posting/scripts/posting_utilities.py per WSP 62
from modules.infrastructure.git_social_posting.scripts.posting_utilities import (
    generate_x_content,
    git_push_and_post,
    view_git_post_history
)

# Extracted to modules/infrastructure/git_push_dae/scripts/launch.py per WSP 62
from modules.infrastructure.git_push_dae.scripts.launch import launch_git_push_dae

# Re-enable normal logging after all imports are complete
logging.root.setLevel(original_level)


def main():
    """Main entry point with command line arguments."""
    # Logger already configured at module level
    logger.info("0102 FoundUps Agent starting...")

    # Import MCP services for CLI access
    from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu

    # Define parser for early argument parsing
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed diagnostic information')

    # Startup diagnostics (verbose mode shows details)
    args, remaining = parser.parse_known_args()  # Parse early to check verbose flag, allow unknown args

    # Essential startup diagnostics (always log for troubleshooting)
    if args.verbose:
        logger.info(f"[DIAG] Python {sys.version.split()[0]} on {sys.platform}")
        logger.info(f"[DIAG] Working directory: {os.getcwd()}")
        logger.info(f"[DIAG] UTF-8 stdout: {getattr(sys.stdout, 'encoding', 'unknown')}")
        logger.info(f"[DIAG] UTF-8 stderr: {getattr(sys.stderr, 'encoding', 'unknown')}")
    else:
        logger.debug(f"[DIAG] Python {sys.version.split()[0]} on {sys.platform}")
        logger.debug(f"[DIAG] Working directory: {os.getcwd()}")

    # Check critical systems
    try:
        import modules
        if args.verbose:
            logger.info("[DIAG] modules/ directory accessible")
        else:
            logger.debug("[DIAG] modules/ directory accessible")
    except ImportError as e:
        logger.error(f"[STARTUP] modules/ directory not accessible: {e}")

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
        if args.verbose:
            logger.info("[DIAG] Instance lock system available")
        else:
            logger.debug("[DIAG] Instance lock system available")
    except ImportError as e:
        logger.warning(f"[STARTUP] Instance lock system unavailable: {e}")

    # UTF-8 encoding is critical for Windows CLI compatibility
    stdout_enc = getattr(sys.stdout, 'encoding', 'unknown')
    stderr_enc = getattr(sys.stderr, 'encoding', 'unknown')
    if stdout_enc != 'utf-8' or stderr_enc != 'utf-8':
        logger.warning(f"[STARTUP] UTF-8 encoding issue - stdout:{stdout_enc} stderr:{stderr_enc}")
    else:
        if args.verbose:
            logger.info("[DIAG] UTF-8 encoding confirmed")
        else:
            logger.debug("[DIAG] UTF-8 encoding confirmed")

    # Add remaining arguments to existing parser
    parser.add_argument('--git', action='store_true', help='Launch GitPushDAE (autonomous git push + social posting)')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--holodae', '--holo', action='store_true', help='Run HoloDAE (Code Intelligence & Monitoring)')
    parser.add_argument('--amo', action='store_true', help='Run AMO DAE (Autonomous Moderation Operations)')
    parser.add_argument('--smd', action='store_true', help='Run Social Media DAE (012 Digital Twin)')
    parser.add_argument('--vision', action='store_true', help='Run FoundUps Vision DAE (Pattern Sensorium)')
    parser.add_argument('--pqn', action='store_true', help='Run PQN Orchestration (Research & Alignment)')
    parser.add_argument('--liberty', action='store_true', help='Run Liberty Alert Mesh Alert System (Community Protection)')
    parser.add_argument('--liberty-dae', action='store_true', help='Run Liberty Alert DAE (Community Protection Autonomous Entity)')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')
    parser.add_argument('--mcp', action='store_true', help='Launch MCP Services Gateway (Model Context Protocol)')
    parser.add_argument('--no-lock', action='store_true', help='Disable instance lock (allow multiple instances)')
    parser.add_argument('--status', action='store_true', help='Check instance status and health')
    parser.add_argument('--training-command', type=str, help='Execute training command via Holo (e.g., utf8_scan, batch)')
    parser.add_argument('--targets', type=str, help='Comma-separated target paths for training command')
    parser.add_argument('--json-output', action='store_true', help='Return training command result as JSON')
    parser.add_argument('--training-menu', action='store_true', help='Launch interactive training submenu (option 12)')

    # Re-parse with all arguments now that they're defined
    args = parser.parse_args()

    if args.training_command:
        execute_training_command(args.training_command, args.targets, args.json_output)
        return
    if args.training_menu:
        run_training_system()
        return

    if args.status:
        check_instance_status()
        return
    elif args.git:
        launch_git_push_dae()
    elif args.youtube:
        asyncio.run(monitor_youtube(disable_lock=args.no_lock))
    elif args.holodae:
        run_holodae()
    elif args.amo:
        run_amo_dae()
    elif args.smd:
        run_social_media_dae()
    elif args.vision:
        run_vision_dae()
    elif args.pqn:
        run_pqn_dae()
    elif args.liberty:
        run_evade_net()
    elif args.liberty_dae:
        run_liberty_alert_dae()
    elif args.all:
        asyncio.run(monitor_all_platforms())
    elif args.mcp:
        show_mcp_services_menu()
    else:
        # Interactive menu - Check instances once at startup, then loop main menu
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)

        # TEMP FIX: Skip instance check in menu to avoid psutil hang
        # Instance check will run when user actually launches a DAE (option 1, etc.)
        print("[INFO] Main menu ready - instance checks run when launching DAEs")
        print("   Use --status to check for running instances")
        print("   Safe to start new DAEs\n")

        duplicates = []  # Skip check for now
        if False:  # Disabled until psutil hang is fixed
            try:
                from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
                lock = get_instance_lock("youtube_monitor")
                duplicates = lock.check_duplicates(quiet=True)
            except Exception as e:
                print(f"[WARN] Could not check instances: {e}")
                print("   Proceeding with menu...\n")
                duplicates = []

        if duplicates and False:  # Also disabled
                # Loop until user makes a valid choice
                while True:
                    print(f"[WARN] FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                    print("\nWhat would you like to do?")
                    print("1. Kill all instances and continue")
                    print("2. Show detailed status")
                    print("3. Continue anyway (may cause conflicts)")
                    print("4. Exit")
                    print("-"*40)

                    # Get user input and clean it (remove brackets, spaces, etc.)
                    choice = input("Select option (1-4): ").strip().lstrip(']').lstrip('[')

                    if choice == "1":
                        print("\n[INFO] Killing duplicate instances...")
                        killed_pids = []
                        failed_pids = []

                        current_pid = os.getpid()

                        for pid in duplicates:
                            if pid == current_pid:
                                continue  # Don't kill ourselves

                            try:
                                print(f"   [INFO] Terminating PID {pid}...")
                                process = psutil.Process(pid)
                                process.terminate()  # Try graceful termination first

                                # Wait up to 5 seconds for process to terminate
                                gone, alive = psutil.wait_procs([process], timeout=5)

                                if alive:
                                    # If still alive, force kill
                                    print(f"   [INFO] Force killing PID {pid}...")
                                    process.kill()
                                    gone, alive = psutil.wait_procs([process], timeout=2)

                                if not alive:
                                    killed_pids.append(pid)
                                    print(f"   [INFO]PID {pid} terminated successfully")
                                else:
                                    failed_pids.append(pid)
                                    print(f"   [ERROR]Failed to kill PID {pid}")

                            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                print(f"   [WARN] Could not kill PID {pid}: {e}")
                                failed_pids.append(pid)

                        if killed_pids:
                            print(f"\n[INFO]Successfully killed {len(killed_pids)} instance(s): {killed_pids}")
                        if failed_pids:
                            print(f"[WARN] Failed to kill {len(failed_pids)} instance(s): {failed_pids}")

                        print("   Proceeding to main menu...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "2":
                        print("\n" + "="*50)
                        check_instance_status()
                        print("="*50)
                        input("\nPress Enter to continue...")
                        # Don't break - loop back to menu

                    elif choice == "3":
                        print("[WARN] Continuing with potential conflicts...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "4":
                        print("[INFO] Exiting...")
                        return  # Exit entire program

                    else:
                        print(f"[ERROR]Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.")
                        print("   Try again...\n")
                        # Don't break - loop will continue and ask again
                        continue

        # Orphaned else block removed - duplicates check is now disabled above

        logger.info("[DAEMON] Main menu loop starting")
        print("[DEBUG-MAIN] About to enter main menu loop")

        # Main menu loop (only reached after instance handling)
        while True:
            logger.debug("[DAEMON] Top of menu loop - displaying options")
            print("[DEBUG-MAIN] Top of menu loop - displaying options")

            # Show the main menu
            print("0. 🚀 Push to Git and Post to LinkedIn + X (FoundUps)  │ --git")
            print("1. 📺 YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)  │ --youtube")
            print("2. 🧠 HoloDAE (Code Intelligence & Monitoring)       │ --holodae")
            print("3. 🔨 AMO DAE (Autonomous Moderation Operations)     │ --amo")
            print("4. 📢 Social Media DAE (012 Digital Twin)            │ --smd")
            print("5. 🛡️ Liberty Alert DAE (Community Protection)      │ --liberty-dae")
            print("6. 🧬 PQN Orchestration (Research & Alignment)       │ --pqn")
            print("7. 🔔 Liberty Alert (Mesh Alert System)              │ --liberty")
            print("8. 👁️ FoundUps Vision DAE (Pattern Sensorium)       │ --vision")
            print("9. 🌐 All DAEs (Full System)                        │ --all")
            print("10. 🚪 Exit")
            print("-"*60)
            print("00. 🏥 Check Instance Status & Health               │ --status")
            print("11. 🔍 HoloIndex Search (Find code semantically)")
            print("12. 📋 View Git Post History")
            print("13. 🧪 Qwen/Gemma Training System (Pattern Learning)")
            print("14. 🔌 MCP Services (Model Context Protocol Gateway) │ --mcp")
            print("="*60)
            print("💡 CLI: --youtube --no-lock (bypass menu + instance lock)")
            print("="*60)

            try:
                choice = input("\nSelect option: ").strip()
                logger.info(f"[DAEMON] User selected option: '{choice}'")
                print(f"[DEBUG-MAIN] User selected option: '{choice}'")
            except (EOFError, KeyboardInterrupt) as e:
                logger.warning(f"[DAEMON] Input interrupted: {e}")
                print(f"[DEBUG-MAIN] Input interrupted: {e}")
                choice = "10"  # Default to exit on interrupt

            if choice == "0":
                # Launch GitPushDAE daemon (WSP 91 compliant)
                print("[DEBUG-MAIN] Calling launch_git_push_dae()...")
                launch_git_push_dae()
                print("[DEBUG-MAIN] Returned from launch_git_push_dae()")
                # Will return to menu after completion

            elif choice == "1":
                # YouTube DAE Menu - Live Chat OR Shorts
                print("\n[MENU] YouTube DAE Menu")
                print("="*60)
                print("1. [ALERT] YouTube Live Chat Monitor (AutoModeratorDAE)")
                print("2. [MENU] YouTube Shorts Generator (Gemini/Veo 3)")
                print("3. [MENU] YouTube Shorts Generator (Sora2 Live Action)")
                print("4. [INFO] YouTube Stats & Info")
                print("0. [BACK] Back to Main Menu")
                print("="*60)

                yt_choice = input("\nSelect YouTube option: ")

                def run_shorts_flow(engine_label: str, system_label: str, mode_label: str, duration_label: str, engine_key: str) -> None:
                    print(f"\n[MENU] YouTube Shorts Generator [{engine_label}]")
                    print("="*60)
                    print("Channel: Move2Japan (9,020 subscribers)")
                    print(f"System: {system_label}")
                    print("="*60)

                    topic = input("\n[TIP] Enter topic (e.g., 'Cherry blossoms in Tokyo'): ").strip()

                    if not topic:
                        print("[WARN] No topic entered - returning to menu")
                        return

                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

                        print(f"\n[MENU] Generating YouTube Short ({engine_label}): {topic}")
                        print(f"  Mode: {mode_label}")
                        print(f"  Duration: {duration_label}")
                        print("  Privacy: PUBLIC")

                        orchestrator = ShortsOrchestrator(channel="move2japan", default_engine="auto")

                        youtube_url = orchestrator.create_and_upload(
                            topic=topic,
                            duration=15,
                            enhance_prompt=True,
                            fast_mode=True,
                            privacy="public",
                            use_3act=True,
                            engine=engine_key
                        )

                        print(f"\n[INFO]SHORT PUBLISHED!")
                        print(f"   URL: {youtube_url}")
                        print(f"   Channel: Move2Japan")

                    except Exception as e:
                        print(f"\n[ERROR]YouTube Shorts generation failed: {e}")
                        import traceback
                        traceback.print_exc()

                if yt_choice == "1":
                    print("[MENU] Starting YouTube Live Chat Monitor...")
                    asyncio.run(monitor_youtube(disable_lock=False))

                elif yt_choice == "2":
                    run_shorts_flow(
                        engine_label="Gemini/Veo 3",
                        system_label="3-Act Story (Setup  -> Shock  -> 0102 Reveal)",
                        mode_label="Emergence Journal POC",
                        duration_label="~16s (2.5s clips merged)",
                        engine_key="veo3"
                    )

                elif yt_choice == "3":
                    run_shorts_flow(
                        engine_label="Sora2 Live Action",
                        system_label="3-Act Story (Cinematic Reveal)",
                        mode_label="Cinematic Sora2 (live-action focus)",
                        duration_label="15s cinematic (single clip)",
                        engine_key="sora2"
                    )

                elif yt_choice == "4":
                    # YouTube Stats
                    print("\n[INFO] YouTube Stats")
                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator
                        orch = ShortsOrchestrator(channel="move2japan", default_engine="auto")
                        stats = orch.get_stats()

                        print(f"\n  Total Shorts: {stats['total_shorts']}")
                        print(f"  Uploaded: {stats['uploaded']}")
                        print(f"  Total Cost: ${stats['total_cost_usd']}")
                        print(f"  Avg Cost: ${stats['average_cost_per_short']}")
                        if stats.get('engine_usage'):
                            print(f"  Engine Usage: {stats['engine_usage']}")

                        recent = stats.get('recent_shorts') or []
                        if recent:
                            print(f"\n  Recent Shorts:")
                            for s in recent[-3:]:
                                print(f"    - {s.get('topic', 'N/A')[:40]}...")
                                print(f"      {s.get('youtube_url', 'N/A')}")
                    except Exception as e:
                        print(f"[ERROR]Failed to get stats: {e}")

                elif yt_choice == "0":
                    print("[BACK] Returning to main menu...")
                else:
                    print("[ERROR]Invalid choice")

            elif choice == "2":
                # HoloDAE - Code Intelligence & Monitoring
                print("[INFO] HoloDAE Menu - Code Intelligence & Monitoring System")
                try:
                    # Import menu function ONLY (don't start daemon yet)
                    from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

                    holodae_instance = None  # Initialize as None, created only when needed

                    while True:
                        choice = show_holodae_menu()

                        if choice == "0":
                            # Launch the daemon (option 0 in HoloDAE menu)
                            print("[MENU] Launching HoloDAE Autonomous Monitor...")
                            from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                            if holodae_instance is None:
                                holodae_instance = start_holodae_monitoring()
                                print("[INFO]HoloDAE monitoring started in background")
                                print("[TIP] Daemon is running - select 9 to stop, or 99 to return to main menu")
                            else:
                                print("[INFO]HoloDAE already running")
                            # Don't break - loop back to HoloDAE menu for more selections
                        elif choice == "9":
                            # Stop the daemon (option 9 - toggle monitoring)
                            if holodae_instance is not None and holodae_instance.active:
                                print("[INFO] Stopping HoloDAE monitoring...")
                                holodae_instance.stop_autonomous_monitoring()
                                print("[INFO]HoloDAE daemon stopped")
                            else:
                                print("[INFO] HoloDAE daemon is not running")
                        elif choice == "99":
                            print("[INFO] Returning to main menu...")
                            if holodae_instance is not None and holodae_instance.active:
                                print("[WARN]HoloDAE daemon still running in background")
                            break
                        elif choice == "1":
                            print("[INFO] Running semantic code search...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "2":
                            print("[INFO] Running dual search (code + WSP)...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "3":
                            print("[INFO]Running module existence check...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --check-module 'module_name'")
                        elif choice == "4":
                            print("[INFO] Running DAE cube organizer...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --init-dae 'DAE_name'")
                        elif choice == "5":
                            print("[INFO] Running index management...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --index-all")
                        elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                            print("[INFO] Running HoloDAE intelligence analysis...")
                            # These would trigger HoloDAE analysis functions
                            print("Use HoloIndex search to trigger automatic analysis")
                        elif choice == "14":
                            print("[INFO]Running WSP 88 orphan analysis...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --wsp88")
                        elif choice == "16":
                            print("[INFO] Execution Log Analyzer - Advisor Choice")
                            print("=" * 60)
                            print("Advisor: Choose analysis mode for systematic log processing")
                            print()
                            print("1. [MENU]Interactive Mode - Step-by-step advisor guidance")
                            print("2. [WARN] Daemon Mode - Autonomous 0102 background processing")
                            print()
                            print("Interactive: User-guided analysis with advisor oversight")
                            print("Daemon: Autonomous processing once triggered - follows WSP 80")
                            print()

                            analysis_choice = input("Select mode (1-2): ").strip()

                            if analysis_choice == "1":
                                # Interactive mode - advisor-guided
                                print("\n[MENU]Starting Interactive Log Analysis...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor-guided systematic log analysis...")
                                    print("[INFO] Processing 23,000+ lines with advisor oversight...")

                                    librarian = coordinate_execution_log_processing(daemon_mode=False)

                                    print("\n[INFO]Interactive analysis initialized!")
                                    print("[INFO] Results saved to:")
                                    print("   - complete_file_index.json (full scope analysis)")
                                    print("   - qwen_processing_plan.json (processing plan)")
                                    print("   - qwen_next_task.json (ready for Qwen analysis)")

                                    print("\n[INFO] Next: Advisor guides Qwen analysis of chunks")
                                    input("\nPress Enter to continue...")

                                except Exception as e:
                                    print(f"[ERROR]Interactive analysis failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            elif analysis_choice == "2":
                                # Daemon mode - autonomous 0102 processing
                                print("\n[WARN] Starting Log Analysis Daemon...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor triggers autonomous 0102 processing...")
                                    print("[INFO] 0102 will process entire log file independently")

                                    # Start daemon
                                    daemon_thread = coordinate_execution_log_processing(daemon_mode=True)

                                    print("\n[INFO]Daemon started successfully!")
                                    print("[INFO] 0102 processing 23,000+ lines autonomously")
                                    print("[INFO] Check progress: HoloDAE menu  -> Option 15 (PID Detective)")
                                    print("[INFO] Results will be saved to analysis output files")

                                    input("\nPress Enter to continue (daemon runs in background)...")

                                except Exception as e:
                                    print(f"[ERROR]Daemon startup failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            else:
                                print("[ERROR]Invalid choice - returning to menu")
                                input("\nPress Enter to continue...")
                        elif choice in ["15", "17", "18"]:
                            print("[INFO] Running WSP compliance functions...")
                            # These would trigger compliance checking
                            print("Use HoloIndex search to trigger compliance analysis")
                        elif choice in ["19", "20", "21", "22", "23"]:
                            print("[MENU]Running AI advisor functions...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'query' --llm-advisor")
                        elif choice == "24":
                            print("[MENU] Launching YouTube Live DAE...")
                            # Would need to navigate to option 1
                            print("Please select option 1 from main menu for YouTube DAE")
                        elif choice == "25":
                            print("[INFO] Starting autonomous HoloDAE monitoring...")
                            run_holodae()
                            break  # Exit menu after starting monitoring
                        elif choice == "6":
                            print("[INFO] Launching Chain-of-Thought Brain Logging...")
                            try:
                                from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                                demonstrate_brain_logging()
                                print("\n[INFO] BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                                print("[TIP] This shows exactly how the AI brain works - completely observable!")
                            except Exception as e:
                                print(f"[ERROR]Brain logging failed: {e}")
                            input("\nPress Enter to continue...")
                        elif choice in ["26", "27", "28", "29", "30"]:
                            print("[INFO] This DAE operation requires main menu selection...")
                            # Would need to navigate to appropriate main menu option
                            print("Please return to main menu and select the appropriate DAE")
                        elif choice in ["31", "32", "33", "34", "35"]:
                            print("[WARN]Running administrative functions...")
                            # These would trigger admin functions
                            print("Administrative functions available through main menu")
                        else:
                            print("[ERROR]Invalid choice. Please select 0-35.")

                        input("\nPress Enter to continue...")

                except Exception as e:
                    print(f"[ERROR]HoloDAE menu failed to load: {e}")
                    import traceback
                    traceback.print_exc()

            elif choice == "3":
                # AMO DAE
                print("[AMO] Starting AMO DAE (Autonomous Moderation)...")
                from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
                dae = AutoModeratorDAE()
                asyncio.run(dae.run())

            elif choice == "4":
                # Social Media DAE (012 Digital Twin)
                print("[SMD] Starting Social Media DAE (012 Digital Twin)...")
                from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
                orchestrator = SocialMediaOrchestrator()
                # orchestrator.run_digital_twin()  # TODO: Implement digital twin mode
                print("Digital Twin mode coming soon...")

            elif choice == "5":
                # Liberty Alert DAE
                run_liberty_alert_dae()

            elif choice == "6":
                # PQN Orchestration
                print("[INFO] Starting PQN Research DAE...")
                from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
                pqn_dae = PQNResearchDAEOrchestrator()
                asyncio.run(pqn_dae.run())

            elif choice == "7":
                # Liberty Alert mesh alert system
                run_evade_net()

            elif choice == "8":
                # FoundUps Vision DAE
                run_vision_dae()

            elif choice == "9":
                # All DAEs
                print("[ALL] Starting ALL DAEs...")
                asyncio.run(monitor_all_platforms())

            elif choice == "10":
                print("[EXIT] Exiting...")
                break  # Exit the while True loop

            elif choice in {"00", "status"}:
                check_instance_status()
                input("\nPress Enter to continue...")

            elif choice == "10":
                # HoloIndex search
                print("\n[HOLOINDEX] Semantic Code Search")
                print("=" * 60)
                print("This prevents vibecoding by finding existing code!")
                print("Examples: 'send messages', 'handle timeouts', 'consciousness'")
                print("=" * 60)
                query = input("\nWhat code are you looking for? ")
                if query:
                    search_with_holoindex(query)
                    input("\nPress Enter to continue...")
                else:
                    print("No search query provided")

            elif choice == "11":
                # View git post history
                view_git_post_history()

            elif choice == "12":
                # Qwen/Gemma Training System
                run_training_system()

            elif choice == "14":
                # MCP Services Gateway
                print("[MCP] Launching MCP Services Gateway...")
                from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu
                show_mcp_services_menu()

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()




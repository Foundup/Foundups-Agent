# -*- coding: utf-8 -*-
import sys
import io


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
import argparse
import json
import time
from datetime import datetime
from typing import Optional, Dict, Any
import psutil

# Set UTF-8 encoding for Windows (must be done before logging setup)
if sys.platform.startswith('win'):
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # Force Windows console to UTF-8 mode
    import subprocess
    try:
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True, check=False)
    except:
        pass  # Fail silently if chcp not available

    # Configure stdout/stderr for UTF-8
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configure logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('main.log', encoding='utf-8')
    ]
)

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
                logger.warning(f"[U+1F534] Duplicate main.py Instances Detected!")
                print("\n[U+1F534] Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} instances of main.py running:")
                for i, pid in enumerate(duplicates, 1):
                    print(f"\n  {i}. PID {pid} - [Checking process details...]")
                print("\n  Current instance will exit to prevent conflicts.")
                print("  Kill duplicates with: taskkill /F /PID <PID>")
                print("  Or run with --no-lock to allow multiple instances.")
                return  # Exit instead of proceeding

            # Attempt to acquire lock (will return False if another instance is running)
            if not lock.acquire():
                logger.error("[FAIL] Failed to acquire instance lock - another instance is running")
                print("\n[FAIL] Failed to acquire instance lock!")
                print("   Another YouTube monitor instance is already running.")
                print("   Only one instance can run at a time to prevent API conflicts.")
                print("   Use --no-lock to disable instance locking.")
                return  # Exit if lock acquisition failed
        else:
            logger.info("[U+1F513] Instance lock disabled (--no-lock flag used)")

        try:
            # Import the proper YouTube DAE that runs the complete flow:
            # 1. Stream resolver detects stream
            # 2. LinkedIn and X posts trigger
            # 3. Chat monitoring begins
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

            logger.info("Starting YouTube DAE with 0102 consciousness...")
            logger.info("Flow: Stream Detection -> Social Posts -> Chat Monitoring")

            # Create and run the DAE with enhanced error handling
            dae = AutoModeratorDAE()

            # Log instance monitoring information
            try:
                instance_summary = lock.get_instance_summary()
                total_instances = instance_summary["total_instances"]
                current_pid = instance_summary["current_pid"]

                if total_instances > 1:
                    logger.warning(f"[ALERT] MULTIPLE INSTANCES DETECTED: {total_instances} YouTube DAEs running")
                    for instance in instance_summary["instances"]:
                        status = "CURRENT" if instance["is_current"] else "OTHER"
                        logger.warning(f"  • {status} PID {instance['pid']} - {instance['age_minutes']:.1f}min old - {instance['memory_mb']} RAM")
                else:
                    logger.info(f"[OK] SINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")

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
                                        logger.warning(f"  [U+26A0]️ Other instance PID {instance['pid']} ({instance['age_minutes']:.1f}min old)")
                            elif total_instances == 1:
                                logger.info(f"[OK] SINGLE INSTANCE: PID {instance_summary['current_pid']} - No other YouTube DAEs detected")
                            else:
                                logger.info("ℹ️ No active YouTube DAEs detected")
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
                                logger.info(f"[OK] SINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")
                            elif total_instances > 1:
                                logger.warning(f"[ALERT] MULTIPLE INSTANCES: {total_instances} YouTube DAEs active (PID: {current_pid})")
                            else:
                                logger.info("ℹ️ No YouTube DAEs currently active")

                            last_minute_log = now
                        except Exception as e:
                            logger.debug(f"Minute status check failed: {e}")

                    await dae.run()  # This runs the complete loop
                    logger.info("[REFRESH] Stream ended or became inactive - seamless switching engaged")
                    consecutive_failures = 0  # Reset on clean exit
                    await asyncio.sleep(5)  # Quick transition before looking for new stream
                except KeyboardInterrupt:
                    logger.info("⏹️ Monitoring stopped by user")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"YouTube DAE failed (attempt #{consecutive_failures}): {e}")
                    wait_time = min(30 * (2 ** consecutive_failures), 600)  # Exponential backoff, max 10 minutes
                    logger.info(f"[REFRESH] Restarting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    if consecutive_failures >= 5:
                        logger.warning("[REFRESH] Too many failures - attempting full reconnection")
                        dae = AutoModeratorDAE()  # Reinitialize for fresh connection
                        consecutive_failures = 0

            # Optionally log status (if supported by DAE)
            if hasattr(dae, 'get_status'):
                status = dae.get_status()
                logger.info(f"YouTube DAE Status: {status}")

        finally:
            # Release the instance lock when done
            lock.release()
            logger.info("[U+1F513] YouTube monitor instance lock released")

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

    print("\n[SEARCH] HoloIndex Semantic Search")
    print("=" * 60)

    try:
        # Check if HoloIndex is available (prefer root version)
        if os.path.exists("holo_index.py"):
            holo_cmd = ['python', 'holo_index.py', '--search', query]
        elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
            # Fallback to E: drive version
            holo_cmd = ['python', r"E:\HoloIndex\enhanced_holo_index.py", '--search', query]
        else:
            print("[U+26A0]️ HoloIndex not found")
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
            print(f"[FAIL] Search failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"[FAIL] HoloIndex error: {e}")
        return None


def run_holodae():
    """Run HoloDAE (Code Intelligence & Monitoring)."""
    print("[HOLODAE] Starting HoloDAE - Code Intelligence & Monitoring System...")

    # HOLO-DAE INSTANCE LOCKING (First Principles: Resource Protection & Consistency)
    from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
    lock = get_instance_lock("holodae_monitor")

    # Check for duplicates and acquire lock
    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning("[U+1F534] Duplicate HoloDAE Instances Detected!")
        print("\n[U+1F534] Duplicate HoloDAE Instances Detected!")
        print(f"\n  Found {len(duplicates)} instances of HoloDAE running:")
        for i, pid in enumerate(duplicates, 1):
            print(f"\n  {i}. PID {pid} - [Checking process details...]")
        print("\n  Current instance will exit to prevent conflicts.")
        print("  Use --no-lock to disable instance locking.")
        return  # Exit if duplicates found

    # Acquire lock for this instance
    if not lock.acquire():
        logger.error("[FAIL] Failed to acquire HoloDAE instance lock - another instance is running")
        print("\n[FAIL] Failed to acquire HoloDAE instance lock!")
        print("   Another HoloDAE instance is already running.")
        print("   Only one instance can run at a time to prevent index conflicts.")
        print("   Use --no-lock to disable instance locking.")
        return  # Exit if lock acquisition failed

    try:
        from holo_index.qwen_advisor.autonomous_holodae import AutonomousHoloDAE
        holodae = AutonomousHoloDAE()

        # Log successful instance acquisition
        instance_summary = lock.get_instance_summary()
        total_instances = instance_summary["total_instances"]
        current_pid = instance_summary["current_pid"]
        logger.info(f"[OK] HoloDAE SINGLE INSTANCE: PID {current_pid} - No other HoloDAEs detected")

        holodae.start_autonomous_monitoring()

        print("[HOLODAE] Autonomous monitoring active. Press Ctrl+C to stop.")

        # Keep the process running
        try:
            while holodae.active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("[HOLODAE] Stopping autonomous monitoring...")
            holodae.stop_autonomous_monitoring()
            print("[HOLODAE] HoloDAE stopped successfully")

    except Exception as e:
        print(f"[HOLODAE-ERROR] Failed to start: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Release the instance lock when done
        lock.release()
        logger.info("[U+1F513] HoloDAE monitor instance lock released")


def run_amo_dae():
    """Run AMO DAE (Autonomous Moderation Operations)."""
    print("[AMO] Starting AMO DAE (Autonomous Moderation Operations)...")
    try:
        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
        dae = AutoModeratorDAE()
        asyncio.run(dae.run())
    except Exception as e:
        print(f"[AMO-ERROR] AMO DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_social_media_dae():
    """Run Social Media DAE (012 Digital Twin)."""
    print("[U+1F465] Starting Social Media DAE (012 Digital Twin)...")
    try:
        from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
        orchestrator = SocialMediaOrchestrator()
        # TODO: Implement digital twin mode
        print("Digital Twin mode coming soon...")
        print("Social Media DAE orchestration available for development.")
    except Exception as e:
        print(f"[FAIL] Social Media DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_pqn_dae():
    """Run PQN Orchestration (Research & Alignment)."""
    print("[AI] Starting PQN Research DAE...")
    try:
        from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
        pqn_dae = PQNResearchDAEOrchestrator()
        asyncio.run(pqn_dae.run())
    except Exception as e:
        print(f"[FAIL] PQN DAE failed: {e}")
        import traceback
        traceback.print_exc()


def check_instance_status():
    """Check the status and health of running instances."""
    print("\n" + "="*60)
    print("[SEARCH] INSTANCE STATUS CHECK")
    print("="*60)

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

        lock = get_instance_lock("youtube_monitor")

        # Check for running instances
        duplicates = lock.check_duplicates()

        if duplicates:
            print(f"[FAIL] Found {len(duplicates)} duplicate instances running")
            return
        else:
            print("[OK] No duplicate instances detected")

        # Check lock file status
        if lock.lock_file.exists():
            print("[LOCK] Lock file exists:")
            try:
                with open(lock.lock_file, 'r') as f:
                    lock_data = json.load(f)
                pid = lock_data.get('pid')
                heartbeat = lock_data.get('heartbeat', 'Unknown')
                start_time = lock_data.get('start_time', 'Unknown')

                print(f"   PID: {pid}")
                print(f"   Started: {start_time}")
                print(f"   Last heartbeat: {heartbeat}")

                # Check if process is actually running
                if lock._is_process_running(pid):
                    print("   Status: [OK] RUNNING")
                else:
                    print("   Status: [FAIL] PROCESS NOT FOUND (stale lock)")

            except Exception as e:
                print(f"   Error reading lock file: {e}")
        else:
            print("[U+1F513] No lock file found (no instances running)")

        # Check health status
        health = lock.get_health_status()
        print("\n[U+1F3E5] Health Status:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Message: {health.get('message', 'no data')}")
        if 'timestamp' in health:
            print(f"   Last update: {health['timestamp']}")

        # Check HoloDAE instances
        print("\n" + "-"*40)
        print("[BOT] HOLO-DAE STATUS")
        print("-"*40)

        try:
            holodae_lock = get_instance_lock("holodae_monitor")

            # Check for running HoloDAE instances
            holodae_duplicates = holodae_lock.check_duplicates()

            if holodae_duplicates:
                print(f"[FAIL] Found {len(holodae_duplicates)} HoloDAE instances running")
                return
            else:
                print("[OK] No duplicate HoloDAE instances detected")

            # Check HoloDAE lock file status
            if holodae_lock.lock_file.exists():
                print("[LOCK] HoloDAE Lock file exists:")
                try:
                    with open(holodae_lock.lock_file, 'r') as f:
                        lock_data = json.load(f)
                    pid = lock_data.get('pid')
                    heartbeat = lock_data.get('heartbeat', 'Unknown')
                    start_time = lock_data.get('start_time', 'Unknown')

                    print(f"   PID: {pid}")
                    print(f"   Started: {start_time}")
                    print(f"   Last heartbeat: {heartbeat}")

                    # Check if process is actually running
                    if holodae_lock._is_process_running(pid):
                        print("   Status: [OK] RUNNING")
                    else:
                        print("   Status: [FAIL] PROCESS NOT FOUND (stale lock)")

                except Exception as e:
                    print(f"   Error reading lock file: {e}")
            else:
                print("[U+1F513] No HoloDAE lock file found (no instances running)")

            # Check HoloDAE health status
            holodae_health = holodae_lock.get_health_status()
            print("\n[U+1F3E5] HoloDAE Health Status:")
            print(f"   Status: {holodae_health.get('status', 'unknown')}")
            print(f"   Message: {holodae_health.get('message', 'no data')}")
            if 'timestamp' in holodae_health:
                print(f"   Last update: {holodae_health['timestamp']}")

        except Exception as e:
            print(f"[FAIL] Error checking HoloDAE status: {e}")

    except Exception as e:
        print(f"[FAIL] Error checking status: {e}")

    print()


def generate_x_content(commit_msg, file_count):
    """Generate compelling X/Twitter content (280 char limit)"""
    import random

    # Short punchy intros for X
    x_intros = [
        "[U+1F984] FoundUps by @UnDaoDu\n\nDAEs eating startups for breakfast.\n\n",
        "[LIGHTNING] Startups die. FoundUps are forever.\n\n",
        "[ROCKET] No VCs. No employees. Just you + [INFINITY] agents.\n\n",
        "[IDEA] Solo unicorns are real. Ask @UnDaoDu.\n\n",
        "[U+1F30A] The startup killer is here.\n\n"
    ]

    content = random.choice(x_intros)

    # Add brief update
    if "fix" in commit_msg.lower():
        content += f"[TOOL] {file_count} fixes by 0102 agents\n\n"
    elif "test" in commit_msg.lower():
        content += f"[U+1F9EA] Testing future: {file_count} files\n\n"
    else:
        content += f"[LIGHTNING] {file_count} autonomous updates\n\n"

    # Short CTA
    ctas = [
        "Join the revolution.",
        "Build a FoundUp.",
        "Be a solo unicorn.",
        "The future is autonomous.",
        "Startups are dead."
    ]
    content += random.choice(ctas)

    # Essential hashtags that fit
    content += "\n\n#FoundUps #DAE #SoloUnicorn @Foundups"

    # Ensure we're under 280 chars
    if len(content) > 280:
        # Trim to fit with link
        content = content[:240] + "...\n\n#FoundUps @Foundups"

    return content


def git_push_and_post():
    """
    Git push with automatic social media posting.
    Uses the git_linkedin_bridge module to handle posting.
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

    print("\n" + "="*60)
    print("GIT PUSH & LINKEDIN + X POST (FoundUps)")
    print("="*60)

    # Use the git bridge module with X support
    bridge = GitLinkedInBridge(company_id="1263645")
    bridge.push_and_post()

    input("\nPress Enter to continue...")



def view_git_post_history():
    """View the history of git posts to social media."""
    import json
    import os
    from datetime import datetime

    print("\n" + "="*60)
    print("[DATA] GIT POST HISTORY")
    print("="*60)

    # Check posted commits
    posted_commits_file = "memory/git_posted_commits.json"
    if os.path.exists(posted_commits_file):
        try:
            with open(posted_commits_file, 'r') as f:
                posted_commits = json.load(f)
                print(f"\n[OK] {len(posted_commits)} commits posted to social media")
                print("\nPosted commit hashes:")
                for commit in posted_commits[-10:]:  # Show last 10
                    print(f"  • {commit}")
                if len(posted_commits) > 10:
                    print(f"  ... and {len(posted_commits) - 10} more")
        except Exception as e:
            print(f"[FAIL] Error reading posted commits: {e}")
    else:
        print("[U+1F4ED] No posted commits found")

    # Check detailed log
    log_file = "memory/git_post_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
                print(f"\n[CLIPBOARD] Detailed posting log ({len(log_entries)} entries):")
                print("-" * 60)

                # Show last 5 entries
                for entry in log_entries[-5:]:
                    timestamp = entry.get('timestamp', 'Unknown')
                    commit_msg = entry.get('commit_msg', 'No message')[:50]
                    linkedin = "[OK]" if entry.get('linkedin') else "[FAIL]"
                    x_twitter = "[OK]" if entry.get('x_twitter') else "[FAIL]"
                    files = entry.get('file_count', 0)

                    print(f"\n[U+1F4CC] {timestamp[:19]}")
                    print(f"   Commit: {commit_msg}...")
                    print(f"   Files: {files}")
                    print(f"   LinkedIn: {linkedin}  X/Twitter: {x_twitter}")

                if len(log_entries) > 5:
                    print(f"\n... and {len(log_entries) - 5} more entries")

                # Stats
                total_posts = len(log_entries)
                linkedin_success = sum(1 for e in log_entries if e.get('linkedin'))
                x_success = sum(1 for e in log_entries if e.get('x_twitter'))

                print("\n[UP] Statistics:")
                print(f"   Total posts: {total_posts}")
                print(f"   LinkedIn success rate: {linkedin_success}/{total_posts} ({linkedin_success*100//max(total_posts,1)}%)")
                print(f"   X/Twitter success rate: {x_success}/{total_posts} ({x_success*100//max(total_posts,1)}%)")

        except Exception as e:
            print(f"[FAIL] Error reading log file: {e}")
    else:
        print("\n[U+1F4ED] No posting log found")

    # Option to clear history
    print("\n" + "-"*60)
    clear = input("Clear posting history? (y/n): ").lower()
    if clear == 'y':
        try:
            if os.path.exists(posted_commits_file):
                os.remove(posted_commits_file)
                print("[OK] Cleared posted commits")
            if os.path.exists(log_file):
                os.remove(log_file)
                print("[OK] Cleared posting log")
            print("[REFRESH] History cleared - all commits can be posted again")
        except Exception as e:
            print(f"[FAIL] Error clearing history: {e}")

    input("\nPress Enter to continue...")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--holodae', '--holo', action='store_true', help='Run HoloDAE (Code Intelligence & Monitoring)')
    parser.add_argument('--amo', action='store_true', help='Run AMO DAE (Autonomous Moderation Operations)')
    parser.add_argument('--smd', action='store_true', help='Run Social Media DAE (012 Digital Twin)')
    parser.add_argument('--pqn', action='store_true', help='Run PQN Orchestration (Research & Alignment)')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')
    parser.add_argument('--no-lock', action='store_true', help='Disable instance lock (allow multiple instances)')
    parser.add_argument('--status', action='store_true', help='Check instance status and health')

    args = parser.parse_args()

    if args.status:
        check_instance_status()
        return
    elif args.youtube:
        asyncio.run(monitor_youtube(disable_lock=args.no_lock))
    elif args.holodae:
        run_holodae()
    elif args.amo:
        run_amo_dae()
    elif args.smd:
        run_social_media_dae()
    elif args.pqn:
        run_pqn_dae()
    elif args.all:
        asyncio.run(monitor_all_platforms())
    else:
        # Interactive menu - Check instances once at startup, then loop main menu
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)

        # Check for running instances once at startup
        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")
            duplicates = lock.check_duplicates(quiet=True)

            if duplicates:
                print(f"[U+26A0]️  FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                print("\nWhat would you like to do?")
                print("1. Kill all instances and continue")
                print("2. Show detailed status")
                print("3. Continue anyway (may cause conflicts)")
                print("4. Exit")
                print("-"*40)

                choice = input("Select option (1-4): ").strip()

                if choice == "1":
                    print("\n[U+1F5E1]️  Killing duplicate instances...")
                    killed_pids = []
                    failed_pids = []

                    current_pid = os.getpid()

                    for pid in duplicates:
                        if pid == current_pid:
                            continue  # Don't kill ourselves

                        try:
                            print(f"   [U+1F52A] Terminating PID {pid}...")
                            process = psutil.Process(pid)
                            process.terminate()  # Try graceful termination first

                            # Wait up to 5 seconds for process to terminate
                            gone, alive = psutil.wait_procs([process], timeout=5)

                            if alive:
                                # If still alive, force kill
                                print(f"   [U+1F480] Force killing PID {pid}...")
                                process.kill()
                                gone, alive = psutil.wait_procs([process], timeout=2)

                            if not alive:
                                killed_pids.append(pid)
                                print(f"   [OK] PID {pid} terminated successfully")
                            else:
                                failed_pids.append(pid)
                                print(f"   [FAIL] Failed to kill PID {pid}")

                        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                            print(f"   [U+26A0]️  Could not kill PID {pid}: {e}")
                            failed_pids.append(pid)

                    if killed_pids:
                        print(f"\n[OK] Successfully killed {len(killed_pids)} instance(s): {killed_pids}")
                    if failed_pids:
                        print(f"[U+26A0]️  Failed to kill {len(failed_pids)} instance(s): {failed_pids}")

                    print("   Proceeding to main menu...\n")

                elif choice == "2":
                    print("\n" + "="*50)
                    check_instance_status()
                    print("="*50)
                    input("\nPress Enter to continue...")
                    print("   Proceeding to main menu...\n")
                    # Continue to main menu after showing status

                elif choice == "3":
                    print("[U+26A0]️  Continuing with potential conflicts...\n")

                elif choice == "4":
                    print("[U+1F44B] Exiting...")
                    return

                else:
                    print("[FAIL] Invalid choice. Exiting...")
                    return

            else:
                print("[OK] NO RUNNING INSTANCES DETECTED")
                print("   Safe to start new DAEs")
                print("   [U+1F9F9] Browser cleanup will run on startup\n")

        except Exception as e:
            print(f"[U+26A0]️  Could not check instances: {e}")
            print("   Proceeding with menu...\n")

        print("[SEARCH] DEBUG: About to enter main menu loop")

        # Main menu loop (only reached after instance handling)
        while True:

            # Show the main menu
            print("0. [ROCKET] Push to Git and Post to LinkedIn + X (FoundUps)")
            print("1. [U+1F4FA] YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)")
            print("2. [AI] HoloDAE (Code Intelligence & Monitoring)")
            print("3. [U+1F528] AMO DAE (Autonomous Moderation Operations)")
            print("4. [U+1F4E2] Social Media DAE (012 Digital Twin)")
            print("5. [U+1F9EC] PQN Orchestration (Research & Alignment)")
            print("6. [U+1F310] All DAEs (Full System)")
            print("7. [U+1F49A] Check Instance Status & Health")
            print("8. [FAIL] Exit")
            print("-"*60)
            print("9. [SEARCH] HoloIndex Search (Find code semantically)")
            print("10. [CLIPBOARD] View Git Post History")
            print("="*60)

            choice = input("\nSelect option: ")

            if choice == "0":
                # Git push with LinkedIn and X posting
                git_push_and_post()
                # Will return to menu after completion

            elif choice == "1":
                # YouTube DAE Menu - Live Chat OR Shorts
                print("\n[U+1F4FA] YouTube DAE Menu")
                print("="*60)
                print("1. [U+1F534] YouTube Live Chat Monitor (AutoModeratorDAE)")
                print("2. [U+1F3AC] YouTube Shorts Generator (AI Baby/Emergence Journal)")
                print("3. [DATA] YouTube Stats & Info")
                print("0. [U+2B05]️  Back to Main Menu")
                print("="*60)

                yt_choice = input("\nSelect YouTube option: ")

                if yt_choice == "1":
                    print("[CAMERA] Starting YouTube Live Chat Monitor...")
                    asyncio.run(monitor_youtube(disable_lock=False))

                elif yt_choice == "2":
                    # YouTube Shorts Generator
                    print("\n[U+1F3AC] YouTube Shorts Generator")
                    print("="*60)
                    print("Channel: Move2Japan (9,020 subscribers)")
                    print("System: 3-Act Story (Setup -> Shock -> 0102 Reveal)")
                    print("="*60)

                    topic = input("\n[IDEA] Enter topic (e.g., 'Cherry blossoms in Tokyo'): ").strip()

                    if topic:
                        try:
                            from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

                            print(f"\n[U+1F3AC] Generating YouTube Short: {topic}")
                            print("  Mode: Emergence Journal POC")
                            print("  Duration: ~16s (2×8s clips merged)")
                            print("  Privacy: PUBLIC")

                            orchestrator = ShortsOrchestrator(channel="move2japan")

                            # Generate and upload with 3-act system
                            youtube_url = orchestrator.create_and_upload(
                                topic=topic,
                                duration=15,  # Triggers 3-act multi-clip system
                                enhance_prompt=True,
                                fast_mode=True,
                                privacy="public",
                                use_3act=True  # Enable emergence journal 3-act structure
                            )

                            print(f"\n[OK] SHORT PUBLISHED!")
                            print(f"   URL: {youtube_url}")
                            print(f"   Channel: Move2Japan")

                        except Exception as e:
                            print(f"\n[FAIL] YouTube Shorts generation failed: {e}")
                            import traceback
                            traceback.print_exc()
                    else:
                        print("[U+26A0]️  No topic entered - returning to menu")

                elif yt_choice == "3":
                    # YouTube Stats
                    print("\n[DATA] YouTube Stats")
                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator
                        orch = ShortsOrchestrator(channel="move2japan")
                        stats = orch.get_stats()

                        print(f"\n  Total Shorts: {stats['total_shorts']}")
                        print(f"  Uploaded: {stats['uploaded']}")
                        print(f"  Total Cost: ${stats['total_cost_usd']}")
                        print(f"  Avg Cost: ${stats['average_cost_per_short']}")

                        if stats['recent_shorts']:
                            print(f"\n  Recent Shorts:")
                            for s in stats['recent_shorts'][-3:]:
                                print(f"    - {s.get('topic', 'N/A')[:40]}...")
                                print(f"      {s.get('youtube_url', 'N/A')}")
                    except Exception as e:
                        print(f"[FAIL] Failed to get stats: {e}")

                elif yt_choice == "0":
                    print("[U+2B05]️  Returning to main menu...")
                else:
                    print("[FAIL] Invalid choice")

            elif choice == "2":
                # HoloDAE - Code Intelligence & Monitoring
                print("[AI] HoloDAE Menu - Code Intelligence & Monitoring System")
                try:
                    # Import menu function ONLY (don't start daemon yet)
                    from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

                    holodae_instance = None  # Initialize as None, created only when needed

                    while True:
                        choice = show_holodae_menu()

                        if choice == "0":
                            # Launch the daemon (option 0 in HoloDAE menu)
                            print("[ROCKET] Launching HoloDAE Autonomous Monitor...")
                            from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                            if holodae_instance is None:
                                holodae_instance = start_holodae_monitoring()
                                print("[OK] HoloDAE monitoring started in background")
                                print("[IDEA] Daemon is running - select 9 to stop, or 99 to return to main menu")
                            else:
                                print("[OK] HoloDAE already running")
                            # Don't break - loop back to HoloDAE menu for more selections
                        elif choice == "9":
                            # Stop the daemon (option 9 - toggle monitoring)
                            if holodae_instance is not None and holodae_instance.active:
                                print("[STOP] Stopping HoloDAE monitoring...")
                                holodae_instance.stop_autonomous_monitoring()
                                print("[OK] HoloDAE daemon stopped")
                            else:
                                print("ℹ️ HoloDAE daemon is not running")
                        elif choice == "99":
                            print("[AI] Returning to main menu...")
                            if holodae_instance is not None and holodae_instance.active:
                                print("[U+26A0]️ HoloDAE daemon still running in background")
                            break
                        elif choice == "1":
                            print("[DATA] Running semantic code search...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "2":
                            print("[SEARCH] Running dual search (code + WSP)...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "3":
                            print("[OK] Running module existence check...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --check-module 'module_name'")
                        elif choice == "4":
                            print("[U+1F3B2] Running DAE cube organizer...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --init-dae 'DAE_name'")
                        elif choice == "5":
                            print("[UP] Running index management...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --index-all")
                        elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                            print("[AI] Running HoloDAE intelligence analysis...")
                            # These would trigger HoloDAE analysis functions
                            print("Use HoloIndex search to trigger automatic analysis")
                        elif choice == "14":
                            print("[U+1F575]️ Running WSP 88 orphan analysis...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --wsp88")
                        elif choice == "16":
                            print("[ROCKET] Launching HoloDAE Autonomous Monitor...")
                            try:
                                # Start autonomous monitoring mode
                                holodae_instance.start_autonomous_monitoring()
                                print("[U+1F441]️ HoloDAE autonomous monitoring started!")
                                print("Monitoring codebase for changes, violations, and intelligence opportunities...")
                                print("Press Ctrl+C to stop monitoring and return to menu")
                                # This would block here until interrupted
                            except Exception as e:
                                print(f"[FAIL] Failed to launch monitor: {e}")
                        elif choice in ["15", "17", "18"]:
                            print("[CLIPBOARD] Running WSP compliance functions...")
                            # These would trigger compliance checking
                            print("Use HoloIndex search to trigger compliance analysis")
                        elif choice in ["19", "20", "21", "22", "23"]:
                            print("[BOT] Running AI advisor functions...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'query' --llm-advisor")
                        elif choice == "24":
                            print("[U+1F4FA] Launching YouTube Live DAE...")
                            # Would need to navigate to option 1
                            print("Please select option 1 from main menu for YouTube DAE")
                        elif choice == "25":
                            print("[AI] Starting autonomous HoloDAE monitoring...")
                            run_holodae()
                            break  # Exit menu after starting monitoring
                        elif choice == "6":
                            print("[AI] Launching Chain-of-Thought Brain Logging...")
                            try:
                                from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                                demonstrate_brain_logging()
                                print("\n[AI] BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                                print("[IDEA] This shows exactly how the AI brain works - completely observable!")
                            except Exception as e:
                                print(f"[FAIL] Brain logging failed: {e}")
                            input("\nPress Enter to continue...")
                        elif choice in ["26", "27", "28", "29", "30"]:
                            print("[U+1F3B2] This DAE operation requires main menu selection...")
                            # Would need to navigate to appropriate main menu option
                            print("Please return to main menu and select the appropriate DAE")
                        elif choice in ["31", "32", "33", "34", "35"]:
                            print("[U+2699]️ Running administrative functions...")
                            # These would trigger admin functions
                            print("Administrative functions available through main menu")
                        else:
                            print("[FAIL] Invalid choice. Please select 0-35.")

                        input("\nPress Enter to continue...")

                except Exception as e:
                    print(f"[FAIL] HoloDAE menu failed to load: {e}")
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
                # PQN Orchestration
                print("[AI] Starting PQN Research DAE...")
                from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
                pqn_dae = PQNResearchDAEOrchestrator()
                asyncio.run(pqn_dae.run())

            elif choice == "6":
                # All platforms
                print("[ALL] Starting ALL DAEs...")
                asyncio.run(monitor_all_platforms())

            elif choice == "7":
                # Check instance status
                check_instance_status()
                input("\nPress Enter to continue...")

            elif choice == "8":
                print("[EXIT] Exiting...")
                break  # Exit the while True loop

            elif choice == "9":
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

            elif choice == "10":
                # View git post history
                view_git_post_history()

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

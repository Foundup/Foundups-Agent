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
                logger.warning(f"🔴 Duplicate main.py Instances Detected!")
                print("\n🔴 Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} instances of main.py running:")
                for i, pid in enumerate(duplicates, 1):
                    print(f"\n  {i}. PID {pid} - [Checking process details...]")
                print("\n  Current instance will exit to prevent conflicts.")
                print("  Kill duplicates with: taskkill /F /PID <PID>")
                print("  Or run with --no-lock to allow multiple instances.")
                return  # Exit instead of proceeding

            # Attempt to acquire lock (will return False if another instance is running)
            if not lock.acquire():
                logger.error("❌ Failed to acquire instance lock - another instance is running")
                print("\n❌ Failed to acquire instance lock!")
                print("   Another YouTube monitor instance is already running.")
                print("   Only one instance can run at a time to prevent API conflicts.")
                print("   Use --no-lock to disable instance locking.")
                return  # Exit if lock acquisition failed
        else:
            logger.info("🔓 Instance lock disabled (--no-lock flag used)")

        try:
            # Import the proper YouTube DAE that runs the complete flow:
            # 1. Stream resolver detects stream
            # 2. LinkedIn and X posts trigger
            # 3. Chat monitoring begins
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

            logger.info("Starting YouTube DAE with 0102 consciousness...")
            logger.info("Flow: Stream Detection → Social Posts → Chat Monitoring")

            # Create and run the DAE with enhanced error handling
            dae = AutoModeratorDAE()

            # Log instance monitoring information (duplicate check already done in menu)
            try:
                instance_summary = lock.get_instance_summary()
                current_pid = instance_summary["current_pid"]
                logger.info(f"✅ YouTube DAE started: PID {current_pid}")
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
                                logger.warning(f"🚨 INSTANCE ALERT: {total_instances} YouTube DAEs active")
                                for instance in instance_summary["instances"]:
                                    if not instance["is_current"]:
                                        logger.warning(f"  ⚠️ Other instance PID {instance['pid']} ({instance['age_minutes']:.1f}min old)")
                            elif total_instances == 1:
                                logger.info(f"✅ SINGLE INSTANCE: PID {instance_summary['current_pid']} - No other YouTube DAEs detected")
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
                                logger.info(f"✅ SINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")
                            elif total_instances > 1:
                                logger.warning(f"🚨 MULTIPLE INSTANCES: {total_instances} YouTube DAEs active (PID: {current_pid})")
                            else:
                                logger.info("ℹ️ No YouTube DAEs currently active")

                            last_minute_log = now
                        except Exception as e:
                            logger.debug(f"Minute status check failed: {e}")

                    await dae.run()  # This runs the complete loop
                    logger.info("🔄 Stream ended or became inactive - seamless switching engaged")
                    consecutive_failures = 0  # Reset on clean exit
                    await asyncio.sleep(5)  # Quick transition before looking for new stream
                except KeyboardInterrupt:
                    logger.info("⏹️ Monitoring stopped by user")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"YouTube DAE failed (attempt #{consecutive_failures}): {e}")
                    wait_time = min(30 * (2 ** consecutive_failures), 600)  # Exponential backoff, max 10 minutes
                    logger.info(f"🔄 Restarting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    if consecutive_failures >= 5:
                        logger.warning("🔄 Too many failures - attempting full reconnection")
                        dae = AutoModeratorDAE()  # Reinitialize for fresh connection
                        consecutive_failures = 0

            # Optionally log status (if supported by DAE)
            if hasattr(dae, 'get_status'):
                status = dae.get_status()
                logger.info(f"YouTube DAE Status: {status}")

        finally:
            # Release the instance lock when done
            lock.release()
            logger.info("🔓 YouTube monitor instance lock released")

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

    print("\n🔍 HoloIndex Semantic Search")
    print("=" * 60)

    try:
        # Check if HoloIndex is available (prefer root version)
        if os.path.exists("holo_index.py"):
            holo_cmd = ['python', 'holo_index.py', '--search', query]
        elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
            # Fallback to E: drive version
            holo_cmd = ['python', r"E:\HoloIndex\enhanced_holo_index.py", '--search', query]
        else:
            print("⚠️ HoloIndex not found")
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
            print(f"❌ Search failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"❌ HoloIndex error: {e}")
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
        logger.warning("🔴 Duplicate HoloDAE Instances Detected!")
        print("\n🔴 Duplicate HoloDAE Instances Detected!")
        print(f"\n  Found {len(duplicates)} instances of HoloDAE running:")
        for i, pid in enumerate(duplicates, 1):
            print(f"\n  {i}. PID {pid} - [Checking process details...]")
        print("\n  Current instance will exit to prevent conflicts.")
        print("  Use --no-lock to disable instance locking.")
        return  # Exit if duplicates found

    # Acquire lock for this instance
    if not lock.acquire():
        logger.error("❌ Failed to acquire HoloDAE instance lock - another instance is running")
        print("\n❌ Failed to acquire HoloDAE instance lock!")
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
        logger.info(f"✅ HoloDAE SINGLE INSTANCE: PID {current_pid} - No other HoloDAEs detected")

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
        logger.info("🔓 HoloDAE monitor instance lock released")


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
    print("👥 Starting Social Media DAE (012 Digital Twin)...")
    try:
        from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
        orchestrator = SocialMediaOrchestrator()
        # TODO: Implement digital twin mode
        print("Digital Twin mode coming soon...")
        print("Social Media DAE orchestration available for development.")
    except Exception as e:
        print(f"❌ Social Media DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_pqn_dae():
    """Run PQN Orchestration (Research & Alignment)."""
    print("🧠 Starting PQN Research DAE...")
    try:
        from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
        pqn_dae = PQNResearchDAEOrchestrator()
        asyncio.run(pqn_dae.run())
    except Exception as e:
        print(f"❌ PQN DAE failed: {e}")
        import traceback
        traceback.print_exc()


def run_evade_net():
    """Run Liberty Alert Mesh Alert System (Community Protection)."""
    print("🚨 Starting Liberty Alert - Mesh Alert System...")
    print("📡 Offline P2P alerts for community protection")
    try:
        from modules.communication.liberty_alert.src.liberty_alert_orchestrator import LibertyAlertOrchestrator
        from modules.communication.liberty_alert.src.models import LibertyAlertConfig

        # Configure Liberty Alert
        config = LibertyAlertConfig(
            mesh_enabled=True,
            voice_enabled=True,
            default_language="es",
            alert_radius_km=5.0,
        )

        orchestrator = LibertyAlertOrchestrator(config)
        asyncio.run(orchestrator.run())
    except Exception as e:
        print(f"❌ Liberty Alert failed: {e}")
        import traceback
        traceback.print_exc()


def check_instance_status():
    """Check the status and health of running instances."""
    print("\n" + "="*60)
    print("🔍 INSTANCE STATUS CHECK")
    print("="*60)

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

        lock = get_instance_lock("youtube_monitor")

        # Check for running instances
        duplicates = lock.check_duplicates()

        if duplicates:
            print(f"❌ Found {len(duplicates)} duplicate instances running")
            return
        else:
            print("✅ No duplicate instances detected")

        # Check lock file status
        if lock.lock_file.exists():
            print("🔒 Lock file exists:")
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
                    print("   Status: ✅ RUNNING")
                else:
                    print("   Status: ❌ PROCESS NOT FOUND (stale lock)")

            except Exception as e:
                print(f"   Error reading lock file: {e}")
        else:
            print("🔓 No lock file found (no instances running)")

        # Check health status
        health = lock.get_health_status()
        print("\n🏥 Health Status:")
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Message: {health.get('message', 'no data')}")
        if 'timestamp' in health:
            print(f"   Last update: {health['timestamp']}")

        # Check HoloDAE instances
        print("\n" + "-"*40)
        print("🤖 HOLO-DAE STATUS")
        print("-"*40)

        try:
            holodae_lock = get_instance_lock("holodae_monitor")

            # Check for running HoloDAE instances
            holodae_duplicates = holodae_lock.check_duplicates()

            if holodae_duplicates:
                print(f"❌ Found {len(holodae_duplicates)} HoloDAE instances running")
                return
            else:
                print("✅ No duplicate HoloDAE instances detected")

            # Check HoloDAE lock file status
            if holodae_lock.lock_file.exists():
                print("🔒 HoloDAE Lock file exists:")
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
                        print("   Status: ✅ RUNNING")
                    else:
                        print("   Status: ❌ PROCESS NOT FOUND (stale lock)")

                except Exception as e:
                    print(f"   Error reading lock file: {e}")
            else:
                print("🔓 No HoloDAE lock file found (no instances running)")

            # Check HoloDAE health status
            holodae_health = holodae_lock.get_health_status()
            print("\n🏥 HoloDAE Health Status:")
            print(f"   Status: {holodae_health.get('status', 'unknown')}")
            print(f"   Message: {holodae_health.get('message', 'no data')}")
            if 'timestamp' in holodae_health:
                print(f"   Last update: {holodae_health['timestamp']}")

        except Exception as e:
            print(f"❌ Error checking HoloDAE status: {e}")

    except Exception as e:
        print(f"❌ Error checking status: {e}")

    print()


def generate_x_content(commit_msg, file_count):
    """Generate compelling X/Twitter content (280 char limit)"""
    import random

    # Short punchy intros for X
    x_intros = [
        "🦄 FoundUps by @UnDaoDu\n\nDAEs eating startups for breakfast.\n\n",
        "⚡ Startups die. FoundUps are forever.\n\n",
        "🚀 No VCs. No employees. Just you + ∞ agents.\n\n",
        "💡 Solo unicorns are real. Ask @UnDaoDu.\n\n",
        "🌊 The startup killer is here.\n\n"
    ]

    content = random.choice(x_intros)

    # Add brief update
    if "fix" in commit_msg.lower():
        content += f"🔧 {file_count} fixes by 0102 agents\n\n"
    elif "test" in commit_msg.lower():
        content += f"🧪 Testing future: {file_count} files\n\n"
    else:
        content += f"⚡ {file_count} autonomous updates\n\n"

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


def launch_git_push_dae():
    """
    Launch GitPushDAE daemon with WSP 91 full observability.
    Transforms git push from human-triggered action to autonomous DAE.
    """
    print("\n" + "="*60)
    print("🚀 GIT PUSH DAE - AUTONOMOUS DEVELOPMENT")
    print("="*60)
    print("WSP 91 DAEMON: Fully autonomous git push with observability")
    print("No human decision required - agentic parameters drive decisions")
    print("="*60)

    try:
        # Import and launch the GitPushDAE
        from modules.infrastructure.git_push_dae.src.git_push_dae import GitPushDAE

        # Create and start the daemon
        dae = GitPushDAE(domain="foundups_development", check_interval=300)  # 5-minute checks
        dae.start()

        print("\n✅ GitPushDAE launched successfully!")
        print("📊 Monitor logs at: logs/git_push_dae.log")
        print("🛑 Press Ctrl+C to stop the daemon")

        try:
            # Keep running until interrupted
            while dae.active:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping GitPushDAE...")
            dae.stop()

    except ImportError as e:
        print(f"❌ Failed to import GitPushDAE: {e}")
        print("Falling back to legacy git_push_and_post...")

        # Fallback to old method
        git_push_and_post()

    except Exception as e:
        print(f"❌ GitPushDAE failed: {e}")
        input("\nPress Enter to continue...")


def git_push_and_post():
    """
    LEGACY: Git push with automatic social media posting.
    Uses the git_linkedin_bridge module to handle posting.
    DEPRECATED: Use GitPushDAE instead for full autonomy.
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge

    print("\n" + "="*60)
    print("GIT PUSH & LINKEDIN + X POST (FoundUps)")
    print("="*60)
    print("⚠️  LEGACY MODE: Consider using GitPushDAE for full autonomy")

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
    print("📊 GIT POST HISTORY")
    print("="*60)

    # Check posted commits
    posted_commits_file = "memory/git_posted_commits.json"
    if os.path.exists(posted_commits_file):
        try:
            with open(posted_commits_file, 'r') as f:
                posted_commits = json.load(f)
                print(f"\n✅ {len(posted_commits)} commits posted to social media")
                print("\nPosted commit hashes:")
                for commit in posted_commits[-10:]:  # Show last 10
                    print(f"  • {commit}")
                if len(posted_commits) > 10:
                    print(f"  ... and {len(posted_commits) - 10} more")
        except Exception as e:
            print(f"❌ Error reading posted commits: {e}")
    else:
        print("📭 No posted commits found")

    # Check detailed log
    log_file = "memory/git_post_log.json"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                log_entries = json.load(f)
                print(f"\n📋 Detailed posting log ({len(log_entries)} entries):")
                print("-" * 60)

                # Show last 5 entries
                for entry in log_entries[-5:]:
                    timestamp = entry.get('timestamp', 'Unknown')
                    commit_msg = entry.get('commit_msg', 'No message')[:50]
                    linkedin = "✅" if entry.get('linkedin') else "❌"
                    x_twitter = "✅" if entry.get('x_twitter') else "❌"
                    files = entry.get('file_count', 0)

                    print(f"\n📌 {timestamp[:19]}")
                    print(f"   Commit: {commit_msg}...")
                    print(f"   Files: {files}")
                    print(f"   LinkedIn: {linkedin}  X/Twitter: {x_twitter}")

                if len(log_entries) > 5:
                    print(f"\n... and {len(log_entries) - 5} more entries")

                # Stats
                total_posts = len(log_entries)
                linkedin_success = sum(1 for e in log_entries if e.get('linkedin'))
                x_success = sum(1 for e in log_entries if e.get('x_twitter'))

                print("\n📈 Statistics:")
                print(f"   Total posts: {total_posts}")
                print(f"   LinkedIn success rate: {linkedin_success}/{total_posts} ({linkedin_success*100//max(total_posts,1)}%)")
                print(f"   X/Twitter success rate: {x_success}/{total_posts} ({x_success*100//max(total_posts,1)}%)")

        except Exception as e:
            print(f"❌ Error reading log file: {e}")
    else:
        print("\n📭 No posting log found")

    # Option to clear history
    print("\n" + "-"*60)
    clear = input("Clear posting history? (y/n): ").lower()
    if clear == 'y':
        try:
            if os.path.exists(posted_commits_file):
                os.remove(posted_commits_file)
                print("✅ Cleared posted commits")
            if os.path.exists(log_file):
                os.remove(log_file)
                print("✅ Cleared posting log")
            print("🔄 History cleared - all commits can be posted again")
        except Exception as e:
            print(f"❌ Error clearing history: {e}")

    input("\nPress Enter to continue...")


def run_training_system():
    """
    Qwen/Gemma Training System - Pattern Learning from 012.txt
    Implements WRE pattern (WSP 46): Learn from 0102's operational decisions
    """
    from holo_index.qwen_advisor.pattern_memory import PatternMemory
    import asyncio

    while True:
        print("\n" + "="*60)
        print("🤖 QWEN/GEMMA TRAINING SYSTEM")
        print("="*60)
        print("Implements WRE Pattern (WSP 46): Qwen coordinates, Gemma executes")
        print("Training Data: 012.txt (28K+ lines of 0102 operational decisions)")
        print("="*60)

        # Get stats
        try:
            memory = PatternMemory()
            stats = memory.get_stats()

            print(f"\n📊 CURRENT STATUS:")
            print(f"   Patterns Stored: {stats['total_patterns']}")
            print(f"   012.txt Progress: {stats['checkpoint_line']}/28326 ({stats['checkpoint_line']/283.26:.1f}%)")
            print(f"   Verification Rate: {stats['verification_rate']:.1%}")
            print(f"   Sources: {stats['sources']}")

        except Exception as e:
            print(f"⚠️  Could not load stats: {e}")
            print(f"   Pattern memory may need initialization")

        print("\n" + "-"*60)
        print("TRAINING OPTIONS:")
        print("-"*60)
        print("1. 🏃 Start Batch Training (Process 012.txt)")
        print("2. 📊 View Training Progress")
        print("3. 🧪 Test Pattern Recall")
        print("4. 🔄 Test Qwen/Gemma Routing (Adaptive AI)")
        print("5. 📈 View Training Metrics")
        print("6. 🗑️  Clear Pattern Memory (Reset)")
        print("7. 🔙 Back to Main Menu")
        print("-"*60)

        choice = input("\nSelect option (1-7): ").strip()

        if choice == "1":
            # Batch training
            print("\n🏃 Starting Batch Training...")
            print("="*60)

            try:
                from modules.infrastructure.idle_automation.src.idle_automation_dae import IdleAutomationDAE

                # Create DAE and run training phase
                dae = IdleAutomationDAE()
                result = asyncio.run(dae._execute_pattern_training())

                print(f"\n[RESULT]")
                print(f"  Success: {'✅ Yes' if result['success'] else '❌ No'}")
                print(f"  Patterns Stored: {result['patterns_stored']}")
                print(f"  Lines Processed: {result['lines_processed']}")
                print(f"  Duration: {result['duration']:.1f}s")

                if 'progress' in result:
                    print(f"  Progress: {result['progress']}")

                if 'error' in result:
                    print(f"  Error: {result['error']}")

            except Exception as e:
                print(f"❌ Batch training failed: {e}")

            input("\nPress Enter to continue...")

        elif choice == "2":
            # View progress
            print("\n📊 Training Progress")
            print("="*60)

            try:
                memory = PatternMemory()
                stats = memory.get_stats()

                total_lines = 28326
                processed = stats['checkpoint_line']
                remaining = total_lines - processed
                progress_pct = (processed / total_lines) * 100

                print(f"\n📈 Progress:")
                print(f"   Total Lines: {total_lines:,}")
                print(f"   Processed: {processed:,} ({progress_pct:.1f}%)")
                print(f"   Remaining: {remaining:,}")
                print(f"   Estimated Chunks: {remaining // 1000} @ 1000 lines/chunk")

                print(f"\n🗂️  Pattern Storage:")
                print(f"   Total Patterns: {stats['total_patterns']}")
                print(f"   Verified: {int(stats['total_patterns'] * stats['verification_rate'])}")
                print(f"   Verification Rate: {stats['verification_rate']:.1%}")

                if stats['sources']:
                    print(f"\n📚 Sources:")
                    for source, count in stats['sources'].items():
                        print(f"   {source}: {count} patterns")

                # Progress bar
                bar_width = 40
                filled = int(bar_width * progress_pct / 100)
                bar = '█' * filled + '░' * (bar_width - filled)
                print(f"\n[{bar}] {progress_pct:.1f}%")

            except Exception as e:
                print(f"❌ Could not load progress: {e}")

            input("\nPress Enter to continue...")

        elif choice == "3":
            # Test pattern recall
            print("\n🧪 Test Pattern Recall")
            print("="*60)
            print("Enter a query to test Gemma pattern recall:")
            print("Examples:")
            print("  - 'Which module handles YouTube authentication?'")
            print("  - 'How does priority scoring work?'")
            print("  - 'Where should test files be placed?'")
            print("="*60)

            query = input("\nQuery: ").strip()

            if not query:
                print("⚠️  No query entered")
                input("\nPress Enter to continue...")
                continue

            try:
                memory = PatternMemory()
                patterns = memory.recall_similar(query, n=5, min_similarity=0.3)

                if patterns:
                    print(f"\n✅ Found {len(patterns)} similar patterns:\n")

                    for i, pattern in enumerate(patterns, 1):
                        print(f"Pattern {i}:")
                        print(f"  ID: {pattern['id']}")
                        print(f"  Similarity: {pattern['similarity']:.2f}")
                        print(f"  Context: {pattern['context'][:100]}...")
                        print(f"  Module: {pattern['metadata'].get('module', 'unknown')}")
                        print()
                else:
                    print(f"\n❌ No patterns found above similarity threshold (0.3)")

            except Exception as e:
                print(f"❌ Pattern recall failed: {e}")

            input("\nPress Enter to continue...")

        elif choice == "4":
            # Test Gemma/Qwen routing
            print("\n🔄 Qwen/Gemma Routing Test")
            print("="*60)
            print("WRE Pattern: 012 → 0102 → Qwen (Coordinator) → Gemma (Executor)")
            print("="*60)

            try:
                from pathlib import Path
                from holo_index.qwen_advisor.gemma_rag_inference import GemmaRAGInference

                # Initialize inference engine with correct model paths
                gemma_path = Path("E:/HoloIndex/models/gemma-3-270m-it-Q4_K_M.gguf")
                qwen_path = Path("E:/HoloIndex/models/qwen-coder-1.5b.gguf")

                if not gemma_path.exists() or not qwen_path.exists():
                    print(f"\n❌ Models not found:")
                    if not gemma_path.exists():
                        print(f"   Missing: {gemma_path}")
                    if not qwen_path.exists():
                        print(f"   Missing: {qwen_path}")
                    print("\n   Download models and place in E:/HoloIndex/models/")
                    input("\nPress Enter to continue...")
                    continue

                print("\n✓ Initializing Gemma/Qwen routing engine...")
                engine = GemmaRAGInference(
                    gemma_model_path=gemma_path,
                    qwen_model_path=qwen_path,
                    confidence_threshold=0.7
                )

                # Test queries menu
                while True:
                    print("\n" + "-"*60)
                    print("TEST QUERIES:")
                    print("-"*60)
                    print("1. Which module handles YouTube authentication? (simple)")
                    print("2. How does priority scoring work? (medium)")
                    print("3. Why did Move2Japan get score 1.00? (complex)")
                    print("4. Where should test files be placed? (simple)")
                    print("5. Custom query")
                    print("6. View performance stats")
                    print("7. Back to training menu")
                    print("-"*60)

                    query_choice = input("\nSelect option (1-7): ").strip()

                    if query_choice == "1":
                        query = "Which module handles YouTube authentication?"
                    elif query_choice == "2":
                        query = "How does priority scoring work?"
                    elif query_choice == "3":
                        query = "Why did Move2Japan get score 1.00?"
                    elif query_choice == "4":
                        query = "Where should test files be placed?"
                    elif query_choice == "5":
                        query = input("\nEnter your query: ").strip()
                        if not query:
                            print("❌ No query entered")
                            continue
                    elif query_choice == "6":
                        # Show stats
                        stats = engine.get_stats()
                        print("\n📊 ROUTING PERFORMANCE:")
                        print(f"   Total Queries: {stats['total_queries']}")
                        print(f"   Gemma Handled: {stats['gemma_handled']} ({stats['gemma_percentage']:.1f}%)")
                        print(f"   Qwen Escalated: {stats['qwen_escalated']} ({stats['qwen_percentage']:.1f}%)")
                        print(f"\n🎯 TARGET: 70% Gemma / 30% Qwen")
                        print(f"   ACTUAL: {stats['gemma_percentage']:.1f}% Gemma / {stats['qwen_percentage']:.1f}% Qwen")

                        if 50 <= stats['gemma_percentage'] <= 90:
                            print("\n✓ Performance within target range!")
                        else:
                            print("\n⚠️  Performance needs tuning")

                        input("\nPress Enter to continue...")
                        continue
                    elif query_choice == "7":
                        print("🔙 Returning to training menu...")
                        break
                    else:
                        print(f"❌ Invalid choice '{query_choice}'")
                        continue

                    # Run inference
                    print(f"\n[QUERY] {query}")
                    print("⏱️  Processing...")

                    result = engine.infer(query)

                    print(f"\n[RESULT]")
                    print(f"   Model Used: {result.model_used}")
                    print(f"   Latency: {result.latency_ms}ms")
                    print(f"   Confidence: {result.confidence:.2f}")
                    print(f"   Patterns Used: {result.patterns_used}")

                    if result.escalated:
                        print(f"   ⬆️  Escalated: {result.escalation_reason}")

                    print(f"\n[RESPONSE]")
                    print(f"   {result.response}")

                    input("\nPress Enter to continue...")

            except Exception as e:
                print(f"\n❌ Routing test failed: {e}")
                import traceback
                traceback.print_exc()

            input("\nPress Enter to continue...")

        elif choice == "5":
            # View metrics
            print("\n📈 Training Metrics")
            print("="*60)

            try:
                memory = PatternMemory()
                stats = memory.get_stats()

                print(f"\n🎯 Performance Metrics:")
                print(f"   Total Patterns: {stats['total_patterns']}")
                print(f"   Verification Rate: {stats['verification_rate']:.1%}")
                print(f"   Storage Location: holo_index/memory/chroma/")

                print(f"\n📊 Training Coverage:")
                print(f"   Lines Processed: {stats['checkpoint_line']:,} / 28,326")
                print(f"   Progress: {stats['checkpoint_line']/283.26:.1f}%")

                print(f"\n🔍 Pattern Distribution:")
                if stats['sources']:
                    for source, count in stats['sources'].items():
                        pct = (count / stats['total_patterns'] * 100) if stats['total_patterns'] > 0 else 0
                        print(f"   {source}: {count} ({pct:.1f}%)")

                print(f"\n💾 Storage Stats:")
                print(f"   Database: ChromaDB (vector embeddings)")
                print(f"   Checkpoint File: checkpoint.txt")
                print(f"   Training Method: In-context learning (RAG)")
                print(f"   Cost: $0 (no fine-tuning)")

            except Exception as e:
                print(f"❌ Could not load metrics: {e}")

            input("\nPress Enter to continue...")

        elif choice == "6":
            # Clear memory
            print("\n🗑️  Clear Pattern Memory")
            print("="*60)
            print("⚠️  WARNING: This will delete ALL stored patterns!")
            print("   - Pattern memory will be reset to empty")
            print("   - Checkpoint will be reset to 0")
            print("   - Training will need to restart from beginning")
            print("="*60)

            confirm = input("\nType 'CONFIRM' to proceed: ").strip()

            if confirm == "CONFIRM":
                try:
                    memory = PatternMemory()
                    memory.clear_all(confirm=True)
                    memory.save_checkpoint(0)
                    print("\n✅ Pattern memory cleared successfully")
                    print("   All patterns deleted")
                    print("   Checkpoint reset to 0")
                except Exception as e:
                    print(f"❌ Clear failed: {e}")
            else:
                print("\n❌ Clear aborted - memory preserved")

            input("\nPress Enter to continue...")

        elif choice == "7":
            # Back to main menu
            print("🔙 Returning to main menu...")
            break

        else:
            print(f"❌ Invalid choice '{choice}'. Please enter 1-7.")
            input("\nPress Enter to continue...")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--git', action='store_true', help='Launch GitPushDAE (autonomous git push + social posting)')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--holodae', '--holo', action='store_true', help='Run HoloDAE (Code Intelligence & Monitoring)')
    parser.add_argument('--amo', action='store_true', help='Run AMO DAE (Autonomous Moderation Operations)')
    parser.add_argument('--smd', action='store_true', help='Run Social Media DAE (012 Digital Twin)')
    parser.add_argument('--pqn', action='store_true', help='Run PQN Orchestration (Research & Alignment)')
    parser.add_argument('--liberty', action='store_true', help='Run Liberty Alert Mesh Alert System (Community Protection)')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')
    parser.add_argument('--no-lock', action='store_true', help='Disable instance lock (allow multiple instances)')
    parser.add_argument('--status', action='store_true', help='Check instance status and health')

    args = parser.parse_args()

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
    elif args.pqn:
        run_pqn_dae()
    elif args.liberty:
        run_evade_net()
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
                # Loop until user makes a valid choice
                while True:
                    print(f"⚠️  FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                    print("\nWhat would you like to do?")
                    print("1. Kill all instances and continue")
                    print("2. Show detailed status")
                    print("3. Continue anyway (may cause conflicts)")
                    print("4. Exit")
                    print("-"*40)

                    # Get user input and clean it (remove brackets, spaces, etc.)
                    choice = input("Select option (1-4): ").strip().lstrip(']').lstrip('[')

                    if choice == "1":
                        print("\n🗡️  Killing duplicate instances...")
                        killed_pids = []
                        failed_pids = []

                        current_pid = os.getpid()

                        for pid in duplicates:
                            if pid == current_pid:
                                continue  # Don't kill ourselves

                            try:
                                print(f"   🔪 Terminating PID {pid}...")
                                process = psutil.Process(pid)
                                process.terminate()  # Try graceful termination first

                                # Wait up to 5 seconds for process to terminate
                                gone, alive = psutil.wait_procs([process], timeout=5)

                                if alive:
                                    # If still alive, force kill
                                    print(f"   💀 Force killing PID {pid}...")
                                    process.kill()
                                    gone, alive = psutil.wait_procs([process], timeout=2)

                                if not alive:
                                    killed_pids.append(pid)
                                    print(f"   ✅ PID {pid} terminated successfully")
                                else:
                                    failed_pids.append(pid)
                                    print(f"   ❌ Failed to kill PID {pid}")

                            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                print(f"   ⚠️  Could not kill PID {pid}: {e}")
                                failed_pids.append(pid)

                        if killed_pids:
                            print(f"\n✅ Successfully killed {len(killed_pids)} instance(s): {killed_pids}")
                        if failed_pids:
                            print(f"⚠️  Failed to kill {len(failed_pids)} instance(s): {failed_pids}")

                        print("   Proceeding to main menu...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "2":
                        print("\n" + "="*50)
                        check_instance_status()
                        print("="*50)
                        input("\nPress Enter to continue...")
                        # Don't break - loop back to menu

                    elif choice == "3":
                        print("⚠️  Continuing with potential conflicts...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "4":
                        print("👋 Exiting...")
                        return  # Exit entire program

                    else:
                        print(f"❌ Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.")
                        print("   Try again...\n")
                        # Don't break - loop will continue and ask again
                        continue

            else:
                print("✅ NO RUNNING INSTANCES DETECTED")
                print("   Safe to start new DAEs")
                print("   🧹 Browser cleanup will run on startup\n")

        except Exception as e:
            print(f"⚠️  Could not check instances: {e}")
            print("   Proceeding with menu...\n")

        print("🔍 DEBUG: About to enter main menu loop")

        # Main menu loop (only reached after instance handling)
        while True:

            # Show the main menu
            print("0. 🚀 Push to Git and Post to LinkedIn + X (FoundUps)  │ --git")
            print("1. 📺 YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)  │ --youtube")
            print("2. 🧠 HoloDAE (Code Intelligence & Monitoring)       │ --holodae")
            print("3. 🔨 AMO DAE (Autonomous Moderation Operations)     │ --amo")
            print("4. 📢 Social Media DAE (012 Digital Twin)            │ --smd")
            print("5. 🧬 PQN Orchestration (Research & Alignment)       │ --pqn")
            print("6. 🚨 Liberty Alert (Mesh Alert System)              │ --liberty")
            print("7. 🌐 All DAEs (Full System)                         │ --all")
            print("8. 💚 Check Instance Status & Health                 │ --status")
            print("9. ❌ Exit")
            print("-"*60)
            print("10. 🔍 HoloIndex Search (Find code semantically)")
            print("11. 📋 View Git Post History")
            print("12. 🤖 Qwen/Gemma Training System (Pattern Learning)")
            print("="*60)
            print("💡 CLI: --youtube --no-lock (bypass menu + instance lock)")
            print("="*60)

            choice = input("\nSelect option: ")

            if choice == "0":
                # Launch GitPushDAE daemon (WSP 91 compliant)
                launch_git_push_dae()
                # Will return to menu after completion

            elif choice == "1":
                # YouTube DAE Menu - Live Chat OR Shorts
                print("\n📺 YouTube DAE Menu")
                print("="*60)
                print("1. 🔴 YouTube Live Chat Monitor (AutoModeratorDAE)")
                print("2. 🎬 YouTube Shorts Generator (Gemini/Veo 3)")
                print("3. 🎥 YouTube Shorts Generator (Sora2 Live Action)")
                print("4. 📊 YouTube Stats & Info")
                print("0. ⬅️  Back to Main Menu")
                print("="*60)

                yt_choice = input("\nSelect YouTube option: ")

                def run_shorts_flow(engine_label: str, system_label: str, mode_label: str, duration_label: str, engine_key: str) -> None:
                    print(f"\n🎬 YouTube Shorts Generator [{engine_label}]")
                    print("="*60)
                    print("Channel: Move2Japan (9,020 subscribers)")
                    print(f"System: {system_label}")
                    print("="*60)

                    topic = input("\n💡 Enter topic (e.g., 'Cherry blossoms in Tokyo'): ").strip()

                    if not topic:
                        print("⚠️  No topic entered - returning to menu")
                        return

                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator

                        print(f"\n🎬 Generating YouTube Short ({engine_label}): {topic}")
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

                        print(f"\n✅ SHORT PUBLISHED!")
                        print(f"   URL: {youtube_url}")
                        print(f"   Channel: Move2Japan")

                    except Exception as e:
                        print(f"\n❌ YouTube Shorts generation failed: {e}")
                        import traceback
                        traceback.print_exc()

                if yt_choice == "1":
                    print("🎥 Starting YouTube Live Chat Monitor...")
                    asyncio.run(monitor_youtube(disable_lock=False))

                elif yt_choice == "2":
                    run_shorts_flow(
                        engine_label="Gemini/Veo 3",
                        system_label="3-Act Story (Setup → Shock → 0102 Reveal)",
                        mode_label="Emergence Journal POC",
                        duration_label="~16s (2×8s clips merged)",
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
                    print("\n📊 YouTube Stats")
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
                        print(f"❌ Failed to get stats: {e}")

                elif yt_choice == "0":
                    print("⬅️  Returning to main menu...")
                else:
                    print("❌ Invalid choice")

            elif choice == "2":
                # HoloDAE - Code Intelligence & Monitoring
                print("🧠 HoloDAE Menu - Code Intelligence & Monitoring System")
                try:
                    # Import menu function ONLY (don't start daemon yet)
                    from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

                    holodae_instance = None  # Initialize as None, created only when needed

                    while True:
                        choice = show_holodae_menu()

                        if choice == "0":
                            # Launch the daemon (option 0 in HoloDAE menu)
                            print("🚀 Launching HoloDAE Autonomous Monitor...")
                            from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                            if holodae_instance is None:
                                holodae_instance = start_holodae_monitoring()
                                print("✅ HoloDAE monitoring started in background")
                                print("💡 Daemon is running - select 9 to stop, or 99 to return to main menu")
                            else:
                                print("✅ HoloDAE already running")
                            # Don't break - loop back to HoloDAE menu for more selections
                        elif choice == "9":
                            # Stop the daemon (option 9 - toggle monitoring)
                            if holodae_instance is not None and holodae_instance.active:
                                print("🛑 Stopping HoloDAE monitoring...")
                                holodae_instance.stop_autonomous_monitoring()
                                print("✅ HoloDAE daemon stopped")
                            else:
                                print("ℹ️ HoloDAE daemon is not running")
                        elif choice == "99":
                            print("🧠 Returning to main menu...")
                            if holodae_instance is not None and holodae_instance.active:
                                print("⚠️ HoloDAE daemon still running in background")
                            break
                        elif choice == "1":
                            print("📊 Running semantic code search...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "2":
                            print("🔍 Running dual search (code + WSP)...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'your query'")
                        elif choice == "3":
                            print("✅ Running module existence check...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --check-module 'module_name'")
                        elif choice == "4":
                            print("🎲 Running DAE cube organizer...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --init-dae 'DAE_name'")
                        elif choice == "5":
                            print("📈 Running index management...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --index-all")
                        elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                            print("🧠 Running HoloDAE intelligence analysis...")
                            # These would trigger HoloDAE analysis functions
                            print("Use HoloIndex search to trigger automatic analysis")
                        elif choice == "14":
                            print("🕵️ Running WSP 88 orphan analysis...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --wsp88")
                        elif choice == "16":
                            print("📊 Execution Log Analyzer - Advisor Choice")
                            print("=" * 60)
                            print("Advisor: Choose analysis mode for systematic log processing")
                            print()
                            print("1. 🤖 Interactive Mode - Step-by-step advisor guidance")
                            print("2. ⚡ Daemon Mode - Autonomous 0102 background processing")
                            print()
                            print("Interactive: User-guided analysis with advisor oversight")
                            print("Daemon: Autonomous processing once triggered - follows WSP 80")
                            print()

                            analysis_choice = input("Select mode (1-2): ").strip()

                            if analysis_choice == "1":
                                # Interactive mode - advisor-guided
                                print("\n🤖 Starting Interactive Log Analysis...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("🔍 Advisor-guided systematic log analysis...")
                                    print("📈 Processing 23,000+ lines with advisor oversight...")

                                    librarian = coordinate_execution_log_processing(daemon_mode=False)

                                    print("\n✅ Interactive analysis initialized!")
                                    print("📋 Results saved to:")
                                    print("   - complete_file_index.json (full scope analysis)")
                                    print("   - qwen_processing_plan.json (processing plan)")
                                    print("   - qwen_next_task.json (ready for Qwen analysis)")

                                    print("\n🎯 Next: Advisor guides Qwen analysis of chunks")
                                    input("\nPress Enter to continue...")

                                except Exception as e:
                                    print(f"❌ Interactive analysis failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            elif analysis_choice == "2":
                                # Daemon mode - autonomous 0102 processing
                                print("\n⚡ Starting Log Analysis Daemon...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("🔄 Advisor triggers autonomous 0102 processing...")
                                    print("📊 0102 will process entire log file independently")

                                    # Start daemon
                                    daemon_thread = coordinate_execution_log_processing(daemon_mode=True)

                                    print("\n✅ Daemon started successfully!")
                                    print("🔍 0102 processing 23,000+ lines autonomously")
                                    print("📊 Check progress: HoloDAE menu → Option 15 (PID Detective)")
                                    print("📈 Results will be saved to analysis output files")

                                    input("\nPress Enter to continue (daemon runs in background)...")

                                except Exception as e:
                                    print(f"❌ Daemon startup failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            else:
                                print("❌ Invalid choice - returning to menu")
                                input("\nPress Enter to continue...")
                        elif choice in ["15", "17", "18"]:
                            print("📋 Running WSP compliance functions...")
                            # These would trigger compliance checking
                            print("Use HoloIndex search to trigger compliance analysis")
                        elif choice in ["19", "20", "21", "22", "23"]:
                            print("🤖 Running AI advisor functions...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'query' --llm-advisor")
                        elif choice == "24":
                            print("📺 Launching YouTube Live DAE...")
                            # Would need to navigate to option 1
                            print("Please select option 1 from main menu for YouTube DAE")
                        elif choice == "25":
                            print("🧠 Starting autonomous HoloDAE monitoring...")
                            run_holodae()
                            break  # Exit menu after starting monitoring
                        elif choice == "6":
                            print("🧠 Launching Chain-of-Thought Brain Logging...")
                            try:
                                from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                                demonstrate_brain_logging()
                                print("\n🧠 BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                                print("💡 This shows exactly how the AI brain works - completely observable!")
                            except Exception as e:
                                print(f"❌ Brain logging failed: {e}")
                            input("\nPress Enter to continue...")
                        elif choice in ["26", "27", "28", "29", "30"]:
                            print("🎲 This DAE operation requires main menu selection...")
                            # Would need to navigate to appropriate main menu option
                            print("Please return to main menu and select the appropriate DAE")
                        elif choice in ["31", "32", "33", "34", "35"]:
                            print("⚙️ Running administrative functions...")
                            # These would trigger admin functions
                            print("Administrative functions available through main menu")
                        else:
                            print("❌ Invalid choice. Please select 0-35.")

                        input("\nPress Enter to continue...")

                except Exception as e:
                    print(f"❌ HoloDAE menu failed to load: {e}")
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
                print("🧠 Starting PQN Research DAE...")
                from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
                pqn_dae = PQNResearchDAEOrchestrator()
                asyncio.run(pqn_dae.run())

            elif choice == "6":
                # Liberty Alert mesh alert system
                run_evade_net()

            elif choice == "7":
                # All platforms
                print("[ALL] Starting ALL DAEs...")
                asyncio.run(monitor_all_platforms())

            elif choice == "8":
                # Check instance status
                check_instance_status()
                input("\nPress Enter to continue...")

            elif choice == "9":
                print("[EXIT] Exiting...")
                break  # Exit the while True loop

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

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

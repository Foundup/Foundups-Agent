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

            # Log instance monitoring information
            try:
                instance_summary = lock.get_instance_summary()
                total_instances = instance_summary["total_instances"]
                current_pid = instance_summary["current_pid"]

                if total_instances > 1:
                    logger.warning(f"🚨 MULTIPLE INSTANCES DETECTED: {total_instances} YouTube DAEs running")
                    for instance in instance_summary["instances"]:
                        status = "CURRENT" if instance["is_current"] else "OTHER"
                        logger.warning(f"  • {status} PID {instance['pid']} - {instance['age_minutes']:.1f}min old - {instance['memory_mb']} RAM")
                else:
                    logger.info(f"✅ SINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")

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
        # Check if HoloIndex is available
        holo_path = r"E:\HoloIndex\enhanced_holo_index.py"
        if not os.path.exists(holo_path):
            print("⚠️ HoloIndex not found at E:\\HoloIndex")
            print("Install HoloIndex to prevent vibecoding!")
            return None

        # Run HoloIndex search
        result = subprocess.run(
            ['python', holo_path, '--search', query],
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


def run_amo_dae():
    """Run AMO DAE (Autonomous Moderation Operations)."""
    print("🤖 Starting AMO DAE (Autonomous Moderation Operations)...")
    try:
        from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
        dae = AutoModeratorDAE()
        asyncio.run(dae.run())
    except Exception as e:
        print(f"❌ AMO DAE failed: {e}")
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

    except Exception as e:
        print(f"❌ Error checking status: {e}")

    print()


def git_push_and_post():
    """
    Git push with automatic social media posting.
    Pushes code changes and posts updates to LinkedIn FoundUps page.
    Uses browser automation (same as YouTube stream detection).
    """
    import subprocess
    from datetime import datetime

    print("\n" + "="*60)
    print("GIT PUSH & LINKEDIN POST (FoundUps)")
    print("="*60)

    # Check git status
    try:
        status = subprocess.run(['git', 'status', '--porcelain'],
                              capture_output=True, text=True, check=True)

        if not status.stdout.strip():
            print("✅ No changes to commit")
            input("\nPress Enter to continue...")
            return

        print("\n📝 Changes detected:")
        print("-" * 40)
        files = status.stdout.strip().split('\n')
        for file in files[:10]:
            print(f"  {file}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more files")
        print("-" * 40)

        # Get commit message
        commit_msg = input("\n📝 Enter commit message (or press Enter for auto): ").strip()
        if not commit_msg:
            # Auto-generate commit message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            commit_msg = f"Update codebase ({len(files)} files) - {timestamp}"

        print(f"\n🔄 Committing: {commit_msg}")

        # Git operations
        print("\n⚙️  Executing git commands...")
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
        subprocess.run(['git', 'push'], check=True)
        print("✅ Successfully pushed to git!")

        # Generate LinkedIn content
        print("\n📱 Preparing LinkedIn post...")
        content = f"🚀 Development Update: {commit_msg}\n\n"
        content += f"✨ {len(files)} files updated\n"

        # Add key changes
        if len(files) <= 5:
            content += "Key changes:\n"
            for file in files:
                fname = file.split()[-1] if ' ' in file else file
                content += f"  • {fname}\n"
        else:
            content += "Key changes:\n"
            for file in files[:3]:
                fname = file.split()[-1] if ' ' in file else file
                content += f"  • {fname}\n"
            content += f"  ... and {len(files) - 3} more\n"

        content += "\n#SoftwareDevelopment #OpenSource #Coding #TechUpdates #AI #Automation"
        content += "\n\n🔗 github.com/Foundups-Agent"

        print(f"\n📱 LinkedIn Post Preview:\n{'-'*40}\n{content}\n{'-'*40}")

        # Post to LinkedIn using browser automation (like YouTube stream detection)
        confirm = input("\n📤 Post to LinkedIn? (y/n): ").lower()
        if confirm == 'y':
            try:
                # Use the same anti-detection poster that YouTube uses
                from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn

                print("\n🌐 Starting browser automation...")
                poster = AntiDetectionLinkedIn()
                # Already configured for FoundUps (1263645) by default
                poster.setup_driver(use_existing_session=True)
                poster.post_to_company_page(content)
                print("✅ Successfully posted to LinkedIn!")
            except ImportError as e:
                print(f"⚠️  LinkedIn module not found: {e}")
                print("   Using fallback method...")

                # Fallback to orchestrator method (same as YouTube stream)
                try:
                    from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
                    orchestrator = SimplePostingOrchestrator()

                    # Create a pseudo-stream event for git commit
                    import asyncio
                    response = asyncio.run(orchestrator.post_git_update(
                        commit_message=commit_msg,
                        content=content,
                        file_count=len(files)
                    ))

                    if response.results:
                        for result in response.results:
                            if result.success:
                                print(f"✅ Posted to {result.platform.value}")
                            else:
                                print(f"⚠️  Failed to post to {result.platform.value}: {result.message}")
                except Exception as e2:
                    print(f"⚠️  Orchestrator method failed: {e2}")
            except Exception as e:
                print(f"⚠️  LinkedIn posting failed: {e}")
        else:
            print("⏭️  Skipped LinkedIn posting")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
        print("   Make sure you have git configured and are in a git repository")
    except Exception as e:
        print(f"❌ Error: {e}")

    input("\nPress Enter to continue...")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
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
    elif args.amo:
        run_amo_dae()
    elif args.smd:
        run_social_media_dae()
    elif args.pqn:
        run_pqn_dae()
    elif args.all:
        asyncio.run(monitor_all_platforms())
    else:
        # Interactive menu - Check for running instances first
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)

        # Check for running instances proactively
        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")
            duplicates = lock.check_duplicates(quiet=True)

            if duplicates:
                print(f"⚠️  FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                print("\nWhat would you like to do?")
                print("1. Kill all instances and continue")
                print("2. Show detailed status")
                print("3. Continue anyway (may cause conflicts)")
                print("4. Exit")
                print("-"*40)

                choice = input("Select option (1-4): ").strip()

                if choice == "1":
                    print("\n🗡️  Killing duplicate instances...")
                    for pid in duplicates:
                        try:
                            lock._kill_process(pid)
                            print(f"   ✅ Killed PID {pid}")
                        except Exception as e:
                            print(f"   ❌ Failed to kill PID {pid}: {e}")
                    print("   Waiting 2 seconds for cleanup...")
                    time.sleep(2)
                    print("   ✅ Ready to continue\n")

                elif choice == "2":
                    print("\n" + "="*50)
                    check_instance_status()
                    print("="*50)
                    print("Run 'python main.py' again to access the menu.")
                    return

                elif choice == "3":
                    print("⚠️  Continuing with potential conflicts...\n")

                elif choice == "4":
                    print("👋 Exiting...")
                    return

                else:
                    print("❌ Invalid choice. Exiting for safety...")
                    return

            else:
                print("✅ NO RUNNING INSTANCES DETECTED")
                print("   Safe to start new DAEs\n")

        except Exception as e:
            print(f"⚠️  Could not check instances: {e}")
            print("   Proceeding with menu...\n")

        # Show the main menu
        print("0. Push to Git and Post to LinkedIn (FoundUps)")
        print("1. YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)")
        print("2. AMO DAE (Autonomous Moderation Operations)")
        print("3. Social Media DAE (012 Digital Twin)")
        print("4. PQN Orchestration (Research & Alignment)")
        print("5. All DAEs (Full System)")
        print("6. Check Instance Status & Health")
        print("7. Exit")
        print("-"*60)
        print("8. HoloIndex Search (Find code semantically)")
        print("="*60)

        choice = input("\nSelect option: ")

        if choice == "0":
            # Git push with LinkedIn posting
            git_push_and_post()

        elif choice == "1":
            # YouTube Live DAE
            print("🎥 Starting YouTube Live DAE...")
            asyncio.run(monitor_youtube(disable_lock=False))

        elif choice == "2":
            # AMO DAE
            print("🤖 Starting AMO DAE (Autonomous Moderation)...")
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
            dae = AutoModeratorDAE()
            asyncio.run(dae.run())

        elif choice == "3":
            # Social Media DAE (012 Digital Twin)
            print("👥 Starting Social Media DAE (012 Digital Twin)...")
            from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
            orchestrator = SocialMediaOrchestrator()
            # orchestrator.run_digital_twin()  # TODO: Implement digital twin mode
            print("Digital Twin mode coming soon...")

        elif choice == "4":
            # PQN Orchestration
            print("🧠 Starting PQN Research DAE...")
            from modules.ai_intelligence.pqn_alignment.src.pqn_research_dae_orchestrator import PQNResearchDAEOrchestrator
            pqn_dae = PQNResearchDAEOrchestrator()
            asyncio.run(pqn_dae.run())

        elif choice == "5":
            # All platforms
            print("🌐 Starting ALL DAEs...")
            asyncio.run(monitor_all_platforms())

        elif choice == "6":
            # Check instance status
            check_instance_status()
            input("\nPress Enter to continue...")

        elif choice == "7":
            print("👋 Exiting...")

        elif choice == "8":
            # HoloIndex search
            print("\n🔍 HoloIndex Semantic Code Search")
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

        else:
            print("👋 Exiting...")


if __name__ == "__main__":
    main()

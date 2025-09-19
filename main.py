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


async def monitor_youtube():
    """Monitor YouTube streams with 0102 consciousness."""
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
        consecutive_failures = 0
        while True:
            try:
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

    except Exception as e:
        logger.error(f"Initial YouTube DAE setup failed: {e}")


async def monitor_all_platforms():
    """Monitor all social media platforms."""
    tasks = []

    # YouTube monitoring
    tasks.append(asyncio.create_task(monitor_youtube()))

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


def git_push_and_post():
    """
    Git push with automatic social media posting.
    Pushes code changes and posts updates to LinkedIn FoundUps page.
    """
    import subprocess

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

        # Get last commit for LinkedIn post
        last_commit = subprocess.run(['git', 'log', '-1', '--pretty=%B'],
                                    capture_output=True, text=True, check=True)

        print(f"\n📤 Last commit: {last_commit.stdout.strip()}")

        # Try to post to LinkedIn
        try:
            from modules.platform_integration.linkedin_agent.src.git_linkedin_bridge import GitLinkedInBridge
            bridge = GitLinkedInBridge(company_id="foundups")
            commits = bridge.get_recent_commits(1)
            if commits:
                content = bridge.generate_linkedin_content(commits)
                print(f"\n📱 LinkedIn Post Preview:\n{content}")
                # bridge.post_to_linkedin(content)  # Uncomment when ready
        except Exception as e:
            print(f"⚠️ LinkedIn posting failed: {e}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Git error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

    input("\nPress Enter to continue...")


def main():
    """Main entry point with command line arguments."""
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')

    args = parser.parse_args()

    if args.youtube:
        asyncio.run(monitor_youtube())
    elif args.all:
        asyncio.run(monitor_all_platforms())
    else:
        # Interactive menu - Each DAE can be tested independently
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)
        print("0. Push to Git and Post to LinkedIn (FoundUps)")
        print("1. YouTube Live DAE (Move2Japan/UnDaoDu/FoundUps)")
        print("2. AMO DAE (Autonomous Moderation Operations)")
        print("3. Social Media DAE (012 Digital Twin)")
        print("4. PQN Orchestration (Research & Alignment)")
        print("5. All DAEs (Full System)")
        print("6. Exit")
        print("-"*60)
        print("7. HoloIndex Search (Find code semantically)")
        print("="*60)

        choice = input("\nSelect option: ")

        if choice == "0":
            # Git push with LinkedIn posting
            git_push_and_post()

        elif choice == "1":
            # YouTube Live DAE
            print("🎥 Starting YouTube Live DAE...")
            asyncio.run(monitor_youtube())

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

        elif choice == "7":
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

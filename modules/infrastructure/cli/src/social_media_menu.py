"""
Social Media DAE Menu - LinkedIn Automation & Testing

Provides submenu for:
- LinkedIn commenting (Digital Twin)
- LinkedIn group posting (OpenClaw News)
- Test execution with full action logging for troubleshooting

WSP Compliance:
- WSP 62: Extracted from main_menu.py
- WSP 78: Database logging to agents_social_posts
- WSP 90: UTF-8 enforcement for Windows CLI
"""

import os
import sys
import io
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# UTF-8 enforcement for Windows (WSP 90)
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

logger = logging.getLogger(__name__)


class ActionLogger:
    """
    Full action logging for DAEmon troubleshooting.
    Captures all actions so 012 can copy/paste to Claude for debugging.
    """

    def __init__(self, session_id: Optional[str] = None):
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.actions: List[Dict[str, Any]] = []
        self.start_time = datetime.now()

    def log(self, action_type: str, details: Dict[str, Any], result: Optional[str] = None) -> None:
        """Log an action with full details."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "elapsed_ms": int((datetime.now() - self.start_time).total_seconds() * 1000),
            "action_type": action_type,
            "details": details,
            "result": result,
        }
        self.actions.append(entry)
        logger.info(f"[ACTION] {action_type}: {json.dumps(details, default=str)[:200]}")

    def get_report(self) -> str:
        """Generate copy/paste-friendly report for troubleshooting."""
        lines = [
            "=" * 60,
            f"DAEmon Action Log - Session: {self.session_id}",
            f"Started: {self.start_time.isoformat()}",
            f"Total Actions: {len(self.actions)}",
            "=" * 60,
            "",
        ]

        for i, action in enumerate(self.actions, 1):
            lines.append(f"[{i}] {action['timestamp']} (+{action['elapsed_ms']}ms)")
            lines.append(f"    Action: {action['action_type']}")
            lines.append(f"    Details: {json.dumps(action['details'], indent=8, default=str)}")
            if action.get('result'):
                lines.append(f"    Result: {action['result']}")
            lines.append("")

        lines.append("=" * 60)
        lines.append("END OF LOG - Copy above for troubleshooting")
        lines.append("=" * 60)

        return "\n".join(lines)

    def save_to_file(self, path: Optional[Path] = None) -> Path:
        """Save log to file for later reference."""
        if path is None:
            logs_dir = Path("logs/social_media_dae")
            logs_dir.mkdir(parents=True, exist_ok=True)
            path = logs_dir / f"session_{self.session_id}.log"

        path.write_text(self.get_report(), encoding='utf-8')
        return path


def handle_social_media_menu() -> bool:
    """
    Social Media DAE submenu.

    Returns:
        True to exit to main menu, False to continue in submenu
    """
    while True:
        print("\n" + "=" * 60)
        print("  Social Media DAE - 012 Digital Twin")
        print("  " + "-" * 56)
        print("  1. LinkedIn Comment Engagement")
        print("  2. LinkedIn Group Post (OpenClaw News)")
        print("  3. Test Submenu (Full Action Logging)")
        print("  0. Back to Main Menu")
        print("=" * 60)

        try:
            choice = input("\n  Select option: ").strip()
        except (EOFError, KeyboardInterrupt):
            return True

        if choice == "0":
            return True

        elif choice == "1":
            _run_linkedin_commenting()

        elif choice == "2":
            _run_linkedin_group_post()

        elif choice == "3":
            _handle_test_submenu()

        else:
            print("  Invalid choice. Please try again.")


def _run_linkedin_commenting() -> None:
    """Run LinkedIn comment engagement with Digital Twin."""
    print("\n[LN-COMMENT] Starting LinkedIn Comment Engagement...")

    action_log = ActionLogger()
    action_log.log("session_start", {"mode": "linkedin_commenting"})

    try:
        from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator

        action_log.log("import_success", {"module": "SocialMediaOrchestrator"})

        orchestrator = SocialMediaOrchestrator()
        action_log.log("orchestrator_init", {"status": "success"})

        print("[LN-COMMENT] Digital Twin mode - LinkedIn commenting")
        print("[LN-COMMENT] (Implementation pending - orchestrator initialized)")

        action_log.log("execution_complete", {"status": "pending_implementation"})

    except ImportError as e:
        action_log.log("import_error", {"error": str(e)}, result="FAILED")
        print(f"[ERROR] Could not import SocialMediaOrchestrator: {e}")

    except Exception as e:
        action_log.log("execution_error", {"error": str(e)}, result="FAILED")
        print(f"[ERROR] LinkedIn commenting failed: {e}")

    finally:
        # Show action log for troubleshooting
        print("\n" + action_log.get_report())
        input("\nPress Enter to continue...")


def _run_linkedin_group_post() -> None:
    """Run LinkedIn group news posting for OpenClaw."""
    print("\n[LN-GROUP] Starting LinkedIn Group Post (OpenClaw News)...")

    action_log = ActionLogger()
    action_log.log("session_start", {"mode": "linkedin_group_post", "group": "6729915"})

    try:
        from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
            NewsItem,
            NewsRelevanceRater,
            OpenClawGroupPoster,
            run_openclaw_news_flow,
            LINKEDIN_GROUP_URL,
            RELEVANCE_THRESHOLD,
        )

        action_log.log("import_success", {"module": "openclaw_group_news"})

        print(f"[LN-GROUP] Target: {LINKEDIN_GROUP_URL}")
        print(f"[LN-GROUP] Relevance threshold: {RELEVANCE_THRESHOLD}")

        # Show options
        print("\n  Options:")
        print("  1. Dry run (test without posting)")
        print("  2. Live post (post to LinkedIn group)")
        print("  3. Manual news item (enter URL)")
        print("  0. Back")

        try:
            sub_choice = input("\n  Select: ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if sub_choice == "0":
            return

        elif sub_choice == "1":
            action_log.log("dry_run_start", {"mode": "dry_run"})
            result = run_openclaw_news_flow(dry_run=True)
            action_log.log("dry_run_complete", result)
            print(f"\n[DRY_RUN] Result: {json.dumps(result, indent=2)}")

        elif sub_choice == "2":
            action_log.log("live_post_start", {"mode": "live"})
            confirm = input("\n  Confirm live post to LinkedIn? (yes/no): ").strip().lower()
            if confirm == "yes":
                result = run_openclaw_news_flow(dry_run=False)
                action_log.log("live_post_complete", result)
                print(f"\n[LIVE] Result: {json.dumps(result, indent=2)}")
            else:
                action_log.log("live_post_cancelled", {"reason": "user_cancelled"})
                print("[CANCELLED] Live post cancelled.")

        elif sub_choice == "3":
            _run_manual_news_post(action_log)

        else:
            print("  Invalid choice.")

    except ImportError as e:
        action_log.log("import_error", {"error": str(e)}, result="FAILED")
        print(f"[ERROR] Could not import openclaw_group_news: {e}")

    except Exception as e:
        action_log.log("execution_error", {"error": str(e)}, result="FAILED")
        print(f"[ERROR] LinkedIn group post failed: {e}")

    finally:
        print("\n" + action_log.get_report())
        log_path = action_log.save_to_file()
        print(f"[LOG] Saved to: {log_path}")
        input("\nPress Enter to continue...")


def _run_manual_news_post(action_log: ActionLogger) -> None:
    """Post a manually entered news item."""
    from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
        NewsItem,
        NewsRelevanceRater,
        OpenClawGroupPoster,
    )

    print("\n[MANUAL] Enter news item details:")

    title = input("  Title: ").strip()
    url = input("  URL: ").strip()
    source = input("  Source (e.g., techcrunch): ").strip()
    summary = input("  Summary (optional): ").strip() or None

    if not title or not url:
        print("[ERROR] Title and URL are required.")
        return

    action_log.log("manual_item_created", {
        "title": title,
        "url": url,
        "source": source,
        "has_summary": bool(summary),
    })

    item = NewsItem(title=title, url=url, source=source, summary=summary)

    # Rate the item
    score = NewsRelevanceRater.rate(item)
    action_log.log("relevance_rated", {"score": score})
    print(f"\n[RATE] Relevance score: {score:.2f}")

    if score < 0.6:
        print(f"[WARN] Score below threshold (0.6). Post anyway?")
        confirm = input("  Post anyway? (yes/no): ").strip().lower()
        if confirm != "yes":
            action_log.log("post_skipped", {"reason": "below_threshold"})
            return

    # Check rate limits
    poster = OpenClawGroupPoster()
    can_post, reason = poster.can_post_today()
    action_log.log("rate_limit_check", {"can_post": can_post, "reason": reason})

    if not can_post:
        print(f"[RATE_LIMIT] {reason}")
        return

    # Preview
    content = poster.format_post(item)
    print(f"\n[PREVIEW]\n{content}\n")

    confirm = input("  Post to LinkedIn? (yes/no): ").strip().lower()
    if confirm == "yes":
        action_log.log("manual_post_start", {"title": title})
        success = poster.post_to_group(item, dry_run=False)
        action_log.log("manual_post_complete", {"success": success})
        print(f"[POST] {'Success!' if success else 'Failed'}")
    else:
        action_log.log("manual_post_cancelled", {"reason": "user_cancelled"})
        print("[CANCELLED] Post cancelled.")


def _handle_test_submenu() -> None:
    """Test submenu with full action logging for troubleshooting."""
    while True:
        print("\n" + "=" * 60)
        print("  Social Media DAE - Test Submenu")
        print("  " + "-" * 56)
        print("  Full action logging enabled for troubleshooting.")
        print("  Copy/paste logs to Claude for debugging.")
        print("  " + "-" * 56)
        print("  1. Test News Relevance Rating")
        print("  2. Test Rate Limiting")
        print("  3. Test Database Connection")
        print("  4. Test Full News Flow (dry run)")
        print("  5. Run Pytest Suite (openclaw_group_news)")
        print("  0. Back")
        print("=" * 60)

        try:
            choice = input("\n  Select: ").strip()
        except (EOFError, KeyboardInterrupt):
            return

        if choice == "0":
            return

        elif choice == "1":
            _test_news_rating()

        elif choice == "2":
            _test_rate_limiting()

        elif choice == "3":
            _test_database()

        elif choice == "4":
            _test_full_flow()

        elif choice == "5":
            _run_pytest_suite()

        else:
            print("  Invalid choice.")


def _test_news_rating() -> None:
    """Test news relevance rating with sample items."""
    print("\n[TEST] News Relevance Rating")
    print("-" * 40)

    action_log = ActionLogger()
    action_log.log("test_start", {"test": "news_rating"})

    try:
        from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
            NewsItem,
            NewsRelevanceRater,
        )

        # Test cases
        test_items = [
            NewsItem(
                title="OpenClaw AI Framework Launches Revolutionary Agent System",
                url="https://techcrunch.com/openclaw-launch",
                source="techcrunch",
                summary="OpenClaw announces major platform update for AI agents"
            ),
            NewsItem(
                title="Random Tech News About Databases",
                url="https://example.com/databases",
                source="unknown-blog",
                summary="Some database article"
            ),
            NewsItem(
                title="AI Agents Transform Enterprise Automation",
                url="https://wired.com/ai-agents",
                source="wired",
                summary="How autonomous agents are changing business workflows"
            ),
        ]

        print(f"\nTesting {len(test_items)} items:\n")

        for item in test_items:
            score = NewsRelevanceRater.rate(item)
            action_log.log("item_rated", {
                "title": item.title[:50],
                "source": item.source,
                "score": score,
                "passes_threshold": score >= 0.6,
            })
            status = "[PASS]" if score >= 0.6 else "[FAIL]"
            print(f"  {status} {score:.2f} - {item.title[:40]}... ({item.source})")

        action_log.log("test_complete", {"items_tested": len(test_items)})

    except Exception as e:
        action_log.log("test_error", {"error": str(e)})
        print(f"[ERROR] {e}")

    print("\n" + action_log.get_report())
    input("\nPress Enter to continue...")


def _test_rate_limiting() -> None:
    """Test rate limiting logic."""
    print("\n[TEST] Rate Limiting")
    print("-" * 40)

    action_log = ActionLogger()
    action_log.log("test_start", {"test": "rate_limiting"})

    try:
        from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
            OpenClawGroupPoster,
            MAX_POSTS_PER_DAY,
            MIN_POST_INTERVAL_HOURS,
        )

        poster = OpenClawGroupPoster()

        print(f"\nRate Limit Config:")
        print(f"  Max posts/day: {MAX_POSTS_PER_DAY}")
        print(f"  Min interval: {MIN_POST_INTERVAL_HOURS} hours")

        can_post, reason = poster.can_post_today()
        action_log.log("rate_limit_check", {
            "can_post": can_post,
            "reason": reason,
        })

        status = "[OK]" if can_post else "[BLOCKED]"
        print(f"\nCurrent Status: {status}")
        print(f"Reason: {reason}")

        action_log.log("test_complete", {"can_post": can_post})

    except Exception as e:
        action_log.log("test_error", {"error": str(e)})
        print(f"[ERROR] {e}")

    print("\n" + action_log.get_report())
    input("\nPress Enter to continue...")


def _test_database() -> None:
    """Test database connection and table structure."""
    print("\n[TEST] Database Connection")
    print("-" * 40)

    action_log = ActionLogger()
    action_log.log("test_start", {"test": "database"})

    try:
        from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
            OpenClawGroupPoster,
        )
        import sqlite3

        poster = OpenClawGroupPoster()
        action_log.log("poster_init", {"db_path": poster.db_path})

        print(f"\nDatabase path: {poster.db_path}")
        print(f"Exists: {os.path.exists(poster.db_path)}")

        # Check table structure
        conn = sqlite3.connect(poster.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agents_social_posts'")
        table_exists = cursor.fetchone() is not None
        action_log.log("table_check", {"table": "agents_social_posts", "exists": table_exists})

        print(f"Table 'agents_social_posts': {'EXISTS' if table_exists else 'MISSING'}")

        if table_exists:
            cursor.execute("SELECT COUNT(*) FROM agents_social_posts WHERE platform='linkedin'")
            count = cursor.fetchone()[0]
            action_log.log("record_count", {"linkedin_posts": count})
            print(f"LinkedIn posts in DB: {count}")

            # Show recent posts
            cursor.execute("""
                SELECT id, post_status, relevance_score, created_at
                FROM agents_social_posts
                WHERE platform = 'linkedin'
                ORDER BY created_at DESC
                LIMIT 5
            """)
            recent = cursor.fetchall()
            if recent:
                print("\nRecent posts:")
                for row in recent:
                    print(f"  {row[0][:20]}... | {row[1]} | score={row[2]:.2f} | {row[3]}")

        conn.close()
        action_log.log("test_complete", {"status": "success"})

    except Exception as e:
        action_log.log("test_error", {"error": str(e)})
        print(f"[ERROR] {e}")

    print("\n" + action_log.get_report())
    input("\nPress Enter to continue...")


def _test_full_flow() -> None:
    """Test full news flow with dry run."""
    print("\n[TEST] Full News Flow (Dry Run)")
    print("-" * 40)

    action_log = ActionLogger()
    action_log.log("test_start", {"test": "full_flow", "dry_run": True})

    try:
        from modules.platform_integration.linkedin_agent.skillz.openclaw_group_news import (
            run_openclaw_news_flow,
        )

        print("\nRunning full news flow in dry run mode...")
        action_log.log("flow_start", {"mode": "dry_run"})

        result = run_openclaw_news_flow(dry_run=True)

        action_log.log("flow_complete", result)

        print(f"\nResult:")
        print(json.dumps(result, indent=2))

    except Exception as e:
        action_log.log("test_error", {"error": str(e)})
        print(f"[ERROR] {e}")

    print("\n" + action_log.get_report())
    log_path = action_log.save_to_file()
    print(f"[LOG] Saved to: {log_path}")
    input("\nPress Enter to continue...")


def _run_pytest_suite() -> None:
    """Run pytest suite for openclaw_group_news skill."""
    print("\n[TEST] Running Pytest Suite")
    print("-" * 40)

    action_log = ActionLogger()
    action_log.log("test_start", {"test": "pytest_suite"})

    import subprocess

    test_path = "modules/platform_integration/linkedin_agent/skillz/openclaw_group_news/tests"

    print(f"\nTest path: {test_path}")
    print("Running pytest with verbose output...\n")

    action_log.log("pytest_start", {"test_path": test_path})

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120,
        )

        action_log.log("pytest_complete", {
            "returncode": result.returncode,
            "stdout_lines": len(result.stdout.split('\n')),
            "stderr_lines": len(result.stderr.split('\n')) if result.stderr else 0,
        })

        print(result.stdout)
        if result.stderr:
            print("[STDERR]")
            print(result.stderr)

        if result.returncode == 0:
            print("\n[SUCCESS] All tests passed!")
        else:
            print(f"\n[FAILED] Tests failed with code {result.returncode}")

    except subprocess.TimeoutExpired:
        action_log.log("pytest_timeout", {"timeout": 120})
        print("[TIMEOUT] Tests took too long (>120s)")

    except Exception as e:
        action_log.log("pytest_error", {"error": str(e)})
        print(f"[ERROR] {e}")

    print("\n" + action_log.get_report())
    log_path = action_log.save_to_file()
    print(f"[LOG] Saved to: {log_path}")
    input("\nPress Enter to continue...")

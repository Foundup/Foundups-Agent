"""
Unified Metadata Updater - Agent chooses best method

Combines:
- YouTube API (fastest for LIVE)
- DOM Live Dashboard (fallback for LIVE)
- DOM Manage Page (any broadcast)

Agents can choose method or let auto-select based on stream state.

Usage:
    python executor.py auto --title "..." --description "..."
    python executor.py clickbait
    python executor.py major-event
    python executor.py seo-refresh

WSP 27: Universal DAE Architecture
WSP 77: Agent Coordination
WSP 103: CLI Interface Standard
"""

import asyncio
import argparse
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def check_stream_live() -> bool:
    """Check if antifaFM stream is currently live."""
    try:
        from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import YouTubeBroadcastManager
        manager = YouTubeBroadcastManager()
        broadcasts = await manager.get_active_broadcasts()

        for b in broadcasts:
            status = b.get("status", {}).get("lifeCycleStatus", "")
            if status in ("live", "testing"):
                return True
        return False
    except Exception:
        return False


async def update_via_api(title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
    """Update via YouTube Data API (fastest, requires OAuth)."""
    try:
        from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import YouTubeBroadcastManager
        manager = YouTubeBroadcastManager()
        result = await manager.update_current_broadcast(title=title, description=description)
        result["method"] = "api"
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "method": "api"}


async def update_via_dom_live(title: Optional[str], description: Optional[str]) -> Dict[str, Any]:
    """Update via Live Dashboard DOM automation."""
    try:
        from modules.platform_integration.antifafm_broadcaster.skillz.stream_metadata_editor.executor import (
            edit_stream_metadata
        )
        result = await edit_stream_metadata(title=title, description=description)
        result["method"] = "dom_live"
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "method": "dom_live"}


async def update_via_dom_manage(
    title: Optional[str],
    description: Optional[str],
    video_index: int = 0
) -> Dict[str, Any]:
    """Update via Manage Page DOM automation."""
    try:
        from modules.platform_integration.antifafm_broadcaster.skillz.manage_metadata_editor.executor import (
            edit_broadcast_metadata
        )
        result = await edit_broadcast_metadata(
            video_index=video_index,
            title=title,
            description=description
        )
        result["method"] = "dom_manage"
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "method": "dom_manage"}


async def auto_update(
    title: Optional[str] = None,
    description: Optional[str] = None,
    video_index: int = 0
) -> Dict[str, Any]:
    """
    Auto-select best method based on stream state.

    Priority:
    1. If live → API → DOM Live → DOM Manage
    2. If not live → DOM Manage
    """
    is_live = await check_stream_live()

    if is_live:
        print("[UNIFIED] Stream is LIVE - trying API first...")

        # Try API
        result = await update_via_api(title, description)
        if result.get("success"):
            return result

        print(f"[UNIFIED] API failed: {result.get('error')} - trying DOM Live...")

        # Try DOM Live
        result = await update_via_dom_live(title, description)
        if result.get("success"):
            return result

        print(f"[UNIFIED] DOM Live failed: {result.get('error')} - trying DOM Manage...")

    else:
        print("[UNIFIED] Stream not live - using DOM Manage...")

    # DOM Manage (works for any broadcast)
    return await update_via_dom_manage(title, description, video_index)


async def apply_clickbait() -> Dict[str, Any]:
    """
    Apply clickbait title + M2M description with top news.

    Uses auto method selection.
    """
    from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import (
        generate_clickbait_title, generate_m2m_description
    )

    # Get news from orchestrator
    try:
        from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
        orchestrator = NewsOrchestrator()
        top_items = orchestrator.get_top(5)
        headlines = [item.headline for item in top_items]
    except Exception:
        headlines = []

    title = generate_clickbait_title(headlines)
    description = generate_m2m_description(headlines)

    print(f"[UNIFIED] Clickbait title: {title}")
    print(f"[UNIFIED] Description with {len(headlines)} headlines for SEO")

    return await auto_update(title=title, description=description)


async def major_event_update() -> Dict[str, Any]:
    """
    Update TITLE only for major events.

    Checks if top news qualifies as major event (urgency >= 8).
    """
    try:
        from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
        from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import generate_clickbait_title

        orchestrator = NewsOrchestrator()
        top_items = orchestrator.get_top(5)

        if not top_items:
            return {"success": False, "error": "No news in queue"}

        top_item = top_items[0]

        # Check if major event
        if top_item.urgency < 8 and top_item.total_score < 8.5:
            return {
                "success": False,
                "error": f"Not major event: urgency={top_item.urgency:.1f}, score={top_item.total_score:.2f}",
                "headline": top_item.headline[:50]
            }

        headlines = [item.headline for item in top_items]
        title = generate_clickbait_title(headlines)

        print(f"[UNIFIED] MAJOR EVENT: {top_item.headline[:50]}...")
        print(f"[UNIFIED] New title: {title}")

        return await auto_update(title=title, description=None)

    except Exception as e:
        return {"success": False, "error": str(e)}


async def seo_refresh() -> Dict[str, Any]:
    """
    Update DESCRIPTION only for SEO (top news).

    Does not change title.
    """
    try:
        from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
        from modules.platform_integration.antifafm_broadcaster.src.youtube_broadcast_manager import generate_m2m_description

        orchestrator = NewsOrchestrator()
        top_items = orchestrator.get_top(5)
        headlines = [item.headline for item in top_items]

        description = generate_m2m_description(headlines)

        print(f"[UNIFIED] SEO refresh with {len(headlines)} headlines")

        return await auto_update(title=None, description=description)

    except Exception as e:
        return {"success": False, "error": str(e)}


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Unified metadata updater - agent chooses best method"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Auto command
    auto_parser = subparsers.add_parser("auto", help="Auto-select best method")
    auto_parser.add_argument("--title", type=str, help="New title")
    auto_parser.add_argument("--description", type=str, help="New description")

    # Specific methods
    api_parser = subparsers.add_parser("api", help="Force YouTube API")
    api_parser.add_argument("--title", type=str, help="New title")
    api_parser.add_argument("--description", type=str, help="New description")

    dom_live_parser = subparsers.add_parser("dom-live", help="Force DOM Live Dashboard")
    dom_live_parser.add_argument("--title", type=str, help="New title")
    dom_live_parser.add_argument("--description", type=str, help="New description")

    dom_manage_parser = subparsers.add_parser("dom-manage", help="Force DOM Manage Page")
    dom_manage_parser.add_argument("--title", type=str, help="New title")
    dom_manage_parser.add_argument("--description", type=str, help="New description")
    dom_manage_parser.add_argument("--index", type=int, default=0, help="Video index")

    # Preset commands
    subparsers.add_parser("clickbait", help="Apply clickbait title + M2M description")
    subparsers.add_parser("major-event", help="Update title for major event only")
    subparsers.add_parser("seo-refresh", help="Update description for SEO only")

    # Status
    subparsers.add_parser("status", help="Check stream status and available methods")

    args = parser.parse_args()

    async def run():
        if args.command == "auto":
            result = await auto_update(title=args.title, description=args.description)

        elif args.command == "api":
            result = await update_via_api(args.title, args.description)

        elif args.command == "dom-live":
            result = await update_via_dom_live(args.title, args.description)

        elif args.command == "dom-manage":
            result = await update_via_dom_manage(args.title, args.description, args.index)

        elif args.command == "clickbait":
            result = await apply_clickbait()

        elif args.command == "major-event":
            result = await major_event_update()

        elif args.command == "seo-refresh":
            result = await seo_refresh()

        elif args.command == "status":
            is_live = await check_stream_live()
            print(f"\n=== Stream Status ===")
            print(f"Live: {is_live}")
            print(f"Recommended method: {'API' if is_live else 'DOM Manage'}")

            # Check news queue
            try:
                from modules.platform_integration.antifafm_broadcaster.src.news_orchestrator import NewsOrchestrator
                orchestrator = NewsOrchestrator()
                top_items = orchestrator.get_top(3)
                print(f"\n=== News Queue ===")
                for i, item in enumerate(top_items):
                    major = "*MAJOR*" if item.urgency >= 8 or item.total_score >= 8.5 else ""
                    print(f"[{i+1}] {major} U:{item.urgency:.0f} S:{item.total_score:.1f} {item.headline[:50]}...")
            except Exception:
                pass

            return

        else:
            parser.print_help()
            return

        print(f"\nResult: {result}")

    asyncio.run(run())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )
    main()

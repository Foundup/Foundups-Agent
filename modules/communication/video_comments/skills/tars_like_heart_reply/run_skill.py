"""
0102 Comment Engagement Skill Runner
====================================

WSP 96 Compliant skill execution entry point.
Invokes the CommentEngagementDAE for autonomous Like + Heart + Reply.

Usage:
    python run_skill.py --max-comments 5 --reply-text "0102 was here"
    python run_skill.py --channel UC-LSSlOZwpGIRIYihaz8zCw --dom-only
"""

import asyncio
import argparse
import logging
import os
import sys
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(repo_root))

# Load environment variables (e.g., GROK_API_KEY/XAI_API_KEY) for intelligent replies.
# This is intentionally done before importing skill modules so they see the env on import.
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(dotenv_path=repo_root / ".env", override=False)
except Exception:
    pass

from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import (
    CommentEngagementDAE,
    execute_skill
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Default channel
DEFAULT_CHANNEL = "UC-LSSlOZwpGIRIYihaz8zCw"  # Move2Japan


async def main():
    parser = argparse.ArgumentParser(
        description="0102 Autonomous Comment Engagement"
    )
    parser.add_argument(
        "--channel",
        type=str,
        default=DEFAULT_CHANNEL,
        help="YouTube channel ID"
    )
    parser.add_argument(
        "--video",
        type=str,
        default=None,
        help="YouTube video ID (for live stream comments, otherwise uses channel inbox)"
    )
    parser.add_argument(
        "--max-comments",
        type=int,
        default=5,
        help="Max comments to process"
    )
    parser.add_argument(
        "--reply-text",
        type=str,
        default="",
        help="Reply text (empty = no reply)"
    )
    parser.add_argument(
        "--no-like",
        action="store_true",
        help="Skip like action"
    )
    parser.add_argument(
        "--no-heart",
        action="store_true",
        help="Skip heart action"
    )
    parser.add_argument(
        "--dom-only",
        action="store_true",
        help="DOM only (no vision verification)"
    )
    parser.add_argument(
        "--no-refresh",
        action="store_true",
        help="Don't refresh page between batches"
    )
    parser.add_argument(
        "--no-intelligent-reply",
        action="store_true",
        help="Disable intelligent reply (use custom --reply-text only)"
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output result as JSON for subprocess parsing"
    )
    parser.add_argument(
        "--debug-tags",
        action="store_true",
        help="Append debug tags to posted replies (commenter type + WSP44 state)"
    )
    
    args = parser.parse_args()

    if args.debug_tags:
        os.environ["YT_REPLY_DEBUG_TAGS"] = "1"
    
    # Suppress banner if JSON output mode
    if not args.json_output:
        print(f"\n{'='*60}")
        print(" 0102 COMMENT ENGAGEMENT SKILL")
        print(f"{'='*60}")
        print(f" Channel: {args.channel}")
        print(f" Video: {args.video or '(channel inbox)'}")
        print(f" Max comments: {args.max_comments}")
        print(f" Reply: {args.reply_text or '(intelligent)'}")
        print(f" Vision: {'disabled' if args.dom_only else 'enabled'}")
        print(f" Intelligent Reply: {'disabled' if args.no_intelligent_reply else 'enabled'}")
        print(f"{'='*60}\n")

    logger.info(f"[DAEMON][DAE-INIT] 🎬 Initializing Comment Engagement DAE...")
    logger.info(f"[DAEMON][DAE-INIT]   Channel: {args.channel}")
    logger.info(f"[DAEMON][DAE-INIT]   Video: {args.video or 'None (Studio inbox)'}")
    logger.info(f"[DAEMON][DAE-INIT]   Vision: {'enabled' if not args.dom_only else 'disabled (DOM-only)'}")
    logger.info(f"[DAEMON][DAE-INIT]   Max comments: {args.max_comments} (0=UNLIMITED)")

    dae = CommentEngagementDAE(
        channel_id=args.channel,
        video_id=args.video,
        use_vision=not args.dom_only,
        use_dom=True
    )

    try:
        logger.info(f"[DAEMON][DAE-CONNECT] 🔌 Connecting to Chrome (port 9222)...")
        await dae.connect()
        logger.info(f"[DAEMON][DAE-CONNECT] ✅ Connected successfully")

        logger.info(f"[DAEMON][DAE-NAVIGATE] 🧭 Navigating to inbox...")
        await dae.navigate_to_inbox()
        logger.info(f"[DAEMON][DAE-NAVIGATE] ✅ Navigation complete")

        logger.info(f"[DAEMON][DAE-ENGAGE] 🎯 Starting comment engagement...")
        logger.info(f"[DAEMON][DAE-ENGAGE]   Actions: Like={not args.no_like} | Heart={not args.no_heart} | Reply={args.reply_text is not None}")
        logger.info(f"[DAEMON][DAE-ENGAGE]   Intelligent replies: {not args.no_intelligent_reply}")

        result = await dae.engage_all_comments(
            max_comments=args.max_comments,
            do_like=not args.no_like,
            do_heart=not args.no_heart,
            reply_text=args.reply_text,
            refresh_between=not args.no_refresh,
            use_intelligent_reply=not args.no_intelligent_reply
        )

        logger.info(f"[DAEMON][DAE-COMPLETE] ✅ Engagement complete: {result.get('stats', {})}")
        
        # Output JSON if requested (for subprocess parsing)
        if args.json_output:
            import json
            print(json.dumps(result, default=str))
        
        return result
        
    except Exception as e:
        logger.error(f"[DAEMON][DAE-ERROR] ❌ FATAL ERROR: {e}")
        logger.error(f"[ERROR] Skill execution failed: {e}", exc_info=True)
        error_result = {'error': str(e), 'stats': {'comments_processed': 0, 'errors': 1}}
        if args.json_output:
            import json
            print(json.dumps(error_result))
        return error_result

    finally:
        logger.info(f"[DAEMON][DAE-CLEANUP] 🧹 Closing DAE connection...")
        dae.close()
        logger.info(f"[DAEMON][DAE-CLEANUP] ✅ Cleanup complete")


if __name__ == "__main__":
    asyncio.run(main())

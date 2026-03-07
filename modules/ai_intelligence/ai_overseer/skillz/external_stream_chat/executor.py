#!/usr/bin/env python3
"""
External Stream Chat Executor

CLI and skill executor for external YouTube Live stream engagement.
Enables OpenClaw to interact in any public stream's chat.

Usage:
    # CLI mode
    python -m ai_overseer.skillz.external_stream_chat.executor --url URL --message "Hello!"
    python -m ai_overseer.skillz.external_stream_chat.executor --url URL --party
    python -m ai_overseer.skillz.external_stream_chat.executor --interactive

    # As skill
    from ai_overseer.skillz.external_stream_chat.executor import execute
    result = await execute(url="...", action="send", message="Hello!")
"""

import asyncio
import logging
import os
from typing import Any, Dict, Optional

from .src.stream_chat_dae import ExternalStreamChat, BROWSER_PORT

logger = logging.getLogger(__name__)


async def execute(
    url: Optional[str] = None,
    action: str = "status",
    message: Optional[str] = None,
    party_count: int = 10,
    browser_port: int = BROWSER_PORT
) -> Dict[str, Any]:
    """
    Execute external stream chat skill.

    Args:
        url: YouTube Live URL to engage with
        action: Action to perform (send, party, status, watch)
        message: Message to send (for 'send' action)
        party_count: Number of party clicks (for 'party' action)
        browser_port: Browser debug port

    Returns:
        Result dict with success status and details
    """
    result = {
        "success": False,
        "action": action,
        "url": url,
        "details": {}
    }

    try:
        chat = ExternalStreamChat(url=url, browser_port=browser_port)

        if not await chat.connect():
            result["error"] = "Failed to connect to browser"
            return result

        if action == "send" and message:
            success = await chat.send_message(message)
            result["success"] = success
            result["details"]["message_sent"] = message if success else None

        elif action == "party":
            clicks = await chat.party_loop(party_count)
            result["success"] = clicks > 0
            result["details"]["clicks"] = clicks

        elif action == "watch" and url:
            success = await chat.set_url(url)
            result["success"] = success

        elif action == "status":
            result["success"] = True
            result["details"] = chat.get_status()

        else:
            result["error"] = f"Unknown action: {action}"

        chat.disconnect()

    except Exception as e:
        result["error"] = str(e)
        logger.error(f"[FAIL] Execution failed: {e}")

    return result


def cli_main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="External Stream Chat - OpenClaw Skill")
    parser.add_argument("--url", type=str, help="YouTube Live URL")
    parser.add_argument("--message", "-m", type=str, help="Message to send")
    parser.add_argument("--party", action="store_true", help="Party mode (click hearts)")
    parser.add_argument("--party-count", type=int, default=10, help="Number of party clicks")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("--port", type=int, default=BROWSER_PORT, help="Browser port")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(message)s")

    # Interactive mode uses the DAE's own CLI
    if args.interactive:
        from .src.stream_chat_dae import main as dae_main
        asyncio.run(dae_main())
        return

    # Determine action
    if args.message:
        action = "send"
    elif args.party:
        action = "party"
    else:
        action = "status"

    # Execute
    result = asyncio.run(execute(
        url=args.url,
        action=action,
        message=args.message,
        party_count=args.party_count,
        browser_port=args.port
    ))

    # Output result
    if result["success"]:
        print(f"[OK] {action} completed")
        for k, v in result.get("details", {}).items():
            print(f"  {k}: {v}")
    else:
        print(f"[FAIL] {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    cli_main()

"""
Chrome Pre-flight Check - Fast TCP port detection to avoid Selenium timeouts

WSP Compliance:
    - WSP 91: DAEMON observability (fast failure detection)
    - WSP 77: Multi-tier fallback (vision → scraping)

Problem:
    When Chrome isn't running on port 9222, Selenium waits 60+ seconds before timing out.
    This blocks stream detection and causes poor UX.

Solution:
    Fast TCP socket check (< 1 second) before attempting Selenium connection.
    Skip vision detection gracefully if Chrome unavailable.
"""

import logging
import socket
from typing import Dict, Any

logger = logging.getLogger(__name__)


def is_chrome_debug_port_open(port: int = 9222, timeout: float = 1.0) -> bool:
    """
    Fast check if Chrome debug port is reachable.

    Uses raw TCP socket connection (not HTTP) for speed.
    Returns in < 1 second even when Chrome is offline.

    Args:
        port: Chrome remote debugging port (default 9222)
        timeout: Socket timeout in seconds (default 1.0)

    Returns:
        True if port is listening, False otherwise
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            result = sock.connect_ex(('127.0.0.1', port))
            return result == 0  # 0 means connection successful
    except Exception as e:
        logger.debug(f"[CHROME-CHECK] Port check failed: {e}")
        return False


def check_chrome_availability(port: int = 9222) -> Dict[str, Any]:
    """
    Check Chrome debug port and return detailed status.

    Returns:
        dict with keys:
            - available (bool): True if Chrome is reachable
            - port (int): Port checked
            - message (str): Human-readable status message
            - recommendation (str): Action to take if unavailable
    """
    available = is_chrome_debug_port_open(port)

    if available:
        return {
            "available": True,
            "port": port,
            "message": f"Chrome debug port {port} is reachable",
            "recommendation": None
        }
    else:
        return {
            "available": False,
            "port": port,
            "message": f"Chrome debug port {port} is NOT reachable",
            "recommendation": (
                f"Start Chrome with remote debugging:\n"
                f"  → scripts/launch/launch_chrome_youtube_studio.bat\n"
                f"  OR\n"
                f"  → chrome.exe --remote-debugging-port={port}"
            )
        }


def log_chrome_status(port: int = 9222, context: str = "Vision") -> bool:
    """
    Check Chrome availability and log appropriate message.

    Args:
        port: Chrome remote debugging port
        context: Context for logging (e.g., "Vision", "Comment Engagement")

    Returns:
        True if Chrome is available, False otherwise
    """
    status = check_chrome_availability(port)

    if status["available"]:
        logger.info(f"[{context}] ✅ Chrome debug port {port} is reachable - vision mode available")
        return True
    else:
        logger.warning(f"[{context}] ⚠️ Chrome debug port {port} NOT reachable")
        logger.info(f"[{context}] 💡 Tip: {status['recommendation']}")
        logger.info(f"[{context}] Falling back to non-vision mode...")
        return False


# Test function
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 60)
    print("Chrome Debug Port Pre-flight Check")
    print("=" * 60)
    print()

    status = check_chrome_availability(9222)

    print(f"Port: {status['port']}")
    print(f"Available: {status['available']}")
    print(f"Message: {status['message']}")

    if status['recommendation']:
        print(f"\nRecommendation:")
        print(status['recommendation'])

    print()
    print("=" * 60)

    if status['available']:
        print("✅ Chrome is ready for vision detection")
    else:
        print("⚠️ Chrome not available - vision mode will be skipped")

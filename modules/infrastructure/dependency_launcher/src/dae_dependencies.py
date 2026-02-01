"""
DAE Dependency Launcher - Auto-start Chrome + Edge + LM Studio for YouTube DAE
========================================================================

WSP Compliance:
    - WSP 27: DAE Architecture (Phase -1: Dependency initialization)
    - WSP 80: Cube-Level Orchestration (Cross-module dependency management)

Usage:
    from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies
    
    # Call before DAE starts
    await ensure_dependencies()

Dependencies:
    1. Chrome with remote debugging port 9222 (for Selenium/UI-TARS)
    2. Edge with remote debugging port 9223 (for FoundUps Studio inbox)
    3. LM Studio on port 1234 (for UI-TARS vision model)
"""

import asyncio
import logging
import os
import subprocess
import socket
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Configuration
CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CHROME_DEBUG_PORT = int(os.getenv("FOUNDUPS_CHROME_PORT", "9222"))
CHROME_PROFILE = Path(os.getenv(
    "CHROME_PROFILE_PATH",
    "O:/Foundups-Agent/modules/platform_integration/browser_profiles/youtube_move2japan/chrome"
))
# FIX (2025-12-30): Added NOT_ENGAGED filter to show only unprocessed comments
# Without this filter, already-liked/hearted comments still appear and cause 0-comment detection
STUDIO_FILTER = "%5B%7B%22isDisabled%22%3Afalse%2C%22isPinned%22%3Atrue%2C%22name%22%3A%22SORT_BY%22%2C%22value%22%3A%22SORT_BY_MOST_RELEVANT%22%7D%2C%7B%22name%22%3A%22ENGAGED_STATUS%22%2C%22value%22%3A%5B%22COMMENT_CATEGORY_NOT_ENGAGED%22%5D%7D%2C%7B%22name%22%3A%22PARENT_ENTITY_CONTENT_TYPE%22%2C%22value%22%3A%5B%22PARENT_ENTITY_CONTENT_TYPE_WATCH%22%2C%22PARENT_ENTITY_CONTENT_TYPE_SHORT%22%2C%22PARENT_ENTITY_CONTENT_TYPE_CREATOR_POST%22%5D%7D%5D"
YOUTUBE_STUDIO_URL = f"https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox?filter={STUDIO_FILTER}"

EDGE_DEBUG_PORT = int(os.getenv("FOUNDUPS_EDGE_PORT", os.getenv("EDGE_DEBUG_PORT", "9223")))
EDGE_PROFILE = Path(os.getenv(
    "EDGE_PROFILE_PATH",
    "O:/Foundups-Agent/modules/platform_integration/browser_profiles/youtube_foundups/edge"
))
FOUNDUPS_CHANNEL_ID = os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw")
FOUNDUPS_STUDIO_URL = f"https://studio.youtube.com/channel/{FOUNDUPS_CHANNEL_ID}/comments/inbox?filter={STUDIO_FILTER}"

LM_STUDIO_PORT = int(os.getenv("LM_STUDIO_PORT", "1234"))


def resolve_lm_studio_path() -> Optional[str]:
    """
    Resolve LM Studio executable path.

    Prefers explicit `LM_STUDIO_PATH`, then checks common install locations (including E:\\LM_studio).
    """
    candidates = [
        os.getenv("LM_STUDIO_PATH"),
        r"E:\LM_studio\LM Studio\LM Studio.exe",
        str(Path(os.getenv("LOCALAPPDATA", "")) / "Programs" / "LM Studio" / "LM Studio.exe"),
        r"C:\Users\user\AppData\Local\Programs\LM Studio\LM Studio.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def resolve_edge_path() -> Optional[str]:
    """
    Resolve Microsoft Edge executable path.

    Prefers explicit `EDGE_PATH`, then checks common install locations.
    """
    candidates = [
        os.getenv("EDGE_PATH"),
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return str(Path(candidate))
    return None


def is_port_open(port: int, host: str = "127.0.0.1", timeout: float = 1.0) -> bool:
    """Check if a port is open (service running)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False


def is_chrome_running() -> bool:
    """Check if Chrome with debug port is running."""
    return is_port_open(CHROME_DEBUG_PORT)

def is_edge_running() -> bool:
    """Check if Edge with debug port is running."""
    return is_port_open(EDGE_DEBUG_PORT)


def is_lm_studio_running() -> bool:
    """Check if LM Studio API is running."""
    return is_port_open(LM_STUDIO_PORT)


def launch_chrome() -> Tuple[bool, str]:
    """
    Launch Chrome with remote debugging port and YouTube profile.
    
    Returns:
        Tuple of (success, message)
    """
    if is_chrome_running():
        logger.info(f"[DEPS] Chrome already running on port {CHROME_DEBUG_PORT}")
        return True, "Chrome already running"
    
    if not Path(CHROME_PATH).exists():
        logger.error(f"[DEPS] Chrome not found at: {CHROME_PATH}")
        return False, f"Chrome not found at {CHROME_PATH}"
    
    try:
        cmd = [
            CHROME_PATH,
            f"--remote-debugging-port={CHROME_DEBUG_PORT}",
            f"--user-data-dir={CHROME_PROFILE}",
            # CRITICAL: Anti-backgrounding flags (2025-12-30)
            # Prevents JavaScript/DOM throttling when window not focused
            # Without these, automation stops or becomes erratic when browser is in background
            "--disable-backgrounding-occluded-windows",  # Prevents throttling when behind other windows
            "--disable-renderer-backgrounding",           # Prevents renderer process backgrounding
            "--disable-background-timer-throttling",      # Prevents timer throttling in background tabs
            # FIX (2026-01-23): Prevent multi-tab issue from session restore
            "--no-restore-session-state",                 # Prevents restoring previous tabs
            YOUTUBE_STUDIO_URL
        ]

        logger.info(f"[DEPS] Launching Chrome with debug port {CHROME_DEBUG_PORT} (anti-backgrounding enabled)...")
        
        # Launch Chrome as detached process (won't block)
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Wait for Chrome to be ready
        for i in range(30):  # 30 seconds timeout
            time.sleep(1)
            if is_chrome_running():
                logger.info(f"[DEPS] [OK] Chrome started on port {CHROME_DEBUG_PORT}")
                return True, f"Chrome started on port {CHROME_DEBUG_PORT}"
        
        logger.warning("[DEPS] Chrome launched but port not responding")
        return False, "Chrome launched but debug port not responding"
        
    except Exception as e:
        logger.error(f"[DEPS] Failed to launch Chrome: {e}")
        return False, str(e)


def launch_edge() -> Tuple[bool, str]:
    """
    Launch Edge with remote debugging port and FoundUps profile.

    Returns:
        Tuple of (success, message)
    """
    if is_edge_running():
        logger.info(f"[DEPS] Edge already running on port {EDGE_DEBUG_PORT}")
        return True, "Edge already running"

    edge_path = resolve_edge_path()
    if not edge_path:
        logger.error("[DEPS] Edge executable not found (set EDGE_PATH in .env)")
        return False, "Edge executable not found"

    try:
        EDGE_PROFILE.mkdir(parents=True, exist_ok=True)

        cmd = [
            edge_path,
            f"--remote-debugging-port={EDGE_DEBUG_PORT}",
            f"--user-data-dir={EDGE_PROFILE}",
            # CRITICAL: Anti-backgrounding flags (2025-12-30)
            # Prevents JavaScript/DOM throttling when window not focused
            # Without these, automation stops or becomes erratic when browser is in background
            "--disable-backgrounding-occluded-windows",  # Prevents throttling when behind other windows
            "--disable-renderer-backgrounding",           # Prevents renderer process backgrounding
            "--disable-background-timer-throttling",      # Prevents timer throttling in background tabs
            # FIX (2026-01-23): Prevent 3-tab issue from session restore
            "--no-restore-session-state",                 # Prevents restoring previous tabs
            FOUNDUPS_STUDIO_URL
        ]

        logger.info(f"[DEPS] Launching Edge with debug port {EDGE_DEBUG_PORT} (anti-backgrounding enabled)...")

        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )

        for _ in range(30):
            time.sleep(1)
            if is_edge_running():
                logger.info(f"[DEPS] [OK] Edge started on port {EDGE_DEBUG_PORT}")
                return True, f"Edge started on port {EDGE_DEBUG_PORT}"

        logger.warning("[DEPS] Edge launched but port not responding")
        return False, "Edge launched but debug port not responding"

    except Exception as e:
        logger.error(f"[DEPS] Failed to launch Edge: {e}")
        return False, str(e)


def launch_lm_studio() -> Tuple[bool, str]:
    """
    Launch LM Studio for UI-TARS vision.
    
    Note: LM Studio needs to have the UI-TARS model loaded manually or via startup config.
    
    Returns:
        Tuple of (success, message)
    """
    if is_lm_studio_running():
        logger.info(f"[DEPS] LM Studio already running on port {LM_STUDIO_PORT}")
        return True, "LM Studio already running"

    lm_studio_path = resolve_lm_studio_path()
    if not lm_studio_path:
        logger.warning("[DEPS] LM Studio executable not found (set LM_STUDIO_PATH in .env)")
        logger.warning("[DEPS] Please start LM Studio manually and load UI-TARS model")
        return False, "LM Studio executable not found"
    
    try:
        logger.info(f"[DEPS] Launching LM Studio: {lm_studio_path}")
        
        # Launch LM Studio as detached process
        subprocess.Popen(
            [lm_studio_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        )
        
        # Wait for API to be ready (LM Studio takes longer to start)
        logger.info("[DEPS] Waiting for LM Studio API (this may take 30-60 seconds)...")
        for i in range(120):  # 2 minute timeout
            time.sleep(1)
            if is_lm_studio_running():
                logger.info(f"[DEPS] [OK] LM Studio API ready on port {LM_STUDIO_PORT}")
                return True, f"LM Studio started on port {LM_STUDIO_PORT}"
            if i % 10 == 0 and i > 0:
                logger.info(f"[DEPS] Still waiting for LM Studio... ({i}s)")
        
        logger.warning("[DEPS] LM Studio launched but API not responding")
        logger.warning("[DEPS] Please ensure UI-TARS model is loaded in LM Studio")
        return False, "LM Studio launched but API not responding - load UI-TARS model manually"
        
    except Exception as e:
        logger.error(f"[DEPS] Failed to launch LM Studio: {e}")
        return False, str(e)


async def ensure_dependencies(require_lm_studio: bool = True) -> Dict[str, bool]:
    """
    Ensure all dependencies are running before DAE starts.
    
    Args:
        require_lm_studio: Whether LM Studio is required (for UI-TARS vision)
    
    Returns:
        Dict with status of each dependency
    """
    results = {}
    
    logger.info("="*60)
    logger.info("[DEPS] CHECKING YOUTUBE DAE DEPENDENCIES")
    logger.info("="*60)
    
    # 1. Chrome with debug port
    chrome_ok, chrome_msg = launch_chrome()
    results['chrome'] = chrome_ok
    if not chrome_ok:
        logger.error(f"[DEPS] [ERROR] Chrome: {chrome_msg}")

    # 2. Edge with debug port (optional but recommended for FoundUps)
    edge_auto = os.getenv("YT_EDGE_AUTO_LAUNCH", "true").strip().lower() in ("1", "true", "yes", "y", "on")
    if edge_auto:
        edge_ok, edge_msg = launch_edge()
        results['edge'] = edge_ok
        if not edge_ok:
            logger.warning(f"[DEPS] [WARN] Edge: {edge_msg}")
    else:
        results['edge'] = is_edge_running()
        if results['edge']:
            logger.info("[DEPS] Edge detected (auto-launch disabled)")
    
    # 3. LM Studio for UI-TARS (optional but recommended)
    if require_lm_studio:
        lm_ok, lm_msg = launch_lm_studio()
        results['lm_studio'] = lm_ok
        if not lm_ok:
            logger.warning(f"[DEPS] [WARN] LM Studio: {lm_msg}")
            logger.warning("[DEPS] Comment engagement will use DOM-only mode (no vision verification)")
    else:
        results['lm_studio'] = is_lm_studio_running()
        if results['lm_studio']:
            logger.info("[DEPS] LM Studio detected (optional)")
    
    # Summary
    logger.info("="*60)
    logger.info("[DEPS] DEPENDENCY STATUS:")
    logger.info(f"  Chrome (port {CHROME_DEBUG_PORT}): {'READY' if results['chrome'] else 'NOT READY'}")
    logger.info(f"  Edge (port {EDGE_DEBUG_PORT}): {'READY' if results.get('edge') else 'NOT READY'}")
    logger.info(f"  LM Studio (port {LM_STUDIO_PORT}): {'READY' if results.get('lm_studio') else 'NOT RUNNING'}")
    logger.info("="*60)
    
    return results


def get_dependency_status() -> Dict[str, bool]:
    """Get current status of dependencies without launching."""
    return {
        'chrome': is_chrome_running(),
        'edge': is_edge_running(),
        'lm_studio': is_lm_studio_running()
    }


# Quick test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("\n[INFO] Checking dependency status...")
    status = get_dependency_status()
    print(f"  Chrome (9222): {'READY' if status['chrome'] else 'NOT READY'}")
    print(f"  Edge (9223): {'READY' if status['edge'] else 'NOT READY'}")
    print(f"  LM Studio (1234): {'READY' if status['lm_studio'] else 'NOT READY'}")
    
    if not all(status.values()):
        print("\n[INFO] Launching missing dependencies...")
        asyncio.run(ensure_dependencies())











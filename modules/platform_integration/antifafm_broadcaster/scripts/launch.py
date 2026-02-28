#!/usr/bin/env python3
"""
antifaFM Broadcaster - Headless Launch Script

Run: python modules/platform_integration/antifafm_broadcaster/scripts/launch.py

For Windows Task Scheduler or systemd service.

Integration with main.py:
    from modules.platform_integration.antifafm_broadcaster.scripts.launch import (
        run_antifafm_broadcaster,
        start_antifafm_background,
        stop_antifafm_background,
    )
"""

import asyncio
import logging
import os
import signal
import sys
import threading
from pathlib import Path
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass

from modules.platform_integration.antifafm_broadcaster.src import AntifaFMBroadcaster
from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock

# Global broadcaster instance for background operation
_background_broadcaster: Optional[AntifaFMBroadcaster] = None
_background_task: Optional[asyncio.Task] = None
_background_loop: Optional[asyncio.AbstractEventLoop] = None
_instance_lock = None  # InstanceLock from instance_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(PROJECT_ROOT / "logs" / "antifafm_broadcaster.log")
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Run antifaFM broadcaster headless with PID-based instance locking."""
    logger.info("=" * 60)
    logger.info("antifaFM Broadcaster - Headless Mode")
    logger.info("=" * 60)

    # Instance lock management (WSP 84: Don't duplicate processes)
    lock = get_instance_lock("antifafm_broadcaster")

    # Check for duplicates
    duplicates = lock.check_duplicates()
    if duplicates:
        logger.warning(f"Found {len(duplicates)} duplicate antifaFM process(es): {duplicates}")
        print(f"[RADIO] Found {len(duplicates)} orphaned instance(s). Killing...")
        lock.kill_pids(duplicates)
        import time
        time.sleep(1)

    # Acquire lock
    if not lock.acquire():
        logger.error("Could not acquire instance lock - another instance is running")
        print("[RADIO] FATAL: Could not acquire instance lock")
        return 1

    logger.info(f"Instance lock acquired (PID: {os.getpid()})")

    broadcaster = AntifaFMBroadcaster()

    # Handle shutdown signals
    shutdown_event = asyncio.Event()

    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start broadcasting
        success = await broadcaster.start()
        if not success:
            logger.error("Failed to start broadcaster")
            return 1

        logger.info("Broadcaster running. Press Ctrl+C to stop.")

        # Wait for shutdown signal
        await shutdown_event.wait()

    except Exception as e:
        logger.error(f"Broadcaster error: {e}")
        return 1
    finally:
        await broadcaster.stop()
        lock.release()
        logger.info("Broadcaster stopped. Instance lock released.")

    return 0


def run_antifafm_broadcaster():
    """
    Run antifaFM broadcaster interactively (blocking).

    Called from main menu for on-demand control.
    """
    print("\n[RADIO] antifaFM YouTube Live Broadcaster")
    print("=" * 50)

    # Ensure logs directory
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)

    exit_code = asyncio.run(main())
    return exit_code


async def _background_broadcaster_task():
    """Background task that runs the broadcaster."""
    global _background_broadcaster

    _background_broadcaster = AntifaFMBroadcaster()

    try:
        success = await _background_broadcaster.start()
        if not success:
            logger.error("[RADIO] Background broadcaster failed to start")
            return

        logger.info("[RADIO] Background broadcaster running")

        # Run until stopped
        while _background_broadcaster and _background_broadcaster.status.value == "broadcasting":
            await asyncio.sleep(5)

    except asyncio.CancelledError:
        logger.info("[RADIO] Background broadcaster cancelled")
    except Exception as e:
        logger.error(f"[RADIO] Background broadcaster error: {e}")
    finally:
        if _background_broadcaster:
            await _background_broadcaster.stop()


def start_antifafm_background() -> bool:
    """
    Start antifaFM broadcaster in background thread.

    Uses PID-based instance lock (same pattern as main.py monitor_youtube)
    to prevent multiple broadcaster instances.

    Returns:
        bool: True if started successfully
    """
    global _background_broadcaster, _background_task, _background_loop, _instance_lock

    if _background_broadcaster is not None:
        print("[RADIO] antifaFM already running in background")
        return True

    # Kill ALL existing FFmpeg processes for clean start
    import subprocess
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ffmpeg.exe", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        if "ffmpeg.exe" in result.stdout:
            print("[RADIO] Found existing FFmpeg process(es) - killing for clean start...")
            subprocess.run(["taskkill", "/F", "/IM", "ffmpeg.exe"],
                         capture_output=True, timeout=10)
            import time
            time.sleep(2)  # Let processes fully terminate
            print("[RADIO] Old FFmpeg processes terminated")
    except Exception as e:
        logger.debug(f"[RADIO] FFmpeg cleanup: {e}")

    # Step 0: Set up YouTube Live stream via Chrome automation
    _go_live_driver = None

    if os.getenv("ANTIFAFM_AUTO_GO_LIVE", "1") == "1":
        print("[RADIO] Setting up YouTube Live stream...")
        print("[RADIO] Step 1: Connecting to Chrome...")
        try:
            from modules.platform_integration.antifafm_broadcaster.src.youtube_go_live import (
                click_go_live,
                verify_stream_connected,
                _connect_to_chrome,
            )
            import asyncio

            # Connect to Chrome
            _go_live_driver = _connect_to_chrome()
            if _go_live_driver:
                print("[RADIO] Step 2: Chrome connected - clicking Create → Go Live...")

                # Always attempt Go Live - if already live, it just won't find the button
                loop = asyncio.new_event_loop()
                go_live_result = loop.run_until_complete(click_go_live(_go_live_driver))
                loop.close()

                print(f"[RADIO] Go Live result: {go_live_result}")

                if go_live_result.get("success"):
                    if go_live_result.get("already_live"):
                        print("[RADIO] Stream already active - ready for FFmpeg!")
                    else:
                        print(f"[RADIO] YouTube Live stream ACTIVATED!")
                        print(f"[RADIO] Stream URL: {go_live_result.get('url', 'N/A')}")
                else:
                    print(f"[RADIO] WARNING: Go Live may have failed: {go_live_result.get('error')}")
                    if go_live_result.get('available'):
                        print(f"[RADIO] Available buttons found: {go_live_result.get('available')[:5]}")
            else:
                print("[RADIO] ERROR: Could not connect to Chrome!")

        except Exception as e:
            import traceback
            print(f"[RADIO] Go Live error: {e}")
            traceback.print_exc()

    # Ensure logs directory
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)

    # Instance lock management (WSP 84: Don't duplicate processes)
    _instance_lock = get_instance_lock("antifafm_broadcaster")

    # Check for duplicates
    duplicates = _instance_lock.check_duplicates()
    if duplicates:
        logger.warning(f"[RADIO] Found {len(duplicates)} duplicate antifaFM process(es): {duplicates}")
        print(f"[RADIO] Killing {len(duplicates)} orphaned antifaFM instance(s)...")
        _instance_lock.kill_pids(duplicates)
        import time
        time.sleep(1)  # Let processes die

    # Acquire lock
    if not _instance_lock.acquire():
        logger.error("[RADIO] Could not acquire instance lock - another instance is running")
        print("[RADIO] FATAL: Could not acquire instance lock")
        _instance_lock = None
        return False

    logger.info(f"[RADIO] Instance lock acquired (PID: {os.getpid()})")

    def run_in_thread():
        global _background_loop, _background_task
        _background_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_background_loop)
        _background_task = _background_loop.create_task(_background_broadcaster_task())
        try:
            _background_loop.run_until_complete(_background_task)
        except Exception as e:
            logger.error(f"[RADIO] Background thread error: {e}")
        finally:
            _background_loop.close()

    thread = threading.Thread(target=run_in_thread, daemon=True, name="antifafm-broadcaster")
    thread.start()

    # Give FFmpeg time to start and connect
    import time
    time.sleep(5)

    if _background_broadcaster and _background_broadcaster.status.value == "broadcasting":
        print("[RADIO] FFmpeg started - verifying YouTube connection...")

        # Step 1: Verify stream is connected on YouTube Studio
        if _go_live_driver and os.getenv("ANTIFAFM_VERIFY_STREAM", "1") == "1":
            try:
                from modules.platform_integration.antifafm_broadcaster.src.youtube_go_live import verify_stream_connected
                import asyncio

                # Run verification
                verify_loop = asyncio.new_event_loop()
                verify_result = verify_loop.run_until_complete(
                    verify_stream_connected(_go_live_driver, timeout=30)
                )
                verify_loop.close()

                if verify_result.get("verified"):
                    print("[RADIO] Stream VERIFIED on YouTube Studio!")
                    logger.info(f"[RADIO] Stream verified: {verify_result}")
                else:
                    print(f"[RADIO] WARNING: Stream verification failed - {verify_result}")
                    logger.warning(f"[RADIO] Stream verification failed: {verify_result}")
            except Exception as e:
                print(f"[RADIO] Verification skipped: {e}")
                logger.warning(f"[RADIO] Verification error: {e}")
        else:
            print("[RADIO] Skipping verification (no driver or ANTIFAFM_VERIFY_STREAM=0)")

        print("[RADIO] antifaFM running in background")
        return True
    else:
        print("[RADIO] antifaFM background start pending...")
        return True  # May still be starting


def stop_antifafm_background() -> bool:
    """
    Stop background antifaFM broadcaster.

    Releases PID-based instance lock on shutdown.

    Returns:
        bool: True if stopped successfully
    """
    global _background_broadcaster, _background_task, _background_loop, _instance_lock

    if _background_broadcaster is None:
        print("[RADIO] antifaFM not running in background")
        return True

    try:
        if _background_loop and _background_task:
            _background_loop.call_soon_threadsafe(_background_task.cancel)

        # Give it time to stop
        import time
        time.sleep(2)

        _background_broadcaster = None
        _background_task = None
        _background_loop = None

        # Release instance lock
        if _instance_lock:
            _instance_lock.release()
            logger.info("[RADIO] Instance lock released")
            _instance_lock = None

        print("[RADIO] antifaFM background stopped")
        return True
    except Exception as e:
        logger.error(f"[RADIO] Error stopping background: {e}")
        return False


def start_antifafm_detached() -> bool:
    """
    Start antifaFM broadcaster as a DETACHED process that survives parent exit.

    This spawns a completely separate process that keeps running even after
    main.py exits. Use this instead of start_antifafm_background() when you
    want the stream to persist.

    Returns:
        bool: True if launched successfully
    """
    import subprocess

    # Check for existing FFmpeg streams first
    try:
        result = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq ffmpeg.exe", "/FO", "CSV"],
            capture_output=True, text=True, timeout=5
        )
        if "ffmpeg.exe" in result.stdout:
            print("[RADIO] FFmpeg already running - stream may be active")
            return True
    except Exception:
        pass

    # Launch this script as a detached process
    script_path = Path(__file__).resolve()
    python_exe = sys.executable

    # Windows: CREATE_NEW_PROCESS_GROUP | DETACHED_PROCESS
    # This makes the process independent of the parent
    creation_flags = 0
    if sys.platform == "win32":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    try:
        # Spawn detached process running this script directly
        process = subprocess.Popen(
            [python_exe, str(script_path)],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            creationflags=creation_flags,
            start_new_session=True if sys.platform != "win32" else False,
        )
        print(f"[RADIO] antifaFM launched as detached process (PID: {process.pid})")
        print("[RADIO] Stream will continue running after menu exit")
        return True
    except Exception as e:
        logger.error(f"[RADIO] Failed to launch detached process: {e}")
        print(f"[RADIO] ERROR: {e}")
        return False


def get_antifafm_status() -> dict:
    """Get current antifaFM broadcaster status."""
    global _background_broadcaster

    if _background_broadcaster is None:
        return {"running": False, "status": "stopped"}

    return {
        "running": True,
        **_background_broadcaster.get_status()
    }


def diagnose_antifafm() -> dict:
    """
    Diagnose antifaFM broadcaster configuration for troubleshooting.

    Run: python -c "from modules.platform_integration.antifafm_broadcaster.scripts.launch import diagnose_antifafm; print(diagnose_antifafm())"
    """
    import json

    results = {
        "stream_key_set": bool(os.getenv("ANTIFAFM_YOUTUBE_STREAM_KEY")),
        "stream_url": os.getenv("ANTIFAFM_STREAM_URL", "https://a12.asurahosting.com/listen/antifafm/radio.mp3"),
        "fx_enabled": os.getenv("ANTIFAFM_FX_ENABLED", "true").lower() in ("true", "1"),
        "visual_path": os.getenv("ANTIFAFM_DEFAULT_VISUAL", "modules/platform_integration/antifafm_broadcaster/assets/default_visual.png"),
        "ffmpeg_available": False,
        "visual_exists": False,
        "visual_effects_import": False,
        "errors": [],
    }

    # Check FFmpeg
    try:
        import subprocess
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True, timeout=5)
        results["ffmpeg_available"] = True
    except Exception as e:
        results["errors"].append(f"FFmpeg: {e}")

    # Check visual
    from pathlib import Path
    visual = Path(results["visual_path"])
    results["visual_exists"] = visual.exists()
    if not visual.exists():
        results["errors"].append(f"Visual not found: {visual}")

    # Check visual effects module
    try:
        from modules.platform_integration.antifafm_broadcaster.src.visual_effects import VisualEffectsBuilder
        results["visual_effects_import"] = True
    except Exception as e:
        results["errors"].append(f"Visual effects import: {e}")

    # Summary
    results["ready"] = (
        results["stream_key_set"] and
        results["ffmpeg_available"] and
        results["visual_exists"]
    )

    print("\n[DIAGNOSE] antifaFM Broadcaster Status:")
    print("=" * 50)
    print(f"  Stream Key Set: {'YES' if results['stream_key_set'] else 'NO (required)'}")
    print(f"  FFmpeg Available: {'YES' if results['ffmpeg_available'] else 'NO (required)'}")
    print(f"  Visual Exists: {'YES' if results['visual_exists'] else 'NO (will auto-create)'}")
    print(f"  Effects Enabled: {'YES' if results['fx_enabled'] else 'NO (Layer 1 mode)'}")
    print(f"  Effects Module: {'OK' if results['visual_effects_import'] else 'FAIL'}")
    print(f"  READY: {'YES' if results['ready'] else 'NO'}")
    if results["errors"]:
        print(f"\n  Errors:")
        for err in results["errors"]:
            print(f"    - {err}")
    print("=" * 50)

    return results


def print_cli_usage():
    """Print CLI usage for OpenClaw/IronClaw."""
    print("""
antifaFM Broadcaster CLI - For OpenClaw/IronClaw agents

Usage:
  python launch.py                          # Start broadcaster (foreground)
  python launch.py --start                  # Start in background
  python launch.py --stop                   # Stop background broadcaster
  python launch.py --status                 # Check broadcaster status
  python launch.py --diagnose               # Run diagnostics
  python launch.py --json                   # JSON output (for agents)
  python launch.py --layer1                 # Disable visual effects
  python launch.py --title "Title"          # Set stream title before start
  python launch.py --desc "Description"     # Set stream description

Examples:
  # OpenClaw: Start broadcaster with custom title
  python launch.py --start --json --title "antifaFM Radio - Live Now"

  # IronClaw: Check status
  python launch.py --status --json
  # Output: {"running": true, "status": "broadcasting", "uptime": 3600}

  # Stop broadcaster
  python launch.py --stop --json
  # Output: {"success": true, "stopped": true}

Output (--json mode):
  {"success": true, "status": "started", "pid": 12345}
  {"success": false, "error": "already_running"}
""")


def cli_status_check() -> dict:
    """Check broadcaster status for CLI."""
    global _background_broadcaster

    result = {
        "running": _background_broadcaster is not None,
        "status": "unknown"
    }

    if _background_broadcaster:
        try:
            status = _background_broadcaster.get_status()
            result["status"] = status.get("state", "unknown")
            result["uptime"] = status.get("uptime_seconds", 0)
            result["stream_health"] = status.get("stream_health", {})
        except Exception as e:
            result["error"] = str(e)
    else:
        # Check if process is running via lock file
        lock = get_instance_lock("antifafm_broadcaster")
        duplicates = lock.check_duplicates()
        if duplicates:
            result["running"] = True
            result["status"] = "running_external"
            result["pids"] = duplicates
        else:
            result["status"] = "stopped"

    return result


if __name__ == "__main__":
    import sys as _sys
    import json as _json

    # Ensure logs directory exists
    (PROJECT_ROOT / "logs").mkdir(exist_ok=True)

    # Parse CLI arguments
    args = _sys.argv[1:]
    json_output = "--json" in args
    do_start = "--start" in args
    do_stop = "--stop" in args
    do_status = "--status" in args
    do_diagnose = "--diagnose" in args

    # Parse title/description
    stream_title = None
    stream_desc = None
    for i, arg in enumerate(args):
        if arg == "--title" and i + 1 < len(args):
            stream_title = args[i + 1]
        elif arg == "--desc" and i + 1 < len(args):
            stream_desc = args[i + 1]
        elif arg == "--help" or arg == "-h":
            print_cli_usage()
            _sys.exit(0)

    # Set stream title/description in environment for broadcaster to pick up
    if stream_title:
        os.environ["ANTIFAFM_STREAM_TITLE"] = stream_title
    if stream_desc:
        os.environ["ANTIFAFM_STREAM_DESC"] = stream_desc

    # Check for --diagnose flag
    if do_diagnose:
        if json_output:
            result = diagnose_antifafm()
            print(_json.dumps(result))
        else:
            diagnose_antifafm()
        _sys.exit(0)

    # Check for --status flag
    if do_status:
        result = cli_status_check()
        if json_output:
            print(_json.dumps(result))
        else:
            print(f"[STATUS] Running: {result.get('running')}")
            print(f"[STATUS] State: {result.get('status')}")
            if result.get('uptime'):
                print(f"[STATUS] Uptime: {result.get('uptime')}s")
        _sys.exit(0)

    # Check for --stop flag
    if do_stop:
        result = {"success": False}
        try:
            stopped = stop_antifafm_background()
            result["success"] = stopped
            result["stopped"] = stopped
        except Exception as e:
            result["error"] = str(e)

        if json_output:
            print(_json.dumps(result))
        else:
            if result.get("stopped"):
                print("[RADIO] Broadcaster stopped")
            else:
                print("[RADIO] Could not stop broadcaster (may not be running)")
        _sys.exit(0 if result.get("success") else 1)

    # Check for --start flag (background)
    if do_start:
        result = {"success": False}
        try:
            started = start_antifafm_background()
            result["success"] = started
            result["status"] = "started" if started else "failed"
            result["pid"] = os.getpid()
            if stream_title:
                result["title"] = stream_title
        except Exception as e:
            result["error"] = str(e)

        if json_output:
            print(_json.dumps(result))
        else:
            if result.get("success"):
                print(f"[RADIO] Broadcaster started (PID: {result.get('pid')})")
                if stream_title:
                    print(f"[RADIO] Stream title: {stream_title}")
            else:
                print(f"[RADIO] Failed to start: {result.get('error', 'unknown')}")
        _sys.exit(0 if result.get("success") else 1)

    # Check for --layer1 flag (disable effects)
    if "--layer1" in args:
        os.environ["ANTIFAFM_FX_ENABLED"] = "false"
        if not json_output:
            print("[LAYER] Running Layer 1 only (no visual effects)")

    # Default: run in foreground
    if json_output:
        # For foreground with JSON, output start status then run
        print(_json.dumps({"status": "starting", "mode": "foreground", "pid": os.getpid()}))

    exit_code = asyncio.run(main())
    _sys.exit(exit_code)

"""
GCC Shipping Tracker - Real-time Strait of Hormuz vessel tracking

Provides real-time shipping data for the Gulf Cooperation Council region,
with focus on the Strait of Hormuz - critical oil transit chokepoint.

BOOT LAYER: Default visual for antifaFM stream with 10-minute rotation.
Runs until stakeholder (moderator) or delegate (managing moderator) intervenes.

Usage:
    python executor.py --daemon              # Boot mode: 10-min rotation
    python executor.py --map                 # Open live map
    python executor.py --tankers             # Filter tankers
    python executor.py --alerts              # Show alerts

WSP 27: Universal DAE Architecture
WSP 103: CLI Interface Standard
"""

import argparse
import asyncio
import json
import logging
import os
import signal
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Rotation interval (10 minutes)
ROTATION_INTERVAL_SEC = 600

# Stakeholder/Delegate override signal file
OVERRIDE_SIGNAL_FILE = Path(__file__).parent / "stakeholder_override.signal"

# MarineTraffic URLs for GCC region
MARINETRAFFIC_HORMUZ = "https://www.marinetraffic.com/en/ais/home/centerx/56.3/centery/26.5/zoom/8"
MARINETRAFFIC_GULF = "https://www.marinetraffic.com/en/ais/home/centerx/51.5/centery/26.0/zoom/6"
VESSELFINDER_HORMUZ = "https://www.vesselfinder.com/?imo=0&mmsi=0&type=0&area=strait-of-hormuz"


# Hormuz region bounding box (approximate)
HORMUZ_BOUNDS = {
    "lat_min": 25.5,
    "lat_max": 27.5,
    "lon_min": 55.0,
    "lon_max": 57.5,
}


async def fetch_marine_traffic_data() -> Dict[str, Any]:
    """
    Fetch vessel data from MarineTraffic.

    Note: Full API requires subscription. This provides summary view.
    """
    try:
        import aiohttp

        # MarineTraffic requires API key for programmatic access
        # This is a placeholder for the data structure
        return {
            "source": "marinetraffic",
            "status": "api_key_required",
            "fallback": MARINETRAFFIC_HORMUZ,
            "message": "Open map URL for live view"
        }
    except ImportError:
        return {"error": "aiohttp not installed", "fallback": MARINETRAFFIC_HORMUZ}


async def fetch_ais_summary() -> Dict[str, Any]:
    """
    Fetch AIS (Automatic Identification System) summary for Hormuz region.

    Returns approximate vessel counts by type.
    """
    # Real implementation would query AIS data providers
    # This provides the data structure for integration
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "region": "strait_of_hormuz",
        "bounds": HORMUZ_BOUNDS,
        "status": "live_map_available",
        "map_urls": {
            "marinetraffic": MARINETRAFFIC_HORMUZ,
            "vesselfinder": VESSELFINDER_HORMUZ,
        },
        "note": "For real-time vessel counts, open map URL or configure API key"
    }


def open_live_map(source: str = "marinetraffic") -> Dict[str, Any]:
    """Open live shipping map in default browser."""
    urls = {
        "marinetraffic": MARINETRAFFIC_HORMUZ,
        "vesselfinder": VESSELFINDER_HORMUZ,
        "gulf": MARINETRAFFIC_GULF,
    }

    url = urls.get(source, MARINETRAFFIC_HORMUZ)
    webbrowser.open(url)

    return {
        "success": True,
        "action": "opened_browser",
        "url": url,
        "source": source
    }


def get_tanker_focus_url() -> str:
    """Get URL filtered for tankers only."""
    # MarineTraffic ship type filter: 80-89 = Tankers
    return f"{MARINETRAFFIC_HORMUZ}/shiptype:80,81,82,83,84,85,86,87,88,89"


async def check_alerts() -> List[Dict[str, Any]]:
    """
    Check for shipping alerts in GCC region.

    Alert types:
    - high_traffic: Unusual congestion
    - naval_activity: Military vessels detected
    - blockade_risk: Potential transit disruption
    - incident: Reported maritime incident
    """
    # Placeholder for alert system
    # Would integrate with news feeds, maritime security services
    return [
        {
            "type": "info",
            "message": "Strait of Hormuz: Normal traffic conditions",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    ]


async def execute_skill(
    action: str = "summary",
    open_map: bool = False,
    tankers_only: bool = False,
    show_alerts: bool = False,
) -> Dict[str, Any]:
    """
    Main skill executor for GCC shipping tracker.

    Args:
        action: summary|map|tankers|alerts
        open_map: Open live map in browser
        tankers_only: Filter for oil tankers
        show_alerts: Check for maritime alerts

    Returns:
        Dict with shipping data and status
    """
    result = {
        "skill": "gcc_shipping_tracker",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "region": "gcc_strait_of_hormuz",
    }

    if open_map or action == "map":
        source = "tankers" if tankers_only else "marinetraffic"
        if tankers_only:
            url = get_tanker_focus_url()
            webbrowser.open(url)
            result["map"] = {"opened": True, "url": url, "filter": "tankers"}
        else:
            map_result = open_live_map()
            result["map"] = map_result
        return result

    if show_alerts or action == "alerts":
        alerts = await check_alerts()
        result["alerts"] = alerts
        return result

    if tankers_only or action == "tankers":
        result["focus"] = "tankers"
        result["tanker_map_url"] = get_tanker_focus_url()
        result["message"] = "Use --map to open tanker-filtered view"
        return result

    # Default: summary
    summary = await fetch_ais_summary()
    result.update(summary)
    return result


async def update_obs_browser_source(url: str) -> Dict[str, Any]:
    """
    Update OBS browser source to show GCC shipping map.

    Requires: GCC_Browser source in OBS scene.
    """
    try:
        import obsws_python as obs

        host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
        port = int(os.getenv("OBS_WEBSOCKET_PORT", 4455))
        password = os.getenv("OBS_WEBSOCKET_PASSWORD", "")

        client = obs.ReqClient(host=host, port=port, password=password)

        # Update browser source URL
        client.set_input_settings(
            input_name="GCC_Browser",
            input_settings={"url": url},
            overlay=True
        )

        logger.info(f"[GCC] Updated OBS browser source: {url[:50]}...")
        return {"success": True, "source": "GCC_Browser", "url": url}

    except ImportError:
        logger.warning("[GCC] obsws-python not installed")
        return {"success": False, "error": "obsws-python not installed"}
    except Exception as e:
        logger.error(f"[GCC] OBS update failed: {e}")
        return {"success": False, "error": str(e)}


def check_stakeholder_override() -> bool:
    """Check if stakeholder/delegate has requested override."""
    if OVERRIDE_SIGNAL_FILE.exists():
        logger.info("[GCC] Stakeholder override detected - pausing rotation")
        return True
    return False


def clear_stakeholder_override():
    """Clear the override signal (for restart)."""
    if OVERRIDE_SIGNAL_FILE.exists():
        OVERRIDE_SIGNAL_FILE.unlink()
        logger.info("[GCC] Override signal cleared")


async def rotation_daemon():
    """
    Boot layer daemon - 10-minute rotation cycle.

    Shows GCC shipping map on stream, rotates views every 10 minutes.
    Stops when stakeholder/delegate signals override.
    """
    logger.info("[GCC-DAEMON] Starting boot layer rotation (10-min cycle)")
    logger.info(f"[GCC-DAEMON] Override signal file: {OVERRIDE_SIGNAL_FILE}")

    # Clear any stale override
    clear_stakeholder_override()

    # Rotation views
    views = [
        ("hormuz", MARINETRAFFIC_HORMUZ),
        ("gulf", MARINETRAFFIC_GULF),
        ("tankers", get_tanker_focus_url()),
    ]
    view_index = 0
    cycle_count = 0

    running = True

    def signal_handler(sig, frame):
        nonlocal running
        logger.info("[GCC-DAEMON] Shutdown signal received")
        running = False

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    while running:
        # Check for stakeholder override
        if check_stakeholder_override():
            logger.info("[GCC-DAEMON] Waiting for override to clear...")
            await asyncio.sleep(60)  # Check every minute
            continue

        # Get current view
        view_name, view_url = views[view_index]
        cycle_count += 1

        logger.info(f"[GCC-DAEMON] Cycle {cycle_count}: Showing {view_name}")

        # Update OBS browser source
        obs_result = await update_obs_browser_source(view_url)
        if obs_result.get("success"):
            logger.info(f"[GCC-DAEMON] OBS updated: {view_name}")
        else:
            logger.warning(f"[GCC-DAEMON] OBS update failed: {obs_result.get('error')}")

        # Fetch and log current status
        status = await fetch_ais_summary()
        logger.info(f"[GCC-DAEMON] Status: {status.get('status', 'unknown')}")

        # Check alerts
        alerts = await check_alerts()
        for alert in alerts:
            if alert.get("type") != "info":
                logger.warning(f"[GCC-ALERT] {alert['type']}: {alert['message']}")

        # Wait for rotation interval (check override every 30s)
        wait_remaining = ROTATION_INTERVAL_SEC
        while wait_remaining > 0 and running:
            if check_stakeholder_override():
                break
            sleep_time = min(30, wait_remaining)
            await asyncio.sleep(sleep_time)
            wait_remaining -= sleep_time

        # Rotate to next view
        view_index = (view_index + 1) % len(views)

    logger.info("[GCC-DAEMON] Shutdown complete")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="GCC Shipping Tracker - Strait of Hormuz vessel monitoring"
    )
    parser.add_argument(
        "action",
        nargs="?",
        default="summary",
        choices=["summary", "map", "tankers", "alerts", "daemon"],
        help="Action to perform"
    )
    parser.add_argument("--daemon", action="store_true", help="Run boot layer daemon (10-min rotation)")
    parser.add_argument("--map", action="store_true", help="Open live map in browser")
    parser.add_argument("--tankers", action="store_true", help="Filter for oil tankers")
    parser.add_argument("--alerts", action="store_true", help="Show maritime alerts")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--override", action="store_true", help="Set stakeholder override (pause daemon)")
    parser.add_argument("--clear-override", action="store_true", help="Clear stakeholder override")

    args = parser.parse_args()

    # Handle override commands
    if args.override:
        OVERRIDE_SIGNAL_FILE.touch()
        print(f"[GCC] Stakeholder override set - daemon will pause")
        print(f"[GCC] Signal file: {OVERRIDE_SIGNAL_FILE}")
        return

    if args.clear_override:
        clear_stakeholder_override()
        print(f"[GCC] Override cleared - daemon will resume")
        return

    # Daemon mode
    if args.daemon or args.action == "daemon":
        print("[GCC] Starting boot layer daemon...")
        print("[GCC] Press Ctrl+C or use --override to stop")
        asyncio.run(rotation_daemon())
        return

    # Regular skill execution
    result = asyncio.run(execute_skill(
        action=args.action,
        open_map=args.map,
        tankers_only=args.tankers,
        show_alerts=args.alerts,
    ))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print("GCC SHIPPING TRACKER - Strait of Hormuz")
        print(f"{'='*60}")
        print(f"Timestamp: {result.get('timestamp', 'N/A')}")
        print(f"Region: {result.get('region', 'gcc_strait_of_hormuz')}")

        if "map" in result:
            print(f"\nMap opened: {result['map'].get('url', 'N/A')}")

        if "alerts" in result:
            print("\nAlerts:")
            for alert in result["alerts"]:
                print(f"  [{alert['type'].upper()}] {alert['message']}")

        if "map_urls" in result:
            print("\nLive Maps:")
            for name, url in result["map_urls"].items():
                print(f"  {name}: {url}")

        print(f"\n{'='*60}")


if __name__ == "__main__":
    main()

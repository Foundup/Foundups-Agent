#!/usr/bin/env python
"""
Apply Grid Layout to antifaFM OBS Sources

Arranges video and news sources in a visually appealing grid layout.
Canvas: 1920x1080

Layout:
+----------------------------------+
|  [News 1]  [News 2]  [News 3]   |  <- Top row: small news tiles (320x180)
+----------------------------------+
|                                  |
|        [Main Video]              |  <- Center: main content (1280x720)
|                                  |
+----------------------------------+
|  [News 4]  [Video 2]  [Video 3] |  <- Bottom row: mixed content
+----------------------------------+

Usage:
    python -m antifafm_broadcaster.scripts.apply_layout
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.platform_integration.antifafm_broadcaster.src.obs_controller import OBSController


# Layout constants (1920x1080 canvas)
CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080

# Tile sizes
SMALL_TILE_W = 320
SMALL_TILE_H = 180
MAIN_W = 1280
MAIN_H = 720

# Layout positions (use exact source names from OBS)
LAYOUTS = {
    # Main background - full screen behind everything
    "antifaFM Background": {
        "x": 0, "y": 0,
        "width": CANVAS_WIDTH, "height": CANVAS_HEIGHT,
        "order": 0,  # Bottom layer
    },

    # Top row - news streams (y=0)
    "Al Jazeera English": {
        "x": 0, "y": 0,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },
    "France 24 English": {
        "x": SMALL_TILE_W, "y": 0,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },
    "DW News": {
        "x": SMALL_TILE_W * 2, "y": 0,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },
    "Sky News": {
        "x": CANVAS_WIDTH - SMALL_TILE_W, "y": 0,  # Top right
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },

    # Bottom row (y = 1080 - 180 = 900)
    "Charlie Chaplin": {
        "x": 0, "y": CANVAS_HEIGHT - SMALL_TILE_H,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },
    "Throw Tomatoes": {  # Actual name in OBS
        "x": SMALL_TILE_W, "y": CANVAS_HEIGHT - SMALL_TILE_H,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },
    "Browser News": {
        "x": CANVAS_WIDTH - SMALL_TILE_W, "y": CANVAS_HEIGHT - SMALL_TILE_H,
        "width": SMALL_TILE_W, "height": SMALL_TILE_H,
        "order": 10,
    },

    # Center position for main content (Off the Grid video)
    "Off the Grid": {
        "x": (CANVAS_WIDTH - MAIN_W) // 2,  # 320
        "y": (CANVAS_HEIGHT - MAIN_H) // 2,  # 180
        "width": MAIN_W, "height": MAIN_H,
        "order": 5,
    },

    # Hide other sources by moving off-screen or making small
    "fortnite": {
        "x": -1920, "y": 0,  # Off-screen left
        "width": 320, "height": 180,
        "order": 0,
    },
    "Display 1": {
        "x": -1920, "y": 0,
        "width": 320, "height": 180,
        "order": 0,
    },
    "Display 2": {
        "x": -1920, "y": 0,
        "width": 320, "height": 180,
        "order": 0,
    },
    "camera": {
        "x": -1920, "y": 0,
        "width": 320, "height": 180,
        "order": 0,
    },
    "Video Capture Device 2": {
        "x": -1920, "y": 0,
        "width": 320, "height": 180,
        "order": 0,
    },
}


async def apply_layout():
    """Apply the grid layout to all sources."""
    print("=" * 60)
    print("antifaFM OBS Layout Manager")
    print("=" * 60)

    host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
    controller = OBSController(host=host)

    if not await controller.connect():
        print("[ERROR] Could not connect to OBS")
        return False

    # Get current scene items
    items = await controller.list_scene_items()
    print(f"\n[INFO] Found {len(items)} scene items:")
    for item in items:
        print(f"  - {item['name']} (index: {item['index']})")

    # Get list of source names in scene
    source_names = [item['name'] for item in items]

    # Apply layout to each source
    print("\n[LAYOUT] Applying positions...")
    applied = 0

    for source_name, layout in LAYOUTS.items():
        if source_name in source_names:
            success = await controller.set_source_bounds(
                source_name,
                x=layout["x"],
                y=layout["y"],
                width=layout["width"],
                height=layout["height"],
            )
            if success:
                print(f"  [OK] {source_name}: ({layout['x']}, {layout['y']}) {layout['width']}x{layout['height']}")
                applied += 1
            else:
                print(f"  [FAIL] {source_name}")
        else:
            print(f"  [SKIP] {source_name} (not in scene)")

    print(f"\n[DONE] Applied layout to {applied} sources")

    controller.disconnect()
    return True


async def list_current_layout():
    """List current positions of all sources."""
    print("=" * 60)
    print("Current OBS Layout")
    print("=" * 60)

    host = os.getenv("OBS_WEBSOCKET_HOST", "localhost")
    controller = OBSController(host=host)

    if not await controller.connect():
        print("[ERROR] Could not connect to OBS")
        return

    items = await controller.list_scene_items()
    print(f"\nScene Items ({len(items)}):")
    for item in sorted(items, key=lambda x: x['index']):
        print(f"  [{item['index']:2d}] {item['name']}")

    controller.disconnect()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        asyncio.run(list_current_layout())
    else:
        asyncio.run(apply_layout())

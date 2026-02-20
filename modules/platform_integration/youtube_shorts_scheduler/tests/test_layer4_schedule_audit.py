"""
Layer 4 Test: Scheduled Audit (Dates + Conflicts)

Scans scheduled shorts and reports duplicate date/time conflicts.
Independent layer: no scheduling actions performed.

Run:
  python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_layer4_schedule_audit --selenium
"""

import logging
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"
CHROME_PORT = 9222


def connect_chrome():
    options = Options()
    options.add_experimental_option("debuggerAddress", f"127.0.0.1:{CHROME_PORT}")
    return webdriver.Chrome(options=options)


def audit_scheduled_conflicts(videos):
    by_slot = defaultdict(list)
    for v in videos:
        key = (v.get("date") or v.get("date_text"), v.get("time"))
        by_slot[key].append(v)

    conflicts = {k: v for k, v in by_slot.items() if len(v) > 1}
    return conflicts


def run_audit():
    driver = connect_chrome()
    dom = YouTubeStudioDOM(driver)

    logger.info("[LAYER 4] Navigating to Scheduled filter...")
    if not dom.navigate_to_shorts_with_fallback(CHANNEL_ID, "SCHEDULED", use_ui_tars=True):
        logger.error("[LAYER 4] Failed to apply Scheduled filter")
        return False

    videos = dom.get_scheduled_videos_detailed()
    logger.info(f"[LAYER 4] Found {len(videos)} scheduled videos")

    conflicts = audit_scheduled_conflicts(videos)
    if conflicts:
        logger.warning(f"[LAYER 4] Found {len(conflicts)} conflicting schedule slots")
        for (date_key, time_key), items in conflicts.items():
            logger.warning(f"  - {date_key} {time_key}: {len(items)} videos")
    else:
        logger.info("[LAYER 4] No schedule conflicts detected")

    return True


if __name__ == "__main__":
    run_audit()

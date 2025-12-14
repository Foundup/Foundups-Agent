import asyncio
import sys
import logging
import os
import json
from datetime import datetime
from pathlib import Path

# Add repo root to path
repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.browser_actions.src.action_router import ActionRouter, DriverType

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEMETRY_DIR = repo_root / "telemetry" / "feedback" / "live_engagement"
CONTROL_DIR = repo_root / "telemetry" / "feedback" / "control"
TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)
CONTROL_DIR.mkdir(parents=True, exist_ok=True)


def write_feedback(event: str, payload: dict) -> None:
    """Emit JSON feedback for 012 to observe."""
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
    out_path = TELEMETRY_DIR / f"{ts}_{event}.json"
    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
    except Exception as e:
        logger.warning(f"[FEEDBACK] Failed to write {out_path}: {e}")


def feedback_observer(event: str, payload: dict) -> None:
    write_feedback(event, payload)


async def wait_if_gate(stage: str) -> None:
    """Optional gating: if FEEDBACK_GATE=1, wait for proceed signal."""
    if os.getenv("FEEDBACK_GATE", "").lower() not in {"1", "true", "yes"}:
        return
    proceed_file = CONTROL_DIR / "proceed.txt"
    logger.info(f"[GATE] Waiting for proceed at stage '{stage}' (set FEEDBACK_GATE=0 to skip)")
    write_feedback("gate_wait", {"stage": stage})
    while True:
        try:
            if proceed_file.exists():
                content = proceed_file.read_text(encoding="utf-8").strip().lower()
                if content in {"go", "ok", "continue", stage.lower()}:
                    write_feedback("gate_proceed", {"stage": stage})
                    return
        except Exception:
            pass
        await asyncio.sleep(1)


async def test_live_engagement():
    print("\n" + "=" * 60)
    print("LIVE ENGAGEMENT TEST - Like, Heart, Reply")
    print("=" * 60 + "\n")

    # Force vision-first and disable fallback churn
    router = ActionRouter(
        profile="youtube_move2japan",
        fallback_enabled=False,
        observers=[feedback_observer],
    )

    try:
        # 1. Navigate
        url = "https://studio.youtube.com/channel/UC-LSSlOZwpGIRIYihaz8zCw/comments/inbox"
        print(f"[1] Navigating to: {url}")
        await router.execute("navigate", {"url": url}, driver=DriverType.SELENIUM)

        print("[1.5] Waiting for page load (8s)...")
        await asyncio.sleep(8)
        await wait_if_gate("after_navigate")

        driver = await router._ensure_selenium()
        comment_batch = int(os.getenv("COMMENT_BATCH", "1"))
        consecutive_failures = 0

        # Engage N comments per run to reduce manual repeats
        for idx in range(comment_batch):
            print(f"\n=== Engaging comment #{idx+1} ===")

            # 2. Like (Thumbs Up)
            print("\n[2] Executing LIKE (Thumbs Up)...")
            like_desc = (
                "gray thumbs up icon in the comment action bar, located between the "
                "replies counter and thumbs down icon"
            )
            like_result = await router.execute(
                "click_element",
                {"description": like_desc},
                driver=DriverType.VISION,
            )
            print(f"    Like Result: {like_result.success}")
            write_feedback(
                f"like_result_{idx}",
                {"success": like_result.success, "error": like_result.error},
            )
            await asyncio.sleep(1.0)
            await wait_if_gate(f"after_like_{idx}")

            # 3. Heart (Creator Heart)
            print("\n[3] Executing HEART (Creator Heart)...")
            heart_desc = (
                "gray outlined heart icon in the comment action bar, located between "
                "thumbs down and three-dot menu"
            )
            heart_result = await router.execute(
                "click_element",
                {"description": heart_desc},
                driver=DriverType.VISION,
            )
            print(f"    Heart Result: {heart_result.success}")
            write_feedback(
                f"heart_result_{idx}",
                {"success": heart_result.success, "error": heart_result.error},
            )
            await asyncio.sleep(1.0)
            await wait_if_gate(f"after_heart_{idx}")

            # 4. Reply (Open Box)
            print("\n[4] Opening REPLY box...")
            reply_btn_desc = "gray Reply text button at the start of the comment action bar"
            reply_open_result = await router.execute(
                "click_element",
                {"description": reply_btn_desc},
                driver=DriverType.VISION,
            )
            print(f"    Reply Open Result: {reply_open_result.success}")
            write_feedback(
                f"reply_open_result_{idx}",
                {"success": reply_open_result.success, "error": reply_open_result.error},
            )

            if reply_open_result.success:
                await asyncio.sleep(1.0)
                await wait_if_gate(f"after_reply_open_{idx}")

                # 5. Type Reply
                print("\n[5] Typing REPLY...")
                reply_text = "0102 was here."
                type_result = await router.execute(
                    "type_text",
                    {
                        "description": "reply text input box that appeared below the comment",
                        "text": reply_text,
                    },
                    driver=DriverType.VISION,
                )
                print(f"    Type Result: {type_result.success}")
                write_feedback(
                    f"reply_type_result_{idx}",
                    {"success": type_result.success, "error": type_result.error},
                )

                # 6. Submit reply
                print(f"\n[6] Submitting REPLY...")
                submit_desc = "Reply button to post the typed reply"
                submit_result = await router.execute(
                    "click_element", {"description": submit_desc}, driver=DriverType.VISION
                )
                print(f"    Submit Result: {submit_result.success}")
                write_feedback(
                    f"reply_submit_result_{idx}",
                    {"success": submit_result.success, "error": submit_result.error},
                )

                consecutive_failures = 0
            else:
                consecutive_failures += 1

            # Scroll down to next comment region
            if driver:
                try:
                    driver.execute_script("window.scrollBy(0, 450);")
                    await asyncio.sleep(0.8)
                except Exception as e:
                    logger.warning(f"[SCROLL] Failed to scroll: {e}")

            if consecutive_failures >= 2:
                logger.warning("[LOOP] Too many consecutive failures, stopping batch early.")
                break

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()
    finally:
        print("\n[7] Closing router...")
        router.close()


if __name__ == "__main__":
    asyncio.run(test_live_engagement())

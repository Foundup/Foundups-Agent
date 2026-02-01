# -*- coding: utf-8 -*-
"""
Autonomous Video Enhancement Batch Runner

WSP Compliance:
    WSP 77: Agent Coordination (provider rotation)
    WSP 91: DAE Observability (audit logging)

Purpose:
    Batch enhance all UnDaoDu videos with:
    - Provider rotation (Grok → OpenAI → Gemini)
    - Rate limit handling (exponential backoff)
    - Checkpoint/resume capability
    - Audit logging

Usage:
    python scripts/batch_enhance_videos.py --max-videos 50 --provider grok
    python scripts/batch_enhance_videos.py --resume  # Continue from checkpoint
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.ai_intelligence.video_indexer.src.video_enhancer import VideoEnhancer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# WSP 91: DAEmon Pulse Infrastructure
HOLO_OUTPUT = Path("holo_index/holo_index/output/holo_output_history.jsonl")


def emit_pulse(pulse_type: str, message: str, severity: int = 0, metrics: dict = None):
    """
    Emit cardiovascular pulse to DAEmon (WSP 91).

    Args:
        pulse_type: HEARTBEAT | STATE_CHANGE | COMPLETION | ERROR | THRESHOLD
        message: Concise status (< 80 chars)
        severity: 0=info, 1=warning, 2=error, 3=critical
        metrics: Optional dict of numeric metrics
    """
    try:
        HOLO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        pulse = {
            "ts": datetime.now().isoformat(),
            "dae": "batch_enhance",
            "type": pulse_type,
            "msg": message,
            "sev": severity,
        }
        if metrics:
            pulse["metrics"] = metrics
        with open(HOLO_OUTPUT, "a", encoding="utf-8") as f:
            f.write(json.dumps(pulse) + "\n")
        logger.debug(f"[PULSE] {pulse_type}: {message}")
    except Exception as e:
        logger.warning(f"[PULSE] Failed to emit: {e}")

# Provider rotation order
PROVIDERS = [
    ("grok-3-latest", "Grok"),
    ("gpt-4", "OpenAI"),
    ("gemini-2.5-flash", "Gemini"),  # 2.0-flash retiring Mar 2026; 2.5-flash recommended
]

# Paths
VIDEO_DIR = Path("memory/video_index/undaodu")
CHECKPOINT_FILE = Path("memory/enhancement_checkpoint.json")
AUDIT_FILE = Path("memory/enhancement_audit.jsonl")


def load_checkpoint() -> dict:
    """Load checkpoint or return empty state."""
    if CHECKPOINT_FILE.exists():
        return json.loads(CHECKPOINT_FILE.read_text(encoding="utf-8"))
    return {
        "completed": [],
        "failed": [],
        "current_provider_idx": 0,
        "last_run": None,
    }


def save_checkpoint(state: dict):
    """Save checkpoint state."""
    state["last_run"] = datetime.now().isoformat()
    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def log_audit(video_id: str, provider: str, success: bool, tier: int, error: str = None):
    """Append to audit log."""
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now().isoformat(),
        "video_id": video_id,
        "provider": provider,
        "success": success,
        "quality_tier": tier,
        "error": error,
    }
    with open(AUDIT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def get_videos_needing_enhancement() -> list:
    """Get list of video JSONs that need enhancement."""
    needing = []
    for f in VIDEO_DIR.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if not data.get("training_data"):
                needing.append(f)
        except:
            needing.append(f)
    return needing


def run_batch(
    max_videos: int = 50,
    start_provider_idx: int = 0,
    delay_between: float = 5.0,
    rate_limit_delay: float = 30.0,
):
    """
    Run batch enhancement with provider rotation.

    Args:
        max_videos: Maximum videos to process this run
        start_provider_idx: Which provider to start with
        delay_between: Seconds between videos
        rate_limit_delay: Seconds to wait on rate limit
    """
    state = load_checkpoint()
    completed_set = set(state["completed"])

    # Get videos needing enhancement (excluding already completed)
    all_needing = get_videos_needing_enhancement()
    to_process = [f for f in all_needing if f.stem not in completed_set]

    logger.info(f"Videos needing enhancement: {len(all_needing)}")
    logger.info(f"Already completed: {len(completed_set)}")
    logger.info(f"To process this run: {min(len(to_process), max_videos)}")

    if not to_process:
        logger.info("All videos already enhanced!")
        emit_pulse("COMPLETION", "All 454 videos enhanced", metrics={"total": 454, "remaining": 0})
        return

    # WSP 91: Batch start pulse
    emit_pulse("STATE_CHANGE", f"Batch starting: {min(len(to_process), max_videos)} videos",
               metrics={"to_process": min(len(to_process), max_videos), "remaining": len(to_process)})

    # Limit to max_videos
    to_process = to_process[:max_videos]

    provider_idx = start_provider_idx
    consecutive_failures = 0

    for i, video_path in enumerate(to_process):
        video_id = video_path.stem
        model, provider_name = PROVIDERS[provider_idx]

        logger.info(f"[{i+1}/{len(to_process)}] Enhancing {video_id} with {provider_name}")

        try:
            enhancer = VideoEnhancer(model=model)

            if not enhancer.llm or getattr(enhancer.llm, 'simulation_mode', True):
                logger.warning(f"{provider_name} not available, rotating...")
                provider_idx = (provider_idx + 1) % len(PROVIDERS)
                continue

            result = enhancer.enhance_video(str(video_path), save=True)

            if result:
                tier = result.quality_tier
                logger.info(f"  SUCCESS: Tier {tier}")
                log_audit(video_id, provider_name, True, tier)
                state["completed"].append(video_id)
                consecutive_failures = 0

                # WSP 91: Heartbeat every 10 videos
                if len(state["completed"]) % 10 == 0:
                    emit_pulse("HEARTBEAT", f"Progress: {len(state['completed'])} enhanced",
                               metrics={"completed": len(state["completed"]), "tier": tier})
            else:
                logger.warning(f"  FAILED: No result")
                log_audit(video_id, provider_name, False, 0, "No result returned")
                state["failed"].append(video_id)
                consecutive_failures += 1

        except Exception as e:
            error_str = str(e)
            logger.error(f"  ERROR: {error_str[:100]}")

            # Check for rate limit
            if "429" in error_str or "quota" in error_str.lower():
                logger.warning(f"Rate limit hit on {provider_name}, rotating provider...")
                provider_idx = (provider_idx + 1) % len(PROVIDERS)
                state["current_provider_idx"] = provider_idx
                # WSP 91: Rate limit threshold pulse
                emit_pulse("THRESHOLD", f"Rate limit: rotating to {PROVIDERS[provider_idx][1]}",
                           severity=1, metrics={"provider_idx": provider_idx})
                time.sleep(rate_limit_delay)

            log_audit(video_id, provider_name, False, 0, error_str[:200])
            consecutive_failures += 1

        # Save checkpoint after each video
        save_checkpoint(state)

        # Check for too many failures
        if consecutive_failures >= 3:
            logger.warning("3 consecutive failures, pausing 5 minutes...")
            # WSP 91: Failure streak error pulse
            emit_pulse("ERROR", "3 consecutive failures, pausing 5min",
                       severity=2, metrics={"failures": consecutive_failures, "provider": provider_name})
            time.sleep(300)
            consecutive_failures = 0
            provider_idx = (provider_idx + 1) % len(PROVIDERS)

        # Delay between videos
        if i < len(to_process) - 1:
            time.sleep(delay_between)

    # Final summary
    remaining = len(all_needing) - len(state['completed'])
    logger.info("=" * 60)
    logger.info("BATCH COMPLETE")
    logger.info(f"  Total completed: {len(state['completed'])}")
    logger.info(f"  Total failed: {len(state['failed'])}")
    logger.info(f"  Remaining: {remaining}")

    # WSP 91: Batch completion pulse
    emit_pulse("COMPLETION", f"Batch done: {len(state['completed'])} total, {remaining} remain",
               metrics={"completed": len(state["completed"]), "failed": len(state["failed"]), "remaining": remaining})


def show_status():
    """Show current enhancement status."""
    state = load_checkpoint()
    all_needing = get_videos_needing_enhancement()

    print("=" * 60)
    print("VIDEO ENHANCEMENT STATUS")
    print("=" * 60)
    print(f"Total videos: {len(list(VIDEO_DIR.glob('*.json')))}")
    print(f"Need enhancement: {len(all_needing)}")
    print(f"Completed: {len(state['completed'])}")
    print(f"Failed: {len(state['failed'])}")
    print(f"Last run: {state.get('last_run', 'Never')}")

    if AUDIT_FILE.exists():
        lines = AUDIT_FILE.read_text(encoding="utf-8").strip().split("\n")
        success_count = sum(1 for l in lines if '"success": true' in l)
        print(f"Audit log entries: {len(lines)} ({success_count} successful)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch enhance videos")
    parser.add_argument("--max-videos", type=int, default=50, help="Max videos to process")
    parser.add_argument("--provider", choices=["grok", "openai", "gemini"], default="grok")
    parser.add_argument("--delay", type=float, default=5.0, help="Delay between videos")
    parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
    parser.add_argument("--status", action="store_true", help="Show status only")

    args = parser.parse_args()

    if args.status:
        show_status()
    else:
        provider_map = {"grok": 0, "openai": 1, "gemini": 2}
        start_idx = provider_map.get(args.provider, 0)

        if args.resume:
            state = load_checkpoint()
            start_idx = state.get("current_provider_idx", 0)

        run_batch(
            max_videos=args.max_videos,
            start_provider_idx=start_idx,
            delay_between=args.delay,
        )

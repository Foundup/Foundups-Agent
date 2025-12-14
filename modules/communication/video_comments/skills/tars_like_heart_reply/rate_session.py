"""
012 Rating Tool - WSP 44 / WSP 77 Phase-3 Human Supervision
===========================================================

Rates an engagement session (Like/Heart/Reply) AFTER automation runs.

Why this exists:
- 012 is spectator during execution (0102 runs the skill)
- 012 can later provide "agentic ratings" to drive learning:
  - human semantic state (WSP 44 000–222)
  - optional correction of commenter_type classification
  - notes

Usage:
  python rate_session.py --latest
  python rate_session.py --session session_YYYYMMDD_HHMMSS.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Optional


def _enable_utf8_console() -> None:
    if not sys.platform.startswith("win"):
        return
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except (OSError, ValueError):
        pass


def _find_latest_session_file(repo_root: Path) -> Optional[Path]:
    sessions_dir = repo_root / "modules" / "communication" / "video_comments" / "memory" / "engagement_sessions"
    if not sessions_dir.exists():
        return None
    files = sorted(sessions_dir.glob("session_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def main() -> int:
    _enable_utf8_console()

    repo_root = Path(__file__).resolve().parents[5]
    sys.path.insert(0, str(repo_root))

    from modules.communication.video_comments.src.commenter_history_store import make_commenter_key
    from modules.communication.video_comments.src.engagement_feedback_store import get_engagement_feedback_store
    from modules.infrastructure.wsp_core.src.semantic_state_engine import SemanticStateEngine

    parser = argparse.ArgumentParser(description="Rate a YouTube Studio engagement session (human feedback).")
    parser.add_argument("--latest", action="store_true", help="Rate the most recent session file")
    parser.add_argument("--session", type=str, default="", help="Session file name or full path")
    parser.add_argument("--limit", type=int, default=0, help="Only rate first N results (0 = all)")
    args = parser.parse_args()

    session_path: Optional[Path] = None
    if args.session:
        candidate = Path(args.session)
        session_path = candidate if candidate.exists() else None
        if session_path is None:
            # Try in default sessions dir
            sessions_dir = repo_root / "modules" / "communication" / "video_comments" / "memory" / "engagement_sessions"
            maybe = sessions_dir / args.session
            if maybe.exists():
                session_path = maybe
    if session_path is None and args.latest:
        session_path = _find_latest_session_file(repo_root)

    if session_path is None:
        print("No session file found. Use --latest or --session <file>.")
        return 2

    data = json.loads(session_path.read_text(encoding="utf-8"))
    session_id = str(data.get("session_id") or session_path.stem.replace("session_", ""))
    results = list(data.get("results") or [])
    if args.limit and args.limit > 0:
        results = results[: args.limit]

    store = get_engagement_feedback_store()

    print(f"\nSession: {session_id}")
    print(f"File: {session_path}")
    print(f"Results: {len(results)}\n")

    type_map = {
        "m": "moderator",
        "t": "maga_troll",
        "s": "subscriber",
        "r": "regular",
        "u": "unknown",
    }

    for idx, item in enumerate(results, start=1):
        author_name = str(item.get("author_name") or "Unknown")
        commenter_handle = str(item.get("commenter_handle") or author_name or "Unknown")
        commenter_channel_id = item.get("commenter_channel_id")
        commenter_type_ai = str(item.get("commenter_type") or "unknown")
        semantic_ai = item.get("semantic_state") or item.get("semantic_state_intent")
        semantic_reason = item.get("semantic_state_reason") or item.get("semantic_state_intent_reason") or ""
        context = item.get("context") or {}

        commenter_key = make_commenter_key(channel_id=commenter_channel_id, handle=commenter_handle)

        print("=" * 70)
        print(f"[{idx}/{len(results)}] @{author_name}")
        print(f"AI: type={commenter_type_ai} semantic={semantic_ai} ctx(studio={int(bool(context.get('has_studio_history')))},chat={int(bool(context.get('has_chat_history')))})")
        if semantic_reason:
            print(f"AI reason: {semantic_reason}")

        # 1) Semantic rating
        default_state = str(semantic_ai or "000")
        while True:
            raw = input(f"Human semantic state (000-222) [Enter={default_state}]: ").strip()
            chosen = raw or default_state
            try:
                SemanticStateEngine.validate_state(chosen)
            except Exception as exc:
                print(f"Invalid state: {chosen} ({exc})")
                continue
            human_state = chosen
            break

        # 2) Optional commenter type correction
        raw_type = input(
            f"Correct commenter type? [m/t/s/r/u, Enter=keep '{commenter_type_ai}']: "
        ).strip().lower()
        commenter_type_human = type_map.get(raw_type) if raw_type in type_map else None

        # 3) Optional notes
        notes = input("Notes (optional): ").strip() or None

        store.record_feedback(
            session_id=session_id,
            comment_idx=int(item.get("comment_idx") or idx),
            commenter_key=commenter_key,
            commenter_handle=commenter_handle,
            commenter_channel_id=commenter_channel_id,
            commenter_type_ai=commenter_type_ai,
            semantic_state_ai=str(semantic_ai) if semantic_ai else None,
            semantic_state_human=human_state,
            commenter_type_human=commenter_type_human,
            notes=notes,
        )

        agreement = "YES" if (semantic_ai and str(semantic_ai) == human_state) else "NO"
        print(f"Saved. Agreement with AI semantic state: {agreement}\n")

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


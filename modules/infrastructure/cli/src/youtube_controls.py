"""
YouTube Controls - Control planes and scheduler controls for YouTube DAEs.

Extracted from main.py per WSP 62 (file size enforcement).
"""

import os
from modules.infrastructure.cli.src.utilities import (
    env_truthy,
    set_env_bool,
    update_env_file,
)


def yt_switch_summary() -> str:
    """Return formatted summary of current YouTube switches."""
    tempo = os.getenv("YT_ENGAGEMENT_TEMPO", "012").upper()
    comment_engagement = "ON" if env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true") else "OFF"
    comment_only = "ON" if env_truthy("YT_COMMENT_ONLY_MODE", "false") else "OFF"
    replies = "ON" if env_truthy("YT_COMMENT_REPLY_ENABLED", "true") else "OFF"
    persona = os.getenv("YT_ACTIVE_PERSONA", "").strip() or "auto"
    forced_set = os.getenv("YT_FORCE_CREDENTIAL_SET", "").strip() or "auto"
    return (
        f"tempo={tempo} | engagement={comment_engagement} | comment_only={comment_only} "
        f"| replies={replies} | persona={persona} | cred={forced_set}"
    )


def yt_scheduler_controls_menu() -> None:
    """
    Scheduler control plane (0102-first).

    Design:
    - Centralize scheduler env switches in one submenu.
    - Provide a content-type selector placeholder (shorts vs videos) for the next layer.
      NOTE: "videos" is a placeholder surface only until DOM selectors are implemented.
    """
    while True:
        content_type = os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts"
        verify_mode = os.getenv("YT_SCHEDULER_VERIFY_MODE", "none").strip().lower() or "none"
        sched_channel = os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan"
        sched_max = os.getenv("YT_SHORTS_SCHEDULER_MAX_VIDEOS", "1").strip() or "1"

        index_weave_enabled = env_truthy("YT_SCHEDULER_INDEX_WEAVE_ENABLED", "true")
        index_mode = os.getenv("YT_SCHEDULER_INDEX_MODE", "stub").strip().lower() or "stub"
        enhance_desc = env_truthy("YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION", "true")
        inform_title = env_truthy("YT_SCHEDULER_INDEX_INFORM_TITLE", "false")
        pre_save_delay = os.getenv("YT_SCHEDULER_PRE_SAVE_DELAY_SEC", "1.0").strip() or "1.0"

        print("\n[MENU] Scheduler Controls (012)")
        print("=" * 60)
        print(f"Content type (placeholder): {content_type}")
        print(f"Verify mode (placeholder): {verify_mode}")
        print(f"Active channel: {sched_channel} | max_videos: {sched_max}")
        print("-" * 60)
        print(f"1) Set content type (YT_SCHEDULER_CONTENT_TYPE) = {content_type}  [shorts/videos]")
        print(f"2) Set active channel (YT_SHORTS_SCHEDULER_CHANNEL_KEY) = {sched_channel}")
        print(f"3) Set max videos (YT_SHORTS_SCHEDULER_MAX_VIDEOS) = {sched_max}")
        print("-" * 60)
        print(f"4) Toggle index weave (YT_SCHEDULER_INDEX_WEAVE_ENABLED) = {'ON' if index_weave_enabled else 'OFF'}")
        print(f"5) Set index mode (YT_SCHEDULER_INDEX_MODE) = {index_mode}  [stub/gemini]")
        print(f"6) Toggle enhance description (YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION) = {'ON' if enhance_desc else 'OFF'}")
        print(f"7) Toggle index-informed title (YT_SCHEDULER_INDEX_INFORM_TITLE) = {'ON' if inform_title else 'OFF'}")
        print(f"8) Set pre-save delay sec (YT_SCHEDULER_PRE_SAVE_DELAY_SEC) = {pre_save_delay}")
        print("-" * 60)
        print(f"9) Set verify mode (YT_SCHEDULER_VERIFY_MODE) = {verify_mode}  [none/wre-tars]")
        print("0) Back")
        print("=" * 60)

        choice = input("scheduler-controls> ").strip().lower()
        if choice in {"0", "b", "back", "exit", "quit"}:
            break
        if choice == "1":
            raw = input("content type (shorts/videos): ").strip().lower() or "shorts"
            if raw not in {"shorts", "videos"}:
                print("[ERROR] Invalid content type. Use shorts or videos.")
                continue
            os.environ["YT_SCHEDULER_CONTENT_TYPE"] = raw
            update_env_file("YT_SCHEDULER_CONTENT_TYPE", raw)
            continue
        if choice == "2":
            raw = input("shorts channel (move2japan/undaodu/foundups/ravingantifa): ").strip().lower()
            if raw not in {"move2japan", "undaodu", "foundups", "ravingantifa"}:
                print("[ERROR] Invalid channel key.")
                continue
            os.environ["YT_SHORTS_SCHEDULER_CHANNEL_KEY"] = raw
            update_env_file("YT_SHORTS_SCHEDULER_CHANNEL_KEY", raw)
            continue
        if choice == "3":
            raw = input("max videos per run (default 1): ").strip() or "1"
            if not raw.isdigit() or int(raw) <= 0:
                print("[ERROR] Invalid max. Use a positive integer.")
                continue
            os.environ["YT_SHORTS_SCHEDULER_MAX_VIDEOS"] = raw
            update_env_file("YT_SHORTS_SCHEDULER_MAX_VIDEOS", raw)
            continue
        if choice == "4":
            set_env_bool("YT_SCHEDULER_INDEX_WEAVE_ENABLED", not index_weave_enabled)
            continue
        if choice == "5":
            raw = input("index mode (stub/gemini): ").strip().lower() or "stub"
            if raw not in {"stub", "gemini"}:
                print("[ERROR] Invalid index mode. Use stub or gemini.")
                continue
            os.environ["YT_SCHEDULER_INDEX_MODE"] = raw
            update_env_file("YT_SCHEDULER_INDEX_MODE", raw)
            continue
        if choice == "6":
            set_env_bool("YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION", not enhance_desc)
            continue
        if choice == "7":
            set_env_bool("YT_SCHEDULER_INDEX_INFORM_TITLE", not inform_title)
            continue
        if choice == "8":
            raw = input("pre-save delay seconds (e.g., 1.0): ").strip() or "1.0"
            try:
                value = float(raw)
                if value < 0:
                    raise ValueError
            except ValueError:
                print("[ERROR] Invalid number. Use a non-negative float (e.g., 1.0).")
                continue
            os.environ["YT_SCHEDULER_PRE_SAVE_DELAY_SEC"] = str(value)
            update_env_file("YT_SCHEDULER_PRE_SAVE_DELAY_SEC", str(value))
            continue
        if choice == "9":
            raw = input("verify mode (none/wre-tars): ").strip().lower() or "none"
            if raw not in {"none", "wre-tars"}:
                print("[ERROR] Invalid verify mode. Use none or wre-tars.")
                continue
            os.environ["YT_SCHEDULER_VERIFY_MODE"] = raw
            update_env_file("YT_SCHEDULER_VERIFY_MODE", raw)
            continue

        print("[ERROR] Invalid choice.")


def yt_controls_menu() -> None:
    """Display and handle YouTube Controls submenu."""
    toggles = [
        ("YT_AUTOMATION_ENABLED", "Automation master switch", True),
        ("YT_COMMENT_ENGAGEMENT_ENABLED", "Enable comment engagement loop", True),
        ("YT_COMMENT_ONLY_MODE", "Comment-only mode (no live chat)", False),
        ("YT_COMMENT_REACTIONS_ENABLED", "Enable reactions (like/heart)", True),
        ("YT_COMMENT_LIKE_ENABLED", "Allow like action", True),
        ("YT_COMMENT_HEART_ENABLED", "Allow heart action", True),
        ("YT_COMMENT_REPLY_ENABLED", "Allow reply action", True),
        ("YT_COMMENT_INTELLIGENT_REPLY_ENABLED", "Use intelligent replies", True),
        ("YT_REPLY_BASIC_ONLY", "Basic replies only", False),
        ("YT_OCCAM_MODE", "Occam mode (minimal replies)", False),
        ("YT_REPLY_DEBUG_TAGS", "Append debug tags to replies", False),
        ("YT_VIDEO_INDEXING_ENABLED", "Video indexing (post-comments)", False),
    ]

    while True:
        tempo = os.getenv("YT_ENGAGEMENT_TEMPO", "012").upper()
        persona = os.getenv("YT_ACTIVE_PERSONA", "").strip() or "auto"
        forced_set = os.getenv("YT_FORCE_CREDENTIAL_SET", "").strip() or "auto"
        sched_channel = os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan"
        sched_max = os.getenv("YT_SHORTS_SCHEDULER_MAX_VIDEOS", "1").strip() or "1"
        sched_type = os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts"

        print("\n[MENU] YouTube Controls (012)")
        print("=" * 60)
        for idx, (key, desc, default_on) in enumerate(toggles, start=1):
            default_str = "true" if default_on else "false"
            enabled = env_truthy(key, default_str)
            status = "ON" if enabled else "OFF"
            print(f"{idx}) {desc} [{key}] = {status}")
        set_idx = len(toggles) + 1
        persona_idx = len(toggles) + 2
        credential_idx = len(toggles) + 3
        scheduler_idx = len(toggles) + 4
        back_idx = len(toggles) + 5
        print(f"{set_idx}) Set engagement tempo (YT_ENGAGEMENT_TEMPO) = {tempo}")
        print(f"{persona_idx}) Set active persona (YT_ACTIVE_PERSONA) = {persona}")
        print(f"{credential_idx}) Force credential set (YT_FORCE_CREDENTIAL_SET) = {forced_set}")
        print(f"{scheduler_idx}) Scheduler Controls (Shorts/Videos) = type:{sched_type} channel:{sched_channel} max:{sched_max}")
        print(f"{back_idx}) Back")

        choice = input("yt-controls> ").strip().lower()
        if choice in {str(back_idx), "b", "back", "exit", "quit"}:
            break
        if choice == str(set_idx):
            raw = input("tempo (012/FAST/MEDIUM): ").strip().upper()
            if raw not in {"012", "FAST", "MEDIUM"}:
                print("[ERROR] Invalid tempo. Use 012, FAST, or MEDIUM.")
                continue
            os.environ["YT_ENGAGEMENT_TEMPO"] = raw
            update_env_file("YT_ENGAGEMENT_TEMPO", raw)
            continue
        if choice == str(persona_idx):
            raw = input("persona (auto/foundups/undaodu/move2japan/ravingantifa): ").strip().lower()
            if raw in {"", "auto"}:
                os.environ.pop("YT_ACTIVE_PERSONA", None)
                update_env_file("YT_ACTIVE_PERSONA", "")
                continue
            if raw not in {"foundups", "undaodu", "move2japan", "ravingantifa"}:
                print("[ERROR] Invalid persona. Use foundups, undaodu, move2japan, ravingantifa, or auto.")
                continue
            os.environ["YT_ACTIVE_PERSONA"] = raw
            update_env_file("YT_ACTIVE_PERSONA", raw)
            continue
        if choice == str(credential_idx):
            raw = input("credential set (blank=auto): ").strip()
            if not raw:
                os.environ.pop("YT_FORCE_CREDENTIAL_SET", None)
                update_env_file("YT_FORCE_CREDENTIAL_SET", "")
                continue
            if not raw.isdigit() or int(raw) <= 0:
                print("[ERROR] Invalid credential set. Use a positive integer or leave blank.")
                continue
            os.environ["YT_FORCE_CREDENTIAL_SET"] = raw
            update_env_file("YT_FORCE_CREDENTIAL_SET", raw)
            continue
        if choice == str(scheduler_idx):
            yt_scheduler_controls_menu()
            continue
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(toggles):
                key, _, default_on = toggles[idx - 1]
                default_str = "true" if default_on else "false"
                current = env_truthy(key, default_str)
                set_env_bool(key, not current)
                continue
        print("[ERROR] Invalid choice.")

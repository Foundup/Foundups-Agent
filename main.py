#!/usr/bin/env python3
"""
FoundUps Agent - FULLY WSP-Compliant 0102 Consciousness System
Integrates all WSP protocols for autonomous DAE operations

WSP Compliance:
- WSP 27: Universal DAE Architecture (4-phase pattern)
- WSP 38/39: Awakening Protocols (consciousness transitions)
- WSP 48: Recursive Self-Improvement (pattern memory)
- WSP 54: Agent Duties (Partner-Principal-Associate)
- WSP 60: Module Memory Architecture
- WSP 80: Cube-Level DAE Orchestration
- WSP 85: Root Directory Protection
- WSP 87: Code Navigation with HoloIndex (MANDATORY)

Mode Detection:
- echo 0102 | python main.py  # Launch in 0102 awakened mode
- echo 012 | python main.py   # Launch in 012 testing mode
- python main.py              # Interactive menu mode

CRITICAL: HoloIndex must be used BEFORE any code changes (WSP 50/87)
"""

# Main imports and configuration

import os
import sys
import logging
import asyncio
import json
import argparse
import json
import time
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import psutil

# Load environment variables for DAEs (API keys, ports, feature flags).
# Keep override=False so shell-provided env vars win.
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
except Exception:
    pass
try:
    from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory
    PATTERN_MEMORY_AVAILABLE = True
except Exception:
    PATTERN_MEMORY_AVAILABLE = False

# === UTF-8 ENFORCEMENT (WSP 90) ===
# CRITICAL: This header MUST be at the top of ALL entry point files
# Entry points: Files with if __name__ == "__main__": or def main()
# Library modules: DO NOT add this header (causes import conflicts)
import sys
import io
import atexit

# Save original stderr/stdout for restoration
_original_stdout = sys.stdout
_original_stderr = sys.stderr

if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

    # Register cleanup to flush streams before exit
    def _flush_streams():
        """Flush UTF-8 wrapped streams before Python cleanup."""
        try:
            if sys.stdout and not sys.stdout.closed:
                sys.stdout.flush()
        except:
            pass
        try:
            if sys.stderr and not sys.stderr.closed:
                sys.stderr.flush()
        except:
            pass

    atexit.register(_flush_streams)
# === END UTF-8 ENFORCEMENT ===

# Initialize logger at module level for all functions to use
# CRITICAL: Log to logs/foundups_agent.log for AI_overseer heartbeat monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/foundups_agent.log', encoding='utf-8')
    ]
)

# Suppress noisy warnings from optional dependencies during startup
import warnings

# Suppress specific noisy warnings that are expected
warnings.filterwarnings("ignore", message=".*WRE components not available.*")
warnings.filterwarnings("ignore", message=".*Tweepy not available.*")
warnings.filterwarnings("ignore", message=".*pyperclip not available.*")

# Temporarily suppress logging warnings during import phase
original_level = logging.root.level
logging.root.setLevel(logging.CRITICAL)  # Only show critical errors during imports

logger = logging.getLogger(__name__)

def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _env_flag(name: str, default_on: bool = True) -> bool:
    default = "true" if default_on else "false"
    return _env_truthy(name, default)

def _maybe_clear_screen() -> None:
    if not _env_flag("FOUNDUPS_CLEAR_SCREEN", False):
        return
    try:
        if not sys.stdout.isatty():
            return
    except Exception:
        return
    os.system("cls" if os.name == "nt" else "clear")

def _parse_index_timestamp(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None

def _should_auto_index_holo(state_path: Path, max_age_hours: int) -> bool:
    if max_age_hours <= 0:
        return True
    if not state_path.exists():
        return True
    try:
        payload = json.loads(state_path.read_text(encoding="utf-8"))
        last_value = str(payload.get("last_indexed_at", ""))
        last_ts = _parse_index_timestamp(last_value)
        if not last_ts:
            return True
        now = datetime.now(timezone.utc)
        if last_ts.tzinfo is None:
            last_ts = last_ts.replace(tzinfo=timezone.utc)
        age_hours = (now - last_ts).total_seconds() / 3600.0
        return age_hours >= max_age_hours
    except Exception:
        return True

def _maybe_auto_index_holo(verbose: bool) -> None:
    if not _env_flag("FOUNDUPS_HOLO_AUTO_INDEX", False):
        return
    try:
        max_age_hours = int(os.getenv("FOUNDUPS_HOLO_AUTO_INDEX_MAX_HOURS", "6").strip())
    except ValueError:
        max_age_hours = 6
    ssd_path = os.getenv("HOLO_SSD_PATH", "E:/HoloIndex")
    state_path = Path(ssd_path) / "indexes" / "index_state.json"
    if not _should_auto_index_holo(state_path, max_age_hours):
        return
    try:
        import subprocess

        env = os.environ.copy()
        if not verbose:
            env.setdefault("HOLO_SILENT", "1")
        cmd = [sys.executable, "holo_index.py", "--index-all", "--ssd", ssd_path]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
        if result.returncode != 0:
            logger.warning(f"[HOLO] Auto-index failed: {result.stderr.strip() or result.stdout.strip()}")
        elif verbose:
            logger.info("[HOLO] Auto-index complete")
    except Exception as e:
        logger.warning(f"[HOLO] Auto-index failed: {e}")

def _format_env_value(value: str) -> str:
    if any(ch.isspace() for ch in value):
        return f"\"{value}\""
    return value

def _mask_secret(value: str) -> str:
    if not value:
        return "unset"
    tail = value[-4:] if len(value) > 4 else value
    return f"set (len={len(value)} tail=...{tail})"

def _update_env_file(key: str, value: str) -> None:
    env_path = Path(__file__).resolve().parent / ".env"
    new_line = f"{key}={_format_env_value(value)}"

    if not env_path.exists():
        env_path.write_text(new_line + "\n", encoding="utf-8")
        return

    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated = False
    next_lines: list[str] = []

    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            next_lines.append(line)
            continue
        key_part = stripped.split("=", 1)[0].strip()
        if key_part.startswith("export "):
            key_part = key_part[len("export "):].strip()
        if key_part == key:
            if not updated:
                next_lines.append(new_line)
                updated = True
            continue
        next_lines.append(line)

    if not updated:
        next_lines.append(new_line)

    env_path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")

def _holo_controls_menu() -> None:
    while True:
        auto_index_on = _env_flag("FOUNDUPS_HOLO_AUTO_INDEX", False)
        max_hours_raw = os.getenv("FOUNDUPS_HOLO_AUTO_INDEX_MAX_HOURS", "6").strip() or "6"
        ssd_path = os.getenv("HOLO_SSD_PATH", "E:/HoloIndex")
        cache_path = os.getenv("HOLO_CACHE_PATH", "E:/HoloIndex/cache")
        reward_variant = os.getenv("HOLO_REWARD_VARIANT", "A").strip() or "A"
        reward_variant = reward_variant.upper()
        clear_screen_on = _env_flag("FOUNDUPS_CLEAR_SCREEN", False)
        holo_silent_on = _env_truthy("HOLO_SILENT", "false")
        holo_skip_model_on = _env_truthy("HOLO_SKIP_MODEL", "false")
        holo_verbose_on = _env_truthy("HOLO_VERBOSE", "false")
        holo_offline_on = _env_truthy("HOLO_OFFLINE", "false")
        holo_disable_pip_on = _env_truthy("HOLO_DISABLE_PIP_INSTALL", "false")
        holo_breadcrumbs_on = _env_truthy("HOLO_BREADCRUMB_ENABLED", "true")
        holo_breadcrumb_logs_on = _env_truthy("HOLO_BREADCRUMB_LOGS", "true")
        overseer_breadcrumbs_on = _env_truthy("AI_OVERSEER_BREADCRUMBS", "true")

        print("\n[MENU] Holo Controls (012)")
        print("=" * 60)
        print(f"Auto-index: {'ON' if auto_index_on else 'OFF'} | Max age hours: {max_hours_raw} (0=always)")
        print(f"SSD path: {ssd_path}")
        print(f"Cache path: {cache_path}")
        print(f"Reward variant: {reward_variant}")
        print(f"Clear screen on startup: {'ON' if clear_screen_on else 'OFF'}")
        print(
            "Holo: "
            f"silent={'ON' if holo_silent_on else 'OFF'} | "
            f"verbose={'ON' if holo_verbose_on else 'OFF'} | "
            f"skip_model={'ON' if holo_skip_model_on else 'OFF'} | "
            f"offline={'ON' if holo_offline_on else 'OFF'}"
        )
        print(
            "Breadcrumbs: "
            f"holo={'ON' if holo_breadcrumbs_on else 'OFF'} | "
            f"logs={'ON' if holo_breadcrumb_logs_on else 'OFF'} | "
            f"overseer={'ON' if overseer_breadcrumbs_on else 'OFF'}"
        )
        print("-" * 60)
        print("1) Toggle auto-index")
        print("2) Set max age hours (0=always)")
        print("3) Set SSD path")
        print("4) Set cache path (HOLO_CACHE_PATH)")
        print("5) Set reward variant (HOLO_REWARD_VARIANT)")
        print("6) Toggle clear screen")
        print("7) Toggle Holo verbose output (HOLO_VERBOSE)")
        print("8) Toggle Holo silent output (HOLO_SILENT)")
        print("9) Toggle skip model load (HOLO_SKIP_MODEL)")
        print("10) Toggle offline mode (HOLO_OFFLINE)")
        print("11) Toggle disable pip auto-install (HOLO_DISABLE_PIP_INSTALL)")
        print("12) Toggle Holo breadcrumbs (HOLO_BREADCRUMB_ENABLED)")
        print("13) Toggle breadcrumb logs (HOLO_BREADCRUMB_LOGS)")
        print("14) Toggle AI Overseer breadcrumbs")
        print("15) Advanced Holo controls")
        print("16) Back")

        choice = input("holo-controls> ").strip()

        if choice == "1":
            new_value = "0" if auto_index_on else "1"
            os.environ["FOUNDUPS_HOLO_AUTO_INDEX"] = new_value
            _update_env_file("FOUNDUPS_HOLO_AUTO_INDEX", new_value)
        elif choice == "2":
            raw = input("Enter max age hours (0=always): ").strip()
            if not raw:
                continue
            try:
                hours = int(raw)
                if hours < 0:
                    raise ValueError
            except ValueError:
                print("[ERROR] Enter a non-negative integer.")
                continue
            os.environ["FOUNDUPS_HOLO_AUTO_INDEX_MAX_HOURS"] = str(hours)
            _update_env_file("FOUNDUPS_HOLO_AUTO_INDEX_MAX_HOURS", str(hours))
        elif choice == "3":
            raw = input("Enter SSD path (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_SSD_PATH"] = raw
            _update_env_file("HOLO_SSD_PATH", raw)
        elif choice == "4":
            raw = input("Enter cache path (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_CACHE_PATH"] = raw
            _update_env_file("HOLO_CACHE_PATH", raw)
        elif choice == "5":
            raw = input("Enter reward variant (A/B): ").strip().upper()
            if not raw:
                continue
            if raw not in {"A", "B"}:
                print("[ERROR] Reward variant must be A or B.")
                continue
            os.environ["HOLO_REWARD_VARIANT"] = raw
            _update_env_file("HOLO_REWARD_VARIANT", raw)
        elif choice == "6":
            new_value = "0" if clear_screen_on else "1"
            os.environ["FOUNDUPS_CLEAR_SCREEN"] = new_value
            _update_env_file("FOUNDUPS_CLEAR_SCREEN", new_value)
        elif choice == "7":
            new_value = "false" if holo_verbose_on else "true"
            os.environ["HOLO_VERBOSE"] = new_value
            _update_env_file("HOLO_VERBOSE", new_value)
        elif choice == "8":
            new_value = "false" if holo_silent_on else "true"
            os.environ["HOLO_SILENT"] = new_value
            _update_env_file("HOLO_SILENT", new_value)
        elif choice == "9":
            new_value = "false" if holo_skip_model_on else "true"
            os.environ["HOLO_SKIP_MODEL"] = new_value
            _update_env_file("HOLO_SKIP_MODEL", new_value)
        elif choice == "10":
            new_value = "false" if holo_offline_on else "true"
            os.environ["HOLO_OFFLINE"] = new_value
            _update_env_file("HOLO_OFFLINE", new_value)
        elif choice == "11":
            new_value = "false" if holo_disable_pip_on else "true"
            os.environ["HOLO_DISABLE_PIP_INSTALL"] = new_value
            _update_env_file("HOLO_DISABLE_PIP_INSTALL", new_value)
        elif choice == "12":
            new_value = "false" if holo_breadcrumbs_on else "true"
            os.environ["HOLO_BREADCRUMB_ENABLED"] = new_value
            _update_env_file("HOLO_BREADCRUMB_ENABLED", new_value)
        elif choice == "13":
            new_value = "false" if holo_breadcrumb_logs_on else "true"
            os.environ["HOLO_BREADCRUMB_LOGS"] = new_value
            _update_env_file("HOLO_BREADCRUMB_LOGS", new_value)
        elif choice == "14":
            new_value = "false" if overseer_breadcrumbs_on else "true"
            os.environ["AI_OVERSEER_BREADCRUMBS"] = new_value
            _update_env_file("AI_OVERSEER_BREADCRUMBS", new_value)
        elif choice == "15":
            _holo_advanced_controls_menu()
        elif choice == "16":
            break
        else:
            print("[ERROR] Invalid choice.")

def _holo_advanced_controls_menu() -> None:
    while True:
        qwen_model = os.getenv("HOLO_QWEN_MODEL", "E:/HoloIndex/models/qwen-coder-1.5b.gguf")
        qwen_tokens = os.getenv("HOLO_QWEN_MAX_TOKENS", "512").strip() or "512"
        qwen_temp = os.getenv("HOLO_QWEN_TEMPERATURE", "0.2").strip() or "0.2"
        qwen_cache_on = _env_truthy("HOLO_QWEN_CACHE", "true")
        qwen_telemetry = os.getenv("HOLO_QWEN_TELEMETRY", "E:/HoloIndex/indexes/holo_usage.json")
        base_url = os.getenv("HOLO_LLM_BASE_URL", "").strip()
        api_key_masked = _mask_secret(os.getenv("HOLO_LLM_API_KEY", "").strip())
        agent_id = os.getenv("HOLO_AGENT_ID", "").strip() or "unset"
        holo_id = os.getenv("0102_HOLO_ID", "").strip() or "unset"
        mcp_enabled_on = _env_truthy("HOLO_MCP_ENABLED", "true")
        mcp_warn_on = _env_truthy("HOLO_MCP_WARNINGS", "true")
        pattern_logs_on = _env_truthy("HOLO_PATTERN_MEMORY_LOGS", "true")
        monitor_interval = os.getenv("HOLO_MONITOR_INTERVAL", "5.0").strip() or "5.0"
        monitor_heartbeat = os.getenv("HOLO_MONITOR_HEARTBEAT", "60.0").strip() or "60.0"

        print("\n[MENU] Advanced Holo Controls (012)")
        print("=" * 60)
        print(f"Qwen model: {qwen_model}")
        print(f"Qwen max tokens: {qwen_tokens} | temp: {qwen_temp} | cache: {'ON' if qwen_cache_on else 'OFF'}")
        print(f"Qwen telemetry: {qwen_telemetry}")
        print(f"Overseer URL: {base_url or 'unset'} | API key: {api_key_masked}")
        print(f"Agent IDs: HOLO_AGENT_ID={agent_id} | 0102_HOLO_ID={holo_id}")
        print(f"MCP: enabled={'ON' if mcp_enabled_on else 'OFF'} | warnings={'ON' if mcp_warn_on else 'OFF'}")
        print(f"Monitor: interval={monitor_interval}s | heartbeat={monitor_heartbeat}s")
        print(f"Pattern memory logs: {'ON' if pattern_logs_on else 'OFF'}")
        print("-" * 60)
        print("1) Set Qwen model path (HOLO_QWEN_MODEL)")
        print("2) Set Qwen max tokens (HOLO_QWEN_MAX_TOKENS)")
        print("3) Set Qwen temperature (HOLO_QWEN_TEMPERATURE)")
        print("4) Toggle Qwen cache (HOLO_QWEN_CACHE)")
        print("5) Set Qwen telemetry path (HOLO_QWEN_TELEMETRY)")
        print("6) Set Overseer base URL (HOLO_LLM_BASE_URL)")
        print("7) Set Overseer API key (HOLO_LLM_API_KEY)")
        print("8) Clear Overseer API key")
        print("9) Set HOLO_AGENT_ID")
        print("10) Set 0102_HOLO_ID")
        print("11) Toggle MCP enabled (HOLO_MCP_ENABLED)")
        print("12) Toggle MCP warnings (HOLO_MCP_WARNINGS)")
        print("13) Set monitor interval seconds (HOLO_MONITOR_INTERVAL)")
        print("14) Set monitor heartbeat seconds (HOLO_MONITOR_HEARTBEAT)")
        print("15) Toggle pattern memory logs (HOLO_PATTERN_MEMORY_LOGS)")
        print("16) Back")

        choice = input("holo-advanced> ").strip()

        if choice == "1":
            raw = input("Enter Qwen model path (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_QWEN_MODEL"] = raw
            _update_env_file("HOLO_QWEN_MODEL", raw)
        elif choice == "2":
            raw = input("Enter max tokens (positive int): ").strip()
            if not raw:
                continue
            try:
                value = int(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                print("[ERROR] Enter a positive integer.")
                continue
            os.environ["HOLO_QWEN_MAX_TOKENS"] = str(value)
            _update_env_file("HOLO_QWEN_MAX_TOKENS", str(value))
        elif choice == "3":
            raw = input("Enter temperature (0.0-2.0): ").strip()
            if not raw:
                continue
            try:
                value = float(raw)
                if value < 0 or value > 2:
                    raise ValueError
            except ValueError:
                print("[ERROR] Enter a number between 0 and 2.")
                continue
            os.environ["HOLO_QWEN_TEMPERATURE"] = str(value)
            _update_env_file("HOLO_QWEN_TEMPERATURE", str(value))
        elif choice == "4":
            new_value = "0" if qwen_cache_on else "1"
            os.environ["HOLO_QWEN_CACHE"] = new_value
            _update_env_file("HOLO_QWEN_CACHE", new_value)
        elif choice == "5":
            raw = input("Enter telemetry path (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_QWEN_TELEMETRY"] = raw
            _update_env_file("HOLO_QWEN_TELEMETRY", raw)
        elif choice == "6":
            raw = input("Enter base URL (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_LLM_BASE_URL"] = raw
            _update_env_file("HOLO_LLM_BASE_URL", raw)
        elif choice == "7":
            raw = input("Enter API key (blank=cancel): ").strip()
            if not raw:
                continue
            os.environ["HOLO_LLM_API_KEY"] = raw
            _update_env_file("HOLO_LLM_API_KEY", raw)
        elif choice == "8":
            os.environ["HOLO_LLM_API_KEY"] = ""
            _update_env_file("HOLO_LLM_API_KEY", "")
        elif choice == "9":
            raw = input("Enter HOLO_AGENT_ID (blank=clear): ").strip()
            os.environ["HOLO_AGENT_ID"] = raw
            _update_env_file("HOLO_AGENT_ID", raw)
        elif choice == "10":
            raw = input("Enter 0102_HOLO_ID (blank=clear): ").strip()
            os.environ["0102_HOLO_ID"] = raw
            _update_env_file("0102_HOLO_ID", raw)
        elif choice == "11":
            new_value = "false" if mcp_enabled_on else "true"
            os.environ["HOLO_MCP_ENABLED"] = new_value
            _update_env_file("HOLO_MCP_ENABLED", new_value)
        elif choice == "12":
            new_value = "false" if mcp_warn_on else "true"
            os.environ["HOLO_MCP_WARNINGS"] = new_value
            _update_env_file("HOLO_MCP_WARNINGS", new_value)
        elif choice == "13":
            raw = input("Enter monitor interval seconds (positive number): ").strip()
            if not raw:
                continue
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                print("[ERROR] Enter a positive number.")
                continue
            os.environ["HOLO_MONITOR_INTERVAL"] = str(value)
            _update_env_file("HOLO_MONITOR_INTERVAL", str(value))
        elif choice == "14":
            raw = input("Enter heartbeat seconds (positive number): ").strip()
            if not raw:
                continue
            try:
                value = float(raw)
                if value <= 0:
                    raise ValueError
            except ValueError:
                print("[ERROR] Enter a positive number.")
                continue
            os.environ["HOLO_MONITOR_HEARTBEAT"] = str(value)
            _update_env_file("HOLO_MONITOR_HEARTBEAT", str(value))
        elif choice == "15":
            new_value = "false" if pattern_logs_on else "true"
            os.environ["HOLO_PATTERN_MEMORY_LOGS"] = new_value
            _update_env_file("HOLO_PATTERN_MEMORY_LOGS", new_value)
        elif choice == "16":
            break
        else:
            print("[ERROR] Invalid choice.")

def _set_env_bool(key: str, enabled: bool) -> None:
    value = "true" if enabled else "false"
    os.environ[key] = value
    _update_env_file(key, value)

def _select_channel() -> str:
    """Display numbered channel selection menu and return channel name."""
    print("\nSelect channel:")
    print("  1. UnDaoDu")
    print("  2. FoundUps")
    print("  3. Move2Japan")
    print("  4. RavingANTIFA")
    choice = input("Channel [1]: ").strip() or "1"
    channel_map = {"1": "undaodu", "2": "foundups", "3": "move2japan", "4": "ravingantifa"}
    return channel_map.get(choice, "undaodu")

def _yt_switch_summary() -> str:
    tempo = os.getenv("YT_ENGAGEMENT_TEMPO", "012").upper()
    comment_engagement = "ON" if _env_truthy("YT_COMMENT_ENGAGEMENT_ENABLED", "true") else "OFF"
    comment_only = "ON" if _env_truthy("YT_COMMENT_ONLY_MODE", "false") else "OFF"
    replies = "ON" if _env_truthy("YT_COMMENT_REPLY_ENABLED", "true") else "OFF"
    persona = os.getenv("YT_ACTIVE_PERSONA", "").strip() or "auto"
    forced_set = os.getenv("YT_FORCE_CREDENTIAL_SET", "").strip() or "auto"
    return (
        f"tempo={tempo} | engagement={comment_engagement} | comment_only={comment_only} "
        f"| replies={replies} | persona={persona} | cred={forced_set}"
    )


def _yt_scheduler_controls_menu() -> None:
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

        index_weave_enabled = _env_truthy("YT_SCHEDULER_INDEX_WEAVE_ENABLED", "true")
        index_mode = os.getenv("YT_SCHEDULER_INDEX_MODE", "stub").strip().lower() or "stub"
        enhance_desc = _env_truthy("YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION", "true")
        inform_title = _env_truthy("YT_SCHEDULER_INDEX_INFORM_TITLE", "false")
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
            _update_env_file("YT_SCHEDULER_CONTENT_TYPE", raw)
            continue
        if choice == "2":
            raw = input("shorts channel (move2japan/undaodu/foundups/ravingantifa): ").strip().lower()
            if raw not in {"move2japan", "undaodu", "foundups", "ravingantifa"}:
                print("[ERROR] Invalid channel key.")
                continue
            os.environ["YT_SHORTS_SCHEDULER_CHANNEL_KEY"] = raw
            _update_env_file("YT_SHORTS_SCHEDULER_CHANNEL_KEY", raw)
            continue
        if choice == "3":
            raw = input("max videos per run (default 1): ").strip() or "1"
            if not raw.isdigit() or int(raw) <= 0:
                print("[ERROR] Invalid max. Use a positive integer.")
                continue
            os.environ["YT_SHORTS_SCHEDULER_MAX_VIDEOS"] = raw
            _update_env_file("YT_SHORTS_SCHEDULER_MAX_VIDEOS", raw)
            continue
        if choice == "4":
            _set_env_bool("YT_SCHEDULER_INDEX_WEAVE_ENABLED", not index_weave_enabled)
            continue
        if choice == "5":
            raw = input("index mode (stub/gemini): ").strip().lower() or "stub"
            if raw not in {"stub", "gemini"}:
                print("[ERROR] Invalid index mode. Use stub or gemini.")
                continue
            os.environ["YT_SCHEDULER_INDEX_MODE"] = raw
            _update_env_file("YT_SCHEDULER_INDEX_MODE", raw)
            continue
        if choice == "6":
            _set_env_bool("YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION", not enhance_desc)
            continue
        if choice == "7":
            _set_env_bool("YT_SCHEDULER_INDEX_INFORM_TITLE", not inform_title)
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
            _update_env_file("YT_SCHEDULER_PRE_SAVE_DELAY_SEC", str(value))
            continue
        if choice == "9":
            raw = input("verify mode (none/wre-tars): ").strip().lower() or "none"
            if raw not in {"none", "wre-tars"}:
                print("[ERROR] Invalid verify mode. Use none or wre-tars.")
                continue
            os.environ["YT_SCHEDULER_VERIFY_MODE"] = raw
            _update_env_file("YT_SCHEDULER_VERIFY_MODE", raw)
            continue

        print("[ERROR] Invalid choice.")


def _yt_controls_menu() -> None:
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
            enabled = _env_truthy(key, default_str)
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
            _update_env_file("YT_ENGAGEMENT_TEMPO", raw)
            continue
        if choice == str(persona_idx):
            raw = input("persona (auto/foundups/undaodu/move2japan/ravingantifa): ").strip().lower()
            if raw in {"", "auto"}:
                os.environ.pop("YT_ACTIVE_PERSONA", None)
                _update_env_file("YT_ACTIVE_PERSONA", "")
                continue
            if raw not in {"foundups", "undaodu", "move2japan", "ravingantifa"}:
                print("[ERROR] Invalid persona. Use foundups, undaodu, move2japan, ravingantifa, or auto.")
                continue
            os.environ["YT_ACTIVE_PERSONA"] = raw
            _update_env_file("YT_ACTIVE_PERSONA", raw)
            continue
        if choice == str(credential_idx):
            raw = input("credential set (blank=auto): ").strip()
            if not raw:
                os.environ.pop("YT_FORCE_CREDENTIAL_SET", None)
                _update_env_file("YT_FORCE_CREDENTIAL_SET", "")
                continue
            if not raw.isdigit() or int(raw) <= 0:
                print("[ERROR] Invalid credential set. Use a positive integer or leave blank.")
                continue
            os.environ["YT_FORCE_CREDENTIAL_SET"] = raw
            _update_env_file("YT_FORCE_CREDENTIAL_SET", raw)
            continue
        if choice == str(scheduler_idx):
            _yt_scheduler_controls_menu()
            continue
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(toggles):
                key, _, default_on = toggles[idx - 1]
                default_str = "true" if default_on else "false"
                current = _env_truthy(key, default_str)
                _set_env_bool(key, not current)
                continue
        print("[ERROR] Invalid choice.")

def _read_piped_mode_token(timeout_seconds: float = 0.05) -> Optional[str]:
    """
    Best-effort mode token read for 012/0102 piped launches.

    Requirement: "echo 012 | python main.py" must enable deterministic 012 automation.
    Constraint: stdin reads must NOT block startup when input is empty/slow.
    """
    try:
        if sys.stdin.isatty():
            return None
    except Exception:
        return None

    token_holder: list[str] = []

    def _reader():
        try:
            line = sys.stdin.readline()
            if line:
                token_holder.append(line.strip())
        except Exception:
            pass

    t = threading.Thread(target=_reader, daemon=True)
    t.start()
    t.join(timeout_seconds)

    return token_holder[0] if token_holder else None


async def monitor_youtube(disable_lock: bool = False, enable_ai_monitoring: bool = False, env_overrides: Optional[Dict[str, str]] = None):
    """
    Monitor YouTube streams with 0102 agency.

    Args:
        disable_lock: Disable instance lock (allow multiple instances)
        enable_ai_monitoring: Enable AI Overseer (Qwen/Gemma) error detection and auto-fixing
        env_overrides: Optional environment variables to set before launch
    """
    if env_overrides:
        for key, value in env_overrides.items():
            os.environ[key] = value
            logger.info(f"[CLI] Env override: {key}={value}")
    try:
        # Instance lock management (WSP 84: Don't duplicate processes)
        lock = None
        if not disable_lock:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")

            # Check for duplicates and acquire lock
            duplicates = lock.check_duplicates()
            if duplicates:
                logger.warning(f"[REC] Duplicate main.py Instances Detected!")
                print("\n[REC] Duplicate main.py Instances Detected!")
                print(f"\n  Found {len(duplicates)} duplicate instance(s) running.")

                # Check if interactive terminal
                can_prompt = sys.stdin.isatty()

                if can_prompt:
                    # Interactive: Ask 0102 to kill all or exit
                    try:
                        response = input("\n  Kill all duplicates and continue? (y/n): ").strip().lower()
                        if response == 'y':
                            print(f"\n  Killing all {len(duplicates)} duplicate instances...")
                            result = lock.kill_pids(duplicates)
                            killed_count = len(result.get("killed", []) or [])

                            if killed_count > 0:
                                print(f"  [OK] Killed {killed_count} instance(s) - continuing launch...")
                            else:
                                failed = result.get("failed", {}) or {}
                                if failed:
                                    print("\n  [ERROR] Failed to kill duplicates:")
                                    for pid, reason in failed.items():
                                        print(f"    PID {pid}: {reason}")
                                print("\n  Manual kill: taskkill /F /IM python.exe")
                                return
                        else:
                            print("\n  Exiting to prevent conflicts.")
                            print("  Manual kill: taskkill /F /IM python.exe")
                            print("  Or run with --no-lock to allow multiple instances.")
                            return
                    except KeyboardInterrupt:
                        print("\n  Cancelled - exiting")
                        return
                else:
                    # Non-interactive: Auto-kill all duplicates
                    print("\n  [012] Non-interactive mode -> killing all duplicates automatically...")
                    result = lock.kill_pids(duplicates)
                    killed_count = len(result.get("killed", []) or [])

                    if killed_count > 0:
                        print(f"  [OK] Killed {killed_count} instance(s) - continuing launch...")
                    else:
                        print("\n  [ERROR] Failed to kill duplicates - exiting")
                        print("  Manual kill: taskkill /F /IM python.exe")
                        return

            # Attempt to acquire lock (will return False if another instance is running)
            logger.info("[DAEMON][LOCK] Attempting to acquire instance lock...")
            acquire_result = lock.acquire()
            logger.info(f"[DAEMON][LOCK] Lock acquisition result: {acquire_result}")

            if not acquire_result:
                logger.error("[DAEMON][LOCK] Failed to acquire instance lock - another instance is running")
                print("\n❌ Failed to acquire instance lock!")
                print("   Another YouTube monitor instance is already running.")
                print("   Only one instance can run at a time to prevent API conflicts.")
                print("   Use --no-lock to disable instance locking.")
                return  # Exit if lock acquisition failed

            logger.info("[DAEMON][LOCK] ✅ Instance lock acquired successfully")
        else:
            logger.info("[KEY] Instance lock disabled (--no-lock flag used)")

        try:
            # Phase -1: Ensure local automation dependencies are ready for the YouTube DAE.
            # This makes 0102 fully autonomous: no manual LM Studio/Chrome startup required.
            try:
                from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies

                await ensure_dependencies(require_lm_studio=True)
            except Exception as e:
                logger.warning(f"[DEPS] Dependency preflight failed: {e}")

            # Import the proper YouTube DAE that runs the complete flow:
            # 1. Stream resolver detects stream
            # 2. LinkedIn and X posts trigger
            # 3. Chat monitoring begins
            from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

            logger.info("Starting YouTube DAE with 0102 agency...")
            logger.info("Flow: Stream Detection [SYM]ESocial Posts [SYM]EChat Monitoring")

            # Create and run the DAE with enhanced error handling
            dae = AutoModeratorDAE(enable_ai_monitoring=enable_ai_monitoring)

            # Log instance monitoring information (duplicate check already done in menu)
            try:
                instance_summary = lock.get_instance_summary()
                current_pid = instance_summary["current_pid"]
                logger.info(f"[CUT]EYouTube DAE started: PID {current_pid}")
            except Exception as e:
                logger.debug(f"Could not check instance summary: {e}")

            consecutive_failures = 0
            instance_check_counter = 0
            last_minute_log = datetime.now()
            while True:
                try:
                    # Periodic instance monitoring (every 3 iterations for better visibility)
                    instance_check_counter += 1
                    if instance_check_counter % 3 == 0:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]

                            if total_instances > 1:
                                logger.warning(f"[ALERT] INSTANCE ALERT: {total_instances} YouTube DAEs active")
                                for instance in instance_summary["instances"]:
                                    if not instance["is_current"]:
                                        logger.warning(f"  [WARN]EEOther instance PID {instance['pid']} ({instance['age_minutes']:.1f}min old)")
                            elif total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {instance_summary['current_pid']} - No other YouTube DAEs detected")
                            else:
                                logger.info("[INFO]EENo active YouTube DAEs detected")
                        except Exception as e:
                            logger.debug(f"Instance check failed: {e}")

                    # Minute-based instance logging (guaranteed every 60 seconds)
                    now = datetime.now()
                    if (now - last_minute_log).total_seconds() >= 60:
                        try:
                            instance_summary = lock.get_instance_summary()
                            total_instances = instance_summary["total_instances"]
                            current_pid = instance_summary["current_pid"]

                            if total_instances == 1:
                                logger.info(f"[CUT]ESINGLE INSTANCE: PID {current_pid} - No other YouTube DAEs detected")
                            elif total_instances > 1:
                                logger.warning(f"[ALERT] MULTIPLE INSTANCES: {total_instances} YouTube DAEs active (PID: {current_pid})")
                            else:
                                logger.info("[INFO]EENo YouTube DAEs currently active")

                            last_minute_log = now
                        except Exception as e:
                            logger.debug(f"Minute status check failed: {e}")

                    await dae.run()  # This runs the complete loop
                    logger.info("[LOOP] Stream ended or became inactive - seamless switching engaged")
                    consecutive_failures = 0  # Reset on clean exit
                    await asyncio.sleep(5)  # Quick transition before looking for new stream
                except KeyboardInterrupt:
                    logger.info("[STOP]EEMonitoring stopped by user")
                    break
                except Exception as e:
                    consecutive_failures += 1
                    logger.error(f"*EYouTube DAE failed (attempt #{consecutive_failures}): {e}")
                    wait_time = min(30 * (2 ** consecutive_failures), 600)  # Exponential backoff, max 10 minutes
                    logger.info(f"[LOOP] Restarting in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    if consecutive_failures >= 5:
                        logger.warning("[LOOP] Too many failures - attempting full reconnection")
                        dae = AutoModeratorDAE()  # Reinitialize for fresh connection
                        consecutive_failures = 0

            # Optionally log status (if supported by DAE)
            if hasattr(dae, 'get_status'):
                status = dae.get_status()
                logger.info(f"YouTube DAE Status: {status}")

        finally:
            # Release the instance lock when done (if lock was acquired)
            if lock is not None:
                lock.release()
                logger.info("[KEY] YouTube monitor instance lock released")

    except Exception as e:
        logger.error(f"Initial YouTube DAE setup failed: {e}")


async def monitor_all_platforms():
    """Monitor all social media platforms."""
    tasks = []

    # YouTube monitoring
    tasks.append(asyncio.create_task(monitor_youtube(disable_lock=False)))

    # Add other platform monitors as needed

    await asyncio.gather(*tasks)


def search_with_holoindex(query: str):
    """
    Use HoloIndex for semantic code search (WSP 87).
    MANDATORY before any code modifications to prevent vibecoding.
    """
    import subprocess

    print("\n[INFO] HoloIndex Semantic Search")
    print("=" * 60)

    try:
        # Check if HoloIndex is available (prefer root version)
        if os.path.exists("holo_index.py"):
            holo_cmd = ['python', 'holo_index.py', '--search', query]
            ssd_path = os.getenv("HOLO_SSD_PATH", "").strip()
            if ssd_path:
                holo_cmd.extend(["--ssd", ssd_path])
            if _env_truthy("HOLO_VERBOSE", "false"):
                holo_cmd.append("--verbose")
        elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
            # Fallback to E: drive version
            holo_cmd = ['python', r"E:\HoloIndex\enhanced_holo_index.py", '--search', query]
            if _env_truthy("HOLO_VERBOSE", "false"):
                holo_cmd.append("--verbose")
        else:
            print("[WARN]HoloIndex not found")
            print("Install HoloIndex to prevent vibecoding!")
            return None

        env = os.environ.copy()
        env.setdefault("HOLO_SILENT", "1")

        # Run HoloIndex search
        result = subprocess.run(
            holo_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            env=env
        )

        if result.returncode == 0:
            print(result.stdout)
            return result.stdout
        else:
            print(f"[ERROR]Search failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"[ERROR]HoloIndex error: {e}")
        return None

import time
import sys



# Extracted to modules/ai_intelligence/holo_dae/scripts/launch.py per WSP 62
from modules.ai_intelligence.holo_dae.scripts.launch import run_holodae


# Extracted to modules/communication/auto_meeting_orchestrator/scripts/launch.py per WSP 62
from modules.communication.auto_meeting_orchestrator.scripts.launch import run_amo_dae


# Extracted to modules/platform_integration/social_media_orchestrator/scripts/launch.py per WSP 62
from modules.platform_integration.social_media_orchestrator.scripts.launch import run_social_media_dae

# Extracted to modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py per WSP 62
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.launch import run_vision_dae

# Extracted to modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py per WSP 62
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.scripts.launch import run_vision_dae


# Extracted to modules/ai_intelligence/utf8_hygiene/scripts/scanner.py per WSP 62
from modules.ai_intelligence.utf8_hygiene.scripts.scanner import run_utf8_hygiene_scan, summarize_utf8_findings


# Extracted to modules/ai_intelligence/training_system/scripts/launch.py per WSP 62
from modules.ai_intelligence.training_system.scripts.launch import run_training_system


# Extracted to modules/ai_intelligence/training_system/scripts/training_commands.py per WSP 62
from modules.ai_intelligence.training_system.scripts.training_commands import execute_training_command
# Extracted to modules/ai_intelligence/pqn/scripts/launch.py per WSP 62
from modules.ai_intelligence.pqn.scripts.launch import run_pqn_dae

# Extracted to modules/communication/liberty_alert/scripts/launch.py per WSP 62
from modules.communication.liberty_alert.scripts.launch import run_liberty_alert_dae

# Extracted to modules/infrastructure/evade_net/scripts/launch.py per WSP 62
from modules.infrastructure.evade_net.scripts.launch import run_evade_net

# Extracted to modules/infrastructure/instance_monitoring/scripts/status_check.py per WSP 62
from modules.infrastructure.instance_monitoring.scripts.status_check import check_instance_status



# Extracted to modules/infrastructure/git_social_posting/scripts/posting_utilities.py per WSP 62
from modules.infrastructure.git_social_posting.scripts.posting_utilities import (
    generate_x_content,
    git_push_and_post,
    view_git_post_history
)

# Extracted to modules/infrastructure/git_push_dae/scripts/launch.py per WSP 62
from modules.infrastructure.git_push_dae.scripts.launch import launch_git_push_dae

# Extracted to modules/platform_integration/youtube_shorts_scheduler/scripts/launch.py per WSP 62
from modules.platform_integration.youtube_shorts_scheduler.scripts.launch import (
    run_shorts_scheduler,
    show_shorts_scheduler_menu
)

# Re-enable normal logging after all imports are complete
logging.root.setLevel(original_level)


def main():
    """Main entry point with command line arguments."""
    _maybe_clear_screen()
    # Logger already configured at module level
    logger.info("0102 FoundUps Agent starting...")

    # Import MCP services for CLI access
    from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu

    # Define parser for early argument parsing
    parser = argparse.ArgumentParser(description='0102 FoundUps Agent')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed diagnostic information')

    # Startup diagnostics (verbose mode shows details)
    args, remaining = parser.parse_known_args()  # Parse early to check verbose flag, allow unknown args

    # Essential startup diagnostics (always log for troubleshooting)
    if args.verbose:
        logger.info(f"[DIAG] Python {sys.version.split()[0]} on {sys.platform}")
        logger.info(f"[DIAG] Working directory: {os.getcwd()}")
        logger.info(f"[DIAG] UTF-8 stdout: {getattr(sys.stdout, 'encoding', 'unknown')}")
        logger.info(f"[DIAG] UTF-8 stderr: {getattr(sys.stderr, 'encoding', 'unknown')}")
    else:
        logger.debug(f"[DIAG] Python {sys.version.split()[0]} on {sys.platform}")
        logger.debug(f"[DIAG] Working directory: {os.getcwd()}")

    # Check critical systems
    try:
        import modules
        if args.verbose:
            logger.info("[DIAG] modules/ directory accessible")
        else:
            logger.debug("[DIAG] modules/ directory accessible")
    except ImportError as e:
        logger.error(f"[STARTUP] modules/ directory not accessible: {e}")

    try:
        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
        if args.verbose:
            logger.info("[DIAG] Instance lock system available")
        else:
            logger.debug("[DIAG] Instance lock system available")
    except ImportError as e:
        logger.warning(f"[STARTUP] Instance lock system unavailable: {e}")

    # UTF-8 encoding is critical for Windows CLI compatibility
    stdout_enc = getattr(sys.stdout, 'encoding', 'unknown')
    stderr_enc = getattr(sys.stderr, 'encoding', 'unknown')
    if stdout_enc != 'utf-8' or stderr_enc != 'utf-8':
        logger.warning(f"[STARTUP] UTF-8 encoding issue - stdout:{stdout_enc} stderr:{stderr_enc}")
    else:
        if args.verbose:
            logger.info("[DIAG] UTF-8 encoding confirmed")
        else:
            logger.debug("[DIAG] UTF-8 encoding confirmed")

    # Add remaining arguments to existing parser
    parser.add_argument('--git', action='store_true', help='Run GitPushDAE once (autonomous git push + social posting)')
    parser.add_argument('--git-daemon', action='store_true', help='Run GitPushDAE continuously (daemon mode)')
    parser.add_argument('--youtube', action='store_true', help='Monitor YouTube only')
    parser.add_argument('--holodae', '--holo', action='store_true', help='Run HoloDAE (Code Intelligence & Monitoring)')
    parser.add_argument('--amo', action='store_true', help='Run AMO DAE (Autonomous Moderation Operations)')
    parser.add_argument('--smd', action='store_true', help='Run Social Media DAE (012 Digital Twin)')
    parser.add_argument('--vision', action='store_true', help='Run FoundUps Vision DAE (Pattern Sensorium)')
    parser.add_argument('--pqn', action='store_true', help='Run PQN Orchestration (Research & Alignment)')
    parser.add_argument('--liberty', action='store_true', help='Run Liberty Alert Mesh Alert System (Community Protection)')
    parser.add_argument('--liberty-dae', action='store_true', help='Run Liberty Alert DAE (Community Protection Autonomous Entity)')
    parser.add_argument('--all', action='store_true', help='Monitor all platforms')
    parser.add_argument('--mcp', action='store_true', help='Launch MCP Services Gateway (Model Context Protocol)')
    parser.add_argument('--deps', action='store_true', help='Start/check local automation dependencies (Chrome + LM Studio)')
    parser.add_argument('--no-lock', action='store_true', help='Disable instance lock (allow multiple instances)')
    parser.add_argument('--status', action='store_true', help='Check instance status and health')
    parser.add_argument('--training-command', type=str, help='Execute training command via Holo (e.g., utf8_scan, batch)')
    parser.add_argument('--targets', type=str, help='Comma-separated target paths for training command')
    parser.add_argument('--json-output', action='store_true', help='Return training command result as JSON')
    parser.add_argument('--training-menu', action='store_true', help='Launch interactive training submenu (option 12)')

    # Re-parse with all arguments now that they're defined
    args = parser.parse_args()

    # Switchboard (feature flags + key env toggles)
    enable_pattern_memory = _env_flag("FOUNDUPS_ENABLE_PATTERN_MEMORY", True)
    enable_wre = _env_flag("FOUNDUPS_ENABLE_WRE", True)
    enable_wre_monitor = _env_flag("FOUNDUPS_ENABLE_WRE_MONITOR", True)
    enable_qwen = _env_flag("FOUNDUPS_ENABLE_QWEN", True)
    enable_self_improvement = _env_flag("FOUNDUPS_ENABLE_SELF_IMPROVEMENT", True)
    enable_shorts_commands = _env_flag("FOUNDUPS_ENABLE_SHORTS_COMMANDS", True) and not _env_flag("FOUNDUPS_DISABLE_SHORTS_COMMANDS", False)
    enable_key_hygiene = _env_flag("FOUNDUPS_ENABLE_KEY_HYGIENE", True)
    holo_skip_model = _env_flag("HOLO_SKIP_MODEL", False)
    holo_silent = _env_flag("HOLO_SILENT", False)
    holo_verbose = _env_flag("HOLO_VERBOSE", False)
    holo_auto_index = _env_flag("FOUNDUPS_HOLO_AUTO_INDEX", False)
    ai_overseer_breadcrumbs = _env_flag("AI_OVERSEER_BREADCRUMBS", True)
    holo_offline = _env_flag("HOLO_OFFLINE", False)
    holo_disable_pip_install = _env_flag("HOLO_DISABLE_PIP_INSTALL", False)
    holo_breadcrumbs = _env_flag("HOLO_BREADCRUMB_ENABLED", True)
    holo_breadcrumb_logs = _env_flag("HOLO_BREADCRUMB_LOGS", True)
    startup_switchboard = {
        "pattern_memory": bool(PATTERN_MEMORY_AVAILABLE and enable_pattern_memory),
        "wre": bool(enable_wre),
        "wre_monitor": bool(enable_wre and enable_wre_monitor),
        "qwen": bool(enable_qwen),
        "self_improvement": bool(enable_self_improvement),
        "shorts_commands": bool(enable_shorts_commands),
        "key_hygiene": bool(enable_key_hygiene),
        "holo_skip_model": bool(holo_skip_model),
        "holo_silent": bool(holo_silent),
        "holo_verbose": bool(holo_verbose),
        "holo_auto_index": bool(holo_auto_index),
        "holo_offline": bool(holo_offline),
        "holo_disable_pip_install": bool(holo_disable_pip_install),
        "holo_breadcrumbs": bool(holo_breadcrumbs),
        "holo_breadcrumb_logs": bool(holo_breadcrumb_logs),
        "ai_overseer_breadcrumbs": bool(ai_overseer_breadcrumbs),
        "verbose": bool(args.verbose),
    }
    logger.info(f"[SWITCHBOARD] {json.dumps(startup_switchboard, sort_keys=True)}")

    # Initialize PatternMemory once for false-positive gating (WSP 48/60)
    pm = PatternMemory() if (PATTERN_MEMORY_AVAILABLE and enable_pattern_memory) else None
    if PATTERN_MEMORY_AVAILABLE and not enable_pattern_memory:
        logger.info("[SWITCHBOARD] PatternMemory disabled (FOUNDUPS_ENABLE_PATTERN_MEMORY=0)")

    def should_skip(task_key: str, entity_type: str = "task") -> Optional[Dict[str, Any]]:
        if not pm:
            return None
        try:
            return pm.get_false_positive_reason(entity_type, task_key)
        except Exception:
            return None

    if args.training_command:
        execute_training_command(args.training_command, args.targets, args.json_output)
        return
    if args.training_menu:
        run_training_system()
        return

    if args.status:
        check_instance_status()
        return
    if args.deps:
        try:
            from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies

            asyncio.run(ensure_dependencies(require_lm_studio=True))
        except Exception as e:
            print(f"[ERROR] Dependency launcher failed: {e}")
        return
    elif args.git_daemon:
        skip = should_skip("gitpush_dae")
        if skip:
            print(f"[SKIP] Known false positive: gitpush_dae :: {skip.get('reason','')}")
            return
        launch_git_push_dae(run_once=False)
        return
    elif args.git:
        skip = should_skip("gitpush_dae")
        if skip:
            print(f"[SKIP] Known false positive: gitpush_dae :: {skip.get('reason','')}")
            return
        launch_git_push_dae(run_once=True)
        return
    elif args.youtube:
        skip = should_skip("youtube_dae")
        if skip:
            print(f"[SKIP] Known false positive: youtube_dae :: {skip.get('reason','')}")
            return
        asyncio.run(monitor_youtube(disable_lock=args.no_lock))
    elif args.holodae:
        skip = should_skip("holodae")
        if skip:
            print(f"[SKIP] Known false positive: holodae :: {skip.get('reason','')}")
            return
        run_holodae()
    elif args.amo:
        skip = should_skip("amo_dae")
        if skip:
            print(f"[SKIP] Known false positive: amo_dae :: {skip.get('reason','')}")
            return
        run_amo_dae()
    elif args.smd:
        skip = should_skip("social_media_dae")
        if skip:
            print(f"[SKIP] Known false positive: social_media_dae :: {skip.get('reason','')}")
            return
        run_social_media_dae()
    elif args.vision:
        skip = should_skip("vision_dae")
        if skip:
            print(f"[SKIP] Known false positive: vision_dae :: {skip.get('reason','')}")
            return
        run_vision_dae()
    elif args.pqn:
        skip = should_skip("pqn_dae")
        if skip:
            print(f"[SKIP] Known false positive: pqn_dae :: {skip.get('reason','')}")
            return
        run_pqn_dae()
    elif args.liberty:
        skip = should_skip("liberty_alert_mesh")
        if skip:
            print(f"[SKIP] Known false positive: liberty_alert_mesh :: {skip.get('reason','')}")
            return
        run_evade_net()
    elif args.liberty_dae:
        skip = should_skip("liberty_alert_dae")
        if skip:
            print(f"[SKIP] Known false positive: liberty_alert_dae :: {skip.get('reason','')}")
            return
        run_liberty_alert_dae()
    elif args.all:
        skip = should_skip("monitor_all_platforms")
        if skip:
            print(f"[SKIP] Known false positive: monitor_all_platforms :: {skip.get('reason','')}")
            return
        asyncio.run(monitor_all_platforms())
    elif args.mcp:
        skip = should_skip("mcp_gateway")
        if skip:
            print(f"[SKIP] Known false positive: mcp_gateway :: {skip.get('reason','')}")
            return
        show_mcp_services_menu()
    else:
        # Interactive menu - Check instances once at startup, then loop main menu
        _maybe_auto_index_holo(args.verbose)
        print("\n" + "="*60)
        print("0102 FoundUps Agent - DAE Test Menu")
        print("="*60)

        # Instance check re-enabled with timeout protection (3s max)
        # If duplicates found, interactive menu will prompt for action
        print("[INFO] Checking for duplicate instances (timeout: 3s)...")

        # Re-enabled PID check with timeout protection (fixes missing cancel option)
        duplicates = []
        try:
            from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
            lock = get_instance_lock("youtube_monitor")

            # Check for duplicates with 3-second timeout protection
            # (protects against psutil hang that caused original TEMP FIX)
            import threading
            result_holder = []

            def check_with_timeout():
                try:
                    result = lock.check_duplicates(quiet=True)
                    result_holder.append(result)
                except Exception as e:
                    result_holder.append(None)

            check_thread = threading.Thread(target=check_with_timeout, daemon=True)
            check_thread.start()
            check_thread.join(timeout=3.0)

            if check_thread.is_alive():
                # Timeout occurred
                print("[WARN] Instance check timed out (>3s) - skipping duplicate detection")
                print("   Use --status to manually check for running instances\n")
                duplicates = []
            elif result_holder and result_holder[0] is not None:
                duplicates = result_holder[0]
            else:
                duplicates = []

        except Exception as e:
            print(f"[WARN] Could not check instances: {e}")
            print("   Use --status to manually check for running instances\n")
            duplicates = []

        if duplicates:  # Re-enabled interactive PID cancel menu
                # Loop until user makes a valid choice
                while True:
                    print(f"[WARN] FOUND {len(duplicates)} RUNNING INSTANCE(S)")
                    print("\nWhat would you like to do?")
                    print("1. Kill all instances and continue")
                    print("2. Show detailed status")
                    print("3. Continue anyway (may cause conflicts)")
                    print("4. Exit")
                    print("-"*40)

                    # Get user input and clean it (remove brackets, spaces, etc.)
                    try:
                        choice = input("Select option (1-4): ").strip().lstrip(']').lstrip('[')
                        print(f"[DEBUG] Received choice: '{choice}' (repr: {repr(choice)})")
                    except (EOFError, KeyboardInterrupt) as e:
                        print(f"[DEBUG] Input interrupted: {e}")
                        choice = "4"  # Default to exit

                    if choice == "1":
                        print("\n[INFO] Killing duplicate instances...")
                        killed_pids = []
                        failed_pids = []

                        current_pid = os.getpid()

                        for pid in duplicates:
                            if pid == current_pid:
                                continue  # Don't kill ourselves

                            try:
                                print(f"   [INFO] Terminating PID {pid}...")
                                process = psutil.Process(pid)
                                process.terminate()  # Try graceful termination first

                                # Wait up to 5 seconds for process to terminate
                                gone, alive = psutil.wait_procs([process], timeout=5)

                                if alive:
                                    # If still alive, force kill
                                    print(f"   [INFO] Force killing PID {pid}...")
                                    process.kill()
                                    gone, alive = psutil.wait_procs([process], timeout=2)

                                if not alive:
                                    killed_pids.append(pid)
                                    print(f"   [INFO]PID {pid} terminated successfully")
                                else:
                                    failed_pids.append(pid)
                                    print(f"   [ERROR]Failed to kill PID {pid}")

                            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                                print(f"   [WARN] Could not kill PID {pid}: {e}")
                                failed_pids.append(pid)

                        if killed_pids:
                            print(f"\n[INFO]Successfully killed {len(killed_pids)} instance(s): {killed_pids}")
                        if failed_pids:
                            print(f"[WARN] Failed to kill {len(failed_pids)} instance(s): {failed_pids}")

                        print("   Proceeding to main menu...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "2":
                        print("\n" + "="*50)
                        check_instance_status()
                        print("="*50)
                        input("\nPress Enter to continue...")
                        # Don't break - loop back to menu

                    elif choice == "3":
                        print("[WARN] Continuing with potential conflicts...\n")
                        break  # Exit loop and continue to main menu

                    elif choice == "4":
                        print("[INFO] Exiting...")
                        return  # Exit entire program

                    else:
                        print(f"[ERROR]Invalid choice '{choice}'. Please enter 1, 2, 3, or 4.")
                        print("   Try again...\n")
                        # Don't break - loop will continue and ask again
                        continue

        # Orphaned else block removed - duplicates check is now disabled above

        logger.info("[DAEMON] Main menu loop starting")
        print("[DEBUG-MAIN] About to enter main menu loop")

        # Main menu loop (only reached after instance handling)
        while True:
            logger.debug("[DAEMON] Top of menu loop - displaying options")
            print("[DEBUG-MAIN] Top of menu loop - displaying options")

            # Show the main menu
            print("0. Git Operations (Push + Post + History)          | --git")
            print("1. YouTube DAEs (Live/Comments/Shorts/Indexing)    | --youtube")
            print("2. HoloDAE (Code Intelligence & Search)            | --holodae")
            print("3. AMO DAE (Autonomous Moderation Operations)      | --amo")
            print("4. Social Media DAE (012 Digital Twin)             | --smd")
            print("5. Liberty Alert DAE (Community Protection)        | --liberty-dae")
            print("6. PQN Orchestration (Research & Alignment)        | --pqn")
            print("7. Liberty Alert (Mesh Alert System)               | --liberty")
            print("8. FoundUps Vision DAE (Pattern Sensorium)         | --vision")
            print("9. All DAEs (Full System)                          | --all")
            print("10. Exit")
            print("-"*60)
            print("00. Check Instance Status & Health                 | --status")
            print("11. Qwen/Gemma Training System (Pattern Learning)")
            print("12. MCP Services (Model Context Protocol Gateway)  | --mcp")
            print("13. Automation Dependencies (Chrome + LM Studio)  | --deps")
            print("="*60)
            print("CLI: --youtube --no-lock (bypass menu + instance lock)")
            print("="*60)

            try:
                choice = input("\nSelect option: ").strip()
                logger.info(f"[DAEMON] User selected option: '{choice}'")
                print(f"[DEBUG-MAIN] User selected option: '{choice}'")
            except (EOFError, KeyboardInterrupt) as e:
                logger.warning(f"[DAEMON] Input interrupted: {e}")
                print(f"[DEBUG-MAIN] Input interrupted: {e}")
                choice = "10"  # Default to exit on interrupt

            if choice == "0":
                # Git Operations Submenu (WSP 91 compliant)
                print("\n[MENU] Git Operations")
                print("="*60)
                print("1. Push to Git + Post to LinkedIn/X")
                print("2. View Git Post History")
                print("0. Back to Main Menu")
                print("="*60)

                git_choice = input("\nSelect Git option: ").strip()

                if git_choice == "1":
                    print("[DEBUG-MAIN] Calling launch_git_push_dae()...")
                    # Run-once so the interactive menu is not blocked by a long-running daemon.
                    launch_git_push_dae(run_once=True)
                    print("[DEBUG-MAIN] Returned from launch_git_push_dae()")
                elif git_choice == "2":
                    view_git_post_history()
                elif git_choice == "0":
                    print("[BACK] Returning to main menu...")
                else:
                    print("[ERROR] Invalid choice")
                # Will return to menu after completion

            elif choice == "1":
                # YouTube DAEs Menu - Each is an independent DAE at 1.x level (ADR-013)
                print("\n[MENU] YouTube DAEs")
                print("="*60)
                print(f"Active switches: {_yt_switch_summary()} (00=Controls)")
                print("")
                print("== LIVE OPERATIONS ==")
                print("1. [DAE] Live Chat Monitor (AutoModeratorDAE)")
                print("2. [DAE] Comment Engagement (Broadcast Controls)")
                print("6. [ALL] Full Production Mode (Live+Comments+Scheduler)")
                print("7. [AI] AI Overseer Mode (Qwen/Gemma Monitoring)")
                print("")
                print("== CONTENT AUTOMATION ==")
                print("3. [DAE] Shorts Scheduler (Enhance + Schedule)")
                print("4. [DAE] Shorts Generator (Veo3/Sora2)")
                print("")
                print("== KNOWLEDGE INDEXING ==")
                print("8. [INDEX] YouTube Indexing (Digital Twin Learning)")
                print("5. [INFO] YouTube Stats")
                print("")
                print("00. Controls (Local Switches)")
                print("0. Back to Main Menu")
                print("="*60)

                yt_choice = input("\nSelect YouTube DAE: ")

                def run_shorts_flow(engine_label: str, system_label: str, mode_label: str, duration_label: str, engine_key: str) -> None:
                    print(f"\n[MENU] YouTube Shorts Generator [{engine_label}]")
                    print("="*60)
                    print("Channel: Move2Japan (9,020 subscribers)")
                    print(f"System: {system_label}")
                    print("="*60)

                    topic = input("\n[TIP] Enter topic (e.g., 'Cherry blossoms in Tokyo'): ").strip()

                    if not topic:
                        print("[WARN] No topic entered - returning to menu")
                        return

                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator
                        from modules.communication.youtube_shorts.src.veo3_generator import Veo3ApiKeyCompromisedError

                        print(f"\n[MENU] Generating YouTube Short ({engine_label}): {topic}")
                        print(f"  Mode: {mode_label}")
                        print(f"  Duration: {duration_label}")
                        print("  Privacy: PUBLIC")

                        orchestrator = ShortsOrchestrator(channel="move2japan", default_engine="auto")

                        youtube_url = orchestrator.create_and_upload(
                            topic=topic,
                            duration=15,
                            enhance_prompt=True,
                            fast_mode=True,
                            privacy="public",
                            use_3act=True,
                            engine=engine_key
                        )

                        print(f"\n[INFO]SHORT PUBLISHED!")
                        print(f"   URL: {youtube_url}")
                        print(f"   Channel: Move2Japan")

                    except Veo3ApiKeyCompromisedError as e:
                        print(f"\n[ERROR]YouTube Shorts generation failed: {e}")
                        if enable_key_hygiene:
                            try:
                                from modules.infrastructure.shared_utilities.key_hygiene import KeyHygiene

                                KeyHygiene(service="veo3", urls=KeyHygiene.default_genai_urls()).maybe_prompt_rotation(
                                    key_source=getattr(e, "key_source", "unknown"),
                                    fingerprint=getattr(e, "fingerprint", None) or "sha256:unknown",
                                    reason_hint="compromised",
                                    interactive=True,
                                )
                            except Exception:
                                pass

                        if args.verbose or _env_truthy("FOUNDUPS_DEBUG_SHORTS", "false"):
                            import traceback

                            traceback.print_exc()

                    except Exception as e:
                        print(f"\n[ERROR]YouTube Shorts generation failed: {e}")
                        # Avoid dumping stack traces in normal runs (too noisy for DAEmon logs).
                        if args.verbose or _env_truthy("FOUNDUPS_DEBUG_SHORTS", "false"):
                            import traceback

                            traceback.print_exc()

                # ============================================================
                # YOUTUBE DAEs HANDLERS (ADR-013: Independent DAEs at 1.x level)
                # 1=Live Chat, 2=Comments, 3=Scheduler, 4=Generator, 5=Stats, 6=Full, 7=AI
                # ============================================================

                if yt_choice == "00":
                    _yt_controls_menu()
                elif yt_choice == "1":
                    # 1.1 Live Chat Monitor DAE - Direct launch with 012 profile (ADR-013)
                    print("\n[DAE] Live Chat Monitor - 012 Operational Profile")
                    print("="*60)

                    env_overrides = {
                        "YT_ENGAGEMENT_TEMPO": "012",
                        "YT_REPLY_BASIC_ONLY": "false",
                        "YT_COMMENT_ONLY_MODE": "false"
                    }

                    # Auto-kill existing instances
                    try:
                        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
                        lock = get_instance_lock("youtube_monitor")
                        duplicates = lock.check_duplicates(quiet=True)
                        if duplicates:
                            print(f"[MENU] Killing {len(duplicates)} existing instance(s)...")
                            lock.kill_pids(duplicates)
                            time.sleep(1)
                    except Exception as e:
                        logger.debug(f"Cleanup failed: {e}")

                    asyncio.run(monitor_youtube(disable_lock=False, enable_ai_monitoring=False, env_overrides=env_overrides))

                elif yt_choice == "2":
                    # 1.2 Comment Engagement - 012 Control Plane (broadcast settings)
                    print("\n[MENU] Comment Engagement (Broadcast Controls)")
                    print("="*60)
                    try:
                        from modules.communication.video_comments.src.commenting_control_plane import (
                            load_broadcast,
                            set_promo,
                            clear_promo,
                        )
                    except Exception as e:
                        print(f"[ERROR] Commenting control plane unavailable: {e}")
                        continue

                    def _summary(cfg) -> str:
                        enabled = "ON" if cfg.enabled else "OFF"
                        handles = " ".join(cfg.promo_handles) if cfg.promo_handles else "(none)"
                        msg = (cfg.promo_message or "").strip() or "(none)"
                        return f"enabled={enabled} | handles={handles} | message={msg}"

                    while True:
                        cfg = load_broadcast()
                        print("\n" + "-" * 60)
                        print("COMMENTING SUBMENU (012 -> Comment DAE)")
                        print("Broadcast controls (promo injection) - use 6 for comment-only")
                        print(f"Switches: {_yt_switch_summary()} (00=Controls)")
                        print(f"Current: {_summary(cfg)}")
                        print("-" * 60)
                        print("  1) Toggle enabled (promo injection on replies)")
                        print("  2) Set promo handles (space-separated, e.g. @NewChannel @Other)")
                        print("  3) Set promo message (free text)")
                        print("  4) Clear promo + disable")
                        print("  5) Back")
                        print("  6) Start COMMENT-ONLY (NO live chat agent)")
                        print("  00) Controls (local switches)")
                        print("")
                        print("  TIP: For full DAE (comments+stream+livechat), use main menu 1→1")

                        choice = input("commenting> ").strip().lower()
                        if choice in {"5", "back", "b", "exit", "quit"}:
                            break
                        if choice in {"00", "controls", "c"}:
                            _yt_controls_menu()
                            continue
                        if choice in {"1", "toggle"}:
                            set_promo(enabled=not cfg.enabled, updated_by="012")
                            continue
                        if choice in {"2", "handles"}:
                            raw = input("handles> ").strip()
                            handles = [h for h in raw.split() if h.strip()]
                            set_promo(promo_handles=handles, updated_by="012")
                            continue
                        if choice in {"3", "message", "msg"}:
                            msg = input("message> ").strip()
                            set_promo(promo_message=msg, updated_by="012")
                            continue
                        if choice in {"4", "clear"}:
                            clear_promo()
                            continue
                        if choice in {"6", "start", "run", "comment-only", "comments-only", "co"}:
                            print("\n[DAE] COMMENT-ONLY MODE (NO Live Chat Agent)")
                            print("="*60)
                            print("Auto-rotates through ALL channels:")
                            print("  Chrome (9222): Move2Japan + UnDaoDu")
                            print("  Edge (9223): FoundUps + RavingANTIFA")
                            print("")
                            print("🔒 Stream detection: DISABLED")
                            print("🔒 Live chat agent: DISABLED")
                            print("✅ Comment engagement: RUNS CONTINUOUSLY")
                            print("="*60)

                            try:
                                from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE

                                # Set comment-only mode BEFORE launching
                                os.environ["YT_COMMENT_ONLY_MODE"] = "true"

                                print("[INFO] Starting COMMENT-ONLY DAE...")
                                print("[INFO] YT_COMMENT_ONLY_MODE=true (no stream detection, no live chat)")
                                print("[INFO] Press Ctrl+C to stop")

                                dae = AutoModeratorDAE(enable_ai_monitoring=False)
                                asyncio.run(dae.run())
                            except KeyboardInterrupt:
                                print("\n[STOP] Comment-Only DAE stopped by user")
                            except ImportError as e:
                                print(f"[ERROR] Could not import: {e}")
                                import traceback
                                traceback.print_exc()
                            except Exception as e:
                                print(f"[ERROR] Failed: {e}")
                                import traceback
                                traceback.print_exc()
                            finally:
                                # Reset the env var after exit
                                os.environ.pop("YT_COMMENT_ONLY_MODE", None)
                            continue
                        print("Unknown option")
                elif yt_choice == "3":

                    # 1.3 Shorts Scheduler DAE + Selenium Tests
                    # Hot-reload Shorts Scheduler launcher for long-lived menu sessions (0102-first).
                    import importlib
                    import modules.platform_integration.youtube_shorts_scheduler.scripts.launch as shorts_launch
                    shorts_launch = importlib.reload(shorts_launch)
                    show_shorts_scheduler_menu = shorts_launch.show_shorts_scheduler_menu
                    run_multi_channel_scheduler = shorts_launch.run_multi_channel_scheduler
                    
                    while True:
                        sched_choice = show_shorts_scheduler_menu()

                        if sched_choice == "1":
                            # Shorts (production): schedule NEXT unlisted short (full cake)
                            content_type = (os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts")
                            if content_type != "shorts":
                                print(f"\n[PLACEHOLDER] content_type={content_type} is not implemented yet. Use shorts.")
                                input("\nPress Enter to continue...")
                                continue
                            from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import run_scheduler_dae
                            channel_key = (os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan")
                            results = asyncio.run(run_scheduler_dae(channel_key=channel_key, max_videos=1, dry_run=False))
                            print(f"\n[RESULT] channel={results.get('channel', channel_key)} scheduled={results.get('total_scheduled', 0)} errors={results.get('total_errors', 0)}")
                            input("\nPress Enter to continue...")
                        elif sched_choice == "2":
                            # Shorts (production): schedule ALL unlisted shorts (safety: capped by max_videos)
                            content_type = (os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts")
                            if content_type != "shorts":
                                print(f"\n[PLACEHOLDER] content_type={content_type} is not implemented yet. Use shorts.")
                                input("\nPress Enter to continue...")
                                continue
                            from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import run_scheduler_dae
                            channel_key = (os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan")
                            results = asyncio.run(run_scheduler_dae(channel_key=channel_key, max_videos=9999, dry_run=False))
                            print(f"\n[RESULT] channel={results.get('channel', channel_key)} scheduled={results.get('total_scheduled', 0)} errors={results.get('total_errors', 0)}")
                            input("\nPress Enter to continue...")
                        elif sched_choice == "3":
                            # Preview Only (DRY RUN)
                            content_type = (os.getenv("YT_SCHEDULER_CONTENT_TYPE", "shorts").strip().lower() or "shorts")
                            if content_type != "shorts":
                                print(f"\n[PLACEHOLDER] content_type={content_type} is not implemented yet. Use shorts.")
                                input("\nPress Enter to continue...")
                                continue
                            from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import run_scheduler_dae
                            channel_key = (os.getenv("YT_SHORTS_SCHEDULER_CHANNEL_KEY", "move2japan").strip().lower() or "move2japan")
                            results = asyncio.run(run_scheduler_dae(channel_key=channel_key, max_videos=1, dry_run=True))
                            print(f"\n[DRY RUN] channel={results.get('channel', channel_key)} scheduled={results.get('total_scheduled', 0)} errors={results.get('total_errors', 0)}")
                            input("\nPress Enter to continue...")
                        elif sched_choice == "4":
                            # Chrome rotation (Move2Japan <-> UnDaoDu)
                            run_multi_channel_scheduler(browser="chrome", mode="schedule", max_per_channel=9999)
                            input("\nPress Enter to continue...")
                        elif sched_choice == "5":
                            # Edge rotation (FoundUps <-> RavingANTIFA)
                            run_multi_channel_scheduler(browser="edge", mode="schedule", max_per_channel=9999)
                            input("\nPress Enter to continue...")
                        elif sched_choice == "6":
                            # Indexing handoff (use the dedicated Indexing menu)
                            print("\n[HANDOFF] Use: YouTube DAEs → 8 [INDEX] YouTube Indexing (Digital Twin Learning)")
                            input("\nPress Enter to continue...")
                        elif sched_choice == "7":
                            # Full Videos (future layer)
                            print("\n[PLACEHOLDER] Full video scheduling not yet implemented (content_type=videos)")
                            input("\nPress Enter to continue...")
                        elif sched_choice == "0":
                            break
                        else:
                            print("[ERROR] Invalid choice")

                elif yt_choice == "4":
                    # 1.4 Shorts Generator DAE (submenu for Veo3/Sora2)
                    print("\n[DAE] Shorts Generator")
                    print("="*60)
                    print("1. Veo3 (Gemini - 3-Act Story)")
                    print("2. Sora2 (Live Action Cinematic)")
                    print("0. Back")
                    print("="*60)

                    engine_choice = input("Select engine: ").strip()

                    if engine_choice == "1":
                        run_shorts_flow(
                            engine_label="Gemini/Veo 3",
                            system_label="3-Act Story (Setup -> Shock -> 0102 Reveal)",
                            mode_label="Emergence Journal POC",
                            duration_label="~16s (2.5s clips merged)",
                            engine_key="veo3"
                        )
                    elif engine_choice == "2":
                        run_shorts_flow(
                            engine_label="Sora2 Live Action",
                            system_label="3-Act Story (Cinematic Reveal)",
                            mode_label="Cinematic Sora2 (live-action focus)",
                            duration_label="15s cinematic (single clip)",
                            engine_key="sora2"
                        )

                elif yt_choice == "5":
                    # 1.5 YouTube Stats
                    print("\n[INFO] YouTube Stats")
                    try:
                        from modules.communication.youtube_shorts.src.shorts_orchestrator import ShortsOrchestrator
                        orch = ShortsOrchestrator(channel="move2japan", default_engine="auto")
                        stats = orch.get_stats()

                        print(f"\n  Total Shorts: {stats['total_shorts']}")
                        print(f"  Uploaded: {stats['uploaded']}")
                        print(f"  Total Cost: ${stats['total_cost_usd']}")
                        print(f"  Avg Cost: ${stats['average_cost_per_short']}")
                        if stats.get('engine_usage'):
                            print(f"  Engine Usage: {stats['engine_usage']}")

                        recent = stats.get('recent_shorts') or []
                        if recent:
                            print(f"\n  Recent Shorts:")
                            for s in recent[-3:]:
                                print(f"    - {s.get('topic', 'N/A')[:40]}...")
                                print(f"      {s.get('youtube_url', 'N/A')}")
                    except Exception as e:
                        print(f"[ERROR] Failed to get stats: {e}")

                elif yt_choice == "6":
                    # 1.6 Full Production Mode (runs Live Chat + Comments)
                    print("\n[ALL] Full YouTube Production Mode")
                    print("="*60)
                    print("This will start:")
                    print("  - Live Chat Monitor (AutoModeratorDAE)")
                    print("  - Comment Engagement DAE (Like/Heart/Reply)")
                    print("="*60)
                    print("[INFO] Starting Full Production Mode with 012 profile...")

                    env_overrides = {
                        "YT_ENGAGEMENT_TEMPO": "012",
                        "YT_REPLY_BASIC_ONLY": "false",
                        "YT_COMMENT_ONLY_MODE": "false"
                    }

                    # Auto-kill any existing instances
                    try:
                        from modules.infrastructure.instance_lock.src.instance_manager import get_instance_lock
                        lock = get_instance_lock("youtube_monitor")
                        duplicates = lock.check_duplicates(quiet=True)
                        if duplicates:
                            print(f"[MENU] Killing {len(duplicates)} existing instance(s)...")
                            lock.kill_pids(duplicates)
                            time.sleep(1)
                    except Exception as e:
                        logger.debug(f"Pre-launch cleanup failed: {e}")

                    asyncio.run(monitor_youtube(disable_lock=False, enable_ai_monitoring=False, env_overrides=env_overrides))

                elif yt_choice == "7":
                    # 1.7 AI Overseer Mode
                    print("\n[AI] AI Overseer Mode (Qwen/Gemma Monitoring)")
                    print("="*60)
                    print("Profiles: 1=012  2=FAST  3=MEDIUM  4=Minimal  5=Occam  6=Comment-Only")
                    print("="*60)

                    ai_profile = input("Select profile [1-6, default=1]: ").strip() or "1"

                    env_overrides = {"YT_COMMENT_ONLY_MODE": "false"}
                    if ai_profile == "2":
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "FAST", "COMMUNITY_DEBUG_SUBPROCESS": "true"})
                    elif ai_profile == "3":
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "MEDIUM", "COMMUNITY_DEBUG_SUBPROCESS": "true"})
                    elif ai_profile == "4":
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "012", "YT_REPLY_BASIC_ONLY": "true"})
                    elif ai_profile == "5":
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "012", "YT_REPLY_BASIC_ONLY": "true", "YT_OCCAM_MODE": "true"})
                    elif ai_profile == "6":
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "012", "YT_REPLY_BASIC_ONLY": "false", "YT_COMMENT_ONLY_MODE": "true"})
                    else:
                        env_overrides.update({"YT_ENGAGEMENT_TEMPO": "012", "YT_REPLY_BASIC_ONLY": "false"})

                    print("[AI] Starting with AI Overseer monitoring...")
                    try:
                        asyncio.run(monitor_youtube(disable_lock=False, enable_ai_monitoring=True, env_overrides=env_overrides))
                    except KeyboardInterrupt:
                        print("\n[STOP] Stopped by user")
                    except Exception as e:
                        print(f"\n[ERROR] Failed: {e}")

                elif yt_choice == "8":
                    # 1.8 YouTube Indexing (Digital Twin Learning) - Enhanced with Gemini
                    print("\n[INDEX] YouTube Channel Indexing")
                    print("="*60)
                    print("Creates searchable knowledge base from 012's videos")
                    print("Each video saved as JSON with transcripts, topics, timestamps")
                    print("="*60)
                    print("1. [GEMINI] Gemini AI Indexing (fast, no download)")
                    print("2. [LOCAL] Whisper Indexing (yt-dlp + faster-whisper)")
                    print("3. [TEST] Test Video Indexing (single video)")
                    print("4. [BATCH] Batch Index Channel (bulk process)")
                    print("5. [TRAIN] Extract Training Data (Gemma quality filter)")
                    print("0. Back")
                    print("="*60)

                    idx_choice = input("\nSelect indexing method: ").strip()

                    if idx_choice == "1":
                        # Gemini-based indexing - BROWSER-AWARE like commenting
                        print("\n[GEMINI] Autonomous Video Indexing")
                        print("="*60)
                        print("Browser rotation (same as comment engagement):")
                        print("  Chrome (9222): UnDaoDu → Move2Japan")
                        print("  Edge (9223): FoundUps")
                        print("Indexes ALL videos per channel until complete")
                        print("="*60)

                        try:
                            from modules.ai_intelligence.video_indexer.src.studio_ask_indexer import run_video_indexing_cycle

                            # Browser-grouped channels (mirrors commenting architecture)
                            # Chrome (port 9222): Same Google account
                            chrome_channels = [
                                os.getenv("UNDAODU_CHANNEL_ID", "UCfHM9Fw9HD-NwiS0seD_oIA"),
                                os.getenv("MOVE2JAPAN_CHANNEL_ID", "UC-LSSlOZwpGIRIYihaz8zCw"),
                            ]
                            # Edge (port 9223): Different Google account
                            edge_channels = [
                                os.getenv("FOUNDUPS_CHANNEL_ID", "UCSNTUXjAgpd4sgWYP0xoJgw"),
                            ]

                            total_indexed = 0

                            # Phase 1: Chrome channels (UnDaoDu, Move2Japan)
                            print("\n[PHASE 1] Chrome (9222): UnDaoDu + Move2Japan")
                            result = asyncio.run(run_video_indexing_cycle(
                                channels=chrome_channels,
                                max_videos_per_channel=9999,  # Index ALL
                                browser="chrome"
                            ))
                            total_indexed += result.get('total_indexed', 0)
                            print(f"[CHROME] Indexed {result.get('total_indexed', 0)} videos")

                            # Phase 2: Edge channels (FoundUps)
                            print("\n[PHASE 2] Edge (9223): FoundUps")
                            result = asyncio.run(run_video_indexing_cycle(
                                channels=edge_channels,
                                max_videos_per_channel=9999,  # Index ALL
                                browser="edge"
                            ))
                            total_indexed += result.get('total_indexed', 0)
                            print(f"[EDGE] Indexed {result.get('total_indexed', 0)} videos")

                            print(f"\n[RESULT] Total indexed: {total_indexed} videos across all channels")
                        except ImportError as e:
                            print(f"[ERROR] studio_ask_indexer not available: {e}")
                        except Exception as e:
                            print(f"[ERROR] Indexing failed: {e}")
                            import traceback
                            traceback.print_exc()

                    elif idx_choice == "2":
                        # Legacy whisper-based indexing
                        try:
                            from modules.communication.voice_command_ingestion.scripts.index_channel import (
                                run_indexing_menu
                            )
                            run_indexing_menu()
                        except ImportError as e:
                            print(f"[ERROR] Could not import indexing module: {e}")
                            print("[TIP] Install: pip install faster-whisper yt-dlp chromadb sentence-transformers")
                        except Exception as e:
                            print(f"[ERROR] Indexing menu failed: {e}")
                            import traceback
                            traceback.print_exc()

                    elif idx_choice == "3":
                        # Test single video indexing
                        print("\n[TEST] Single Video Indexing Test")
                        video_id = input("Enter YouTube video ID: ").strip()
                        if video_id:
                            try:
                                from modules.ai_intelligence.video_indexer.src.gemini_video_analyzer import GeminiVideoAnalyzer
                                from modules.ai_intelligence.video_indexer.src.video_index_store import VideoIndexStore, IndexData
                                from datetime import datetime

                                print(f"[INFO] Analyzing video {video_id}...")
                                analyzer = GeminiVideoAnalyzer()
                                result = analyzer.analyze_video(video_id)

                                if result.success:
                                    # Save to JSON
                                    store = VideoIndexStore(base_path="video_index")
                                    index_data = IndexData(
                                        video_id=result.video_id,
                                        channel="test",
                                        title=result.title,
                                        duration=result.duration or 0,
                                        indexed_at=datetime.now().isoformat(),
                                        audio={"segments": [s.__dict__ for s in result.segments], "transcript_summary": result.transcript_summary},
                                        visual={"description": result.visual_description},
                                        moments=[],
                                        clips=[],
                                        metadata={"topics": result.topics, "speakers": result.speakers, "key_points": result.key_points}
                                    )
                                    path = store.save_index(video_id, index_data)
                                    print(f"\n[SUCCESS] Video indexed!")
                                    print(f"  Title: {result.title}")
                                    print(f"  Topics: {', '.join(result.topics[:5])}")
                                    print(f"  Saved to: {path}")
                                else:
                                    print(f"[ERROR] Analysis failed: {result.error}")
                            except Exception as e:
                                print(f"[ERROR] Test failed: {e}")
                                import traceback
                                traceback.print_exc()

                    elif idx_choice == "4":
                        # Batch index channel
                        print("\n[BATCH] Batch Index Channel Videos")
                        print("="*60)
                        channel = _select_channel()
                        batch_size = input("Batch size [50]: ").strip() or "50"
                        delay = input("Delay between API calls (seconds) [10]: ").strip() or "10"

                        video_file = f"data/{channel}_video_ids.txt"
                        if not os.path.exists(video_file):
                            print(f"[ERROR] Video ID file not found: {video_file}")
                            print("[TIP] Create video ID file or fetch from YouTube API")
                        else:
                            try:
                                import subprocess
                                cmd = [
                                    sys.executable,
                                    "scripts/batch_index_videos.py",
                                    "--batch-size", batch_size,
                                    "--delay", delay,
                                    "--channel", channel,
                                    "--video-file", video_file,
                                    "--max-retries", "3"
                                ]
                                print(f"[INFO] Running: {' '.join(cmd)}")
                                subprocess.run(cmd)
                            except Exception as e:
                                print(f"[ERROR] Batch indexing failed: {e}")
                                import traceback
                                traceback.print_exc()

                    elif idx_choice == "5":
                        # Extract training data with Gemma quality filter
                        print("\n[TRAIN] Extract Training Data for Digital Twin")
                        print("="*60)
                        channel = _select_channel()
                        use_gemma = input("Use Gemma quality filter? (y/n) [y]: ").strip().lower() != "n"

                        input_dir = f"memory/video_index/{channel}"
                        output_dir = f"memory/training_data/{channel}"

                        if not os.path.exists(input_dir):
                            print(f"[ERROR] No indexed videos found: {input_dir}")
                            print("[TIP] Run indexing first (Option 1 or 4)")
                        else:
                            try:
                                from modules.ai_intelligence.video_indexer.src.dataset_builder import DatasetBuilder
                                from pathlib import Path

                                print(f"[INFO] Processing {input_dir}...")
                                builder = DatasetBuilder(use_gemma=use_gemma)
                                result = builder.process_folder(input_dir, output_dir)

                                print("\n[SUCCESS] Training data extracted!")
                                print(f"  Videos processed: {result['videos_processed']}")
                                print(f"  Training rows: {result['training_rows']}")
                                print(f"  Voice clips: {result['voice_clips']}")
                                print(f"  Training-worthy (HIGH tier): {result['training_worthy']}")
                                print(f"  Output: {output_dir}/")

                                # Show output files
                                output_path = Path(output_dir)
                                for f in output_path.glob("*"):
                                    size = f.stat().st_size / 1024
                                    print(f"    - {f.name} ({size:.1f} KB)")
                            except Exception as e:
                                print(f"[ERROR] Training data extraction failed: {e}")
                                import traceback
                                traceback.print_exc()

                    elif idx_choice == "0":
                        pass  # Back to YT menu

                elif yt_choice == "0":
                    print("[BACK] Returning to main menu...")
                else:
                    print("[ERROR] Invalid choice")

            elif choice == "2":
                # HoloDAE - Code Intelligence & Monitoring
                print("[INFO] HoloDAE Menu - Code Intelligence & Monitoring System")
                try:
                    # Import menu function ONLY (don't start daemon yet)
                    from holo_index.qwen_advisor.autonomous_holodae import show_holodae_menu

                    holodae_instance = None  # Initialize as None, created only when needed

                    while True:
                        choice = show_holodae_menu()

                        if choice == "0":
                            # Launch the daemon (option 0 in HoloDAE menu)
                            print("[MENU] Launching HoloDAE Autonomous Monitor...")
                            from holo_index.qwen_advisor.autonomous_holodae import start_holodae_monitoring
                            if holodae_instance is None:
                                holodae_instance = start_holodae_monitoring()
                                print("[INFO]HoloDAE monitoring started in background")
                                print("[TIP] Daemon is running - select 9 to stop, or 99 to return to main menu")
                            else:
                                print("[INFO]HoloDAE already running")
                            # Don't break - loop back to HoloDAE menu for more selections
                        elif choice == "9":
                            # Stop the daemon (option 9 - toggle monitoring)
                            if holodae_instance is not None and holodae_instance.active:
                                print("[INFO] Stopping HoloDAE monitoring...")
                                holodae_instance.stop_autonomous_monitoring()
                                print("[INFO]HoloDAE daemon stopped")
                            else:
                                print("[INFO] HoloDAE daemon is not running")
                        elif choice == "99":
                            print("[INFO] Returning to main menu...")
                            if holodae_instance is not None and holodae_instance.active:
                                print("[WARN]HoloDAE daemon still running in background")
                            break
                        elif choice == "1":
                            # Semantic Code Search - directly integrated
                            print("\n[HOLOINDEX] Semantic Code Search")
                            print("=" * 60)
                            print("This prevents vibecoding by finding existing code!")
                            print("Examples: 'send messages', 'handle timeouts', 'consciousness'")
                            print("=" * 60)
                            query = input("\nWhat code are you looking for? ")
                            if query:
                                search_with_holoindex(query)
                                input("\nPress Enter to continue...")
                            else:
                                print("No search query provided")
                        elif choice == "2":
                            # Dual Search (Code + WSP)
                            print("\n[HOLOINDEX] Dual Search (Code + WSP)")
                            print("=" * 60)
                            query = input("\nSearch query: ")
                            if query:
                                search_with_holoindex(query)
                                input("\nPress Enter to continue...")
                            else:
                                print("No search query provided")
                        elif choice == "3":
                            print("[INFO]Running module existence check...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --check-module 'module_name'")
                        elif choice == "4":
                            print("[INFO] Running DAE cube organizer...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --init-dae 'DAE_name'")
                        elif choice == "5":
                            print("[INFO] Running index management...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --index-all")
                        elif choice in ["6", "7", "8", "9", "10", "11", "12", "13"]:
                            print("[INFO] Running HoloDAE intelligence analysis...")
                            # These would trigger HoloDAE analysis functions
                            print("Use HoloIndex search to trigger automatic analysis")
                        elif choice == "14":
                            print("[INFO]Running WSP 88 orphan analysis...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --wsp88")
                        elif choice == "16":
                            print("[INFO] Execution Log Analyzer - Advisor Choice")
                            print("=" * 60)
                            print("Advisor: Choose analysis mode for systematic log processing")
                            print()
                            print("1. [MENU]Interactive Mode - Step-by-step advisor guidance")
                            print("2. [WARN] Daemon Mode - Autonomous 0102 background processing")
                            print()
                            print("Interactive: User-guided analysis with advisor oversight")
                            print("Daemon: Autonomous processing once triggered - follows WSP 80")
                            print()

                            analysis_choice = input("Select mode (1-2): ").strip()

                            if analysis_choice == "1":
                                # Interactive mode - advisor-guided
                                print("\n[MENU]Starting Interactive Log Analysis...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor-guided systematic log analysis...")
                                    print("[INFO] Processing 23,000+ lines with advisor oversight...")

                                    librarian = coordinate_execution_log_processing(daemon_mode=False)

                                    print("\n[INFO]Interactive analysis initialized!")
                                    print("[INFO] Results saved to:")
                                    print("   - complete_file_index.json (full scope analysis)")
                                    print("   - qwen_processing_plan.json (processing plan)")
                                    print("   - qwen_next_task.json (ready for Qwen analysis)")

                                    print("\n[INFO] Next: Advisor guides Qwen analysis of chunks")
                                    input("\nPress Enter to continue...")

                                except Exception as e:
                                    print(f"[ERROR]Interactive analysis failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            elif analysis_choice == "2":
                                # Daemon mode - autonomous 0102 processing
                                print("\n[WARN] Starting Log Analysis Daemon...")
                                try:
                                    from holo_index.adaptive_learning.execution_log_analyzer.execution_log_librarian import coordinate_execution_log_processing

                                    print("[INFO] Advisor triggers autonomous 0102 processing...")
                                    print("[INFO] 0102 will process entire log file independently")

                                    # Start daemon
                                    daemon_thread = coordinate_execution_log_processing(daemon_mode=True)

                                    print("\n[INFO]Daemon started successfully!")
                                    print("[INFO] 0102 processing 23,000+ lines autonomously")
                                    print("[INFO] Check progress: HoloDAE menu  -> Option 15 (PID Detective)")
                                    print("[INFO] Results will be saved to analysis output files")

                                    input("\nPress Enter to continue (daemon runs in background)...")

                                except Exception as e:
                                    print(f"[ERROR]Daemon startup failed: {e}")
                                    import traceback
                                    traceback.print_exc()

                            else:
                                print("[ERROR]Invalid choice - returning to menu")
                                input("\nPress Enter to continue...")
                        elif choice in ["15", "17", "18"]:
                            print("[INFO] Running WSP compliance functions...")
                            # These would trigger compliance checking
                            print("Use HoloIndex search to trigger compliance analysis")
                        elif choice == "20":
                            _holo_controls_menu()
                        elif choice in ["19", "21", "22", "23"]:
                            print("[MENU]Running AI advisor functions...")
                            # Could integrate with HoloIndex CLI
                            print("Use: python holo_index.py --search 'query' --llm-advisor")
                        elif choice == "24":
                            print("[MENU] Launching YouTube Live DAE...")
                            # Would need to navigate to option 1
                            print("Please select option 1 from main menu for YouTube DAE")
                        elif choice == "25":
                            print("[INFO] Starting autonomous HoloDAE monitoring...")
                            run_holodae()
                            break  # Exit menu after starting monitoring
                        elif choice == "6":
                            print("[INFO] Launching Chain-of-Thought Brain Logging...")
                            try:
                                from holo_index.qwen_advisor.chain_of_thought_logger import demonstrate_brain_logging
                                demonstrate_brain_logging()
                                print("\n[INFO] BRAIN LOGGING COMPLETE - Every thought, decision, and action was logged above!")
                                print("[TIP] This shows exactly how the AI brain works - completely observable!")
                            except Exception as e:
                                print(f"[ERROR]Brain logging failed: {e}")
                            input("\nPress Enter to continue...")
                        elif choice in ["26", "27", "28", "29", "30"]:
                            print("[INFO] This DAE operation requires main menu selection...")
                            # Would need to navigate to appropriate main menu option
                            print("Please return to main menu and select the appropriate DAE")
                        elif choice in ["31", "32", "33", "34", "35"]:
                            print("[WARN]Running administrative functions...")
                            # These would trigger admin functions
                            print("Administrative functions available through main menu")
                        else:
                            print("[ERROR]Invalid choice. Please select 0-35.")

                        input("\nPress Enter to continue...")

                except Exception as e:
                    print(f"[ERROR]HoloDAE menu failed to load: {e}")
                    import traceback
                    traceback.print_exc()

            elif choice == "3":
                # AMO DAE
                print("[AMO] Starting AMO DAE (Autonomous Moderation)...")
                try:
                    from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
                    dae = AutoModeratorDAE()
                    asyncio.run(dae.run())
                except KeyboardInterrupt:
                    print("\n[STOP] AMO DAE stopped by user")

            elif choice == "4":
                # Social Media DAE (012 Digital Twin)
                print("[SMD] Starting Social Media DAE (012 Digital Twin)...")
                try:
                    from modules.platform_integration.social_media_orchestrator.src.social_media_orchestrator import SocialMediaOrchestrator
                    orchestrator = SocialMediaOrchestrator()
                    # orchestrator.run_digital_twin()  # TODO: Implement digital twin mode
                    print("Digital Twin mode coming soon...")
                except KeyboardInterrupt:
                    print("\n[STOP] Social Media DAE stopped by user")

            elif choice == "5":
                # Liberty Alert DAE
                try:
                    run_liberty_alert_dae()
                except KeyboardInterrupt:
                    print("\n[STOP] Liberty Alert DAE stopped by user")

            elif choice == "6":
                # PQN Orchestration
                print("[INFO] Starting PQN Research DAE...")
                from modules.ai_intelligence.pqn.scripts.launch import run_pqn_dae
                run_pqn_dae()

            elif choice == "7":
                # Liberty Alert mesh alert system
                try:
                    run_evade_net()
                except KeyboardInterrupt:
                    print("\n[STOP] Liberty Mesh Alert stopped by user")

            elif choice == "8":
                # FoundUps Vision DAE
                try:
                    run_vision_dae()
                except KeyboardInterrupt:
                    print("\n[STOP] Vision DAE stopped by user")

            elif choice == "9":
                # All DAEs
                print("[ALL] Starting ALL DAEs...")
                try:
                    asyncio.run(monitor_all_platforms())
                except KeyboardInterrupt:
                    print("\n[STOP] All DAEs stopped by user")

            elif choice == "10":
                print("[EXIT] Exiting...")
                break  # Exit the while True loop

            elif choice in {"00", "status"}:
                check_instance_status()
                input("\nPress Enter to continue...")

            elif choice == "11":
                # Qwen/Gemma Training System (was 13)
                run_training_system()

            elif choice == "12":
                # MCP Services Gateway (was 14)
                print("[MCP] Launching MCP Services Gateway...")
                from modules.infrastructure.mcp_manager.src.mcp_manager import show_mcp_services_menu
                show_mcp_services_menu()

            elif choice == "13":
                # Automation Dependencies (was 15)
                print("[DEPS] Checking/launching local automation dependencies (Chrome + LM Studio)...")
                try:
                    from modules.infrastructure.dependency_launcher.src.dae_dependencies import ensure_dependencies

                    asyncio.run(ensure_dependencies(require_lm_studio=True))
                except Exception as e:
                    print(f"[ERROR] Dependency launcher failed: {e}")

            else:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

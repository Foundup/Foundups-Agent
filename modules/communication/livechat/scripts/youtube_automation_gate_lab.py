#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube Automation Gate Lab (WSP 77/91)
======================================

Purpose
-------
Run short, controlled "gate flip" experiments for the YouTube DAE and capture
logs + a compact vitals report per scenario.

This is designed to help 0102 isolate which automation surface correlates with
YouTube warnings (e.g., chat sends vs. Studio engagement vs. UI actions) by
turning features on one-at-a-time and observing outcomes.

Safety
------
- This script does NOT attempt to bypass platform safety systems.
- Use a dedicated test channel (e.g., `@foundups1934`) and respect YouTube ToS.

Usage
-----
Run a single scenario for 10 minutes on a specific channel:
  python modules/communication/livechat/scripts/youtube_automation_gate_lab.py ^
    --scenario observe_only ^
    --channels UCROkIz1wOCP3tPk-1j3umyQ ^
    --duration-seconds 600

Run all scenarios sequentially:
  python modules/communication/livechat/scripts/youtube_automation_gate_lab.py ^
    --run-all ^
    --channels UCROkIz1wOCP3tPk-1j3umyQ ^
    --duration-seconds 600
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from modules.infrastructure.instance_monitoring.scripts.log_vitals import compute_vitals  # noqa: E402


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


def _new_run_id() -> str:
    return f"gate_{datetime.now().strftime('%Y%m%d_%H%M%S')}"


def _read_tail(path: Path, max_lines: int) -> List[str]:
    tail: List[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            tail.append(line.rstrip("\n"))
            if len(tail) > max_lines:
                tail.pop(0)
    return tail


def _heartbeat_file(repo_root: Path) -> Path:
    return (repo_root / "logs" / "youtube_dae_heartbeat.jsonl").resolve()


def _read_heartbeat_delta(
    *,
    heartbeat_path: Path,
    start_offset: int,
    run_id: str,
    max_entries: int = 50,
) -> List[Dict[str, object]]:
    if not heartbeat_path.exists():
        return []

    try:
        with heartbeat_path.open("rb") as handle:
            handle.seek(max(start_offset, 0))
            chunk = handle.read()
    except OSError:
        return []

    text = chunk.decode("utf-8", errors="replace")
    entries: List[Dict[str, object]] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        try:
            payload = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if payload.get("run_id") == run_id:
            entries.append(payload)
    return entries[-max_entries:]


def _compact_heartbeat(payload: Dict[str, object]) -> Dict[str, object]:
    return {
        "timestamp": payload.get("timestamp"),
        "status": payload.get("status"),
        "errors_detected": payload.get("errors_detected"),
        "fixes_applied": payload.get("fixes_applied"),
        "stream_active": payload.get("stream_active"),
        "stream_video_id": payload.get("stream_video_id"),
        "automation_gates": payload.get("automation_gates"),
    }


@dataclass(frozen=True)
class Scenario:
    name: str
    description: str
    env: Dict[str, str]


SCENARIOS: List[Scenario] = [
    Scenario(
        name="observe_only",
        description="Stream scan only; no chat sends; no Studio engagement; no UI actions.",
        env={
            "YT_AUTOMATION_ENABLED": "true",
            "YT_LIVECHAT_SEND_ENABLED": "false",
            "YT_LIVECHAT_DRY_RUN": "false",
            "YT_COMMENT_ENGAGEMENT_ENABLED": "false",
            "COMMUNITY_STARTUP_ENGAGE": "false",
            "YT_LIVECHAT_UI_ACTIONS_ENABLED": "false",
            "YT_PARTY_REACTIONS_ENABLED": "false",
            "YT_LIVECHAT_ANNOUNCEMENTS_ENABLED": "false",
            "STREAM_VISION_DISABLED": "true",
            "YT_STREAM_SCRAPING_ENABLED": "true",
            "YT_DEPS_AUTO_LAUNCH": "false",
        },
    ),
    Scenario(
        name="api_chat_send",
        description="Enable YouTube API chat sends; keep UI + Studio engagement disabled.",
        env={
            "YT_AUTOMATION_ENABLED": "true",
            "YT_LIVECHAT_SEND_ENABLED": "true",
            "YT_LIVECHAT_DRY_RUN": "false",
            "YT_COMMENT_ENGAGEMENT_ENABLED": "false",
            "COMMUNITY_STARTUP_ENGAGE": "false",
            "YT_LIVECHAT_UI_ACTIONS_ENABLED": "false",
            "YT_PARTY_REACTIONS_ENABLED": "false",
            "YT_LIVECHAT_ANNOUNCEMENTS_ENABLED": "false",
            "STREAM_VISION_DISABLED": "true",
            "YT_STREAM_SCRAPING_ENABLED": "true",
            "YT_DEPS_AUTO_LAUNCH": "false",
        },
    ),
    Scenario(
        name="studio_like_heart_only",
        description="Enable Studio engagement (like+heart only); keep live chat sends disabled.",
        env={
            "YT_AUTOMATION_ENABLED": "true",
            "YT_LIVECHAT_SEND_ENABLED": "false",
            "YT_LIVECHAT_DRY_RUN": "false",
            "YT_COMMENT_ENGAGEMENT_ENABLED": "true",
            "COMMUNITY_STARTUP_ENGAGE": "true",
            "YT_COMMENT_ACTIONS": "like,heart",
            "YT_COMMENT_INTELLIGENT_REPLY_ENABLED": "false",
            "YT_LIVECHAT_UI_ACTIONS_ENABLED": "true",
            "YT_PARTY_REACTIONS_ENABLED": "false",
            "YT_LIVECHAT_ANNOUNCEMENTS_ENABLED": "false",
            "STREAM_VISION_DISABLED": "true",
            "YT_STREAM_SCRAPING_ENABLED": "true",
            "YT_DEPS_AUTO_LAUNCH": "true",
        },
    ),
]


def _scenario_by_name(name: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.name == name:
            return scenario
    raise KeyError(name)


def _default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _base_env(run_id: str, channels: Optional[str]) -> Dict[str, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    env["YT_AUTOMATION_RUN_ID"] = run_id
    if channels:
        env["YT_CHANNELS_TO_CHECK"] = channels
    return env


async def _run_scenario(
    *,
    repo_root: Path,
    scenario: Scenario,
    run_id: str,
    channels: Optional[str],
    duration_seconds: int,
    output_dir: Path,
) -> Dict[str, object]:
    started_at = datetime.utcnow().isoformat() + "Z"
    env = _base_env(run_id, channels)
    env.update(scenario.env)

    cmd = [sys.executable, "-u", "main.py", "--youtube", "--no-lock"]
    log_path = output_dir / f"{scenario.name}.log"
    heartbeat_path = _heartbeat_file(repo_root)
    heartbeat_offset = heartbeat_path.stat().st_size if heartbeat_path.exists() else 0

    output_dir.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as log_handle:
        log_handle.write(f"[GATE-LAB] run_id={run_id} scenario={scenario.name}\n")
        log_handle.write(f"[GATE-LAB] started_at={started_at} duration_seconds={duration_seconds}\n")
        log_handle.write(f"[GATE-LAB] channels={channels or '(default rotation)'}\n")
        log_handle.write(f"[GATE-LAB] env_overrides={json.dumps(scenario.env, ensure_ascii=False)}\n\n")
        log_handle.flush()

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(repo_root),
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        async def _drain(stream: asyncio.StreamReader) -> None:
            while True:
                line = await stream.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace")
                # Preserve raw log lines so downstream vitals parsing (WSP 91) can match patterns.
                log_handle.write(text)
                log_handle.flush()

        stdout_task = asyncio.create_task(_drain(process.stdout))
        stderr_task = asyncio.create_task(_drain(process.stderr))

        timed_out = False
        try:
            await asyncio.wait_for(process.wait(), timeout=duration_seconds)
        except asyncio.TimeoutError:
            timed_out = True
            try:
                process.terminate()
            except ProcessLookupError:
                pass

            try:
                await asyncio.wait_for(process.wait(), timeout=10)
            except asyncio.TimeoutError:
                try:
                    process.kill()
                except ProcessLookupError:
                    pass

        await asyncio.gather(stdout_task, stderr_task, return_exceptions=True)

        exit_code = process.returncode
        finished_at = datetime.utcnow().isoformat() + "Z"
        log_handle.write(f"\n[GATE-LAB] finished_at={finished_at} exit_code={exit_code} timed_out={timed_out}\n")
        log_handle.flush()

    # Compute vitals on the tail to keep this fast/reliable.
    tail_lines = _read_tail(log_path, max_lines=2000)
    vitals = compute_vitals(tail_lines).to_dict()

    # Simple counters for quick comparisons across scenarios.
    send_count = sum(1 for line in tail_lines if "Sending message (type=" in line)
    subprocess_count = sum(1 for line in tail_lines if "[SUBPROCESS] Running:" in line)

    heartbeats = _read_heartbeat_delta(
        heartbeat_path=heartbeat_path,
        start_offset=heartbeat_offset,
        run_id=run_id,
        max_entries=50,
    )
    compact_heartbeats = [_compact_heartbeat(entry) for entry in heartbeats]

    return {
        "scenario": scenario.name,
        "description": scenario.description,
        "log_path": str(log_path),
        "duration_seconds": duration_seconds,
        "timed_out": timed_out,
        "exit_code": exit_code,
        "counters": {
            "livechat_send_lines": send_count,
            "comment_engagement_subprocess_runs": subprocess_count,
        },
        "vitals_tail": vitals,
        "heartbeats": {
            "path": str(heartbeat_path),
            "count": len(compact_heartbeats),
            "last": compact_heartbeats[-1] if compact_heartbeats else None,
            "entries": compact_heartbeats[-10:],
        },
    }


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Run YouTube DAE automation gate experiments (writes logs + vitals).")
    parser.add_argument("--scenario", choices=[s.name for s in SCENARIOS], help="Scenario name to run")
    parser.add_argument("--run-all", action="store_true", help="Run all scenarios sequentially (safe -> riskier)")
    parser.add_argument("--duration-seconds", type=int, default=600, help="Duration per scenario (default: 600)")
    parser.add_argument("--channels", default="", help="Comma-separated channel IDs to check (overrides rotation)")
    parser.add_argument("--run-id", default="", help="Optional run id (default: auto-generated)")
    parser.add_argument("--output-dir", default="logs/automation_gate_lab", help="Base output dir for logs/summaries")

    args = parser.parse_args(argv)
    if not args.run_all and not args.scenario:
        parser.error("Provide --scenario or --run-all")

    run_id = (args.run_id or "").strip() or _new_run_id()
    channels = (args.channels or "").strip() or None
    repo_root = _default_repo_root()
    output_dir = Path(args.output_dir) / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    selected = SCENARIOS if args.run_all else [_scenario_by_name(args.scenario)]

    results: List[Dict[str, object]] = []

    async def _run() -> None:
        for scenario in selected:
            print(f"\n[GATE-LAB] Running scenario={scenario.name} ({scenario.description})")
            result = await _run_scenario(
                repo_root=repo_root,
                scenario=scenario,
                run_id=run_id,
                channels=channels,
                duration_seconds=args.duration_seconds,
                output_dir=output_dir,
            )
            results.append(result)
            print(f"[GATE-LAB] Complete scenario={scenario.name} exit_code={result['exit_code']} timed_out={result['timed_out']}")

    asyncio.run(_run())

    summary_path = output_dir / "summary.json"
    with summary_path.open("w", encoding="utf-8") as handle:
        json.dump(
            {
                "run_id": run_id,
                "channels": channels,
                "duration_seconds": args.duration_seconds,
                "scenarios": results,
            },
            handle,
            indent=2,
            ensure_ascii=False,
        )

    report_path = output_dir / "report.md"
    report_lines: List[str] = [
        f"# YouTube Automation Gate‑Lab Report: `{run_id}`",
        "",
        f"- Channels: `{channels or '(default rotation)'}`",
        f"- Duration per scenario: `{args.duration_seconds}s`",
        "",
    ]

    for result in results:
        scenario_name = str(result.get("scenario"))
        report_lines.append(f"## {scenario_name}")
        report_lines.append("")
        report_lines.append(str(result.get("description", "")).strip())
        report_lines.append("")
        report_lines.append(f"- Exit: `{result.get('exit_code')}` timed_out=`{result.get('timed_out')}`")

        counters = result.get("counters", {})
        report_lines.append(f"- Counters: `{json.dumps(counters, ensure_ascii=False)}`")

        vitals = result.get("vitals_tail", {}) or {}
        signals = (vitals.get("signals") or {}) if isinstance(vitals, dict) else {}
        if signals:
            report_lines.append(
                "- Signals:"
                f" missing_script=`{signals.get('missing_script_detected')}`"
                f" terminated_chrome=`{signals.get('terminated_chrome_count')}`"
                f" oauth_cache_noise=`{signals.get('oauth_cache_noise_count')}`"
                f" offline_indicators=`{signals.get('offline_indicators_count')}`"
            )

        heartbeats = result.get("heartbeats", {}) or {}
        last_hb = heartbeats.get("last") if isinstance(heartbeats, dict) else None
        if isinstance(heartbeats, dict) and heartbeats.get("count"):
            report_lines.append(
                f"- Heartbeat: pulses=`{heartbeats.get('count')}`"
                f" last_status=`{(last_hb or {}).get('status')}`"
                f" last_errors=`{(last_hb or {}).get('errors_detected')}`"
            )

        report_lines.append("")

    report_path.write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"\n[GATE-LAB] Wrote summary: {summary_path}")
    print(f"[GATE-LAB] Wrote report:  {report_path}")
    print(f"[GATE-LAB] Logs: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

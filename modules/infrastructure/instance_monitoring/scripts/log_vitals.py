#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Vitals (Cardiovascular) Report
=================================

Purpose
-------
Provide a compact, actionable health summary of a log capture for 0102/WRE.

This is intentionally "dumb but reliable" (regex + counts) so it can run
without any model dependency, then feed higher-level analysis later.

Examples
--------
Head (first N lines):
  python modules/infrastructure/instance_monitoring/scripts/log_vitals.py --file 012.txt --lines 910 --head

Tail (last N lines):
  python modules/infrastructure/instance_monitoring/scripts/log_vitals.py --file logs/youtube_dae.log --lines 500 --tail
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


LOG_LINE_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - "
    r"(?P<logger>[^ ]+) - (?P<level>[A-Z]+) - (?P<msg>.*)$"
)


@dataclass(frozen=True)
class Vitals:
    lines_scanned: int
    levels: Dict[str, int]
    top_errors: List[Tuple[str, int]]
    top_warnings: List[Tuple[str, int]]
    signals: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "lines_scanned": self.lines_scanned,
            "levels": dict(self.levels),
            "top_errors": [{"logger": k, "count": v} for k, v in self.top_errors],
            "top_warnings": [{"logger": k, "count": v} for k, v in self.top_warnings],
            "signals": self.signals,
        }


def _read_head(path: Path, max_lines: int) -> List[str]:
    lines: List[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for idx, line in enumerate(handle):
            if idx >= max_lines:
                break
            lines.append(line.rstrip("\n"))
    return lines


def _read_tail(path: Path, max_lines: int) -> List[str]:
    tail: deque[str] = deque(maxlen=max_lines)
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            tail.append(line.rstrip("\n"))
    return list(tail)


def _iter_parsed(lines: Iterable[str]) -> Iterable[Tuple[str, str, str, str]]:
    for line in lines:
        match = LOG_LINE_RE.match(line)
        if not match:
            continue
        yield (
            match.group("ts"),
            match.group("logger"),
            match.group("level"),
            match.group("msg"),
        )


def compute_vitals(lines: List[str]) -> Vitals:
    levels: Counter[str] = Counter()
    errors_by_logger: Counter[str] = Counter()
    warnings_by_logger: Counter[str] = Counter()

    script_missing_lines: List[str] = []
    terminated_chrome_count = 0
    oauth_cache_noise_count = 0
    stream_offline_count = 0

    for _, logger_name, level, msg in _iter_parsed(lines):
        levels[level] += 1

        if level == "ERROR":
            errors_by_logger[logger_name] += 1
        elif level == "WARNING":
            warnings_by_logger[logger_name] += 1

        if "Script missing:" in msg or "missing_script" in msg:
            script_missing_lines.append(msg)

        if "Terminated chrome.exe" in msg:
            terminated_chrome_count += 1

        if "googleapiclient.discovery_cache" in logger_name and "file_cache is only supported" in msg:
            oauth_cache_noise_count += 1

        if msg.startswith("[OFFLINE]") or "No live streams found" in msg:
            stream_offline_count += 1

    signals: Dict[str, Any] = {
        "missing_script_detected": bool(script_missing_lines),
        "missing_script_samples": script_missing_lines[:3],
        "terminated_chrome_count": terminated_chrome_count,
        "oauth_cache_noise_count": oauth_cache_noise_count,
        "offline_indicators_count": stream_offline_count,
    }

    return Vitals(
        lines_scanned=len(lines),
        levels=dict(levels),
        top_errors=errors_by_logger.most_common(5),
        top_warnings=warnings_by_logger.most_common(5),
        signals=signals,
    )


def _print_human(vitals: Vitals) -> None:
    levels = vitals.levels
    error_count = levels.get("ERROR", 0)
    warning_count = levels.get("WARNING", 0)

    print("\n" + "=" * 60)
    print("[VITALS] Log Cardiovascular Report")
    print("=" * 60)
    print(f"[HEARTBEAT] Lines scanned: {vitals.lines_scanned}")
    print(f"[ALERTS] Errors: {error_count} | Warnings: {warning_count}")

    if vitals.top_errors:
        print("\n[ERROR] Top sources:")
        for logger_name, count in vitals.top_errors:
            print(f"  - {logger_name}: {count}")

    if vitals.top_warnings:
        print("\n[WARN] Top sources:")
        for logger_name, count in vitals.top_warnings:
            print(f"  - {logger_name}: {count}")

    sig = vitals.signals
    print("\n[SIGNALS]")
    print(f"  - missing_script_detected: {sig.get('missing_script_detected')}")
    print(f"  - terminated_chrome_count: {sig.get('terminated_chrome_count')}")
    print(f"  - oauth_cache_noise_count: {sig.get('oauth_cache_noise_count')}")
    print(f"  - offline_indicators_count: {sig.get('offline_indicators_count')}")

    if sig.get("missing_script_samples"):
        print("\n[SAMPLES] missing_script:")
        for sample in sig["missing_script_samples"]:
            print(f"  - {sample}")

    print()


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Print a compact vitals summary from a log capture.")
    parser.add_argument("--file", default="012.txt", help="Path to log file (default: 012.txt)")
    parser.add_argument("--lines", type=int, default=910, help="Number of lines to scan (default: 910)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--head", action="store_true", help="Scan first N lines (default)")
    group.add_argument("--tail", action="store_true", help="Scan last N lines")
    parser.add_argument("--json", action="store_true", help="Output JSON to stdout")

    args = parser.parse_args(argv)
    path = Path(args.file)
    if not path.exists():
        print(f"[ERROR] File not found: {path}", file=sys.stderr)
        return 2

    if args.tail:
        lines = _read_tail(path, args.lines)
    else:
        lines = _read_head(path, args.lines)

    vitals = compute_vitals(lines)

    if args.json:
        print(json.dumps(vitals.to_dict(), indent=2, ensure_ascii=False))
    else:
        _print_human(vitals)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

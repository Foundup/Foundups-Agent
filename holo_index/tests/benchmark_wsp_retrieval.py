#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP Retrieval Micro-Benchmark for HoloIndex

Measures Top-1 / Top-3 accuracy and latency for WSP-related queries.
Avoids default E:/ path by setting a local SSD cache dir.
"""

import time
from typing import List, Dict, Any

from holo_index.core.holo_index import HoloIndex


def run_benchmark() -> Dict[str, Any]:
    queries = [
        {"q": "WSP 15", "expect": "WSP 15"},
        {"q": "Module Prioritization Scoring", "expect": "WSP 15"},
        {"q": "WSP 37", "expect": "WSP 37"},
        {"q": "Roadmap Scoring System", "expect": "WSP 37"},
        {"q": "WSP 60", "expect": "WSP 60"},
        {"q": "Module Memory Architecture", "expect": "WSP 60"},
        {"q": "WSP 85", "expect": "WSP 85"},
        {"q": "Root Directory Protection Protocol", "expect": "WSP 85"},
        {"q": "WSP 96", "expect": "WSP 96"},
        {"q": "MCP Governance", "expect": "WSP 96"},
    ]

    # Use local SSD dir to avoid E:/ requirement
    hi = HoloIndex(ssd_path="holo_index/.ssd")
    # Ensure WSP index is loaded for accuracy test
    try:
        from pathlib import Path
        wsp_root = Path("WSP_framework/src")
        if wsp_root.exists():
            hi.index_wsp_entries(paths=[wsp_root])
    except Exception:
        pass

    top1 = 0
    top3 = 0
    elapsed = []
    warn_counts = []
    details: List[str] = []

    for item in queries:
        q = item["q"]
        expect = item["expect"]

        t0 = time.time()
        res = hi.search(q, limit=3)
        dt = (time.time() - t0) * 1000
        elapsed.append(dt)
        warn_counts.append(res.get("warnings_count", 0))

        wsps = res.get("wsps", [])
        found_idx = -1
        for idx, hit in enumerate(wsps[:3]):
            if (hit.get("wsp") or "").strip().lower() == expect.lower():
                found_idx = idx
                break

        if found_idx == 0:
            top1 += 1
            details.append(f"[OK] Top1: {q} -> {expect}")
        elif 0 <= found_idx < 3:
            top3 += 1
            details.append(f"[OK] Top3: {q} -> {expect} at {found_idx+1}")
        else:
            details.append(f"[MISS] {q} -> expected {expect}; got {[h.get('wsp') for h in wsps[:3]]}")

    n = len(queries)
    summary = {
        "n": n,
        "top1": top1,
        "top3": top3,
        "top1_rate": f"{(top1/n)*100:.1f}%",
        "top3_rate": f"{(top3/n)*100:.1f}%",
        "avg_latency_ms": f"{(sum(elapsed)/n):.1f}",
        "avg_warnings": f"{(sum(warn_counts)/n):.2f}",
        "details": details,
    }
    return summary


if __name__ == "__main__":
    out = run_benchmark()
    print("=== WSP Retrieval Micro-Benchmark ===")
    print(f"Queries: {out['n']}")
    print(f"Top-1: {out['top1']} ({out['top1_rate']})")
    print(f"Top-3: {out['top3']} ({out['top3_rate']})")
    print(f"Avg latency: {out['avg_latency_ms']} ms")
    print(f"Avg warnings: {out['avg_warnings']}")
    print("-- Details --")
    for line in out["details"]:
        print(line)



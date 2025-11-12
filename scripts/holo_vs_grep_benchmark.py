#!/usr/bin/env python3
"""
Compare HoloIndex semantic search against ripgrep/glob style workflows.

Outputs a small table showing hit counts and timings for both approaches so 0102
can demonstrate why Holo replaces manual grepping.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

REPO_ROOT = Path(__file__).resolve().parents[1]

# Ensure repo root is importable
import sys

sys.path.insert(0, str(REPO_ROOT))

from holo_index.core.holo_index import HoloIndex
RG_PATH = shutil.which("rg")
DEFAULT_QUERIES = [
    {
        "id": "semantic_pqn",
        "query": "PQN module in youtube dae",
        "description": "Semantic architecture query for PQN within YouTube DAE"
    },
    {
        "id": "handle_item_classification",
        "query": "handle item classification flow",
        "description": "Fuzzy TSX hook search for GotJunk classification modal"
    },
    {
        "id": "literal_symbol",
        "query": "pendingClassificationItem",
        "description": "Literal state variable to show parity with ripgrep"
    }
]


def run_holo(holo: HoloIndex, query: str, limit: int = 5) -> Dict[str, Any]:
    start = time.time()
    result = holo.search(query, limit=limit)
    duration = time.time() - start
    code_hits = result.get("code_hits", [])
    wsp_hits = result.get("wsp_hits", [])
    top_preview = ""
    if code_hits:
        preview = code_hits[0].get("preview") or ""
        top_preview = preview.replace("\n", " ")
        if len(top_preview) > 120:
            top_preview = top_preview[:117] + "..."
    return {
        "code_hits": len(code_hits),
        "wsp_hits": len(wsp_hits),
        "duration": duration,
        "preview": top_preview
    }


def run_rg(query: str) -> Dict[str, Any]:
    if not RG_PATH:
        return {"available": False, "matches": 0, "duration": 0.0}

    start = time.time()
    proc = subprocess.run(
        [RG_PATH, "-n", query, "modules"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    duration = time.time() - start
    matches = [line for line in proc.stdout.splitlines() if line.strip()]
    return {"available": True, "matches": len(matches), "duration": duration}


def format_row(label: str, holo_stats: Dict[str, Any], rg_stats: Dict[str, Any]) -> str:
    if rg_stats.get("available"):
        rg_summary = f"{rg_stats['matches']} hits / {rg_stats['duration']*1000:.1f} ms"
    else:
        rg_summary = "rg unavailable"
    return (
        f"{label:<28}"
        f"{holo_stats['code_hits']:>3} code / {holo_stats['wsp_hits']:>3} WSP "
        f"({holo_stats['duration']*1000:.1f} ms)"
        f"    {rg_summary}"
        f"\n    Preview: {holo_stats['preview'] or '[none]'}"
    )


def main():
    parser = argparse.ArgumentParser(description="Benchmark HoloIndex vs ripgrep.")
    parser.add_argument(
        "--queries",
        help="Path to JSON file containing a list of {id, query, description}",
        type=Path
    )
    parser.add_argument("--limit", type=int, default=5, help="Max Holo code hits to request.")
    args = parser.parse_args()

    queries: List[Dict[str, str]] = DEFAULT_QUERIES
    if args.queries:
        data = json.loads(args.queries.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Queries JSON must be a list of objects")
        queries = data

    holo = HoloIndex(quiet=True)
    print("[INFO] Running HoloIndex vs ripgrep benchmark\n")
    for entry in queries:
        query = entry["query"]
        label = entry.get("id", query)
        description = entry.get("description", "")
        print(f"--- {label} ---")
        if description:
            print(f"{description}")
        holo_stats = run_holo(holo, query, limit=args.limit)
        rg_stats = run_rg(query)
        print(format_row(query, holo_stats, rg_stats))
        print()


if __name__ == "__main__":
    main()

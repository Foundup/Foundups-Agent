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

012-derived Intent + Retrieval Benchmark

- Loads derived queries from adaptive_learning/012_corpus/memory/012_queries.json
- Classifies intent via intent_classifier
- Measures WSP retrieval Top-1/Top-3 using HoloIndex
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from holo_index.core.holo_index import HoloIndex
from holo_index.intent_classifier import get_classifier, IntentType


def run() -> Dict[str, Any]:
    repo = Path(__file__).resolve().parents[2]
    qpath = repo / "adaptive_learning" / "012_corpus" / "memory" / "012_queries.json"
    if not qpath.exists():
        return {"error": f"queries not found: {qpath}"}

    queries = json.loads(qpath.read_text(encoding="utf-8"))
    wsp_qs: List[str] = queries.get("wsp", [])[:100]
    code_qs: List[str] = queries.get("code", [])[:100]

    # Initialize components
    hi = HoloIndex(ssd_path="holo_index/.ssd")
    # Ensure WSP index present
    wsp_root = Path("WSP_framework/src")
    if wsp_root.exists():
        hi.index_wsp_entries(paths=[wsp_root])
    clf = get_classifier()

    # Intent accuracy proxy: expected intents
    # wsp queries -> DOC_LOOKUP; code queries -> CODE_LOCATION
    intent_ok = 0
    intent_total = 0

    for q in wsp_qs:
        ic = clf.classify(q)
        intent_total += 1
        if ic.intent == IntentType.DOC_LOOKUP:
            intent_ok += 1

    for q in code_qs:
        ic = clf.classify(q)
        intent_total += 1
        if ic.intent == IntentType.CODE_LOCATION or ic.intent == IntentType.GENERAL:
            # allow GENERAL as fallback for open phrasing
            intent_ok += 1

    # Retrieval: test wsp queries
    top1 = 0
    top3 = 0
    for q in wsp_qs:
        res = hi.search(q, limit=3)
        hits = res.get("wsps", [])
        # Match by exact wsp tag if present in q
        import re
        m = re.search(r"\bWSP\s*(\d+)\b", q, re.IGNORECASE)
        expect = f"WSP {m.group(1)}" if m else None
        if expect:
            if hits and hits[0].get("wsp") == expect:
                top1 += 1
            elif any(h.get("wsp") == expect for h in hits[:3]):
                top3 += 1
        else:
            # When no explicit id, accept any wsp hit
            if hits:
                top1 += 1

    n = max(1, len(wsp_qs))
    return {
        "intent_acc": f"{(intent_ok/max(1,intent_total))*100:.1f}%",
        "wsp_top1": f"{(top1/n)*100:.1f}%",
        "wsp_top3": f"{(top3/n)*100:.1f}%",
        "counts": {"wsp": len(wsp_qs), "code": len(code_qs)},
    }


if __name__ == "__main__":
    out = run()
    print(json.dumps(out, indent=2))

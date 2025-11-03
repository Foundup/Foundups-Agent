#!/usr/bin/env python3
"""
UTF-8 Hygiene Scanner
Extracted from main.py per WSP 62 Large File Refactoring Protocol

Purpose: Scan and summarize UTF-8 violations in codebase
Domain: ai_intelligence
Module: utf8_hygiene

Functions:
- run_utf8_hygiene_scan: Scan target paths for non-ASCII characters
- summarize_utf8_findings: Summarize stored UTF-8 violations from PatternMemory
"""

import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List


def run_utf8_hygiene_scan(
    memory: Optional[Any] = None,
    targets: Optional[List[str]] = None,
    interactive: bool = True
) -> List[Dict[str, Any]]:
    """Scan target paths for non-ASCII characters and log findings."""
    default_targets = [
        "modules/infrastructure/dae_infrastructure/foundups_vision_dae",
        "modules/platform_integration/social_media_orchestrator/src/core/browser_manager.py"
    ]

    if interactive:
        print("\n" + "=" * 60)
        print("[INFO] UTF-8 Hygiene Scan")
        print("=" * 60)
        print("Detect non-ASCII characters that can corrupt CLI or log output.")
        print(f"Default targets: {', '.join(default_targets)}")
        print("=" * 60)
        target_input = input("Enter comma-separated paths to scan (leave blank for defaults): ").strip()
        if target_input:
            targets = [item.strip() for item in target_input.split(",") if item.strip()]
        else:
            targets = None

    if not targets:
        targets = default_targets

    allowed_ext = {".py", ".md", ".txt", ".json", ".yaml", ".yml"}
    findings: list[dict[str, Any]] = []
    missing_paths: list[str] = []

    def scan_file(path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8") as handle:
                for lineno, line in enumerate(handle, 1):
                    if any(ord(ch) > 127 for ch in line):
                        offending = "".join(sorted(set(ch for ch in line if ord(ch) > 127)))
                        snippet = line.rstrip("\n")
                        findings.append(
                            {
                                "path": str(path),
                                "line": lineno,
                                "snippet": snippet.strip(),
                                "offending": offending,
                            }
                        )
        except Exception as exc:
            print(f"[WARN] Unable to read {path}: {exc}")

    for target in targets:
        path = Path(target)
        if path.is_dir():
            for file_path in path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in allowed_ext:
                    scan_file(file_path)
        elif path.is_file():
            if path.suffix.lower() in allowed_ext:
                scan_file(path)
        else:
            missing_paths.append(str(path))

    if interactive or missing_paths:
        if missing_paths:
            print("\n[WARN] Missing paths:")
            for entry in missing_paths:
                print(f"   {entry}")

    if not findings:
        if interactive:
            print("\n[INFO] No non-ASCII characters detected in selected paths.")
            input("\nPress Enter to continue...")
        return findings

    print(f"\n[RESULT] Detected {len(findings)} potential UTF-8 issues:")
    max_display = 50
    unique_chars = sorted({ch for item in findings for ch in item["offending"]})
    for item in findings[:max_display]:
        snippet = item["snippet"]
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        print(f" - {item['path']}:{item['line']} | offending: {repr(item['offending'])}")
        print(f"   {snippet}")
    if len(findings) > max_display:
        print(f"   ... {len(findings) - max_display} more")

    if unique_chars:
        print(f"\n[INFO] Unique offending characters: {''.join(unique_chars)}")

    stored = 0
    if memory is None:
        try:
            from holo_index.qwen_advisor.pattern_memory import PatternMemory

            memory = PatternMemory()
        except Exception as exc:
            print(f"[WARN] Unable to store findings in PatternMemory: {exc}")
            memory = None

    if memory is not None:
        timestamp = datetime.utcnow().isoformat()
        base_id = int(time.time())
        for idx, item in enumerate(findings, 1):
            pattern = {
                "id": f"utf8_{base_id}_{idx}",
                "context": f"UTF-8 hygiene violation in {item['path']}:{item['line']} -> {item['snippet']}",
                "decision": {
                    "action": "replace_non_ascii_characters",
                    "reasoning": "Ensure CLI and logs remain ASCII-safe across operating systems.",
                },
                "outcome": {"result": "pending_fix", "success": False},
                "module": item["path"],
                "timestamp": timestamp,
                "verified": False,
                "source": "utf8_hygiene_scan",
            }
            if memory.store_pattern(pattern):
                stored += 1

        if stored:
            print(f"\n[INFO] Stored {stored} hygiene patterns for Gemma/Qwen training.")

    if interactive:
        input("\nPress Enter to continue...")

    return findings


def summarize_utf8_findings(
    memory: Optional[Any] = None,
    target_filters: Optional[List[str]] = None,
    limit: int = 50
) -> Dict[str, Any]:
    """Summarize stored UTF-8 hygiene findings from PatternMemory."""
    try:
        mem = memory or __import__(
            "holo_index.qwen_advisor.pattern_memory",
            fromlist=["PatternMemory"],
        ).PatternMemory()
    except Exception as exc:
        return {"status": "error", "message": f"PatternMemory load failed: {exc}"}

    try:
        records = mem.collection.get(
            where={"source": "utf8_hygiene_scan"},
            include=["metadatas", "documents"],
        )
    except Exception as exc:
        return {"status": "error", "message": f"PatternMemory query failed: {exc}"}

    metadatas = records.get("metadatas") or []
    documents = records.get("documents") or []
    filters = target_filters or []

    summary: Dict[str, Dict[str, Any]] = {}
    total_findings = 0
    unique_chars: set = set()

    for doc, meta in zip(documents, metadatas):
        path = meta.get("module", "unknown")
        if filters and not any(fragment in path for fragment in filters):
            continue

        entry = summary.setdefault(path, {"count": 0, "samples": [], "chars": set()})
        entry["count"] += 1
        total_findings += 1

        if len(entry["samples"]) < 3:
            entry["samples"].append(doc[:120])

        for character in doc:
            if ord(character) > 127:
                entry["chars"].add(character)
                unique_chars.add(character)

    ranked = sorted(summary.items(), key=lambda item: item[1]["count"], reverse=True)
    top_entries = []
    for path, info in ranked[:limit]:
        top_entries.append(
            {
                "path": path,
                "count": info["count"],
                "unique_characters": "".join(sorted(info["chars"])),
                "samples": info["samples"],
            }
        )

    return {
        "status": "ok",
        "total_findings": total_findings,
        "files": len(summary),
        "unique_characters": "".join(sorted(unique_chars)),
        "top": top_entries,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == "scan":
        run_utf8_hygiene_scan()
    elif len(sys.argv) >= 2 and sys.argv[1] == "summary":
        result = summarize_utf8_findings()
        print(f"Total findings: {result.get('total_findings', 0)}")
        print(f"Files affected: {result.get('files', 0)}")
    else:
        print("Usage: python scanner.py [scan|summary]")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

HoloIndex Integration for WRE Pattern Recall
WSP 87: Semantic Code Discovery to Prevent Vibecoding

This module integrates HoloIndex into the WRE pattern recall system,
making semantic search MANDATORY before any code changes.
"""

import os
import sys
import subprocess
import json
from typing import Optional, List, Dict, Any
from pathlib import Path


class HoloIndexIntegration:
    """
    Integrates HoloIndex semantic search into WRE pattern recall.
    MANDATORY usage per WSP 87 to prevent vibecoding.
    """

    def __init__(self):
        """Initialize HoloIndex integration."""
        # Prefer root holo_index.py, fallback to E: drive version
        root_path = Path(__file__).resolve().parents[5] / "holo_index.py"
        if root_path.exists():
            self.holo_path = root_path
            self.enabled = True
        else:
            self.holo_path = Path(r"E:\HoloIndex\enhanced_holo_index.py")
            self.enabled = self.holo_path.exists()

        if not self.enabled:
            print("[U+26A0]️ WARNING: HoloIndex not found - vibecoding risk HIGH!")
            print("Run 'python holo_index.py' from project root to enable semantic search")

    def search_before_code(self, task: str) -> Dict[str, Any]:
        """
        MANDATORY search before any code modifications.
        Prevents vibecoding by finding existing implementations.

        Args:
            task: Description of what code is needed

        Returns:
            Dict with search results and recommendations
        """
        if not self.enabled:
            return {
                "error": "HoloIndex not installed",
                "vibecoding_risk": "CRITICAL",
                "recommendation": "Install HoloIndex immediately"
            }

        try:
            # Run HoloIndex search
            result = subprocess.run(
                ['python', str(self.holo_path), '--search', task],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )

            if result.returncode == 0:
                # Parse results from output
                output = result.stdout

                # Extract matches (look for percentage matches)
                import re
                matches = re.findall(r'\[(-?\d+\.?\d*)%\] (.+?)\n\s+-> (.+)', output)

                results = {
                    "task": task,
                    "matches": [
                        {
                            "confidence": float(match[0]),
                            "description": match[1],
                            "location": match[2]
                        }
                        for match in matches
                    ],
                    "vibecoding_prevented": len(matches) > 0 and float(matches[0][0]) > 50,
                    "raw_output": output
                }

                # If high confidence match found, prevent vibecoding
                if results["vibecoding_prevented"]:
                    print(f"[OK] VIBECODING PREVENTED: Found existing code with {matches[0][0]}% match")
                    print(f"   Use: {matches[0][2]}")
                else:
                    print(f"[U+26A0]️ Low confidence matches - verify before creating new code")

                return results

            else:
                return {
                    "error": f"Search failed: {result.stderr}",
                    "vibecoding_risk": "HIGH"
                }

        except subprocess.TimeoutExpired:
            return {
                "error": "Search timeout",
                "vibecoding_risk": "MEDIUM"
            }
        except Exception as e:
            return {
                "error": str(e),
                "vibecoding_risk": "UNKNOWN"
            }

    def retrieve_structured_memory(self, module_hint: str) -> Dict[str, Any]:
        """
        WSP Memory System (WSP_CORE): enforce structured-memory retrieval for a module.

        This is intentionally lightweight and CLI-driven:
        - uses `python holo_index.py --search ...` as the canonical retrieval interface
        - returns a machine-first summary suitable for orchestration logs
        """
        artifacts = [
            "README.md",
            "INTERFACE.md",
            "ROADMAP.md",
            "ModLog.md",
            "tests/README.md",
            "tests/TestModLog.md",
            "memory/README.md",
            "requirements.txt",
        ]

        retrieval: Dict[str, Any] = {
            "module_hint": module_hint,
            "artifacts": {},
            "missing": [],
        }

        for artifact in artifacts:
            query = f"{module_hint} {artifact}"
            result = self.search_before_code(query)
            retrieval["artifacts"][artifact] = {
                "query": query,
                "ok": "error" not in result,
                "matches": result.get("matches", []),
            }
            # Consider artifact "present" if we got at least one match location back
            if not result.get("matches"):
                retrieval["missing"].append(artifact)

        return retrieval

    def evaluate_retrieval_quality(self, retrieval: Dict[str, Any]) -> Dict[str, Any]:
        """
        Proxy metrics per WSP_CORE Retrieval Quality Metrics.
        (Used-chunks cannot be observed here; we measure structural completeness + duplication.)
        """
        artifacts = retrieval.get("artifacts", {}) or {}
        returned = 0
        locations: List[str] = []
        for info in artifacts.values():
            matches = info.get("matches") or []
            returned += len(matches)
            for m in matches:
                loc = (m or {}).get("location")
                if loc:
                    locations.append(str(loc))

        unique_locations = set(locations)
        duplication_rate = 0.0
        if returned > 0:
            duplication_rate = max(0.0, (len(locations) - len(unique_locations)) / float(returned))

        return {
            "returned_chunks_proxy": returned,
            "missing_artifacts": retrieval.get("missing", []),
            "duplication_rate_proxy": round(duplication_rate, 3),
            "ordering_correctness_proxy": None,  # not observable in CLI-only mode
            "staleness_risk_proxy": None,        # requires git/log correlation
            "pattern_recall_ok": len(retrieval.get("missing", [])) == 0,
        }

    def start_of_work_loop(self, task: str, module_hint: str) -> Dict[str, Any]:
        """
        WRE Start-of-Work Loop (WSP_CORE):
        1) retrieve structured memory
        2) evaluate retrieval quality
        3) (optional) improve retrieval (not implemented here; delegated to HoloIndex/WRE plugins)
        4) return a structured bundle for orchestration decisions
        """
        structured = self.retrieve_structured_memory(module_hint)
        quality = self.evaluate_retrieval_quality(structured)

        # Improvement iteration hook: keep explicit, even if no-op in this adapter.
        improvement = {
            "attempted": False,
            "actions": [],
            "note": "Improvement iteration delegated (HoloIndex/WRE plugin layer).",
        }

        # Always retrieve task-level code context too (existing WSP 87 guard)
        task_retrieval = self.search_before_code(task)

        return {
            "task": task,
            "module_hint": module_hint,
            "structured_memory": structured,
            "retrieval_quality": quality,
            "improvement_iteration": improvement,
            "task_retrieval": task_retrieval,
        }

    def enforce_wsp_87(self, code_task: str) -> bool:
        """
        Enforce WSP 87: MANDATORY semantic search before code.

        Args:
            code_task: What code needs to be written/modified

        Returns:
            True if existing code found, False if new code may be needed
        """
        print("\n" + "="*60)
        print("WSP 87 ENFORCEMENT: Semantic Search Required")
        print("="*60)
        print(f"Task: {code_task}")
        print("Searching for existing implementations...")

        results = self.search_before_code(code_task)

        if "error" in results:
            print(f"[FAIL] Search failed: {results['error']}")
            print(f"[U+26A0]️ Vibecoding risk: {results.get('vibecoding_risk', 'UNKNOWN')}")
            return False

        if results.get("vibecoding_prevented"):
            print("\n" + "="*60)
            print("EXISTING CODE FOUND - DO NOT VIBECODE!")
            print("="*60)
            for match in results["matches"][:3]:
                if match["confidence"] > 0:
                    print(f"[{match['confidence']:.1f}%] {match['description']}")
                    print(f"        -> {match['location']}")
            return True
        else:
            print("\n[U+26A0]️ No high-confidence matches found")
            print("Verify these don't meet your needs before creating new code:")
            for match in results["matches"][:3]:
                print(f"[{match['confidence']:.1f}%] {match['description']}")
            return False

    def pattern_recall_with_search(self, pattern_type: str) -> Optional[Dict]:
        """
        Combine WRE pattern recall with HoloIndex semantic search.

        Args:
            pattern_type: Type of pattern needed

        Returns:
            Pattern data with semantic search results
        """
        # First use HoloIndex to find related code
        search_results = self.search_before_code(pattern_type)

        # Then combine with WRE pattern memory
        pattern_data = {
            "pattern_type": pattern_type,
            "semantic_matches": search_results.get("matches", []),
            "vibecoding_prevented": search_results.get("vibecoding_prevented", False)
        }

        # Load from pattern memory if exists
        pattern_file = Path(f"memory/patterns/{pattern_type}.json")
        if pattern_file.exists():
            with open(pattern_file, 'r') as f:
                pattern_data["stored_pattern"] = json.load(f)

        return pattern_data


# Integration with WRE
def before_any_code_change(task: str) -> bool:
    """
    MANDATORY function to call before ANY code modifications.
    This enforces WSP 87 and prevents vibecoding.

    Args:
        task: Description of code change needed

    Returns:
        True if should proceed with existing code, False if new code may be needed
    """
    integration = HoloIndexIntegration()
    return integration.enforce_wsp_87(task)


if __name__ == "__main__":
    # Test the integration
    print("Testing HoloIndex Integration...")

    test_queries = [
        "send messages to chat",
        "handle consciousness triggers",
        "post to linkedin",
        "git push and commit"
    ]

    integration = HoloIndexIntegration()

    for query in test_queries:
        print(f"\nTesting: {query}")
        print("-" * 40)
        integration.enforce_wsp_87(query)
        print()
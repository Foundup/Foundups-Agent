#!/usr/bin/env python3
"""
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
        self.holo_path = Path(r"E:\HoloIndex\enhanced_holo_index.py")
        self.enabled = self.holo_path.exists()

        if not self.enabled:
            print("⚠️ WARNING: HoloIndex not found - vibecoding risk HIGH!")
            print("Install HoloIndex at E:\\HoloIndex to enable semantic search")

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
                    print(f"✅ VIBECODING PREVENTED: Found existing code with {matches[0][0]}% match")
                    print(f"   Use: {matches[0][2]}")
                else:
                    print(f"⚠️ Low confidence matches - verify before creating new code")

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
            print(f"❌ Search failed: {results['error']}")
            print(f"⚠️ Vibecoding risk: {results.get('vibecoding_risk', 'UNKNOWN')}")
            return False

        if results.get("vibecoding_prevented"):
            print("\n" + "="*60)
            print("EXISTING CODE FOUND - DO NOT VIBECODE!")
            print("="*60)
            for match in results["matches"][:3]:
                if match["confidence"] > 0:
                    print(f"[{match['confidence']:.1f}%] {match['description']}")
                    print(f"        → {match['location']}")
            return True
        else:
            print("\n⚠️ No high-confidence matches found")
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
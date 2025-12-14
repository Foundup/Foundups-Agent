#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HoloIndex Relevance Testing - Random Query Verification

Tests that HoloIndex returns RELEVANT results, not just any results.
Uses ground truth data to verify search correctness.

Run with:
    python holo_index/tests/test_holo_relevance.py
    python holo_index/tests/test_holo_relevance.py --random 10  # 10 random tests
    python holo_index/tests/test_holo_relevance.py --all  # All ground truth tests
"""

import subprocess
import time
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = "python"


# === GROUND TRUTH: Known content and where it should be found ===

GROUND_TRUTH = {
    # ModLog queries
    "modlog_pqn": {
        "query": "PQN module",
        "expected_files": ["holo_index/ModLog.md", "holo_index/qwen_advisor/ModLog.md"],
        "expected_content": ["PQN", "pqn", "pattern", "queue"],
        "forbidden_content": ["gotjunk", "classification", "geolocation"],
        "category": "modlog",
    },
    "modlog_wsp62": {
        "query": "WSP 62 refactoring",
        "expected_files": ["holo_index/ModLog.md", "holo_index/qwen_advisor/ModLog.md"],
        "expected_content": ["WSP 62", "refactor", "coordinator", "modularity"],
        "forbidden_content": ["gotjunk", "classification"],
        "category": "modlog",
    },

    # README queries
    "readme_youtube_chat": {
        "query": "youtube live chat integration",
        "expected_files": ["modules/communication/youtube_dae/README.md", "modules/communication/livechat/README.md"],
        "expected_content": ["youtube", "chat", "live", "stream"],
        "forbidden_content": ["gotjunk", "classification", "geolocation"],
        "category": "readme",
    },
    "readme_holodae": {
        "query": "HoloDAE coordinator",
        "expected_files": ["holo_index/qwen_advisor/README.md", "holo_index/README.md"],
        "expected_content": ["HoloDAE", "coordinator", "qwen", "advisor"],
        "forbidden_content": ["gotjunk"],
        "category": "readme",
    },

    # Module-specific queries (NAVIGATION.py entries)
    "module_classification": {
        "query": "handle item classification",
        "expected_files": ["modules/foundups/gotjunk/frontend/App.tsx"],
        "expected_content": ["handleClassify", "classification", "item", "modal"],
        "forbidden_content": ["telemetry", "overseer", "wsp_orchestrator"],
        "category": "module",
    },
    "module_telemetry": {
        "query": "monitor telemetry from HoloDAE",
        "expected_files": ["modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py"],
        "expected_content": ["telemetry", "monitor", "HoloDAE", "tail"],
        "forbidden_content": ["gotjunk", "classification", "geolocation"],
        "category": "module",
    },
    "module_wsp_orchestrator": {
        "query": "WSP orchestration",
        "expected_files": ["modules/infrastructure/wsp_orchestrator/src/wsp_orchestrator.py"],
        "expected_content": ["WSPOrchestrator", "orchestrat", "route", "agent"],
        "forbidden_content": ["gotjunk", "classification"],
        "category": "module",
    },

    # WSP protocol queries
    "wsp_navigation": {
        "query": "WSP 87 code navigation",
        "expected_files": ["WSP_framework/", "NAVIGATION.py"],
        "expected_content": ["WSP 87", "navigation", "vibecoding"],
        "forbidden_content": ["gotjunk"],
        "category": "wsp",
    },
    "wsp_modularity": {
        "query": "WSP 62 modularity",
        "expected_files": ["WSP_framework/"],
        "expected_content": ["WSP 62", "modular", "refactor"],
        "forbidden_content": ["gotjunk"],
        "category": "wsp",
    },

    # Code implementation queries
    "code_qwen_analyze": {
        "query": "qwen analyze context",
        "expected_files": ["holo_index/qwen_advisor/holodae_coordinator.py"],
        "expected_content": ["qwen", "analyze", "context", "coordinator"],
        "forbidden_content": ["gotjunk", "classification"],
        "category": "code",
    },
    "code_mcp_manager": {
        "query": "MCP server management",
        "expected_files": ["modules/infrastructure/mcp_manager/src/mcp_manager.py"],
        "expected_content": ["MCP", "server", "manager", "ensure"],
        "forbidden_content": ["gotjunk"],
        "category": "code",
    },

    # Negative tests (should NOT find irrelevant results)
    "negative_telemetry_no_gotjunk": {
        "query": "telemetry monitor",
        "expected_files": ["modules/ai_intelligence/ai_overseer/src/holo_telemetry_monitor.py"],
        "expected_content": ["telemetry", "monitor"],
        "forbidden_content": ["Math.cos", "geolocation", "ClassificationModal", "SOS Morse"],
        "forbidden_files": ["modules/foundups/gotjunk/frontend/App.tsx"],
        "category": "negative",
    },
    "negative_wsp_no_gotjunk": {
        "query": "WSP orchestrator",
        "expected_files": ["modules/infrastructure/wsp_orchestrator/"],
        "expected_content": ["WSP", "orchestrat"],
        "forbidden_content": ["handleClassify", "classification", "geolocation"],
        "forbidden_files": ["modules/foundups/gotjunk/"],
        "category": "negative",
    },
}


class RelevanceTester:
    """Test HoloIndex search relevance with ground truth verification."""

    def __init__(self):
        self.results = []
        self.passed = 0
        self.failed = 0

    def run_holo_search(self, query: str, limit: int = 3) -> Tuple[str, float]:
        """Run HoloIndex search and return output."""
        cmd = [PYTHON_EXE, "holo_index.py", "--search", query, "--limit", str(limit), "--verbose"]

        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'  # Replace invalid characters instead of failing
            )
            elapsed = time.time() - start
            stdout = result.stdout if result.stdout else ""
            return stdout, elapsed
        except Exception as e:
            elapsed = time.time() - start
            return f"ERROR: {e}", elapsed

    def normalize_path(self, path: str) -> str:
        """Normalize path separators for cross-platform comparison."""
        return path.replace('\\', '/').lower()

    def extract_result_files(self, output: str) -> List[str]:
        """Extract file paths from HoloIndex output."""
        if not output or output.startswith("ERROR"):
            return []

        files = []

        # Extract from [CODE RESULTS] section
        code_results_match = re.search(r'\[CODE RESULTS\](.*?)(?:\[WSP GUIDANCE\]|$)', output, re.DOTALL)
        if code_results_match:
            code_section = code_results_match.group(1)
            # Match file paths like: O:\Foundups-Agent\modules\...\file.py
            file_paths = re.findall(r'O:\\Foundups-Agent\\([^\s:]+)', code_section)
            # Normalize paths
            files.extend([self.normalize_path(p) for p in file_paths])

        # Extract from [MODULES] section
        modules_match = re.search(r'\[MODULES\] Found implementations across \d+ modules?: (.+)', output)
        if modules_match:
            modules = modules_match.group(1).strip()
            files.append(self.normalize_path(modules))

        return files

    def extract_result_content(self, output: str) -> str:
        """Extract result content/previews from HoloIndex output."""
        if not output or output.startswith("ERROR"):
            return ""

        content = ""

        # Extract previews from [CODE RESULTS]
        code_results_match = re.search(r'\[CODE RESULTS\](.*?)(?:\[WSP GUIDANCE\]|$)', output, re.DOTALL)
        if code_results_match:
            content += code_results_match.group(1)

        # Extract from [WSP GUIDANCE]
        wsp_match = re.search(r'\[WSP GUIDANCE\](.*?)(?:\[ACTION\]|$)', output, re.DOTALL)
        if wsp_match:
            content += wsp_match.group(1)

        return content.lower()

    def verify_result(self, test_name: str, test_data: Dict, output: str, elapsed: float) -> Dict:
        """Verify a single test result against ground truth."""
        result = {
            "test": test_name,
            "query": test_data["query"],
            "category": test_data["category"],
            "elapsed": elapsed,
            "passed": True,
            "errors": [],
            "warnings": [],
        }

        # Extract results
        result_files = self.extract_result_files(output)
        result_content = self.extract_result_content(output)

        # Check 1: Expected files found
        expected_files = test_data.get("expected_files", [])
        if expected_files:
            found_expected = False
            for expected_file in expected_files:
                expected_normalized = self.normalize_path(expected_file)
                if any(expected_normalized in rf for rf in result_files):
                    found_expected = True
                    break

            if not found_expected:
                result["errors"].append(f"Expected file not found. Expected one of: {expected_files}, Got: {result_files}")
                result["passed"] = False

        # Check 2: Expected content present
        expected_content = test_data.get("expected_content", [])
        for expected in expected_content:
            if expected.lower() not in result_content:
                result["warnings"].append(f"Expected content missing: '{expected}'")

        # Check 3: Forbidden content NOT present (CRITICAL)
        forbidden_content = test_data.get("forbidden_content", [])
        for forbidden in forbidden_content:
            if forbidden.lower() in result_content:
                result["errors"].append(f"FORBIDDEN content found: '{forbidden}' (irrelevant result!)")
                result["passed"] = False

        # Check 4: Forbidden files NOT present (CRITICAL)
        forbidden_files = test_data.get("forbidden_files", [])
        for forbidden_file in forbidden_files:
            forbidden_normalized = self.normalize_path(forbidden_file)
            if any(forbidden_normalized in rf for rf in result_files):
                result["errors"].append(f"FORBIDDEN file found: '{forbidden_file}' (irrelevant result!)")
                result["passed"] = False

        # Check 5: Result found (not empty)
        if "[SOLUTION FOUND]" not in output and "[RESULTS]" not in output:
            result["errors"].append("No results found")
            result["passed"] = False

        return result

    def run_test(self, test_name: str, test_data: Dict) -> Dict:
        """Run a single test."""
        print(f"\n{'='*70}")
        print(f"TEST: {test_name}")
        print(f"Query: '{test_data['query']}'")
        print(f"Category: {test_data['category']}")
        print("-" * 70)

        # Run search
        output, elapsed = self.run_holo_search(test_data["query"])

        # Verify result
        result = self.verify_result(test_name, test_data, output, elapsed)

        # Print result
        if result["passed"]:
            print(f"[PASS] {elapsed:.2f}s")
            self.passed += 1
        else:
            print(f"[FAIL] {elapsed:.2f}s")
            self.failed += 1
            for error in result["errors"]:
                print(f"  ERROR: {error}")

        if result["warnings"]:
            for warning in result["warnings"]:
                print(f"  WARNING: {warning}")

        self.results.append(result)
        return result

    def run_random_tests(self, count: int = 5):
        """Run random subset of tests."""
        test_names = list(GROUND_TRUTH.keys())
        random.shuffle(test_names)
        selected = test_names[:count]

        print(f"\n{'='*70}")
        print(f"RUNNING {count} RANDOM TESTS (selected from {len(test_names)} total)")
        print(f"{'='*70}")

        for test_name in selected:
            self.run_test(test_name, GROUND_TRUTH[test_name])

    def run_all_tests(self):
        """Run all ground truth tests."""
        print(f"\n{'='*70}")
        print(f"RUNNING ALL TESTS ({len(GROUND_TRUTH)} total)")
        print(f"{'='*70}")

        for test_name, test_data in GROUND_TRUTH.items():
            self.run_test(test_name, test_data)

    def run_category_tests(self, category: str):
        """Run tests from specific category."""
        tests = {name: data for name, data in GROUND_TRUTH.items() if data["category"] == category}

        print(f"\n{'='*70}")
        print(f"RUNNING {category.upper()} TESTS ({len(tests)} total)")
        print(f"{'='*70}")

        for test_name, test_data in tests.items():
            self.run_test(test_name, test_data)

    def generate_report(self):
        """Generate final test report."""
        print(f"\n{'='*70}")
        print("RELEVANCE TEST REPORT")
        print(f"{'='*70}")

        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0

        print(f"\nTotal Tests: {total}")
        print(f"Passed: {self.passed} ({pass_rate:.1f}%)")
        print(f"Failed: {self.failed}")

        # Group by category
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"passed": 0, "failed": 0}

            if result["passed"]:
                categories[cat]["passed"] += 1
            else:
                categories[cat]["failed"] += 1

        print(f"\nBy Category:")
        for cat, stats in categories.items():
            total_cat = stats["passed"] + stats["failed"]
            pass_rate_cat = (stats["passed"] / total_cat * 100) if total_cat > 0 else 0
            print(f"  {cat:15} {stats['passed']}/{total_cat} ({pass_rate_cat:.1f}%)")

        # Failed tests detail
        if self.failed > 0:
            print(f"\nFailed Tests:")
            for result in self.results:
                if not result["passed"]:
                    print(f"\n  {result['test']} - '{result['query']}'")
                    for error in result["errors"]:
                        print(f"    - {error}")

        # Critical failures (forbidden content found)
        critical_failures = []
        for result in self.results:
            for error in result.get("errors", []):
                if "FORBIDDEN" in error:
                    critical_failures.append((result["test"], error))

        if critical_failures:
            print(f"\n{'!'*70}")
            print("CRITICAL FAILURES (Irrelevant Results Returned):")
            print(f"{'!'*70}")
            for test, error in critical_failures:
                print(f"  {test}: {error}")

        print(f"\n{'='*70}")

        if pass_rate == 100:
            print("[SUCCESS] All relevance tests passed!")
            return 0
        elif pass_rate >= 80:
            print(f"[WARNING] {self.failed} test(s) failed (pass rate: {pass_rate:.1f}%)")
            return 1
        else:
            print(f"[FAIL] {self.failed} test(s) failed (pass rate: {pass_rate:.1f}%)")
            return 2


def main():
    """Main test runner."""
    import sys

    tester = RelevanceTester()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            tester.run_all_tests()
        elif sys.argv[1] == "--random":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
            tester.run_random_tests(count)
        elif sys.argv[1].startswith("--category="):
            category = sys.argv[1].split("=")[1]
            tester.run_category_tests(category)
        else:
            print("Usage:")
            print("  python test_holo_relevance.py                 # 5 random tests")
            print("  python test_holo_relevance.py --all           # All tests")
            print("  python test_holo_relevance.py --random 10     # 10 random tests")
            print("  python test_holo_relevance.py --category=negative  # Category tests")
            sys.exit(1)
    else:
        # Default: 5 random tests
        tester.run_random_tests(5)

    exit_code = tester.generate_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
